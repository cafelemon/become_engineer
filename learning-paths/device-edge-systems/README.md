<div class="be-page-hero be-map-hero" markdown>

<span class="be-page-eyebrow">跨 C++、CS 与 AI 的后置专业方向</span>

# 设备系统与边缘智能

这是一条面向真实设备、实时系统和端侧智能的跨主线专业路线。它不属于所有学习者的默认必修，也不会阻塞 AI 推荐深化、强化学习或 LLM/Agent；只有明确需要 MCU、嵌入式 Linux、工业控制或边缘 AI 能力时再进入。

本页目前只公布能力架构、解锁关系和验收口径。正式课程、参考硬件和助教尚未建设，不应把规划状态理解为已经开放。

<div class="be-page-actions" markdown>

[查看完整课程地图](../curriculum-map.md){ .md-button .md-button--primary }
[查看 CS 前置](../cs-core/README.md){ .md-button }
[查看 AI 前置](../ai-foundation/README.md){ .md-button }

</div>

</div>

## 在总路线中的位置

<div class="be-edge-flow" role="img" aria-label="设备系统与边缘智能的课程解锁关系">
  <div class="be-edge-flow__node be-edge-flow__node--required">
    <span>共同前置</span>
    <strong>C++ 核心 ＋ CS 系统编程、并发与网络</strong>
  </div>
  <div class="be-edge-flow__arrow">↓ 解锁设备共同基础</div>
  <div class="be-edge-flow__node be-edge-flow__node--common">
    <span>跨平台共同能力</span>
    <strong>设备系统共同基础</strong>
  </div>
  <div class="be-edge-flow__arrow">↓ 选择需要的平台方向</div>
  <div class="be-edge-flow__platforms">
    <div class="be-edge-flow__node"><strong>MCU / RTOS</strong></div>
    <div class="be-edge-flow__node"><strong>嵌入式 Linux / BSP</strong></div>
    <div class="be-edge-flow__node"><strong>工业控制与实时通信</strong></div>
  </div>
  <div class="be-edge-flow__outcomes">
    <div class="be-edge-flow__outcome">
      <span>AI 基础 ＋ MCU/RTOS 或 Linux/BSP</span>
      <strong>边缘智能 / 嵌入式 AI</strong>
      <small>强化学习不是通用前置</small>
    </div>
    <div class="be-edge-flow__outcome">
      <span>强化学习 ＋ 任一设备平台能力</span>
      <strong>智能控制实验</strong>
      <small>只服务控制与决策方向</small>
    </div>
  </div>
</div>

- 设备共同基础要求完成 [C++ 核心](../programming-languages/cpp-core/README.md)，以及 CS 的系统编程、并发、网络和序列化前置。
- 边缘智能必须同时具备 AI 基础和至少一条设备平台能力；强化学习不是通用前置。
- 智能控制实验需要强化学习与设备平台能力汇合，只服务控制与决策方向。
- 不进入本路线时，继续沿默认路线学习 AI 推荐深化、其他 AI 专业选修或 LLM/Agent。

## 五层能力树

| 层级 | 能力范围 | 可观察产出 |
| --- | --- | --- |
| 设备共同基础 | 嵌入式 C/C++、交叉编译、内存与链接、硬件接口、调试、实时性、可靠性、设计文档和单元测试 | 在仿真环境完成可重复构建、接口实验、时序观察和失败分析 |
| MCU / RTOS | GPIO、中断、定时器、UART、I²C、SPI、CAN、任务、队列、同步、内存、看门狗和功耗 | 在 MCU 或受控仿真中完成外设采集、任务通信和故障恢复 |
| Linux / BSP | 启动链、Bootloader、内核、设备树、驱动框架、BSP 移植裁剪、模块调试、性能优化和应用支持 | 在嵌入式 Linux 平台完成构建、启动、驱动或系统模块验证 |
| 设备专项 | USB、Flash、Camera、GPS、LCD、视频图像处理，以及 PLC、TwinCAT、ADS、DDS | 完成一个外设、媒体链路或工业数据链路的集成和错误验证 |
| 边缘智能 | 数据采集、预处理、模型导出与量化、CPU/GPU/NPU/DSP 推理、延迟、内存、功耗、精度和恢复 | 在真实设备上提交模型运行、资源测量、精度比较和失败恢复证据 |

