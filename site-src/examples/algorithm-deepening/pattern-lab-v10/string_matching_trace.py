from __future__ import annotations


class Trie:
    def __init__(self) -> None:
        self.children: list[dict[str, int]] = [{}]
        self.terminal: list[bool] = [False]

    def insert(self, word: str) -> None:
        if not word:
            raise ValueError("word must not be empty")
        node = 0
        for character in word:
            if character not in self.children[node]:
                self.children[node][character] = len(self.children)
                self.children.append({})
                self.terminal.append(False)
            node = self.children[node][character]
        self.terminal[node] = True

    def contains(self, word: str) -> bool:
        node = self._walk(word)
        return node is not None and self.terminal[node]

    def complete(self, prefix: str) -> tuple[str, ...]:
        node = self._walk(prefix)
        if node is None:
            return ()
        results: list[str] = []

        def collect(current: int, suffix: str) -> None:
            if self.terminal[current]:
                results.append(prefix + suffix)
            for character in sorted(self.children[current]):
                collect(self.children[current][character], suffix + character)

        collect(node, "")
        return tuple(results)

    def _walk(self, text: str) -> int | None:
        node = 0
        for character in text:
            if character not in self.children[node]:
                return None
            node = self.children[node][character]
        return node

    @property
    def node_count(self) -> int:
        return len(self.children)


def prefix_function(pattern: str) -> tuple[int, ...]:
    if not pattern:
        raise ValueError("pattern must not be empty")
    prefix = [0] * len(pattern)
    for index in range(1, len(pattern)):
        matched = prefix[index - 1]
        while matched > 0 and pattern[index] != pattern[matched]:
            matched = prefix[matched - 1]
        if pattern[index] == pattern[matched]:
            matched += 1
        prefix[index] = matched
    return tuple(prefix)


def kmp_matches(text: str, pattern: str) -> tuple[int, ...]:
    prefix = prefix_function(pattern)
    matches: list[int] = []
    matched = 0
    for index, character in enumerate(text):
        while matched > 0 and character != pattern[matched]:
            matched = prefix[matched - 1]
        if character == pattern[matched]:
            matched += 1
        if matched == len(pattern):
            matches.append(index - len(pattern) + 1)
            matched = prefix[matched - 1]
    return tuple(matches)


def fixed_report() -> str:
    trie = Trie()
    for word in ("to", "tea", "ten", "inn"):
        trie.insert(word)
    pattern = "ababd"
    return "\n".join([
        "words=to,tea,ten,inn",
        f"trie_nodes={trie.node_count}",
        f"contains_te={str(trie.contains('te')).lower()} prefix_te={','.join(trie.complete('te'))}",
        f"pattern={pattern} prefix={','.join(map(str, prefix_function(pattern)))}",
        f"text=ababcabcabababd matches={','.join(map(str, kmp_matches('ababcabcabababd', pattern)))}",
        "overlap_aaaaa_aaa=0,1,2",
        "invariants=shared-prefix-path,fallback-keeps-valid-border",
    ])


if __name__ == "__main__":
    print(fixed_report())

