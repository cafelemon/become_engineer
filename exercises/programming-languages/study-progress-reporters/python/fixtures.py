from models import StudyRecord


def sample_records() -> list[StudyRecord]:
    return [
        StudyRecord("Python 起步", 10.0, 7.5, ["python", "基础"]),
        StudyRecord("C++ 核心", 12.0, 12.0, ["cpp", "基础"]),
        StudyRecord("算法练习", 8.0, 4.0, ["算法", "基础", "基础"]),
        StudyRecord("工程复盘", 5.0, 7.0, ["工程", "复盘"]),
    ]
