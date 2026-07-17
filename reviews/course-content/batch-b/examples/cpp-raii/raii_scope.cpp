#include <fstream>
#include <iostream>
#include <string>
#include <utility>

class ScopeNote {
public:
    explicit ScopeNote(std::string name) : name_{std::move(name)} {
        std::cout << "进入：" << name_ << '\n';
    }
    ~ScopeNote() { std::cout << "离开：" << name_ << '\n'; }

private:
    std::string name_;
};

bool write_audit(const std::string& path) {
    ScopeNote note{"write_audit"};
    std::ofstream output{path};
    if (!output) {
        return false;
    }
    output << "学习审计快照\n";
    return static_cast<bool>(output);
}

int main(int argc, char* argv[]) {
    const std::string path{argc > 1 ? argv[1] : "audit.txt"};
    const bool ok{write_audit(path)};
    std::cout << "写入：" << (ok ? "成功" : "失败") << '\n';
    return ok ? 0 : 1;
}
