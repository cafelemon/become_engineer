# 文本分类模型演进 v0.7：统一比较与模型卡

本版沿用 v0.1 的 40 条原创教学短句和固定 24/8/8 划分，汇总 v02–v06 的验证指标、错误 ID、参数量与本机运行时间。它使用真实本地 PyTorch，但**没有下载或实测预训练模型**。离线阶段输出六个发布候选；v06 去位置与去 key padding mask 仅在消融附录中展示，不参与发布选择。

默认环境：Python 3.12、PyTorch 2.13.0、CPU。从仓库根目录准备虚拟环境（首次安装会下载 PyTorch wheel），然后：

```bash
python3.12 -m venv .venv-nlp
.venv-nlp/bin/python -m pip install -r site-src/examples/nlp-transformer/text-classification-evolution-v07/requirements.txt
cd site-src/examples/nlp-transformer/text-classification-evolution-v07
../../../../.venv-nlp/bin/python -m unittest -v test_delivery_lab.py
../../../../.venv-nlp/bin/python delivery_lab.py
```

第二条只做验证比较，输出 `selected_before_test=v06-encoder-full` 与 `test_status=sealed_before_selection`。规则先固定为 validation macro-F1、accuracy、参数量、候选 ID 的优先次序；本机时间仅作附注，不作跨机器排名。

只有确认选择记录后，才在一个**新空目录**执行一次：

```bash
../../../../.venv-nlp/bin/python delivery_lab.py --finalize --output /tmp/be-nlp-v07-final-new
```

这一步在预测测试集之前写 `selection.json` 和 `test-opened.json`，然后写 `final-report.json`、`model-card.md`。非空目录会被拒绝；若中途失败，先人工审阅收据与文件，不要直接换目录连续试测。完整且已执行的一次结果另记录于本项目 `MODEL_CARD.md`：验证 8/8，但最终测试仅 4/8；不得按这个结果重新选模。

可选人工预训练路线：先检查拟用权重的模型卡、许可、训练数据与适用范围，记录固定 revision、权重指纹、额外依赖、硬件与费用。只在明确允许下载和拥有足够算力时单独开展，并保持相同语料/划分/指标；该路线当前没有脚本、权重、真实微调结果或分数。预训练实验必须形成新的模型卡，不能混进 v0.7 的离线成绩。
