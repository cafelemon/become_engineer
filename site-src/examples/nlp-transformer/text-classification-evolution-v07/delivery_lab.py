"""Compare offline NLP candidates, freeze one selection, then open test once."""

from __future__ import annotations

import argparse
import importlib.util
import json
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
BASE = HERE.parent
MODULES = {
    "v01": ("text-classification-evolution-v01", "experiment.py"),
    "v02": ("text-classification-evolution-v02", "experiment.py"),
    "v03": ("text-classification-evolution-v03", "embedding_lab.py"),
    "v04": ("text-classification-evolution-v04", "sequence_lab.py"),
    "v05": ("text-classification-evolution-v05", "attention_lab.py"),
    "v06": ("text-classification-evolution-v06", "transformer_lab.py"),
}
EXPECTED_CORPUS_SHA = "8973927ed683f32cf92bb4a1483b960f3b8c09b0b8497bd0c5176891252b713c"
SELECTION_RULE = "eligible candidates only: highest validation macro_f1, then accuracy, then fewer parameters, then lexical candidate_id"


def load_module(version: str):
    folder, filename = MODULES[version]
    path = BASE / folder / filename
    spec = importlib.util.spec_from_file_location(f"nlp_delivery_{version}", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"required project version missing: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def protocol_from_manifest(v01, rows, partitions) -> dict:
    manifest = v01.build_manifest(rows, partitions)
    if manifest["corpus_sha256"] != EXPECTED_CORPUS_SHA:
        raise ValueError("corpus fingerprint changed; freeze a new evaluation protocol")
    return {
        "corpus_sha256": manifest["corpus_sha256"],
        "split_seed": manifest["seed"],
        "train_ids": manifest["partitions"]["train"]["sample_ids"],
        "validation_ids": manifest["partitions"]["validation"]["sample_ids"],
        "test_ids": manifest["partitions"]["test"]["sample_ids"],
    }


def verify_report_protocol(report: dict, protocol: dict, version: str) -> None:
    for key in ("corpus_sha256", "split_seed", "train_ids", "validation_ids"):
        if report.get(key) != protocol[key]:
            raise ValueError(f"{version} report disagrees on {key}")
    if version == "v02":
        sealed = str(report.get("test_policy", "")).startswith("sealed")
    else:
        sealed = report.get("test_status") == "sealed"
    if not sealed:
        raise ValueError(f"{version} tested before selection")


def candidate(candidate_id: str, family: str, validation: dict, errors: list[str], parameters: int, train_seconds: float | None, run_seconds: float) -> dict:
    if set(validation) != {"accuracy", "macro_f1", "confusion"}:
        raise ValueError(f"{candidate_id} has incomplete validation metrics")
    if not 0 <= validation["accuracy"] <= 1 or not 0 <= validation["macro_f1"] <= 1:
        raise ValueError(f"{candidate_id} has invalid metrics")
    if parameters < 1:
        raise ValueError(f"{candidate_id} has invalid parameter count")
    return {"candidate_id": candidate_id, "family": family, "validation": validation,
            "validation_error_ids": errors, "parameter_count": parameters,
            "train_seconds_observed": train_seconds, "validation_run_seconds_observed": run_seconds,
            "eligible_for_release": True}


def collect_validation() -> dict:
    """Run existing v02-v06 validation paths; do not predict or score test."""
    modules = {version: load_module(version) for version in MODULES}
    v01 = modules["v01"]
    rows = v01.read_corpus()
    partitions = v01.split_rows(rows)
    protocol = protocol_from_manifest(v01, rows, partitions)
    reports = {}
    run_seconds = {}
    for version, function in (("v02", modules["v02"].run), ("v03", modules["v03"].run_validation),
                              ("v04", modules["v04"].run_validation), ("v05", modules["v05"].run_validation),
                              ("v06", modules["v06"].run_validation)):
        started = time.perf_counter()
        reports[version] = function()
        run_seconds[version] = round(time.perf_counter() - started, 4)
    for version, report in reports.items():
        verify_report_protocol(report, protocol, version)
    v02, v03, v04, v05, v06 = (reports[version] for version in ("v02", "v03", "v04", "v05", "v06"))
    candidates = [
        candidate("v02-linear", "TF-IDF + logistic", v02["model_validation"],
                  [row["sample_id"] for row in v02["validation_errors"]], v02["vocabulary_size"] + 1, None, run_seconds["v02"]),
        candidate("v03-embedding", "masked mean Embedding", v03["model_validation"],
                  [row["sample_id"] for row in v03["validation_errors"]], v03["parameter_count"], v03["train_seconds"], run_seconds["v03"]),
        candidate("v04-gru", "GRU", v04["results"]["gru"]["validation"],
                  v04["results"]["gru"]["errors"], v04["results"]["gru"]["parameter_count"], v04["results"]["gru"]["train_seconds"], run_seconds["v04"]),
        candidate("v04-cnn", "CNN", v04["results"]["cnn"]["validation"],
                  v04["results"]["cnn"]["errors"], v04["results"]["cnn"]["parameter_count"], v04["results"]["cnn"]["train_seconds"], run_seconds["v04"]),
        candidate("v05-attention", "single-head attention", v05["model_validation"],
                  [row["sample_id"] for row in v05["validation_errors"]], v05["parameter_count"], v05["train_seconds"], run_seconds["v05"]),
        candidate("v06-encoder-full", "Transformer Encoder with position and padding mask",
                  v06["variants"]["full"]["model_validation"],
                  [row["sample_id"] for row in v06["variants"]["full"]["validation_errors"]],
                  v06["variants"]["full"]["parameter_count"], v06["variants"]["full"]["train_seconds"], run_seconds["v06"]),
    ]
    ablations = {
        name: {"validation": v06["variants"][name]["model_validation"],
               "error_ids": [row["sample_id"] for row in v06["variants"][name]["validation_errors"]],
               "eligible_for_release": False, "reason": "intentional structure-removal diagnostic"}
        for name in ("no_position", "no_key_padding_mask")
    }
    return {"project_version": "0.7", "protocol": protocol, "selection_rule": SELECTION_RULE,
            "candidates": candidates, "ablations_not_candidates": ablations,
            "test_status": "sealed_before_selection"}


def select_candidate(plan: dict) -> dict:
    eligible = [item for item in plan["candidates"] if item["eligible_for_release"]]
    if not eligible:
        raise ValueError("no eligible candidate")
    # Reverse metric order without changing the declared tie-breakers.
    return min(eligible, key=lambda item: (-item["validation"]["macro_f1"],
                                            -item["validation"]["accuracy"],
                                            item["parameter_count"], item["candidate_id"]))


def score_rows(rows: list[dict[str, str]], predictions: dict[str, str]) -> dict:
    """Use only after a candidate has been selected and the test receipt exists."""
    ids = {row["sample_id"] for row in rows}
    if set(predictions) != ids or set(predictions.values()) - {"code", "plan"}:
        raise ValueError("predictions must cover exactly the final rows with known labels")
    labels = ("code", "plan")
    confusion = {actual: {predicted: 0 for predicted in labels} for actual in labels}
    for row in rows:
        confusion[row["label"]][predictions[row["sample_id"]]] += 1
    accuracy = sum(confusion[label][label] for label in labels) / len(rows)
    per_class_f1 = []
    for label in labels:
        tp = confusion[label][label]
        fp = sum(confusion[other][label] for other in labels if other != label)
        fn = sum(confusion[label][other] for other in labels if other != label)
        per_class_f1.append(2 * tp / (2 * tp + fp + fn) if 2 * tp + fp + fn else 0.0)
    return {"accuracy": accuracy, "macro_f1": sum(per_class_f1) / 2, "confusion": confusion,
            "error_ids": [row["sample_id"] for row in rows if predictions[row["sample_id"]] != row["label"]]}


def predict_final(candidate_id: str, train_rows: list[dict[str, str]], test_rows: list[dict[str, str]]) -> dict[str, str]:
    if candidate_id == "v02-linear":
        v02 = load_module("v02")
        idf = v02.fit_vectorizer([row["text"] for row in train_rows])
        weights, bias = v02.train_linear(train_rows, idf)
        return {row["sample_id"]: v02.predict(row["text"], idf, weights, bias) for row in test_rows}
    if candidate_id == "v03-embedding":
        v03 = load_module("v03")
        model, vocab = v03.fit(train_rows)
        return v03.predict(model, test_rows, vocab)
    if candidate_id in ("v04-gru", "v04-cnn"):
        v04 = load_module("v04")
        model, vocab = v04.fit(train_rows, candidate_id.removeprefix("v04-"))
        return v04.predict(model, test_rows, vocab)
    if candidate_id == "v05-attention":
        v05 = load_module("v05")
        model, vocab = v05.fit(train_rows)
        return v05.predict(model, test_rows, vocab)
    if candidate_id == "v06-encoder-full":
        v03, v06 = load_module("v03"), load_module("v06")
        vocab = v03.build_vocab(train_rows)
        model = v06.fit(train_rows, vocab, use_position=True, use_key_padding_mask=True)
        return v06.predict(model, test_rows, vocab)
    raise ValueError("candidate is not a release-eligible model")


def model_card(plan: dict, selected: dict, final: dict) -> str:
    validation = selected["validation"]
    test = final["test"]
    return "\n".join([
        "# 文本分类模型卡 v0.7", "",
        f"- 选中模型：`{selected['candidate_id']}`（{selected['family']}）。",
        f"- 选择规则：{plan['selection_rule']}。v0.6 两个消融变体不具备发布资格。",
        f"- 数据：40 条原创教学短句；train/validation/test=24/8/8；语料 SHA-256 `{plan['protocol']['corpus_sha256']}`。",
        f"- 验证：accuracy={validation['accuracy']:.3f}，macro-F1={validation['macro_f1']:.3f}，错误 ID={','.join(selected['validation_error_ids']) or '无'}。",
        f"- 最终测试：accuracy={test['accuracy']:.3f}，macro-F1={test['macro_f1']:.3f}，错误 ID={','.join(test['error_ids']) or '无'}。只对获选模型打开一次，不据测试结果回头重选。",
        f"- 参数量：{selected['parameter_count']}；训练耗时为本机单次观察，不是跨机器性能基准。",
        "- 用途：教学演示同一协议下的模型比较；不用于真实用户分流、自动决策或生产上线。",
        "- 已知限制：样本极少且人工构造；标签范围狭窄；近重复、分布迁移、隐私与公平性未作生产评估。",
        "- 预训练路径：本轮未下载、微调或测量任何预训练权重。可选人工实验必须另记模型来源与许可、权重版本、数据许可、计算成本、相同划分及新模型卡；不能把离线适配器写成预训练实测。",
        "- 可复查文件：selection.json、test-opened.json、final-report.json 与本卡。",
        "",
    ])


def finalize(output: Path) -> dict:
    """A fresh output directory is a one-shot receipt for this evaluation run."""
    if output.exists() and any(output.iterdir()):
        raise FileExistsError("final output directory must be new or empty; do not reopen test")
    plan = collect_validation()
    selected = select_candidate(plan)
    v01 = load_module("v01")
    rows = v01.read_corpus()
    partitions = v01.split_rows(rows)
    if protocol_from_manifest(v01, rows, partitions) != plan["protocol"]:
        raise ValueError("protocol changed after selection")
    output.mkdir(parents=True, exist_ok=True)
    (output / "selection.json").write_text(json.dumps({"selection_rule": plan["selection_rule"], "selected": selected,
                                                       "protocol": plan["protocol"]}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    # Write the receipt before any test prediction. A failed run requires human review, not a silent retry.
    with (output / "test-opened.json").open("x", encoding="utf-8") as receipt:
        receipt.write(json.dumps({"candidate_id": selected["candidate_id"], "test_ids": plan["protocol"]["test_ids"],
                                  "policy": "one final evaluation; no reselection"}, ensure_ascii=False, indent=2) + "\n")
    predictions = predict_final(selected["candidate_id"], partitions["train"], partitions["test"])
    test = score_rows(partitions["test"], predictions)
    final = {"project_version": "0.7", "selected_candidate": selected["candidate_id"],
             "selection_rule": plan["selection_rule"], "corpus_sha256": plan["protocol"]["corpus_sha256"],
             "validation": selected["validation"], "test": test,
             "test_evaluation_count_this_run": 1, "pretrained_model_evidence": "not_run"}
    (output / "final-report.json").write_text(json.dumps(final, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (output / "model-card.md").write_text(model_card(plan, selected, final), encoding="utf-8")
    return final


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--finalize", action="store_true", help="Freeze selection and score test once")
    parser.add_argument("--output", type=Path, help="Fresh output directory required with --finalize")
    args = parser.parse_args()
    if args.finalize:
        if args.output is None:
            parser.error("--finalize requires --output")
        print(json.dumps(finalize(args.output), ensure_ascii=False, sort_keys=True, indent=2))
    else:
        if args.output is not None:
            parser.error("--output only applies to --finalize")
        plan = collect_validation()
        selected = select_candidate(plan)
        plan["selected_before_test"] = selected["candidate_id"]
        print(json.dumps(plan, ensure_ascii=False, sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
