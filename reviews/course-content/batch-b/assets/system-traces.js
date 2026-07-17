(function () {
  "use strict";

  const traces = {
    bfs: [
      { title: "先把 A 放进队列", a: "队列：A", b: "已发现：A", c: "父节点：A ← 无" },
      { title: "取出 A，发现 B 和 C", a: "队列：B, C", b: "距离：B=1, C=1", c: "父节点：B←A, C←A" },
      { title: "取出 B，第一次发现 D", a: "队列：C, D", b: "距离：D=2", c: "父节点：D←B" },
      { title: "取出 C，D 已经见过", a: "队列：D", b: "跳过重复的 D", c: "父节点不改" },
      { title: "取出 D，发现 E", a: "队列：E", b: "距离：E=3", c: "父节点：E←D" },
      { title: "沿父节点倒着走，再反转", a: "E←D←B←A", b: "路径：A→B→D→E", c: "最少经过 3 条边" }
    ],
    lifetime: [
      { title: "进入函数", a: "ScopeNote 构造", b: "ofstream 尚未创建", c: "资源：无" },
      { title: "打开文件", a: "ScopeNote 存活", b: "ofstream 构造", c: "资源：文件句柄" },
      { title: "写入完成", a: "检查流状态", b: "准备 return", c: "不手写 close()" },
      { title: "离开函数", a: "ofstream 析构", b: "文件自动关闭", c: "ScopeNote 析构" }
    ],
    gpio: [
      { title: "按钮还没按下", a: "GPIO：低电平", b: "事件：无", c: "主循环：继续工作" },
      { title: "输入出现上升沿", a: "GPIO：低 → 高", b: "中断请求：挂起", c: "主循环暂未处理" },
      { title: "进入中断函数", a: "记录 pin=13", b: "记录 rising", c: "很快返回" },
      { title: "主循环取走事件", a: "sequence=1", b: "待处理标记清除", c: "打印或交给业务逻辑" },
      { title: "再次检查", a: "GPIO：高电平", b: "事件：无", c: "不会重复消费" }
    ]
  };

  function init() {
    document.querySelectorAll("[data-trace-demo]").forEach(setup);
  }

  function setup(root) {
    if (root.dataset.initialized === "true") return;
    const frames = traces[root.dataset.traceDemo];
    if (!frames) return;
    root.dataset.initialized = "true";
    let index = 0;

    const stage = document.createElement("div");
    stage.className = "be-trace-demo__stage";
    const title = document.createElement("strong");
    const state = document.createElement("div");
    state.className = "be-trace-demo__state";
    const cells = [0, 1, 2].map(function () {
      const cell = document.createElement("span");
      state.append(cell);
      return cell;
    });
    stage.append(title, state);

    const controls = document.createElement("div");
    controls.className = "be-trace-demo__controls";
    const previous = button("上一步");
    const next = button("下一步");
    const reset = button("重新开始");
    const position = document.createElement("span");
    position.className = "be-trace-demo__position";
    controls.append(previous, next, reset, position);
    root.append(stage, controls);

    previous.addEventListener("click", function () { if (index > 0) { index -= 1; render(); } });
    next.addEventListener("click", function () { if (index < frames.length - 1) { index += 1; render(); } });
    reset.addEventListener("click", function () { index = 0; render(); });

    function button(text) {
      const node = document.createElement("button");
      node.type = "button";
      node.textContent = text;
      return node;
    }

    function render() {
      const frame = frames[index];
      title.textContent = frame.title;
      cells[0].textContent = frame.a;
      cells[1].textContent = frame.b;
      cells[2].textContent = frame.c;
      previous.disabled = index === 0;
      next.disabled = index === frames.length - 1;
      position.textContent = (index + 1) + " / " + frames.length;
    }

    render();
  }

  if (window.document$ && typeof window.document$.subscribe === "function") {
    window.document$.subscribe(init);
  } else if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init, { once: true });
  } else {
    init();
  }
})();
