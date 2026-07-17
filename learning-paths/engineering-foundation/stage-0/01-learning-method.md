<div class="be-tutor-mount" data-tutor-lesson="engineering-foundation-01" aria-hidden="true"></div>

<section id="overview-learning-log" class="be-page-hero be-lesson-hero" data-learning-context="overview-learning-log" data-context-type="overview" markdown="1">

<span class="be-page-eyebrow">工程基础入门 · 第一课</span>

# 学习方法

## 先留下第一份学习记录

“我要学会编程”听起来很有决心，但到了晚上，你很难判断今天到底完成了什么。把它换成下面这份短记录，事情就清楚多了：

```text
目标：看懂目录、路径和扩展名
操作：画出一个项目目录，并判断 3 个路径
结果：3 个路径判断正确
问题：还分不清 ./ 和 ../
下一步：带着这个问题学习文件系统
```

这节课就做这样一份记录。它不用漂亮，也不用写成长文；只要第二天打开时，你知道自己做过什么、卡在哪里、接下来从哪儿继续。

<div class="be-page-actions" markdown="1">
[写第一份记录](#reproduce-first-log){ .md-button .md-button--primary }
[查看阶段说明](README.md){ .md-button }
</div>

</section>

<div class="be-lesson-overview">
  <div><span>课程位置</span><strong>工程基础入门 · 1 / 10</strong></div>
  <div><span>前置要求</span><strong>无需前置知识</strong></div>
  <div><span>完成后留下</span><strong>learning-log.md</strong></div>
</div>

<section id="concept-learning-loop" data-learning-context="concept-learning-loop" data-context-type="concept" markdown="1">

## 五行就够了

一份能继续使用的学习记录，只需要回答五个问题：

```text
目标 → 操作 → 结果 → 问题 → 下一步
```

| 要写什么 | 它回答的问题 | 合适的写法 |
| --- | --- | --- |
| 目标 | 这次准备完成什么？ | 能判断完成与否的一件小事 |
| 操作 | 实际做了什么？ | 命令、点击、修改或练习 |
| 结果 | 最后看到了什么？ | 文件、输出、截图或判断结果 |
| 问题 | 哪个地方还没弄明白？ | 带上当时的操作和现象 |
| 下一步 | 下次从哪里接着做？ | 一个可以马上开始的动作 |

这里先别追求写得完整。学习记录的作用是帮你接上下一次学习，不是交作文。

</section>

<section id="example-small-goal" data-learning-context="example-small-goal" data-context-type="example" markdown="1">

## 目标要小到今天能判断

下面这个目标太大：

```text
我要学 Git。
```

它没有说明今天学哪一部分，也没有结束条件。换成这样就容易执行：

```text
今天运行一次 git status，并根据输出判断仓库里有没有尚未提交的修改。
```

一个合适的短目标通常说清三件事：

1. **对象**：今天碰的是 `git status`，不是整个 Git。
2. **动作**：亲自运行并读取输出，不只是看一遍说明。
3. **结束条件**：能根据输出作出判断，就算完成。

再看一个例子：

```text
我要学 Python。
→ 今天修改个人学习档案里的昵称和计划小时，并重新运行程序。
```

不必把未来几个月都塞进今天。先把眼前这一小段走通，后面的课程会自然接上来。

</section>

<section id="reproduce-first-log" data-learning-context="reproduce-first-log" data-context-type="reproduce" markdown="1">

## 写下第一份记录

现在新建一个名为 `learning-log.md` 的文件，把下面内容复制进去：

```markdown
# 学习记录：学习方法

## 目标

完成并保存第一份学习记录，重新打开后内容仍然存在。

## 操作

- 新建 learning-log.md。
- 写入目标、操作、结果、问题和下一步。
- 保存文件，关闭后重新打开。

## 结果

文件已经保存，重新打开后内容仍然存在。

## 问题

我还不知道这份文件实际保存在电脑的哪个目录。

## 下一步

进入文件系统课程，找到 learning-log.md 的完整路径。
```

用你手边熟悉的软件就可以：文本编辑器、记事本或 VS Code 都行。如果还没有编辑器，先用系统自带的文本工具；第四课会带你安装和使用 VS Code。

保存后把文件关掉，再重新打开。屏幕上刚才看得到，不等于文件已经写进磁盘；重新打开仍能看到内容，才算真正保存好了。

</section>

<section id="modify-own-log" data-learning-context="modify-own-log" data-context-type="modify" markdown="1">

## 改成你今天真正要做的事

不要停在复制模板。至少改动下面四处：

1. 把标题改成你今天正在学的内容。
2. 把目标改成一件今天能完成的小事。
3. 在“操作”里写下你已经做过的动作。
4. 把“下一步”改成下次可以直接开始的动作。

如果暂时没有问题，不要为了填满模板硬编一句。可以这样写：

```text
目前没有发现问题；下一课会检查我是否真的理解了文件保存位置。
```

写完以后读一遍：只看这五项，明天的你能不能接着做？如果答案是“能”，这份记录就已经够用了。

</section>

<section id="troubleshoot-vague-log" data-learning-context="troubleshoot-vague-log" data-context-type="troubleshoot" markdown="1">

## 记录写了，为什么还是接不上

最常见的问题不是“写得少”，而是写得太模糊。

| 看似写了 | 真正的问题 | 可以怎样改 |
| --- | --- | --- |
| 目标：学会工程基础 | 今天无法完成，也无法判断 | 今天创建并重新打开一份学习记录 |
| 操作：看了课程 | 不知道你亲手做过什么 | 新建文件、写入模板、保存并重开 |
| 结果：懂了 | 明天无法复查 | 文件已保存；五个标题都能看到 |
| 问题：不会 | 别人不知道你卡在哪里 | 不知道文件保存在电脑的哪个目录 |
| 下一步：继续努力 | 下次仍然不知道从哪开始 | 打开文件系统课并找到文件完整路径 |

遇到失败也照样记录。例如文件重开后变成空白，可以写：

```text
操作：输入内容后直接关闭窗口。
结果：重新打开时内容不见了。
问题：可能关闭前没有保存。
下一步：重新输入一行，按 Ctrl+S / Command+S，再关闭并重开。
```

错误没有让这次学习作废。相反，这段记录已经告诉你下一次该验证什么。

</section>

<section id="project-learning-workspace" data-learning-context="project-learning-workspace" data-context-type="project" markdown="1">

## 工程学习工作台从这里开始

`learning-log.md` 不是一次性作业。接下来的工程基础课程会围绕同一个本地学习工作区继续增加内容：

```text
learning-workspace/
└── learning-log.md   ← 今天先留下这一份
```

下一课会把它放进清楚的目录结构；之后会在终端里找到它、用 VS Code 修改它、用 Git 记录变化，再用验证脚本检查整个工作区。十节课结束时，你得到的不是十份散落的练习，而是一套自己能维护的学习环境。

这节课先保留两样东西：

- `learning-log.md` 文件。
- 一次“关闭后重新打开，内容仍然存在”的检查结果。

</section>

## 完成检查

- [ ] 能把一个大目标改成今天能完成的小目标。
- [ ] `learning-log.md` 包含目标、操作、结果、问题和下一步。
- [ ] 文件关闭后重新打开，内容仍然存在。
- [ ] 记录写的是自己做过的事，不只是抄下来的概念。
- [ ] “下一步”指向一个可以直接开始的动作。

## 来源与版本

- 适用版本：不依赖特定操作系统或软件版本。
- 内容依据：本项目课程内容规范 V2、工程基础阶段既有学习记录方法。
- 核查日期：2026-07-17。

## 下一步

进入[文件系统](02-filesystem.md)。下一节会把这份记录放进一个清楚的目录，并找到它在电脑上的实际位置。

<div class="be-next-panel" markdown="1">

<span class="be-panel-label">完成本课后</span>

**带着刚保存的 `learning-log.md`，继续认识目录与路径。**

[进入下一课：文件系统](02-filesystem.md){ .md-button .md-button--primary }

</div>
