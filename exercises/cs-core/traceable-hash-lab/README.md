# 可追踪哈希实验

这是 CS 核心第 9–11 课共用的阶段作品。Python 3.11 与 C++20 使用同一组确定性规则观察桶冲突、分离链接、扩容和集合应用；只依赖标准库。

## 三种运行模式

| 模式 | 观察对象 | 稳定证据 |
| --- | --- | --- |
| `hash` | `key % bucket_count` 与冲突链 | 桶号、插入前链长、首个冲突 |
| `table` | 分离链接哈希表 | 键比较次数、负载、扩容与搬移数 |
| `applications` | 集合与频次映射 | 首个重复值、保序去重、排序频次 |

无参数等价于 `hash`。未知模式只写入标准错误并返回退出码 `2`。

## Python

```bash
cd exercises/cs-core/traceable-hash-lab/python
python3 -m venv .venv
.venv/bin/python -m pip install -e '.[dev]'
.venv/bin/python -m traceable_hash_lab hash
.venv/bin/python -m traceable_hash_lab table
.venv/bin/python -m traceable_hash_lab applications
.venv/bin/python -m unittest discover -s tests -v
.venv/bin/python -m mypy --strict src tests
```

## C++

```bash
cd exercises/cs-core/traceable-hash-lab
cmake -S cpp -B /tmp/traceable-hash-build -DCMAKE_BUILD_TYPE=Release
cmake --build /tmp/traceable-hash-build
ctest --test-dir /tmp/traceable-hash-build --output-on-failure
/tmp/traceable-hash-build/traceable_hash_lab hash
/tmp/traceable-hash-build/traceable_hash_lab table
/tmp/traceable-hash-build/traceable_hash_lab applications
```

## 公开契约

- `bucket_index`、`trace_bucket_inserts`、`build_bucket_chains`、`first_collision`
- `TraceableHashMap.put/get/erase/size/bucket_count/load_factor/items_sorted`
- `first_duplicate`、`count_frequencies`、`deduplicate_preserving_order`
- Python 公开 `BucketEvent`、`PutTrace`、`LookupTrace`、`EraseTrace`、`DuplicateTrace`、`FrequencyRow`；C++ 提供等价结构。

教学哈希只接受非负整数键，固定为 `key % bucket_count`。这条规则只服务于可复现练习，不描述 Python `dict`／`set` 或 C++ 无序关联容器的实际哈希算法。哈希表最大负载因子固定为 `1.0`：新键插入将超过阈值时桶数翻倍并搬移全部旧键；已有键更新不增加大小，也不提前扩容。

## 迁移任务

- 第 9 课：实现 `first_collision`，返回输入顺序中的首个冲突事件。
- 第 10 课：实现 `erase`，记录桶号和比较次数，缺失时保持状态不变。
- 第 11 课：实现 `deduplicate_preserving_order`，用集合判重并显式保留首次出现顺序。

课程入口：[第 9 课：哈希函数、键相等与冲突](../../../learning-paths/cs-core/09-hash-function-key-equality-collisions.md)。
