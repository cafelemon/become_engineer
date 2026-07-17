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
      return /batch-b\/assets\/tutor-v2\.js(?:\?|$)/.test(item.src);
    });
    if (!script) return;

    const lessonId = marker.dataset.tutorContextLesson;
    const knowledgeUrl = new URL("../data/tutors/" + lessonId + ".json", script.src).href;
    const petUrl = new URL("../../../../assets/tutor/byte-buddy.webp", script.src).href;
    const storageKey = "be:tutor:sample-b:v2:" + lessonId;
    const state = loadState();
    let knowledge = null;
    let currentContextId = "";
    let returnFocus = null;

    const launcher = make("button", "be-sample-tutor-launcher");
    launcher.type = "button";
    launcher.setAttribute("aria-expanded", "false");
    launcher.setAttribute("aria-label", "打开小码同学");
    const pet = document.createElement("img");
    pet.src = petUrl;
    pet.alt = "";
    pet.setAttribute("aria-hidden", "true");
    launcher.append(pet, make("span", "", "问小码"));

    const panel = make("aside", "be-sample-tutor");
    panel.hidden = true;
    panel.setAttribute("role", "dialog");
    panel.setAttribute("aria-labelledby", "be-sample-b-tutor-title");
    const header = make("header", "be-sample-tutor__header");
    const heading = make("div", "be-sample-tutor__heading");
    const title = make("strong", "", "小码同学");
    title.id = "be-sample-b-tutor-title";
    const contextStatus = make("span", "be-sample-tutor__context", "正在看你读到哪里");
    heading.append(title, contextStatus);
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
    input.placeholder = "例如：这里为什么会报错？";
    input.setAttribute("aria-label", "向小码同学提问");
    const submit = make("button", "", "发送");
    submit.type = "submit";
    const privacy = make("span", "be-sample-tutor__privacy", "只记住提示展开到哪里，不保存你的提问");
    form.append(input, submit, privacy);
    panel.append(header, messages, quick, form);
    marker.append(launcher, panel);

    assistant("嗨，我是小码", "哪里没跟上就问我。我只从这节课已经核对过的内容里找答案；找不到时不会乱猜。");
    observeContexts();

    fetch(knowledgeUrl, { credentials: "same-origin" })
      .then(function (response) {
        if (!response.ok) throw new Error(String(response.status));
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
        assistant("课程卡片没有加载出来", "正文、代码和页面里的提示都还能正常使用。稍后刷新页面再试即可。", "error");
      });

    launcher.addEventListener("click", function () { panel.hidden ? openPanel(true) : closePanel(); });
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

    function make(tag, className, text) {
      const node = document.createElement(tag);
      if (className) node.className = className;
      if (text !== undefined) node.textContent = text;
      return node;
    }

    function loadState() {
      try {
        const saved = JSON.parse(localStorage.getItem(storageKey) || "{}");
        return { open: saved.open === true, levels: saved.levels && typeof saved.levels === "object" ? saved.levels : {} };
      } catch (_) {
        return { open: false, levels: {} };
      }
    }

    function saveState() {
      try {
        localStorage.setItem(storageKey, JSON.stringify({ open: state.open, levels: state.levels }));
      } catch (_) {
        // 存储不可用只影响刷新后的恢复。
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

    function message(author) {
      const node = make("article", "be-sample-tutor__message");
      node.dataset.author = author;
      node.append(make("span", "be-sample-tutor__label", author === "assistant" ? "小码同学" : "你"));
      messages.append(node);
      messages.scrollTop = messages.scrollHeight;
      return node;
    }

    function assistant(titleText, bodyText, kind) {
      const node = message("assistant");
      if (kind) node.dataset.kind = kind;
      if (titleText) node.append(make("strong", "", titleText));
      if (bodyText) node.append(make("p", "", bodyText));
      return node;
    }

    function userMessage(text) {
      message("user").append(make("p", "", text));
    }

    function ask(query) {
      if (!knowledge) {
        assistant("卡片还没准备好", "先看看正文里的提示，稍后再试。", "error");
        return;
      }
      const results = window.BeSampleTutorSearch.search(query, knowledge.cards, {
        lessonId: lessonId,
        contextId: currentContextId
      }, { limit: 3, threshold: 24 });
      if (!results.length) {
        const node = assistant("这个问题我还没有可靠答案", "你可以换个问法，或者先回到刚才读到的位置。", "error");
        const link = make("a", "be-sample-tutor__source", "回到刚才读到的地方");
        link.href = "#" + currentContextId;
        node.append(link);
        return;
      }
      renderCard(results[0].card);
      if (results.length > 1) {
        const alternatives = assistant("也许你想问的是", "");
        const list = make("div", "be-sample-tutor__chips");
        results.slice(1).forEach(function (result) {
          const button = make("button", "", result.card.question);
          button.type = "button";
          button.addEventListener("click", function () { renderCard(result.card); });
          list.append(button);
        });
        alternatives.append(list);
      }
    }

    function renderCard(card) {
      const node = assistant(card.question, "");
      node.dataset.cardId = card.id;
      const level = Math.max(0, Math.min(4, Number(state.levels[card.id]) || 0));
      addLevel(node, "先想一下", card.diagnostic);
      if (level >= 1) addLevel(node, "一点提示", card.hints[0]);
      if (level >= 2) addLevel(node, "再提示一点", card.hints[1]);
      if (level >= 3) addLevel(node, "小例子", card.example);
      if (level >= 4) {
        addLevel(node, "完整解释", card.answer || "回到课程对照完成检查再想一次。");
        const source = make("a", "be-sample-tutor__source", "回到课程：" + card.source.label);
        source.href = card.source.href;
        node.append(source);
      } else {
        const labels = ["先给我一点提示", "再提示一步", "看一个小例子", "查看完整解释"];
        const reveal = make("button", "be-sample-tutor__reveal", labels[level]);
        reveal.type = "button";
        reveal.addEventListener("click", function () {
          state.levels[card.id] = level + 1;
          saveState();
          node.remove();
          renderCard(card);
        });
        node.append(reveal);
      }
    }

    function addLevel(node, label, text) {
      const section = make("section", "be-sample-tutor__level");
      section.append(make("b", "", label), make("p", "", text));
      node.append(section);
    }

    function renderQuick() {
      chips.replaceChildren();
      if (!knowledge) return;
      let cards = knowledge.cards.filter(function (card) {
        return card.context_id === currentContextId && card.recommended;
      });
      if (cards.length < 3) {
        cards = cards.concat(knowledge.cards.filter(function (card) {
          return card.recommended && !cards.includes(card);
        }));
      }
      cards.slice(0, 3).forEach(function (card) {
        const button = make("button", "", card.question);
        button.type = "button";
        button.addEventListener("click", function () { renderCard(card); });
        chips.append(button);
      });
    }

    function observeContexts() {
      const sections = Array.from(document.querySelectorAll("[data-learning-context]"));
      if (!sections.length) return;
      currentContextId = sections[0].dataset.learningContext;
      const observer = new IntersectionObserver(function (entries) {
        const visible = entries.filter(function (entry) { return entry.isIntersecting; })
          .sort(function (a, b) { return a.boundingClientRect.top - b.boundingClientRect.top; });
        if (!visible.length) return;
        currentContextId = visible[0].target.dataset.learningContext;
        updateContext();
        renderQuick();
      }, { rootMargin: "-18% 0px -62% 0px", threshold: 0.01 });
      sections.forEach(function (section) { observer.observe(section); });
    }

    function updateContext() {
      if (!knowledge) return;
      const context = knowledge.contexts.find(function (item) { return item.id === currentContextId; });
      contextStatus.textContent = context ? "正在看：" + context.title : "正在看这节课";
    }
  }
})();
