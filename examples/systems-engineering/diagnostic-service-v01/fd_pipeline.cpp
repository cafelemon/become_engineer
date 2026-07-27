#include <algorithm>
#include <cerrno>
#include <cstring>
#include <iostream>
#include <stdexcept>
#include <string>
#include <string_view>
#include <utility>

#include <fcntl.h>
#include <unistd.h>

class UniqueFd {
 public:
  explicit UniqueFd(int fd = -1) noexcept : fd_(fd) {}
  ~UniqueFd() { reset(); }

  UniqueFd(const UniqueFd&) = delete;
  UniqueFd& operator=(const UniqueFd&) = delete;

  UniqueFd(UniqueFd&& other) noexcept : fd_(std::exchange(other.fd_, -1)) {}
  UniqueFd& operator=(UniqueFd&& other) noexcept {
    if (this != &other) {
      reset(std::exchange(other.fd_, -1));
    }
    return *this;
  }

  [[nodiscard]] int get() const noexcept { return fd_; }
  [[nodiscard]] bool valid() const noexcept { return fd_ >= 0; }

  void reset(int replacement = -1) noexcept {
    if (fd_ >= 0) {
      while (::close(fd_) == -1 && errno == EINTR) {
      }
    }
    fd_ = replacement;
  }

 private:
  int fd_;
};

struct Transfer {
  std::string payload;
  int write_calls = 0;
  int read_calls = 0;
};

void write_all_limited(int fd, std::string_view payload, Transfer& trace) {
  std::size_t offset = 0;
  while (offset < payload.size()) {
    const std::size_t request = std::min<std::size_t>(3, payload.size() - offset);
    const ssize_t written = ::write(fd, payload.data() + offset, request);
    ++trace.write_calls;
    if (written == -1 && errno == EINTR) {
      continue;
    }
    if (written <= 0) {
      throw std::runtime_error("write failed");
    }
    offset += static_cast<std::size_t>(written);
  }
}

void read_to_eof_limited(int fd, Transfer& trace) {
  char buffer[4];
  for (;;) {
    const ssize_t received = ::read(fd, buffer, sizeof(buffer));
    ++trace.read_calls;
    if (received == -1 && errno == EINTR) {
      continue;
    }
    if (received == -1) {
      throw std::runtime_error("read failed");
    }
    if (received == 0) {
      return;
    }
    trace.payload.append(buffer, static_cast<std::size_t>(received));
  }
}

bool descriptor_is_open(int fd) {
  errno = 0;
  return ::fcntl(fd, F_GETFD) != -1 || errno != EBADF;
}

int main() {
  int raw_pipe[2];
  if (::pipe(raw_pipe) != 0) {
    std::cerr << "pipe_error=" << std::strerror(errno) << '\n';
    return 2;
  }

  UniqueFd read_end(raw_pipe[0]);
  UniqueFd write_end(raw_pipe[1]);
  UniqueFd moved_write(std::move(write_end));

  const std::string expected = "hello-fd-io";
  Transfer trace;
  write_all_limited(moved_write.get(), expected, trace);
  moved_write.reset();
  read_to_eof_limited(read_end.get(), trace);

  const int observed_read_fd = read_end.get();
  std::cout << "payload_bytes=" << trace.payload.size() << '\n';
  std::cout << "write_calls=" << trace.write_calls << " read_calls=" << trace.read_calls << '\n';
  std::cout << "roundtrip=" << (trace.payload == expected ? "pass" : "fail") << '\n';
  std::cout << "move_source=" << (write_end.valid() ? "open" : "empty")
            << " move_target=closed-after-write\n";
  std::cout << "read_end_before_close="
            << (descriptor_is_open(observed_read_fd) ? "open" : "closed") << '\n';
  read_end.reset();
  std::cout << "read_end_after_close="
            << (descriptor_is_open(observed_read_fd) ? "open" : "closed") << '\n';
  std::cout << "all_descriptors=closed\n";
  return trace.payload == expected ? 0 : 1;
}
