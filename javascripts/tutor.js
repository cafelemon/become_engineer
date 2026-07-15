(function () {
  "use strict";

  const marker = document.querySelector(".be-tutor-mount[data-tutor-lesson]");
  if (!marker || !window.BeTutorSearch) return;

  const script = Array.from(document.scripts).find(function (item) {
    return /\/javascripts\/tutor\.js(?:\?|$)/.test(item.src);
  });
  if (!script) return;

  const lessonId = marker.dataset.tutorLesson;
  const knowledgeUrl = new URL("../data/tutor/" + lessonId + ".json", script.src).href;
  const petUrl = new URL("../assets/tutor/byte-buddy.webp", script.src).href;
  const storageKey = "be:tutor:v1:" + lessonId;
  const state = loadState();
  let knowledge = null;
  let currentStepId = "step-1";
  let returnFocus = null;

  marker.removeAttribute("aria-hidden");
  marker.dataset.ready = "false";

  const launcher = element("button", "be-tutor-launcher");
  launcher.type = "button";
  launcher.setAttribute("aria-expanded", "false");
  launcher.setAttribute("aria-controls", "be-tutor-panel");
  launcher.setAttribute("aria-label", "打开学习助教");

  const sprite = element("span", "be-tutor-sprite");
  sprite.setAttribute("aria-hidden", "true");
  sprite.style.backgroundImage = "url(\"" + petUrl + "\")";
  const launcherText = element("span", "be-tutor-launcher__text", "问助教");
  launcher.append(sprite, launcherText);

  const panel = element("aside", "be-tutor-panel");
  panel.id = "be-tutor-panel";
  panel.hidden = true;
  panel.setAttribute("role", "dialog");
  panel.setAttribute("aria-modal", "false");
  panel.setAttribute("aria-labelledby", "be-tutor-title");

  const header = element("header", "be-tutor-header");
  const headingWrap = element("div", "be-tutor-heading");
  const title = element("h2", "be-tutor-title", "小码同学");
  title.id = "be-tutor-title";
  const stepStatus = element("span", "be-tutor-step", "当前：首次运行");
  headingWrap.append(title, stepStatus);

  const closeButton = element("button", "be-tutor-close", "关闭");
  closeButton.type = "button";
  closeButton.setAttribute("aria-label", "关闭学习助教");
  header.append(headingWrap, closeButton);

  const messages = element("div", "be-tutor-messages");
  messages.setAttribute("aria-live", "polite");
  messages.setAttribute("aria-relevant", "additions");

  const quickWrap = element("section", "be-tutor-quick");
  const quickTitle = element("h3", "be-tutor-quick__title", "你可以这样问");
  const quickList = element("div", "be-tutor-quick__list");
  quickWrap.append(quickTitle, quickList);

  const form = element("form", "be-tutor-form");
  const inputLabel = element("label", "be-tutor-sr-only", "向学习助教提问");
  inputLabel.htmlFor = "be-tutor-input";
  const input = element("input", "be-tutor-input");
  input.id = "be-tutor-input";
  input.name = "question";
  input.type = "text";
  input.autocomplete = "off";
  input.maxLength = 160;
  input.placeholder = "例如：为什么输入是字符串？";
  const submit = element("button", "be-tutor-submit", "发送");
  submit.type = "submit";
  form.append(inputLabel, input, submit);

  const footer = element("footer", "be-tutor-footer");
  const privacy = element("span", "be-tutor-privacy", "只在本机保存提示层级，不保存提问内容");
  const reset = element("button", "be-tutor-reset", "重置本课助教进度");
  reset.type = "button";
  footer.append(privacy, reset);

  panel.append(header, messages, quickWrap, form, footer);
  marker.append(launcher, panel);
  setPetState("idle");
  showWelcome();
  observeSteps();

  fetch(knowledgeUrl, { credentials: "same-origin" })
    .then(function (response) {
      if (!response.ok) throw new Error("知识库请求失败: " + response.status);
      return response.json();
    })
    .then(function (data) {
      const errors = window.BeTutorSearch.validateKnowledgeBase(data);
      if (errors.length) throw new Error(errors.join("；"));
      knowledge = data;
      marker.dataset.ready = "true";
      renderQuickQuestions();
      if (state.open) openPanel(false);
    })
    .catch(function () {
      marker.dataset.ready = "error";
      renderSystemMessage("助教知识库暂时没有加载成功。课程正文和分层提示仍可正常使用。", "error");
      setPetState("failed");
    });

  launcher.addEventListener("click", function () {
    if (panel.hidden) openPanel(true);
    else closePanel();
  });
  closeButton.addEventListener("click", closePanel);
  form.addEventListener("submit", function (event) {
    event.preventDefault();
    const query = input.value.trim();
    if (!query) return;
    input.value = "";
    ask(query);
  });
  input.addEventListener("focus", function () {
    if (!panel.hidden) setPetState("waiting");
  });
  reset.addEventListener("click", resetProgress);
  panel.addEventListener("keydown", trapPanelFocus);
  document.addEventListener("keydown", function (event) {
    if (event.key === "Escape" && !panel.hidden) closePanel();
  });

  function element(tag, className, text) {
    const node = document.createElement(tag);
    if (className) node.className = className;
    if (text !== undefined) node.textContent = text;
    return node;
  }

  function loadState() {
    try {
      const parsed = JSON.parse(localStorage.getItem(storageKey) || "{}");
      return {
        open: parsed.open === true,
        levels: parsed.levels && typeof parsed.levels === "object" ? parsed.levels : {}
      };
    } catch (_) {
      return { open: false, levels: {} };
    }
  }

  function saveState() {
    try {
      localStorage.setItem(storageKey, JSON.stringify({ open: state.open, levels: state.levels }));
    } catch (_) {
      // Storage can be disabled. The current session still remains usable.
    }
  }

  function setPetState(nextState) {
    marker.dataset.petState = nextState;
  }

  function openPanel(fromUser) {
    returnFocus = fromUser ? document.activeElement : launcher;
    panel.hidden = false;
    marker.dataset.panelOpen = "true";
    document.documentElement.classList.add("be-tutor-open");
    panel.setAttribute("aria-modal", String(window.matchMedia("(max-width: 44.984375em)").matches));
    launcher.setAttribute("aria-expanded", "true");
    launcher.setAttribute("aria-label", "关闭学习助教");
    state.open = true;
    saveState();
    setPetState("waving");
    window.setTimeout(function () {
      if (!panel.hidden) setPetState("waiting");
    }, 650);
    input.focus();
  }

  function closePanel() {
    panel.hidden = true;
    marker.dataset.panelOpen = "false";
    document.documentElement.classList.remove("be-tutor-open");
    panel.setAttribute("aria-modal", "false");
    launcher.setAttribute("aria-expanded", "false");
    launcher.setAttribute("aria-label", "打开学习助教");
    state.open = false;
    saveState();
    setPetState("idle");
    if (returnFocus && typeof returnFocus.focus === "function") returnFocus.focus();
    else launcher.focus();
  }

  function trapPanelFocus(event) {
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

  function showWelcome() {
    const message = element("div", "be-tutor-message be-tutor-message--assistant");
    message.append(
      element("strong", "be-tutor-message__title", "先自己试一次，我再逐层提示"),
      element("p", "", "我只查询这节课已经审核的知识卡。不会编造答案，也不会保存你的提问内容。")
    );
    messages.append(message);
  }

  function renderQuickQuestions() {
    quickList.replaceChildren();
    if (!knowledge) return;
    let cards = knowledge.cards.filter(function (card) {
      return card.step_id === currentStepId && card.recommended;
    });
    if (cards.length < 3) {
      const fallback = knowledge.cards.filter(function (card) {
        return card.step_id === currentStepId && !cards.includes(card);
      });
      cards = cards.concat(fallback).slice(0, 3);
    }
    if (!cards.length) cards = knowledge.cards.filter(function (card) { return card.recommended; }).slice(0, 3);
    for (const card of cards.slice(0, 3)) {
      const button = element("button", "be-tutor-chip", card.question);
      button.type = "button";
      button.addEventListener("click", function () {
        appendUserMessage(card.question);
        renderKnowledgeCard(card);
      });
      quickList.append(button);
    }
  }

  function ask(query) {
    appendUserMessage(query);
    if (!knowledge) {
      renderSystemMessage("当前知识库尚未就绪。请使用课程正文中的提示，稍后再试。", "error");
      setPetState("failed");
      return;
    }
    setPetState("review");
    const results = window.BeTutorSearch.search(
      query,
      knowledge.cards,
      { lessonId: lessonId, stepId: currentStepId },
      { limit: 3, threshold: 24 }
    );
    if (!results.length) {
      renderNoMatch();
      return;
    }
    renderKnowledgeCard(results[0].card);
    if (results.length > 1) renderAlternatives(results.slice(1));
  }

  function appendUserMessage(text) {
    const message = element("div", "be-tutor-message be-tutor-message--user");
    message.append(element("span", "be-tutor-message__label", "你"), element("p", "", text));
    messages.append(message);
    scrollMessages();
  }

  function renderSystemMessage(text, kind) {
    const message = element("div", "be-tutor-message be-tutor-message--assistant");
    if (kind) message.dataset.kind = kind;
    message.append(element("span", "be-tutor-message__label", "小码同学"), element("p", "", text));
    messages.append(message);
    scrollMessages();
  }

  function renderNoMatch() {
    const message = element("div", "be-tutor-message be-tutor-message--assistant");
    message.dataset.kind = "error";
    message.append(
      element("span", "be-tutor-message__label", "小码同学"),
      element("strong", "be-tutor-message__title", "当前知识库没有可靠答案"),
      element("p", "", "我不会根据不完整信息猜测。你可以改用下面的推荐问题，或查看当前任务正文。")
    );
    const source = element("a", "be-tutor-source", "查看当前任务");
    source.href = "#" + currentStepId;
    message.append(source);
    messages.append(message);
    setPetState("failed");
    scrollMessages();
  }

  function renderAlternatives(results) {
    const wrap = element("div", "be-tutor-alternatives");
    wrap.append(element("span", "be-tutor-alternatives__title", "你也可能想问："));
    for (const result of results) {
      const button = element("button", "be-tutor-chip", result.card.question);
      button.type = "button";
      button.addEventListener("click", function () {
        renderKnowledgeCard(result.card);
      });
      wrap.append(button);
    }
    messages.append(wrap);
    scrollMessages();
  }

  function renderKnowledgeCard(card) {
    const message = element("article", "be-tutor-message be-tutor-message--assistant be-tutor-card");
    message.dataset.cardId = card.id;
    message.append(
      element("span", "be-tutor-message__label", "小码同学"),
      element("strong", "be-tutor-message__title", card.question)
    );
    const content = element("div", "be-tutor-card__content");
    const level = Math.max(0, Math.min(4, Number(state.levels[card.id]) || 0));
    appendCardLevel(content, "先检查", card.diagnostic);
    if (level >= 1) appendCardLevel(content, "提示一", card.hints[0]);
    if (level >= 2) appendCardLevel(content, "提示二", card.hints[1]);
    if (level >= 3) appendCardLevel(content, "局部示例", card.example);
    if (level >= 4) {
      appendCardLevel(content, "参考答案", card.answer || "本题没有唯一参考答案，请按完成标准检查。 ");
      const source = element("a", "be-tutor-source", "回到课程：" + card.source.label);
      source.href = card.source.href;
      content.append(source);
    }
    message.append(content);

    if (level < 4) {
      const labels = ["查看提示一", "查看提示二", "查看局部示例", "查看参考答案与来源"];
      const reveal = element("button", "be-tutor-reveal", labels[level]);
      reveal.type = "button";
      reveal.addEventListener("click", function () {
        state.levels[card.id] = level + 1;
        saveState();
        message.replaceWith(renderKnowledgeCard(card));
      });
      message.append(reveal);
    } else {
      message.append(element("span", "be-tutor-complete", "已展开全部提示"));
      setPetState("jumping");
    }

    messages.append(message);
    setPetState(level >= 4 ? "jumping" : "waiting");
    scrollMessages();
    return message;
  }

  function appendCardLevel(container, label, text) {
    const section = element("section", "be-tutor-level");
    section.append(element("strong", "be-tutor-level__label", label), element("p", "", text));
    container.append(section);
  }

  function resetProgress() {
    state.levels = {};
    saveState();
    messages.replaceChildren();
    showWelcome();
    renderSystemMessage("本课提示进度已重置。你的提问内容从未写入本地存储。", "success");
    setPetState("waving");
  }

  function scrollMessages() {
    window.requestAnimationFrame(function () {
      messages.scrollTop = messages.scrollHeight;
    });
  }

  function observeSteps() {
    const steps = Array.from(document.querySelectorAll(".be-task-step[data-step-id]"));
    if (!("IntersectionObserver" in window) || !steps.length) return;
    const observer = new IntersectionObserver(function (entries) {
      const visible = entries
        .filter(function (entry) { return entry.isIntersecting; })
        .sort(function (left, right) { return right.intersectionRatio - left.intersectionRatio; });
      if (!visible.length) return;
      const nextStep = visible[0].target.dataset.stepId;
      if (nextStep === currentStepId) return;
      currentStepId = nextStep;
      updateStepStatus();
      renderQuickQuestions();
    }, { rootMargin: "-20% 0px -58% 0px", threshold: [0.05, 0.3, 0.6] });
    steps.forEach(function (step) { observer.observe(step); });
  }

  function updateStepStatus() {
    const step = knowledge && knowledge.steps.find(function (item) { return item.id === currentStepId; });
    stepStatus.textContent = "当前：" + (step ? step.title : "第 " + currentStepId.replace("step-", "") + " 步");
  }
})();
