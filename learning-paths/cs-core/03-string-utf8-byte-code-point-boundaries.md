<div class="be-tutor-mount" data-tutor-lesson="cs-core-03" aria-hidden="true"></div>

<section id="overview-text-units" class="be-page-hero be-lesson-hero" data-learning-context="overview-text-units" data-context-type="overview" markdown="1">

<span class="be-page-eyebrow">CS 起步 · 第三课 · 长度要带单位</span>

# 字符串、UTF-8 字节与码点边界

## “A工🧪”的长度到底是 3 还是 8

在 Python 里，<code>len("A工🧪")</code> 得到 3；把它编码成 UTF-8 后，<code>len(text.encode("utf-8"))</code> 得到 8。两个答案都对，只是数的单位不同。

这和上一课一样：分析前必须先说清输入规模和基本操作。处理文本时，“长度”可能指 Unicode 码点、编码后的字节，甚至用户眼中的字形。单位没说清，边界、存储、截断和网络传输都会跟着出错。

<div class="be-page-actions" markdown="1">
[拆开三个符号看看](#concept-text-codepoint-byte){ .md-button .md-button--primary }
[运行严格编码例子](#reproduce-text-trace){ .md-button }
</div>

</section>

<div class="be-lesson-overview">
  <div><span>课程位置</span><strong>CS 起步 · 3 / 4</strong></div>
  <div><span>前置</span><strong>序列、扫描、输入规模和操作计数</strong></div>
  <div><span>完成后留下</span><strong>文本单位对照、严格失败记录和项目编码清单</strong></div>
</div>

## 开始前

- 能运行 Python 文件，并读懂 <code>str</code>、<code>bytes</code>、循环和异常。
- 已经习惯在说“长度”前先问单位。
- 本课使用 Python 和 UTF-8 建立共同概念；C++ 字节扫描、所有权与视图生命周期属于后续系统方向。
- 本课统计 Unicode 码点，不把它直接叫作“用户看到的字符数”。

<section id="concept-text-codepoint-byte" data-learning-context="concept-text-codepoint-byte" data-context-type="concept" markdown="1">

## 文本、码点和字节不是一回事

先看 <code>A工🧪</code> 怎样变成 UTF-8 字节：

<div class="be-utf8-map" role="img" aria-label="A、工和试管 emoji 分别编码为 1、3、4 个 UTF-8 字节，总计三个 Unicode 码点和八个字节。">
  <div><span>文本符号</span><strong>A</strong><small>U+0041</small><i>→</i><code>41</code><b>1 字节</b></div>
  <div><span>文本符号</span><strong>工</strong><small>U+5DE5</small><i>→</i><code>E5 B7 A5</code><b>3 字节</b></div>
  <div><span>文本符号</span><strong>🧪</strong><small>U+1F9EA</small><i>→</i><code>F0 9F A7 AA</code><b>4 字节</b></div>
</div>

- **文本**是我们要表达的内容。
- **Unicode 码点**给抽象字符分配编号，例如“工”是 <code>U+5DE5</code>。
- **UTF-8 字节**是把这些码点写入文件或通过网络传输时使用的一种编码形式。

ASCII 范围的码点在 UTF-8 中占 1 字节；更大的码点使用 2、3 或 4 字节。因此 3 个码点可以编码成 8 个字节。

</section>

<section id="concept-python-boundary" data-learning-context="concept-python-boundary" data-context-type="concept" markdown="1">

## Python 把编码边界写得很清楚

Python 的 <code>str</code> 保存 Unicode 文本，<code>bytes</code> 保存 0 到 255 的整数序列。两者不能悄悄混用：

~~~python
text = "A工🧪"
data = text.encode("utf-8")
restored = data.decode("utf-8")

print(len(text))  # 3 个码点
print(len(data))  # 8 个字节
print(restored == text)  # True
~~~

<code>encode()</code> 从文本走向字节，<code>decode()</code> 从字节回到文本。文件、HTTP 和数据库驱动通常会在某个位置完成这次转换；工程代码需要知道边界在哪里，并明确使用哪种编码。

只写“字符串长度不能超过 20”是不完整的。更准确的约束可能是“最多 20 个 Unicode 码点”或“UTF-8 编码后最多 20 字节”，两者接受的中文和 emoji 数量不同。

</section>

<section id="example-count-units" data-learning-context="example-count-units" data-context-type="example" markdown="1">

## 先预测四组长度

运行前，先把后两列写在纸上：

| 文本 | Python <code>len(text)</code> | UTF-8 <code>len(data)</code> |
| --- | ---: | ---: |
| <code>"ABC"</code> | 3 | 3 |
| <code>"工"</code> | 1 | 3 |
| <code>"🧪"</code> | 1 | 4 |
| <code>"A工🧪"</code> | 3 | 8 |

~~~python
samples = ["ABC", "工", "🧪", "A工🧪"]

for text in samples:
    data = text.encode("utf-8")
    print(repr(text), len(text), len(data), data.hex(" "))
~~~

<code>data.hex(" ")</code> 只是在屏幕上把每个字节写成两位十六进制，便于核对；真实数据仍然是 <code>bytes</code>。

</section>

<section id="reproduce-text-trace" data-learning-context="reproduce-text-trace" data-context-type="reproduce" markdown="1">

## 把单位写进结果里

完整例子不会返回一个含糊的 <code>length</code>，而是分别命名：

~~~python
--8<-- "examples/cs-start/text_units.py"
~~~

~~~bash
python site-src/examples/cs-start/text_units.py
~~~

你应该看到：

~~~text
text='A工🧪'
code_points=3, utf8_bytes=8
ascii=1, multibyte=2
hex=41 e5 b7 a5 f0 9f a7 aa
round_trip=True
~~~

<code>ascii + multibyte == code_points</code> 是这份结果的不变量：每个码点只进入其中一类。测试还会覆盖空文本、纯 ASCII、中文、四字节码点和组合附加符。

</section>

<section id="concept-grapheme" data-learning-context="concept-grapheme" data-context-type="concept" markdown="1">

## 码点数也不一定等于“看起来几个字”

下面两段文本看起来都像“é”：

~~~python
composed = "é"       # U+00E9
decomposed = "e\u0301"  # U+0065 + U+0301

print(len(composed))    # 1
print(len(decomposed))  # 2
~~~

第二种由字母 <code>e</code> 和组合重音符号两个码点组成，界面通常把它们显示成一个字形簇。旗帜、家庭 emoji 和肤色修饰也可能由多个码点组成。

所以本课字段叫 <code>code_points</code>，不叫 <code>characters</code>。真正按用户感知字符切分，需要 Unicode 字形簇规则；这比简单遍历 Python 字符串更深，本课只先把边界说明白。

</section>

<section id="troubleshoot-invalid-utf8" data-learning-context="troubleshoot-invalid-utf8" data-context-type="troubleshoot" markdown="1">

## 字节不完整时，不要悄悄猜

这是一段被截断的 UTF-8：

~~~python
broken = bytes.fromhex("e5 b7")
broken.decode("utf-8")
~~~

“工”需要 <code>e5 b7 a5</code> 三个字节，现在缺了最后一个。Python 默认使用严格解码，会抛出 <code>UnicodeDecodeError</code>，而不是访问边界之外或假装得到正确文本。

再试几组固定坏数据：

| 十六进制字节 | 问题 |
| --- | --- |
| <code>80</code> | 孤立的续字节 |
| <code>e5 b7</code> | 三字节序列被截断 |
| <code>c0 af</code> | 过长编码 |
| <code>f4 90 80 80</code> | 超过 Unicode 最大码点 |

~~~python
for raw_hex in ["80", "e5 b7", "c0 af", "f4 90 80 80"]:
    try:
        bytes.fromhex(raw_hex).decode("utf-8", errors="strict")
    except UnicodeDecodeError as error:
        print(raw_hex, error.reason)
~~~

<code>errors="ignore"</code> 会丢数据，<code>errors="replace"</code> 会插入替换符。它们有自己的用途，但不能用来证明原始输入是合法 UTF-8。需要校验时，保持严格失败。

</section>

<section id="modify-new-text" data-learning-context="modify-new-text" data-context-type="modify" markdown="1">

## 换成你自己的文本

选择一段同时包含 ASCII、中文和 emoji 的短文本，例如：

~~~python
text = "week 3：完成✅"
~~~

运行前先写下：

1. Python <code>len(text)</code> 会是多少。
2. 哪些码点各占 1、3 或 4 个 UTF-8 字节。
3. 编码后的总字节数。
4. ASCII 与多字节码点分别有几个。

再运行 <code>analyze_text()</code> 核对，并确认 <code>decode(encode(text)) == text</code>。最后把末尾 emoji 换成组合形式的 <code>"e\u0301"</code>，看看码点数和屏幕观感如何分开。

不要只换一行输入就结束。把自己的预测、实际结果和一次猜错的原因留在学习记录里。

</section>

<section id="project-report-text" data-learning-context="project-report-text" data-context-type="project" markdown="1">

## 检查报告器的文本边界

学习进度报告器会读取 UTF-8 JSON，再把昵称、课程名和标签写入文本报告。给项目补一张“文本边界清单”：

| 位置 | 程序中的类型 | 编码发生在哪里 | 失败时会看到什么 |
| --- | --- | --- | --- |
| JSON 文件 | UTF-8 字节 | <code>Path.read_text(encoding="utf-8")</code> | <code>UnicodeDecodeError</code> |
| 解析后的昵称 | <code>str</code> | 已经完成解码 | 可按码点读取 |
| 报告输出文件 | UTF-8 字节 | <code>write_text(encoding="utf-8")</code> | 编码或写入异常 |

选择昵称和课程名各一个字段，记录：

~~~python
nickname_code_points = len(nickname)
nickname_utf8_bytes = len(nickname.encode("utf-8"))
~~~

这次不修改主报告文字，只把计数写进测试或单独的诊断输出。用纯 ASCII、中文和 emoji 三组输入证明边界，并确认 JSON 输入文件保持不变。

这份清单会在 Web、数据库和 LLM 结构化输出课程继续使用：每次文本跨组件，都要知道谁负责编码、使用什么格式、失败怎样暴露。

</section>

<section id="deepen-normalization" data-learning-context="deepen-normalization" data-context-type="deepen" markdown="1">

## 看起来相同，不代表字节相同

前面的两个“é”不仅码点数不同，UTF-8 字节也不同。若系统直接按原始字节比较，它们不会相等。

Unicode 规范化可以把某些等价表示转换成统一形式，但不能在不了解业务时随手套用：用户名、搜索、密码、数字标识和签名数据对“等价”的要求并不相同。尤其密码和加密签名，擅自规范化会改变原始数据。

这节课只要求你识别问题，并在接口契约中说明是否规范化。真正的国际化搜索、排序、大小写折叠和字形簇处理需要专门工具与测试。

</section>

<section id="career-text-boundary" data-learning-context="career-text-boundary" data-context-type="career" markdown="1">

## 遇到“截断到 20 个字符”时先追问

工程需求里的“字符”经常含糊。先确认：

- 限制的是 Unicode 码点、UTF-8 字节、数据库列长度，还是界面字形数？
- 截断后是否必须保持合法 UTF-8？
- 组合字符和 emoji 序列能否被拆开？
- 限制发生在客户端、API、数据库还是全部层？

一个可靠回答可以是：“如果协议限制 20 个 UTF-8 字节，我会先编码并在码点边界上截断，不能直接切前 20 个字节；如果产品说的是用户看到的 20 个字符，则需要按字形簇规则处理，并补多语言和 emoji 测试。”

重点不是背 Unicode 名词，而是把单位、边界和失败后果问清楚。

</section>

## 完成检查

- [ ] 我能解释 <code>A工🧪</code> 为什么是 3 个码点、8 个 UTF-8 字节。
- [ ] 我能说明 <code>str</code>、<code>bytes</code>、<code>encode()</code> 和 <code>decode()</code> 的关系。
- [ ] 我预测并运行了四组文本单位对照。
- [ ] 我运行了完整例子，并核对分类不变量与往返结果。
- [ ] 我知道码点数不等于用户看到的字形簇数。
- [ ] 我严格复现了一次 <code>UnicodeDecodeError</code>，没有用忽略错误冒充合法输入。
- [ ] 我换成自己的中英文与 emoji 文本，保存了预测和实际结果。
- [ ] 我为报告器写下文本从文件字节到 Python 文本再到输出字节的路径。
- [ ] 我没有把共同 CS 起步变成 C++ 字节状态机课程。
- [ ] 我能在“20 个字符”需求中追问真正的计数单位。

## 来源与版本

- 适用版本：Python 3.11 及以上；示例只使用标准库。
- 核查日期：2026-07-17。
- 事实来源：[Python 文本序列 `str`](https://docs.python.org/3.11/library/stdtypes.html#text-sequence-type-str)用于 Unicode 文本、编码和不可变序列语义；[Python Unicode HOWTO](https://docs.python.org/3.11/howto/unicode.html)用于码点、编码、严格解码与错误策略；[Unicode 17 核心规范第 2 章](https://www.unicode.org/versions/Unicode17.0.0/core-spec/chapter-2/)用于码点、编码形式与 UTF-8 边界；[Unicode 文本分段 UAX #29](https://www.unicode.org/reports/tr29/)用于码点与扩展字形簇的边界说明。
- 代码验证：仓库脚本检查空文本、ASCII、中文、四字节码点、组合附加符、UTF-8 往返和四类非法字节；不联网、不安装第三方包。

## 下一步

进入[二维网格、行优先布局与坐标边界](04-two-dimensional-grid-row-major-layout.md)，把一维下标扩展成行列坐标，并观察二维问题怎样映射回一维位置。

[进入下一课](04-two-dimensional-grid-row-major-layout.md){ .md-button .md-button--primary }
