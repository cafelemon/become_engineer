from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class TextTrace:
    text: str
    code_points: int
    utf8_bytes: int
    ascii_count: int
    multibyte_count: int
    utf8_hex: str


def analyze_text(text: str) -> TextTrace:
    encoded = text.encode("utf-8")
    ascii_count = sum(ord(character) <= 0x7F for character in text)
    code_points = len(text)
    return TextTrace(
        text=text,
        code_points=code_points,
        utf8_bytes=len(encoded),
        ascii_count=ascii_count,
        multibyte_count=code_points - ascii_count,
        utf8_hex=encoded.hex(" "),
    )


def decode_strict(data: bytes) -> str:
    return data.decode("utf-8", errors="strict")


def main() -> None:
    trace = analyze_text("A工🧪")
    print(f"text={trace.text!r}")
    print(
        f"code_points={trace.code_points}, "
        f"utf8_bytes={trace.utf8_bytes}"
    )
    print(
        f"ascii={trace.ascii_count}, "
        f"multibyte={trace.multibyte_count}"
    )
    print(f"hex={trace.utf8_hex}")
    restored = decode_strict(trace.text.encode("utf-8"))
    print(f"round_trip={restored == trace.text}")


if __name__ == "__main__":
    main()
