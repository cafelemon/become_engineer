# 深度学习

本组用“可诊断神经网络训练系统”连续建设八课，不提前混入视觉、NLP 或 Transformer 专项结构。

当前进度：已开放 8 / 8。

1. [张量、形状、数据类型与设备契约](01-tensor-shape-dtype-device-contract.md)
2. [线性层、激活函数、参数与前向图](02-linear-layer-activation-parameters-forward-graph.md)
3. [交叉熵、自动微分、反向传播与梯度核查](03-cross-entropy-autograd-backprop-gradient-check.md)
4. [Mini-batch、SGD、学习率与训练循环](04-mini-batch-sgd-learning-rate-training-loop.md)
5. [验证曲线、过拟合、权重衰减与 Dropout](05-validation-curves-overfitting-weight-decay-dropout.md)
6. [初始化、激活分布、梯度诊断与裁剪](06-initialization-activation-gradient-diagnostics-clipping.md)
7. [检查点、随机状态与精确恢复训练](07-checkpoint-rng-resume-exact-training.md)
8. [Eval、推理 Schema、Manifest 与离线交付](08-eval-inference-schema-manifest-delivery.md)

八课已通过 65 项真实 PyTorch 测试、80 卡/160 问检索、严格构建、站内链接与 24 项多模式浏览器组级验收。

默认实验使用 Python 3.12、PyTorch 2.13.0、CPU 与固定种子生成的二维教学数据。不联网、不使用个人数据，不把小型合成数据结果外推为真实业务效果，也不承诺跨硬件逐位一致。
