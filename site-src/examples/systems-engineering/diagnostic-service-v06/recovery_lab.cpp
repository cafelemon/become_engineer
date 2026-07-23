#include <algorithm>
#include <array>
#include <cerrno>
#include <csignal>
#include <cstring>
#include <fcntl.h>
#include <iostream>
#include <stdexcept>
#include <string>
#include <sys/socket.h>
#include <sys/wait.h>
#include <unistd.h>

namespace {

bool descriptor_is_open(int descriptor) {
  errno = 0;
  return fcntl(descriptor, F_GETFD) >= 0 || errno != EBADF;
}

void require(bool condition, const char* message) {
  if (!condition) {
    throw std::runtime_error(message);
  }
}

}  // namespace

int main() {
  try {
    std::signal(SIGPIPE, SIG_IGN);

    int leak_pipe[2] = {-1, -1};
    require(pipe(leak_pipe) == 0, "pipe creation failed");
    const int injected_leak = leak_pipe[0];
    require(descriptor_is_open(injected_leak), "injected fd was not open");
    require(close(injected_leak) == 0, "leaked fd recovery close failed");
    require(!descriptor_is_open(injected_leak), "fd remained open after recovery");
    require(close(leak_pipe[1]) == 0, "pipe writer close failed");

    const pid_t child = fork();
    require(child >= 0, "fork failed");
    if (child == 0) {
      _exit(7);
    }
    int child_status = 0;
    require(waitpid(child, &child_status, 0) == child, "waitpid failed");
    require(WIFEXITED(child_status) && WEXITSTATUS(child_status) == 7,
            "child failure was not preserved");

    int broken_pair[2] = {-1, -1};
    require(socketpair(AF_UNIX, SOCK_STREAM, 0, broken_pair) == 0,
            "broken socketpair creation failed");
    require(close(broken_pair[1]) == 0, "peer close failed");
    errno = 0;
    const char probe = 'x';
    const ssize_t broken_send = send(broken_pair[0], &probe, 1, 0);
    require(broken_send < 0 && errno == EPIPE, "EPIPE was not observed");
    require(close(broken_pair[0]) == 0, "broken writer close failed");

    int recovered_pair[2] = {-1, -1};
    require(socketpair(AF_UNIX, SOCK_STREAM, 0, recovered_pair) == 0,
            "recovery socketpair creation failed");
    constexpr std::array<char, 2> message{'o', 'k'};
    require(send(recovered_pair[0], message.data(), message.size(), 0) ==
                static_cast<ssize_t>(message.size()),
            "recovery send failed");
    std::array<char, message.size()> received{};
    require(recv(recovered_pair[1], received.data(), received.size(), 0) ==
                static_cast<ssize_t>(received.size()),
            "recovery receive failed");
    require(received == message, "recovery message changed");
    require(close(recovered_pair[0]) == 0 &&
                close(recovered_pair[1]) == 0,
            "recovered pair close failed");

    std::array<char, 64> temporary_path{};
    const std::string pattern = "/tmp/diagnostic-recovery-XXXXXX";
    std::copy(pattern.begin(), pattern.end(), temporary_path.begin());
    const int temporary_fd = mkstemp(temporary_path.data());
    require(temporary_fd >= 0, "temporary file creation failed");
    require(write(temporary_fd, message.data(), message.size()) ==
                static_cast<ssize_t>(message.size()),
            "temporary file write failed");
    require(close(temporary_fd) == 0, "temporary file close failed");
    require(unlink(temporary_path.data()) == 0, "temporary file cleanup failed");
    require(access(temporary_path.data(), F_OK) != 0 && errno == ENOENT,
            "temporary artifact remained");

    std::cout << "fault=descriptor-leak injected=1\n";
    std::cout << "detector=fd-still-open\n";
    std::cout << "fd_recovery=explicit-close\n";
    std::cout << "fd_after_recovery=closed\n";
    std::cout << "child_fault=exit-7\n";
    std::cout << "child_recovery=reaped\n";
    std::cout << "transport_fault=EPIPE-observed\n";
    std::cout << "transport_recovery=reconnected\n";
    std::cout << "temporary_artifact=removed\n";
    std::cout << "resource_baseline=restored\n";
    return 0;
  } catch (const std::exception& error) {
    std::cerr << error.what() << '\n';
    return 1;
  }
}
