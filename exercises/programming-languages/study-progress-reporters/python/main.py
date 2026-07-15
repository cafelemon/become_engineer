from fixtures import sample_records
from reporting import build_report


def main() -> int:
    print(build_report(sample_records()))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
