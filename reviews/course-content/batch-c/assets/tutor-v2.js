(function () {
  "use strict";

  if (window.document$ && typeof window.document$.subscribe === "function") window.document$.subscribe(init);
  else if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", init, { once: true });
  else init();

  function init() {
    const marker = document.querySelector(".be-sample-tutor-mount[data-tutor-context-lesson]");
    if (!marker || marker.dataset.initialized === "true" || !window.BeSampleTutorSearch) return;
    marker.dataset.initialized = "true";
    const script = Array.from(document.scripts).find(function (item) { return /batch-c\/assets\/tutor-v2\.js(?:\?|$)/.test(item.src); });
    if (!script) return;

    const lessonId = marker.dataset.tutorContextLesson;
    const knowledgeUrl = new URL("../data/tutors/" + lessonId + ".json", script.src).href;
    const petUrl = new URL("../../../../assets/tutor/byte-buddy.webp", script.src).href;
    const storageKey = "be:tutor:sample-c:v2:" + lessonId;
    const state = load();
    let knowledge = null;
    let contextId = "";
    let returnFocus = null;

    const launcher = make("button", "be-sample-tutor-launcher");
    launcher.type = "button";
    launcher.setAttribute("aria-expanded", "false");
    launcher.setAttribute("aria-label", "打开小码同学");
    const pet = document.createElement("img");
    pet.src = petUrl;
    pet.alt = "";
    launcher.append(pet, make("span", "", "问小码"));

    const panel = make("aside", "be-sample-tutor");
    panel.hidden = true;
    panel.setAttribute("role", "dialog");
    panel.setAttribute("aria-labelledby", "be-sample-c-tutor-title");
    const header = make("header", "be-sample-tutor__header");
    const heading = make("div", "be-sample-tutor__heading");
    const title = make("strong", "", "小码同学");
    title.id = "be-sample-c-tutor-title";
    const context = make("span", "be-sample-tutor__context", "正在看这节课");
    heading.append(title, context);
    const close = make("button", "be-sample-tutor__close", "关闭");
    close.type = "button";
    header.append(heading, close);

    const messages = make("div", "be-sample-tutor__messages");
    messages.setAttribute("aria-live", "polite");
    const quick = make("section", "be-sample-tutor__quick");
    quick.append(make("p", "be-sample-tutor__quick-title", "你可能正想问"));
    const chips = make("div", "be-sample-tutor__chips");
    quick.append(chips);
    const form = make("form", "be-sample-tutor__form");
    const input = document.createElement("input");
    input.type = "text";
    input.maxLength = 160;
    input.autocomplete = "off";
    input.placeholder = "例如：为什么不能直接信模型？";
    input.setAttribute("aria-label", "向小码同学提问");
    const submit = make("button", "", "发送");
    submit.type = "submit";
    form.append(input, submit, make("span", "be-sample-tutor__privacy", "只记住提示展开到哪里，不保存你的提问"));
    panel.append(header, messages, quick, form);
    marker.append(launcher, panel);

    say("嗨，我是小码", "这里的数据流容易绕。哪一段没接上就问，我只按这页核对过的内容回答。 ");
    observe();
    fetch(knowledgeUrl, { credentials: "same-origin" }).then(function (response) {
      if (!response.ok) throw new Error(String(response.status));
      return response.json();
    }).then(function (data) {
      const errors = window.BeSampleTutorSearch.validateKnowledgeBase(data);
      if (errors.length) throw new Error(errors.join("；"));
      knowledge = data;
      if (!contextId && data.contexts.length) contextId = data.contexts[0].id;
      updateContext();
      renderQuick();
      if (state.open) open(false);
    }).catch(function () {
      say("课程卡片没有加载出来", "正文和页面里的例子仍然可以正常使用，稍后刷新再试。", "error");
    });

    launcher.addEventListener("click", function () { panel.hidden ? open(true) : shut(); });
    close.addEventListener("click", shut);
    form.addEventListener("submit", function (event) {
      event.preventDefault();
      const query = input.value.trim();
      if (!query) return;
      input.value = "";
      message("user").append(make("p", "", query));
      ask(query);
    });
    document.addEventListener("keydown", function (event) { if (event.key === "Escape" && !panel.hidden) shut(); });
    panel.addEventListener("keydown", trapFocus);

    function make(tag, className, text) {
      const node = document.createElement(tag);
      if (className) node.className = className;
      if (text !== undefined) node.textContent = text;
      return node;
    }
    function load() {
      try {
        const saved = JSON.parse(localStorage.getItem(storageKey) || "{}");
        return { open: saved.open === true, levels: saved.levels && typeof saved.levels === "object" ? saved.levels : {} };
      } catch (_) { return { open: false, levels: {} }; }
    }
    function save() {
      try { localStorage.setItem(storageKey, JSON.stringify({ open: state.open, levels: state.levels })); } catch (_) {}
    }
    function open(fromUser) {
      returnFocus = fromUser ? document.activeElement : launcher;
      panel.hidden = false;
      panel.setAttribute("aria-modal", String(window.matchMedia("(max-width: 44.984375em)").matches));
      launcher.setAttribute("aria-expanded", "true");
      state.open = true;
      save();
      input.focus();
    }
    function shut() {
      panel.hidden = true;
      panel.setAttribute("aria-modal", "false");
      launcher.setAttribute("aria-expanded", "false");
      state.open = false;
      save();
      (returnFocus || launcher).focus();
    }
    function trapFocus(event) {
      if (event.key !== "Tab") return;
      const items = Array.from(panel.querySelectorAll("button:not([disabled]), input:not([disabled]), a[href]"));
      if (!items.length) return;
      if (event.shiftKey && document.activeElement === items[0]) { event.preventDefault(); items[items.length - 1].focus(); }
      else if (!event.shiftKey && document.activeElement === items[items.length - 1]) { event.preventDefault(); items[0].focus(); }
    }
    function message(author) {
      const node = make("article", "be-sample-tutor__message");
      node.dataset.author = author;
      node.append(make("span", "be-sample-tutor__label", author === "assistant" ? "小码同学" : "你"));
      messages.append(node);
      messages.scrollTop = messages.scrollHeight;
      return node;
    }
    function say(titleText, bodyText, kind) {
      const node = message("assistant");
      if (kind) node.dataset.kind = kind;
      if (titleText) node.append(make("strong", "", titleText));
      if (bodyText) node.append(make("p", "", bodyText));
      return node;
    }
    function ask(query) {
      if (!knowledge) { say("卡片还没准备好", "先看正文，稍后再试。", "error"); return; }
      const results = window.BeSampleTutorSearch.search(query, knowledge.cards, { lessonId: lessonId, contextId: contextId }, { limit: 3, threshold: 24 });
      if (!results.length) {
        const node = say("这个问题我还没有可靠答案", "换个问法，或者先回到刚才读到的位置。", "error");
        const link = make("a", "be-sample-tutor__source", "回到刚才读到的地方");
        link.href = "#" + contextId;
        node.append(link);
        return;
      }
      renderCard(results[0].card);
      if (results.length > 1) {
        const alternatives = say("也许你想问的是", "");
        const list = make("div", "be-sample-tutor__chips");
        results.slice(1).forEach(function (item) {
          const button = make("button", "", item.card.question);
          button.type = "button";
          button.addEventListener("click", function () { renderCard(item.card); });
          list.append(button);
        });
        alternatives.append(list);
      }
    }
    function renderCard(card) {
      const node = say(card.question, "");
      const level = Math.max(0, Math.min(4, Number(state.levels[card.id]) || 0));
      add(node, "先想一下", card.diagnostic);
      if (level >= 1) add(node, "一点提示", card.hints[0]);
      if (level >= 2) add(node, "再提示一点", card.hints[1]);
      if (level >= 3) add(node, "小例子", card.example);
      if (level >= 4) {
        add(node, "完整解释", card.answer || "回到课程对照完成检查再想一次。");
        const source = make("a", "be-sample-tutor__source", "回到课程：" + card.source.label);
        source.href = card.source.href;
        node.append(source);
      } else {
        const labels = ["先给我一点提示", "再提示一步", "看一个小例子", "查看完整解释"];
        const button = make("button", "be-sample-tutor__reveal", labels[level]);
        button.type = "button";
        button.addEventListener("click", function () { state.levels[card.id] = level + 1; save(); node.remove(); renderCard(card); });
        node.append(button);
      }
    }
    function add(node, label, text) {
      const section = make("section", "be-sample-tutor__level");
      section.append(make("b", "", label), make("p", "", text));
      node.append(section);
    }
    function renderQuick() {
      chips.replaceChildren();
      if (!knowledge) return;
      let cards = knowledge.cards.filter(function (card) { return card.context_id === contextId && card.recommended; });
      if (cards.length < 3) cards = cards.concat(knowledge.cards.filter(function (card) { return card.recommended && !cards.includes(card); }));
      cards.slice(0, 3).forEach(function (card) {
        const button = make("button", "", card.question);
        button.type = "button";
        button.addEventListener("click", function () { renderCard(card); });
        chips.append(button);
      });
    }
    function observe() {
      const sections = Array.from(document.querySelectorAll("[data-learning-context]"));
      if (!sections.length) return;
      contextId = sections[0].dataset.learningContext;
      const observer = new IntersectionObserver(function (entries) {
        const visible = entries.filter(function (entry) { return entry.isIntersecting; }).sort(function (a, b) { return a.boundingClientRect.top - b.boundingClientRect.top; });
        if (!visible.length) return;
        contextId = visible[0].target.dataset.learningContext;
        updateContext();
        renderQuick();
      }, { rootMargin: "-18% 0px -62% 0px", threshold: 0.01 });
      sections.forEach(function (section) { observer.observe(section); });
    }
    function updateContext() {
      if (!knowledge) return;
      const item = knowledge.contexts.find(function (candidate) { return candidate.id === contextId; });
      context.textContent = item ? "正在看：" + item.title : "正在看这节课";
    }
  }
})();
