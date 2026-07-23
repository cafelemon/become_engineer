#include <array>
#include <cerrno>
#include <cstring>
#include <fcntl.h>
#include <iostream>
#include <poll.h>
#include <stdexcept>
#include <string>
#include <sys/socket.h>
#include <unistd.h>

namespace {

class FileDescriptor {
 public:
  explicit FileDescriptor(int value) : value_(value) {}
  FileDescriptor(const FileDescriptor&) = delete;
  FileDescriptor& operator=(const FileDescriptor&) = delete;
  ~FileDescriptor() {
    if (value_ >= 0) {
      close(value_);
    }
  }

  int get() const { return value_; }

 private:
  int value_;
};

void make_nonblocking(int descriptor) {
  const int flags = fcntl(descriptor, F_GETFL, 0);
  if (flags < 0 || fcntl(descriptor, F_SETFL, flags | O_NONBLOCK) < 0) {
    throw std::runtime_error("failed to enable O_NONBLOCK");
  }
}

short poll_events(int descriptor, short events, int timeout_ms) {
  pollfd candidate{descriptor, events, 0};
  const int result = poll(&candidate, 1, timeout_ms);
  if (result < 0) {
    throw std::runtime_error("poll failed");
  }
  return candidate.revents;
}

}  // namespace

int main() {
  try {
    int raw_descriptors[2] = {-1, -1};
    if (socketpair(AF_UNIX, SOCK_STREAM, 0, raw_descriptors) != 0) {
      throw std::runtime_error("socketpair failed");
    }
    FileDescriptor writer(raw_descriptors[0]);
    FileDescriptor reader(raw_descriptors[1]);
    make_nonblocking(writer.get());
    make_nonblocking(reader.get());

    std::array<char, 4096> payload{};
    payload.fill('x');
    bool saw_would_block = false;
    constexpr std::size_t kMaximumWrites = 65536;
    for (std::size_t attempt = 0; attempt < kMaximumWrites; ++attempt) {
      const ssize_t sent =
          send(writer.get(), payload.data(), payload.size(), MSG_NOSIGNAL);
      if (sent > 0) {
        continue;
      }
      if (sent < 0 && (errno == EAGAIN || errno == EWOULDBLOCK)) {
        saw_would_block = true;
        break;
      }
      throw std::runtime_error("send failed before backpressure");
    }
    if (!saw_would_block) {
      throw std::runtime_error("bounded write loop did not reach backpressure");
    }

    const bool writable_while_full =
        (poll_events(writer.get(), POLLOUT, 0) & POLLOUT) != 0;

    std::array<char, 16384> drain_buffer{};
    bool drained_any = false;
    while (true) {
      const ssize_t received =
          recv(reader.get(), drain_buffer.data(), drain_buffer.size(), 0);
      if (received > 0) {
        drained_any = true;
        continue;
      }
      if (received < 0 && (errno == EAGAIN || errno == EWOULDBLOCK)) {
        break;
      }
      if (received == 0) {
        break;
      }
      throw std::runtime_error("recv failed while draining");
    }
    if (!drained_any) {
      throw std::runtime_error("peer did not drain queued bytes");
    }

    const bool writable_after_drain =
        (poll_events(writer.get(), POLLOUT, 1000) & POLLOUT) != 0;
    if (!writable_after_drain) {
      throw std::runtime_error("writer did not become writable after drain");
    }

    constexpr std::array<char, 6> marker{'r', 'e', 's', 'u', 'm', 'e'};
    const ssize_t resumed =
        send(writer.get(), marker.data(), marker.size(), MSG_NOSIGNAL);
    if (resumed != static_cast<ssize_t>(marker.size())) {
      throw std::runtime_error("resume send was incomplete");
    }
    const bool reader_ready =
        (poll_events(reader.get(), POLLIN, 1000) & POLLIN) != 0;
    if (!reader_ready) {
      throw std::runtime_error("reader did not observe resumed message");
    }

    std::array<char, marker.size()> received_marker{};
    const ssize_t marker_size =
        recv(reader.get(), received_marker.data(), received_marker.size(), 0);
    if (marker_size != static_cast<ssize_t>(marker.size()) ||
        received_marker != marker) {
      throw std::runtime_error("resumed message was not preserved");
    }

    std::cout << "transport=unix-socketpair\n";
    std::cout << "writer=nonblocking\n";
    std::cout << "backpressure=EAGAIN-observed\n";
    std::cout << "poll_while_full="
              << (writable_while_full ? "writable" : "not-writable") << '\n';
    std::cout << "peer_drain=performed\n";
    std::cout << "poll_after_drain=writable\n";
    std::cout << "resume_send=pass\n";
    std::cout << "reader_event=readable\n";
    std::cout << "socketpair=closed-by-raii\n";
    return writable_while_full ? 2 : 0;
  } catch (const std::exception& error) {
    std::cerr << error.what() << '\n';
    return 1;
  }
}