MCU/RTOS 与嵌入式 Linux/BSP 是并列平台线，不要求学习者先完成一条才能进入另一条。工业控制与实时通信共享设备基础，但保留 PLC 和工业通信的独立知识体系。

## AI 分支保持独立

AI 基础完成后仍有四种互不替代的选择：

- **AI 推荐深化**：优化与统计、实验工程与 MLOps、可解释性与鲁棒性、深度网络与 NLP 深化。
- **强化学习**：面向控制、决策和序列交互；可进一步与设备能力组成智能控制实验。
- **其他 AI 专业选修**：计算机视觉、多模态、时序、推荐和信息抽取。
- **LLM/Agent**：RAG、评估、工具调用和有界工作流。

边缘智能是第五个按需出口，它把模型能力放入受资源、实时性和可靠性约束的设备环境，但不取代上述路线。

## 三级能力出口

| 出口 | 完成含义 | 硬件要求 | 验收证据 |
| --- | --- | --- | --- |
| 一级：基础实践 | 理解设备程序的构建、接口、时序、资源和最小 RTOS/Linux 工作方式 | 允许仿真 | 可重复命令、运行结果、时序或资源观察、一次失败修复 |
| 二级：独立模块开发 | 能独立完成一个外设、驱动、RTOS 任务链或 Linux 系统模块 | 必须使用真实设备 | 需求与设计、代码、构建运行、单元或模块测试、调试记录和回归证据 |
| 三级：BSP／边缘智能高级 | 能完成平台移植或驱动链路、性能分析、系统测试，以及板端推理或视频图像处理项目 | 必须使用真实设备 | BSP/驱动或推理链路、性能与资源测量、异常恢复、系统测试和边界说明 |

三级出口用于描述能力证据，不承诺学习时长，也不等同于真实岗位要求的工作年限。

## 硬件原则

- 采用“仿真入门、真机毕业”，前期不强制购买设备。
- 后续硬件计划分别选择一个 MCU/RTOS 参考平台和一个嵌入式 Linux/AI 参考平台。
- 英伟达、全志和瑞芯微目前只是匿名岗位样本中出现的平台示例，不构成指定购买清单。
- 仿真适合验证构建、接口和基本时序，不能替代二、三级出口的真实设备、资源和故障证据。
- 真实硬件实验必须提供安全边界，仿真结果不得被包装为生产设备验证。

## 匿名岗位样本如何校准本路线

当前只有一份嵌入式 Linux/BSP 中高级岗位描述用于能力校准，不用于推断市场频率：

| 岗位能力信号 | 路线承接位置 |
| --- | --- |
| 驱动开发、调试和 BUG 分析 | Linux/BSP、设备专项、二级与三级出口 |
| 需求、详细设计和单元测试文档 | 设备共同基础和所有真机验收 |
| 嵌入式 Linux 应用支持 | Linux/BSP 平台线 |
| 驱动性能与产品迭代 | Linux/BSP 高级、资源测量和系统测试 |
| Linux 内核、BSP 移植裁剪 | 三级 Linux/BSP 出口 |
| SPI/UART/USB/Flash/Camera/GPS/LCD | MCU/RTOS、Linux 驱动与设备专项 |
| 视频图像处理和编解码 | 设备专项与边缘智能 |

这份样本只能说明一个岗位的能力组合。后续素材阶段仍需通过多来源校准课程优先级，不能把单份 JD 写成行业统一标准。

## 当前建设状态

- 能力树、跨主线依赖、硬件门槛和三级出口：已规划。
- MCU/RTOS、Linux/BSP、工业控制和边缘智能正式课程：尚未建设。
- 参考开发板、仿真环境和厂商平台：尚未选型。
- 专项素材与招聘信号：留到后续独立计划。
- 正式课程数量现为 31 节；本页仍不挂载小码助教，也不进入“开始学习”的默认课程树。
