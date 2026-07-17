(function () {
  "use strict";

  if (window.document$ && typeof window.document$.subscribe === "function") {
    window.document$.subscribe(initTutor);
  } else if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initTutor, { once: true });
  } else {
    initTutor();
  }

  function initTutor() {
    const marker = document.querySelector(".be-sample-tutor-mount[data-tutor-context-lesson]");
    if (!marker || marker.dataset.initialized === "true" || !window.BeSampleTutorSearch) return;
    marker.dataset.initialized = "true";

    const script = Array.from(document.scripts).find(function (item) {
      return /\/tutor-v2\.js(?:\?|$)/.test(item.src);
    });
    if (!script) return;

    const lessonId = marker.dataset.tutorContextLesson;
    const knowledgeUrl = new URL("../data/tutors/" + lessonId + ".json", script.src).href;
    const petUrl = new URL("../../../../assets/tutor/byte-buddy.webp", script.src).href;
    const storageKey = "be:tutor:sample:v2:" + lessonId;
    const state = loadState(storageKey);
    let knowledge = null;
    let currentContextId = "";
    let returnFocus = null;

    const launcher = el("button", "be-sample-tutor-launcher");
    launcher.type = "button";
    launcher.setAttribute("aria-expanded", "false");
    launcher.setAttribute("aria-label", "打开小码同学");
    const pet = document.createElement("img");
    pet.src = petUrl;
    pet.alt = "";
    pet.setAttribute("aria-hidden", "true");
    launcher.append(pet, el("span", "", "问小码"));

    const panel = el("aside", "be-sample-tutor");
    panel.hidden = true;
    panel.setAttribute("role", "dialog");
    panel.setAttribute("aria-labelledby", "be-sample-tutor-title");

    const header = el("header", "be-sample-tutor__header");
    const heading = el("div", "be-sample-tutor__heading");
    const title = el("strong", "", "小码同学");
    title.id = "be-sample-tutor-title";
    const contextStatus = el("span", "be-sample-tutor__context", "正在看你读到哪里");
    heading.append(title, contextStatus);
    const close = el("button", "be-sample-tutor__close", "关闭");
    close.type = "button";
    header.append(heading, close);

    const messages = el("div", "be-sample-tutor__messages");
    messages.setAttribute("aria-live", "polite");
    const quick = el("section", "be-sample-tutor__quick");
    quick.append(el("p", "be-sample-tutor__quick-title", "你可能正想问"));
    const chips = el("div", "be-sample-tutor__chips");
    quick.append(chips);

    const form = el("form", "be-sample-tutor__form");
    const input = document.createElement("input");
    input.type = "text";
    input.maxLength = 160;
    input.autocomplete = "off";
    input.placeholder = "例如：这里为什么会报错？";
    input.setAttribute("aria-label", "向小码同学提问");
    const submit = el("button", "", "发送");
    submit.type = "submit";
    const privacy = el("span", "be-sample-tutor__privacy", "只记住你展开到哪一层，不保存提问内容");
    form.append(input, submit, privacy);

    panel.append(header, messages, quick, form);
    marker.append(launcher, panel);
    welcome();
    observeContexts();

    fetch(knowledgeUrl, { credentials: "same-origin" })
      .then(function (response) {
        if (!response.ok) throw new Error("知识库请求失败: " + response.status);
        return response.json();
      })
      .then(function (data) {
        const errors = window.BeSampleTutorSearch.validateKnowledgeBase(data);
        if (errors.length) throw new Error(errors.join("；"));
        knowledge = data;
        if (!currentContextId && data.contexts.length) currentContextId = data.contexts[0].id;
        updateContext();
        renderQuick();
        if (state.open) openPanel(false);
      })
      .catch(function () {
        systemMessage("小码的课程卡片没能加载。你仍然可以继续阅读正文、运行代码和展开页面里的提示。", "error");
      });

    launcher.addEventListener("click", function () {
      if (panel.hidden) openPanel(true);
      else closePanel();
    });
    close.addEventListener("click", closePanel);
    form.addEventListener("submit", function (event) {
      event.preventDefault();
      const query = input.value.trim();
      if (!query) return;
      input.value = "";
      userMessage(query);
      ask(query);
    });
    panel.addEventListener("keydown", trapFocus);
    document.addEventListener("keydown", function (event) {
      if (event.key === "Escape" && !panel.hidden) closePanel();
    });

    function el(tag, className, text) {
      const node = document.createElement(tag);
      if (className) node.className = className;
      if (text !== undefined) node.textContent = text;
      return node;
    }

    function loadState(key) {
      try {
        const parsed = JSON.parse(localStorage.getItem(key) || "{}");
        return { open: parsed.open === true, levels: parsed.levels && typeof parsed.levels === "object" ? parsed.levels : {} };
      } catch (_) {
        return { open: false, levels: {} };
      }
    }

    function saveState() {
      try {
        localStorage.setItem(storageKey, JSON.stringify({ open: state.open, levels: state.levels }));
      } catch (_) {
        // 存储不可用时只影响刷新后的恢复，不影响当前会话。
      }
    }

    function openPanel(fromUser) {
      returnFocus = fromUser ? document.activeElement : launcher;
      panel.hidden = false;
      panel.setAttribute("aria-modal", String(window.matchMedia("(max-width: 44.984375em)").matches));
      launcher.setAttribute("aria-expanded", "true");
      state.open = true;
      saveState();
      input.focus();
    }

    function closePanel() {
      panel.hidden = true;
      panel.setAttribute("aria-modal", "false");
      launcher.setAttribute("aria-expanded", "false");
      state.open = false;
      saveState();
      if (returnFocus && typeof returnFocus.focus === "function") returnFocus.focus();
      else launcher.focus();
    }

    function trapFocus(event) {
      if (event.key !== "Tab") return;
      const focusable = Array.from(panel.querySelectorAll("button:not([disabled]), input:not([disabled]), a[href]"));
      if (!focusable.length) return;
      const first = focusable[0];
      const last = focusable[focusable.length - 1];
      if (event.shiftKey && document.activeElement === first) {
        event.preventDefault();
        last.focus();
      } else if (!event.shiftKey && document.activeElement === last) {
        event.preventDefault();
        first.focus();
      }
    }

    function welcome() {
      const message = assistantMessage();
      message.append(el("strong", "", "嗨，我是小码"));
      message.append(el("p", "", "有地方卡住就问我。我会从这节课已经整理好的内容里找答案；没把握的事情，我会直接告诉你。"));
    }

    function assistantMessage() {
      const message = el("article", "be-sample-tutor__message");
      message.dataset.author = "assistant";
      message.append(el("span", "be-sample-tutor__label", "小码同学"));
      messages.append(message);
      scrollMessages();
      return message;
    }

    function userMessage(text) {
      const message = el("div", "be-sample-tutor__message");
      message.dataset.author = "user";
      message.append(el("span", "be-sample-tutor__label", "你"), el("p", "", text));
      messages.append(message);
      scrollMessages();
    }

    function systemMessage(text, kind) {
      const message = assistantMessage();
      if (kind) message.dataset.kind = kind;
      message.append(el("p", "", text));
    }

    function ask(query) {
      if (!knowledge) {
        systemMessage("课程卡片还没准备好，请先看看正文里的提示。", "error");
        return;
      }
      const results = window.BeSampleTutorSearch.search(query, knowledge.cards, {
        lessonId: lessonId,
        contextId: currentContextId
      }, { limit: 3, threshold: 24 });
      if (!results.length) {
        const message = assistantMessage();
        message.dataset.kind = "error";
        message.append(el("strong", "", "这个问题我还没有可靠答案"));
        message.append(el("p", "", "我不想随便猜。你可以换个问法，看看下面的相近问题，或者先回到课程继续读。"));
        const link = el("a", "be-sample-tutor__source", "回到刚才读到的地方");
        link.href = "#" + currentContextId;
        message.append(link);
        return;
      }
      renderCard(results[0].card);
      if (results.length > 1) {
        const alternatives = assistantMessage();
        alternatives.append(el("span", "be-sample-tutor__label", "也许你想问的是"));
        const list = el("div", "be-sample-tutor__chips");
        results.slice(1).forEach(function (result) {
          const button = el("button", "", result.card.question);
          button.type = "button";
          button.addEventListener("click", function () { renderCard(result.card); });
          list.append(button);
        });
        alternatives.append(list);
      }
    }

    function renderCard(card) {
      const message = assistantMessage();
      message.dataset.cardId = card.id;
      const level = Math.max(0, Math.min(4, Number(state.levels[card.id]) || 0));
      message.append(el("strong", "", card.question));
      appendLevel(message, "先想一下", card.diagnostic);
      if (level >= 1) appendLevel(message, "给你一点提示", card.hints[0]);
      if (level >= 2) appendLevel(message, "再提示一点", card.hints[1]);
      if (level >= 3) appendLevel(message, "小例子", card.example);
      if (level >= 4) {
        appendLevel(message, "完整解释", card.answer || "这个问题没有唯一答案，可以回到课程的完成检查再对照一次。");
        const source = el("a", "be-sample-tutor__source", "回到课程：" + card.source.label);
        source.href = card.source.href;
        message.append(source);
      } else {
        const labels = ["先给我一点提示", "再提示一步", "看一个小例子", "查看完整解释"];
        const reveal = el("button", "be-sample-tutor__reveal", labels[level]);
        reveal.type = "button";
        reveal.addEventListener("click", function () {
          state.levels[card.id] = level + 1;
          saveState();
          const parent = message.parentNode;
          message.remove();
          const beforeCount = messages.children.length;
          renderCard(card);
          if (parent && messages.children.length > beforeCount) messages.lastElementChild.scrollIntoView({ block: "nearest" });
        });
        message.append(reveal);
      }
    }

    function appendLevel(container, label, text) {
      const level = el("section", "be-sample-tutor__level");
      level.append(el("b", "", label), el("p", "", text));
      container.append(level);
    }

    function renderQuick() {
      chips.replaceChildren();
      if (!knowledge) return;
      let cards = knowledge.cards.filter(function (card) {
        return card.context_id === currentContextId && card.recommended;
      });
      if (cards.length < 3) {
        cards = cards.concat(knowledge.cards.filter(function (card) {
          return card.context_id === currentContextId && !cards.includes(card);
        }));
      }
      if (cards.length < 3) {
        cards = cards.concat(knowledge.cards.filter(function (card) {
          return card.recommended && !cards.includes(card);
        }));
      }
      cards.slice(0, 3).forEach(function (card) {
        const button = el("button", "", card.question);
        button.type = "button";
        button.addEventListener("click", function () {
          userMessage(card.question);
          renderCard(card);
        });
        chips.append(button);
      });
    }

    function observeContexts() {
      const nodes = Array.from(document.querySelectorAll("[data-learning-context]"));
      if (!nodes.length) return;
      currentContextId = nodes[0].dataset.learningContext;
      if (!("IntersectionObserver" in window)) return;
      const observer = new IntersectionObserver(function (entries) {
        const visible = entries
          .filter(function (entry) { return entry.isIntersecting; })
          .sort(function (left, right) { return right.intersectionRatio - left.intersectionRatio; });
        if (!visible.length) return;
        const next = visible[0].target.dataset.learningContext;
        if (!next || next === currentContextId) return;
        currentContextId = next;
        updateContext();
        renderQuick();
      }, { rootMargin: "-18% 0px -62% 0px", threshold: [0.05, 0.3, 0.6] });
      nodes.forEach(function (node) { observer.observe(node); });
    }

    function updateContext() {
      const context = knowledge && knowledge.contexts.find(function (item) { return item.id === currentContextId; });
      contextStatus.textContent = context ? "正在看：" + context.title : "当前内容";
    }

    function scrollMessages() {
      window.requestAnimationFrame(function () { messages.scrollTop = messages.scrollHeight; });
    }
  }
})();
