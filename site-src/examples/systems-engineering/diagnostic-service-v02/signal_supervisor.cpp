#include <cerrno>
#include <cstdlib>
#include <cstring>
#include <iostream>
#include <stdexcept>
#include <string_view>
#include <utility>

#include <fcntl.h>
#include <signal.h>
#include <sys/wait.h>
#include <unistd.h>

class UniqueFd {
 public:
  explicit UniqueFd(int fd = -1) noexcept : fd_(fd) {}
  ~UniqueFd() { reset(); }
  UniqueFd(const UniqueFd&) = delete;
  UniqueFd& operator=(const UniqueFd&) = delete;
  UniqueFd(UniqueFd&& other) noexcept : fd_(std::exchange(other.fd_, -1)) {}
  UniqueFd& operator=(UniqueFd&& other) noexcept {
    if (this != &other) reset(std::exchange(other.fd_, -1));
    return *this;
  }
  [[nodiscard]] int get() const noexcept { return fd_; }
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

volatile sig_atomic_t signal_number = 0;
int signal_event_write_fd = -1;

extern "C" void notify_signal(int signo) {
  const int saved_errno = errno;
  signal_number = signo;
  const unsigned char marker = 1;
  if (signal_event_write_fd >= 0) {
    (void)::write(signal_event_write_fd, &marker, sizeof(marker));
  }
  errno = saved_errno;
}

void install_handler() {
  struct sigaction action {};
  action.sa_handler = notify_signal;
  sigemptyset(&action.sa_mask);
  action.sa_flags = 0;
  if (::sigaction(SIGTERM, &action, nullptr) != 0) {
    throw std::runtime_error("sigaction failed");
  }
}

void set_nonblocking(int fd) {
  const int flags = ::fcntl(fd, F_GETFL);
  if (flags == -1 || ::fcntl(fd, F_SETFL, flags | O_NONBLOCK) == -1) {
    throw std::runtime_error("fcntl failed");
  }
}

void write_marker(int fd) {
  const unsigned char marker = 1;
  if (::write(fd, &marker, sizeof(marker)) != 1) {
    throw std::runtime_error("ready write failed");
  }
}

void read_marker(int fd) {
  unsigned char marker = 0;
  for (;;) {
    const ssize_t received = ::read(fd, &marker, sizeof(marker));
    if (received == -1 && errno == EINTR) continue;
    if (received != 1) throw std::runtime_error("event read failed");
    return;
  }
}

int parse_child_exit(int argc, char** argv) {
  if (argc == 1) return 0;
  if (argc != 3 || std::string_view(argv[1]) != "--child-exit") {
    throw std::invalid_argument("usage: signal_supervisor [--child-exit 0..125]");
  }
  char* end = nullptr;
  const long value = std::strtol(argv[2], &end, 10);
  if (*argv[2] == '\0' || *end != '\0' || value < 0 || value > 125) {
    throw std::invalid_argument("child exit must be from 0 to 125");
  }
  return static_cast<int>(value);
}

int main(int argc, char** argv) {
  int child_exit = 0;
  try {
    child_exit = parse_child_exit(argc, argv);
  } catch (const std::invalid_argument& error) {
    std::cerr << "argument_error=" << error.what() << '\n';
    return 2;
  }

  int parent_event_raw[2];
  int child_event_raw[2];
  int ready_raw[2];
  if (::pipe(parent_event_raw) != 0 || ::pipe(child_event_raw) != 0 ||
      ::pipe(ready_raw) != 0) {
    std::cerr << "pipe_error=" << std::strerror(errno) << '\n';
    return 2;
  }
  UniqueFd parent_read(parent_event_raw[0]);
  UniqueFd parent_write(parent_event_raw[1]);
  UniqueFd child_read(child_event_raw[0]);
  UniqueFd child_write(child_event_raw[1]);
  UniqueFd ready_read(ready_raw[0]);
  UniqueFd ready_write(ready_raw[1]);

  try {
    set_nonblocking(parent_write.get());
    set_nonblocking(child_write.get());
    signal_event_write_fd = parent_write.get();
    install_handler();
  } catch (const std::runtime_error& error) {
    std::cerr << "setup_error=" << error.what() << '\n';
    return 2;
  }

  const pid_t child = ::fork();
  if (child == -1) {
    std::cerr << "fork_error=" << std::strerror(errno) << '\n';
    return 2;
  }
  if (child == 0) {
    parent_read.reset();
    parent_write.reset();
    ready_read.reset();
    signal_number = 0;
    signal_event_write_fd = child_write.get();
    try {
      install_handler();
      write_marker(ready_write.get());
      ready_write.reset();
      read_marker(child_read.get());
      child_read.reset();
      child_write.reset();
      _exit(child_exit);
    } catch (...) {
      _exit(126);
    }
  }

  child_read.reset();
  child_write.reset();
  ready_write.reset();
  try {
    read_marker(ready_read.get());
    ready_read.reset();
    if (::kill(::getpid(), SIGTERM) != 0) throw std::runtime_error("self signal failed");
    read_marker(parent_read.get());
    if (::kill(child, SIGTERM) != 0) throw std::runtime_error("child signal failed");
  } catch (const std::runtime_error& error) {
    std::cerr << "supervisor_error=" << error.what() << '\n';
    (void)::kill(child, SIGKILL);
    (void)::waitpid(child, nullptr, 0);
    return 2;
  }

  int status = 0;
  while (::waitpid(child, &status, 0) == -1) {
    if (errno != EINTR) {
      std::cerr << "wait_error=" << std::strerror(errno) << '\n';
      return 2;
    }
  }
  const int exit_code = WIFEXITED(status) ? WEXITSTATUS(status) : 128;

  parent_read.reset();
  parent_write.reset();
  signal_event_write_fd = -1;
  std::cout << "signal_handler=notification-only\n";
  std::cout << "supervisor_event="
            << (signal_number == SIGTERM ? "SIGTERM" : "unexpected") << '\n';
  std::cout << "worker_stop=requested\n";
  std::cout << "worker_cleanup=confirmed-by-exit\n";
  std::cout << "worker_exit=" << exit_code << '\n';
  std::cout << "worker_reaped=yes\n";
  std::cout << "self_pipe=closed\n";
  std::cout << "supervision_result=" << (exit_code == 0 ? "pass" : "child-failure") << '\n';
  return exit_code == 0 ? 0 : 1;
}
