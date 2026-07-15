from models import StudyRecord


def sample_records() -> list[StudyRecord]:
    return [
        {
            "course_name": "Python 起步",
            "target_hours": 10.0,
            "completed_hours": 7.5,
            "tags": ["python", "基础"],
        },
        {
            "course_name": "C++ 核心",
            "target_hours": 12.0,
            "completed_hours": 12.0,
            "tags": ["cpp", "基础"],
        },
        {
            "course_name": "算法练习",
            "target_hours": 8.0,
            "completed_hours": 4.0,
            "tags": ["算法", "基础", "基础"],
        },
        {
            "course_name": "工程复盘",
            "target_hours": 5.0,
            "completed_hours": 7.0,
            "tags": ["工程", "复盘"],
        },
    ]
