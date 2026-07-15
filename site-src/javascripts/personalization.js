(function () {
  "use strict";

  if (!window.BePersonalization) return;
  const script = Array.from(document.scripts).find(function (item) {
    return /\/javascripts\/personalization\.js(?:\?|$)/.test(item.src);
  });
  if (!script) return;

  const siteRoot = new URL("../", script.src);
  const configUrl = new URL("../data/personalization/v1.json", script.src).href;
  const profileKey = "be:learner-profile:v1";
  const inviteKey = "be:assessment-invite:v1";
  const storageAvailable = canUseStorage();
  const mount = document.querySelector(".be-assessment-mount[data-assessment-version]");
  let config = null;
  let storedProfile = loadProfile();
  let assessmentUi = null;

  fetch(configUrl, { credentials: "same-origin" })
    .then(function (response) {
      if (!response.ok) throw new Error("个性化配置请求失败: " + response.status);
      return response.json();
    })
    .then(function (data) {
      const errors = window.BePersonalization.validateConfig(data);
      if (errors.length) throw new Error(errors.join("；"));
      config = data;
      if (storedProfile && storedProfile.confirmed) applyRoute(storedProfile);
      if (mount) setupAssessment();
      bindPermanentEntry();
    })
    .catch(function () {
      if (mount) mount.dataset.ready = "error";
      bindPermanentEntry(true);
    });

  function canUseStorage() {
    try {
      const key = "be:storage-test";
      localStorage.setItem(key, "1");
      localStorage.removeItem(key);
      return true;
    } catch (_) {
      return false;
    }
  }

  function loadProfile() {
    if (!storageAvailable) return null;
    try {
      const parsed = JSON.parse(localStorage.getItem(profileKey) || "null");
      return parsed && parsed.version === 1 ? parsed : null;
    } catch (_) {
      return null;
    }
  }

  function saveProfile(profile) {
    storedProfile = window.BePersonalization.toStoredProfile(profile);
    if (!storageAvailable) return false;
    try {
      localStorage.setItem(profileKey, JSON.stringify(storedProfile));
      return true;
    } catch (_) {
      return false;
    }
  }

  function setupAssessment() {
    mount.removeAttribute("aria-hidden");
    mount.dataset.ready = "true";
    mount.dataset.petState = "idle";

    const launcher = element("button", "be-assessment-launcher");
    launcher.type = "button";
    launcher.setAttribute("aria-label", "打开小码入学测评");
    const sprite = element("span", "be-tutor-sprite");
    sprite.setAttribute("aria-hidden", "true");
    sprite.style.backgroundImage = "url(\"" + new URL("../assets/tutor/byte-buddy.webp", script.src).href + "\")";
    launcher.append(sprite, element("span", "be-assessment-launcher__text", storedProfile && storedProfile.confirmed ? "查看我的路线" : "规划我的路线"));

    const panel = element("aside", "be-assessment-panel");
    panel.id = "be-assessment-panel";
    panel.hidden = true;
    panel.setAttribute("role", "dialog");
    panel.setAttribute("aria-modal", "true");
    panel.setAttribute("aria-labelledby", "be-assessment-title");
    const header = element("header", "be-assessment-header");
    const heading = element("div", "be-assessment-heading");
    const title = element("h2", "be-assessment-title", "小码入学测评");
    title.id = "be-assessment-title";
    heading.append(title, element("span", "be-assessment-subtitle", "能力画像只保存在当前浏览器"));
    const close = element("button", "be-assessment-close", "关闭");
    close.type = "button";
    header.append(heading, close);
    const body = element("div", "be-assessment-body");
    panel.append(header, body);
    mount.append(launcher, panel);

    assessmentUi = { launcher: launcher, panel: panel, body: body, close: close, returnFocus: null, answers: {}, index: 0 };
    launcher.addEventListener("click", openAssessment);
    close.addEventListener("click", closeAssessment);
    panel.addEventListener("keydown", trapFocus);
    document.addEventListener("keydown", function (event) {
      if (event.key === "Escape" && !panel.hidden) closeAssessment();
    });

    if (!storedProfile || !storedProfile.confirmed) renderWelcome();
    else renderStoredResult();

    if ((!storedProfile || !storedProfile.confirmed) && !wasInviteDismissed()) {
      window.setTimeout(function () {
        if (panel.hidden) openAssessment();
      }, 700);
    }
  }

  function bindPermanentEntry(disabled) {
    document.querySelectorAll(".be-assessment-open").forEach(function (entry) {
      entry.addEventListener("click", function (event) {
        event.preventDefault();
        if (!disabled && assessmentUi) openAssessment();
      });
      if (disabled) {
        entry.setAttribute("aria-disabled", "true");
        entry.title = "测评配置暂时没有加载成功，完整学习路线仍可使用";
      }
    });
  }

  function wasInviteDismissed() {
    if (!storageAvailable) return false;
    return localStorage.getItem(inviteKey) === "dismissed";
  }

  function dismissInvite() {
    if (storageAvailable) localStorage.setItem(inviteKey, "dismissed");
  }

  function openAssessment() {
    assessmentUi.returnFocus = document.activeElement;
    assessmentUi.panel.hidden = false;
    document.documentElement.classList.add("be-assessment-opened");
    mount.dataset.petState = "waving";
    assessmentUi.close.focus();
  }

  function closeAssessment() {
    assessmentUi.panel.hidden = true;
    document.documentElement.classList.remove("be-assessment-opened");
    mount.dataset.petState = "idle";
    if (assessmentUi.returnFocus && typeof assessmentUi.returnFocus.focus === "function") assessmentUi.returnFocus.focus();
    else assessmentUi.launcher.focus();
  }

  function renderWelcome() {
    const wrap = element("div", "be-assessment-screen be-assessment-welcome");
    wrap.append(
      element("span", "be-assessment-eyebrow", "一次可跳过的起点建议"),
      element("h3", "", config.assessment.title),
      element("p", "", config.assessment.intro)
    );
    const facts = element("div", "be-assessment-facts");
    facts.append(infoCard("不设总分", "用四个能力维度解释推荐理由。"), infoCard("不锁内容", "随时切回完整路线或加入未显示课程。"), infoCard("不存答案", "只保存画像摘要、确认状态和导航模式。"));
    wrap.append(facts);
    const actions = element("div", "be-assessment-actions");
    const start = button("开始 3–5 分钟测评", "primary");
    const skip = button("先逛逛，稍后再测", "secondary");
    start.addEventListener("click", renderPurpose);
    skip.addEventListener("click", function () {
      dismissInvite();
      closeAssessment();
    });
    actions.append(start, skip);
    wrap.append(actions);
    replaceBody(wrap);
  }

  function renderPurpose() {
    assessmentUi.answers = {};
    assessmentUi.index = 0;
    const wrap = assessmentScreen("第 1 部分", "你这次学习的主要目的是什么？", "目的只决定是否加入求职训练，不会改变课程事实。", "1 / 9");
    const choices = element("div", "be-assessment-options be-assessment-options--cards");
    config.assessment.purposes.forEach(function (purpose) {
      const choice = element("button", "be-assessment-option");
      choice.type = "button";
      choice.append(element("strong", "", purpose.label), element("span", "", purpose.description));
      choice.addEventListener("click", function () {
        assessmentUi.answers.purpose = purpose.id;
        renderQuestion(0);
      });
      choices.append(choice);
    });
    wrap.append(choices);
    replaceBody(wrap);
  }

  function renderQuestion(index) {
    assessmentUi.index = index;
    const question = config.assessment.questions[index];
    const dimension = config.assessment.dimensions.find(function (item) { return item.id === question.dimension; });
    const wrap = assessmentScreen("能力情境 · " + dimension.label, question.question, "选择最接近你现在状态的一项，不需要猜“正确答案”。", (index + 2) + " / 9");
    const choices = element("div", "be-assessment-options");
    question.options.forEach(function (option) {
      const choice = element("button", "be-assessment-option");
      choice.type = "button";
      choice.append(element("span", "be-assessment-option__marker", String.fromCharCode(65 + question.options.indexOf(option))), element("span", "", option.label));
      choice.addEventListener("click", function () {
        assessmentUi.answers[question.id] = option.id;
        if (index + 1 < config.assessment.questions.length) renderQuestion(index + 1);
        else renderResult(window.BePersonalization.scoreAssessment(config, assessmentUi.answers));
      });
      choices.append(choice);
    });
    wrap.append(choices);
    if (index > 0) {
      const back = button("返回上一题", "text");
      back.addEventListener("click", function () { renderQuestion(index - 1); });
      wrap.append(back);
    } else {
      const back = button("返回学习目的", "text");
      back.addEventListener("click", renderPurpose);
      wrap.append(back);
    }
    replaceBody(wrap);
  }

  function renderResult(result) {
    const profile = config.profiles[result.profileKey];
    const wrap = assessmentScreen("测评结果", profile.label, profile.description, "完成");
    wrap.dataset.profile = result.profileKey;
    wrap.append(element("p", "be-assessment-result-note", "这是一条可解释、可调整的推荐路线，不是能力认证。"));

    const grid = element("div", "be-assessment-dimensions");
    config.assessment.dimensions.forEach(function (dimension) {
      const level = result.dimensions[dimension.id];
      const card = element("article", "be-assessment-dimension");
      const head = element("div", "be-assessment-dimension__head");
      head.append(element("strong", "", dimension.label), element("span", "", ["从零补齐", "已有基础", "可以深化"][level]));
      const meter = element("div", "be-assessment-meter");
      meter.setAttribute("aria-label", dimension.label + "：" + ["从零补齐", "已有基础", "可以深化"][level]);
      for (let i = 0; i < 3; i += 1) meter.append(element("span", i <= level ? "is-active" : ""));
      card.append(head, meter, element("p", "", dimension.descriptions[level]));
      grid.append(card);
    });
    wrap.append(grid);

    const routeSummary = element("section", "be-assessment-route-summary");
    const first = catalogItemByUrl(result.startUrl);
    routeSummary.append(element("h4", "", "建议从这里开始"), element("strong", "", first ? first.title : "学习方法"));
    const reasonCounts = countReasons(result.hidden);
    routeSummary.append(element("p", "", "当前路线保留 " + result.includedIds.length + " 个模块；另有 " + result.hidden.length + " 个未显示内容。"));
    const reasonList = element("ul", "be-assessment-reason-list");
    Object.keys(reasonCounts).forEach(function (reason) {
      const li = element("li", "");
      li.append(element("strong", "", reasonLabel(reason)), document.createTextNode(" " + reasonCounts[reason] + " 项"));
      reasonList.append(li);
    });
    routeSummary.append(reasonList, element("p", "be-assessment-confirm-note", "确认前请注意：未显示不等于删除。启用后仍可查看原因、逐项加入或一键切回完整路线。"));
    wrap.append(routeSummary);

    if (!storageAvailable) wrap.append(systemNotice("当前浏览器禁止本地存储，无法持久启用个性化导航；你仍可打开建议起点或继续使用完整路线。"));
    const actions = element("div", "be-assessment-actions");
    const confirm = button("确认使用个性化路线", "primary");
    confirm.disabled = !storageAvailable;
    confirm.addEventListener("click", function () {
      result.confirmed = true;
      result.view = "personalized";
      result.includedOverrides = [];
      saveProfile(result);
      dismissInvite();
      applyRoute(storedProfile);
      assessmentUi.launcher.querySelector(".be-assessment-launcher__text").textContent = "查看我的路线";
      renderStoredResult();
      closeAssessment();
    });
    const full = button("继续使用完整路线", "secondary");
    full.addEventListener("click", function () {
      dismissInvite();
      closeAssessment();
    });
    const adjust = button("重新选择", "text");
    adjust.addEventListener("click", renderPurpose);
    actions.append(confirm, full, adjust);
    wrap.append(actions);
    replaceBody(wrap);
  }

  function renderStoredResult() {
    if (!storedProfile || !storedProfile.confirmed) return renderWelcome();
    const route = window.BePersonalization.buildRoute(config, storedProfile, storedProfile.includedOverrides);
    const profile = config.profiles[storedProfile.profileKey];
    const wrap = assessmentScreen("当前个性化路线", profile.label, profile.description, storedProfile.view === "full" ? "完整模式" : "个性化模式");
    const grid = element("div", "be-assessment-dimensions");
    config.assessment.dimensions.forEach(function (dimension) {
      const level = Number(storedProfile.dimensions[dimension.id] || 0);
      const card = element("article", "be-assessment-dimension");
      card.append(element("strong", "", dimension.label + " · " + ["从零补齐", "已有基础", "可以深化"][level]), element("p", "", dimension.descriptions[level]));
      grid.append(card);
    });
    wrap.append(grid);
    const first = catalogItemByUrl(route.startUrl);
    const actions = element("div", "be-assessment-actions");
    const start = linkButton("继续推荐路线：" + (first ? first.title : "开始学习"), route.startUrl, "primary");
    const missing = button("查看 " + route.hidden.length + " 个未显示内容", "secondary");
    missing.addEventListener("click", function () { openMissingDialog(storedProfile); });
    const retake = button("重新测评", "text");
    retake.addEventListener("click", renderPurpose);
    actions.append(start, missing, retake);
    wrap.append(actions);
    replaceBody(wrap);
  }

  function applyRoute(profile) {
    if (!config || !profile || !profile.confirmed) return;
    const route = window.BePersonalization.buildRoute(config, profile, profile.includedOverrides);
    const included = new Set(route.includedIds);
    const currentPath = relativePath(window.location.href);

    document.querySelectorAll(".be-route-hidden").forEach(function (item) {
      item.classList.remove("be-route-hidden");
      item.removeAttribute("aria-hidden");
    });
    if (profile.view !== "full") {
      document.querySelectorAll("a.md-nav__link[href]").forEach(function (link) {
        const item = catalogItemByUrl(relativePath(link.href));
        if (!item || included.has(item.id) || item.url === currentPath) return;
        const navItem = link.closest("li.md-nav__item");
        if (navItem) {
          navItem.classList.add("be-route-hidden");
          navItem.setAttribute("aria-hidden", "true");
        }
      });
      hideEmptyNavigationGroups();
    }
    updateStartLinks(route.startUrl);
    renderRouteStatus(profile, route, currentPath);
  }

  function hideEmptyNavigationGroups() {
    const groups = Array.from(document.querySelectorAll("li.md-nav__item--nested")).reverse();
    groups.forEach(function (group) {
      const leaves = Array.from(group.querySelectorAll("li.md-nav__item:not(.md-nav__item--nested)"));
      if (leaves.length && leaves.every(function (leaf) { return leaf.classList.contains("be-route-hidden"); })) {
        group.classList.add("be-route-hidden");
        group.setAttribute("aria-hidden", "true");
      }
    });
  }

  function updateStartLinks(startUrl) {
    const absolute = new URL(startUrl, siteRoot).href;
    document.querySelectorAll(".be-personalized-start").forEach(function (link) { link.href = absolute; });
    document.querySelectorAll("a.md-tabs__link, a.md-nav__link").forEach(function (link) {
      if (link.textContent.trim() === "开始学习") link.href = absolute;
    });
  }

  function renderRouteStatus(profile, route, currentPath) {
    document.querySelectorAll(".be-route-status").forEach(function (node) { node.remove(); });
    const target = document.querySelector(".md-content__inner");
    if (!target) return;
    const status = element("aside", "be-route-status");
    const copy = element("div", "be-route-status__copy");
    copy.append(element("span", "be-route-status__eyebrow", profile.view === "full" ? "完整路线模式" : "个性化路线模式"), element("strong", "", config.profiles[profile.profileKey].label));
    const currentItem = catalogItemByUrl(currentPath);
    if (profile.view !== "full" && currentItem && !route.includedIds.includes(currentItem.id)) {
      copy.append(element("p", "", "当前页面不在推荐路线中，但内容没有被限制。"));
    } else {
      copy.append(element("p", "", profile.view === "full" ? "当前显示全部公开内容。" : "另有 " + route.hidden.length + " 个内容未显示，可查看原因或加入路线。"));
    }
    const actions = element("div", "be-route-status__actions");
    const missing = button("查看未显示内容", "secondary");
    missing.addEventListener("click", function () { openMissingDialog(profile); });
    const toggle = button(profile.view === "full" ? "切换个性化路线" : "切换完整路线", "text");
    toggle.addEventListener("click", function () {
      profile.view = profile.view === "full" ? "personalized" : "full";
      saveProfile(profile);
      applyRoute(storedProfile);
    });
    const retake = button("重新测评", "text");
    retake.addEventListener("click", function () {
      if (assessmentUi) {
        openAssessment();
        renderPurpose();
      } else window.location.href = new URL("#learning-assessment", siteRoot).href;
    });
    actions.append(missing, toggle, retake);
    status.append(copy, actions);
    target.insertBefore(status, target.firstChild);
  }

  function openMissingDialog(profile) {
    document.querySelectorAll(".be-missing-overlay").forEach(function (node) { node.remove(); });
    const route = window.BePersonalization.buildRoute(config, profile, profile.includedOverrides);
    const overlay = element("div", "be-missing-overlay");
    const dialog = element("section", "be-missing-dialog");
    dialog.setAttribute("role", "dialog");
    dialog.setAttribute("aria-modal", "true");
    dialog.setAttribute("aria-labelledby", "be-missing-title");
    const header = element("header", "be-missing-header");
    const title = element("h2", "", "未显示内容与原因");
    title.id = "be-missing-title";
    const close = button("关闭", "text");
    header.append(title, close);
    const intro = element("p", "be-missing-intro", "个性化只精简导航，不删除或限制内容。你可以把已开放内容逐项加入，也可以切回完整路线。" );
    const body = element("div", "be-missing-body");
    const grouped = groupByReason(route.hidden);
    ["mastered", "goal_mismatch", "locked", "planned"].forEach(function (reason) {
      if (!grouped[reason] || !grouped[reason].length) return;
      const section = element("section", "be-missing-group");
      section.append(element("h3", "", reasonLabel(reason) + " · " + grouped[reason].length));
      grouped[reason].forEach(function (item) {
        const row = element("article", "be-missing-item");
        const textWrap = element("div", "");
        textWrap.append(element("strong", "", item.title), element("span", "", reasonDescription(reason)));
        row.append(textWrap);
        if (item.canInclude) {
          const add = button("加入路线", "secondary");
          add.addEventListener("click", function () {
            profile.includedOverrides = Array.from(new Set((profile.includedOverrides || []).concat(item.id)));
            saveProfile(profile);
            applyRoute(storedProfile);
            overlay.remove();
            openMissingDialog(storedProfile);
          });
          row.append(add);
        } else row.append(element("span", "be-missing-status", "尚未开放"));
        section.append(row);
      });
      body.append(section);
    });
    const footer = element("footer", "be-missing-footer");
    const full = button("显示完整路线", "primary");
    full.addEventListener("click", function () {
      profile.view = "full";
      saveProfile(profile);
      overlay.remove();
      document.documentElement.classList.remove("be-modal-open");
      applyRoute(storedProfile);
    });
    footer.append(full);
    dialog.append(header, intro, body, footer);
    overlay.append(dialog);
    document.body.append(overlay);
    document.documentElement.classList.add("be-modal-open");
    close.addEventListener("click", dismiss);
    overlay.addEventListener("click", function (event) { if (event.target === overlay) dismiss(); });
    dialog.addEventListener("keydown", function (event) { if (event.key === "Escape") dismiss(); });
    close.focus();
    function dismiss() {
      overlay.remove();
      document.documentElement.classList.remove("be-modal-open");
    }
  }

  function assessmentScreen(eyebrow, title, description, progress) {
    const wrap = element("section", "be-assessment-screen");
    const top = element("div", "be-assessment-progress");
    top.append(element("span", "be-assessment-eyebrow", eyebrow), element("span", "", progress));
    wrap.append(top, element("h3", "", title), element("p", "be-assessment-description", description));
    return wrap;
  }

  function replaceBody(node) {
    assessmentUi.body.replaceChildren(node);
    assessmentUi.body.scrollTop = 0;
    const focusTarget = node.querySelector("button, a[href]");
    if (focusTarget) focusTarget.focus();
  }

  function trapFocus(event) {
    if (event.key !== "Tab") return;
    const focusable = Array.from(assessmentUi.panel.querySelectorAll("button:not([disabled]), a[href]"));
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

  function relativePath(value) {
    const url = new URL(value, window.location.href);
    let pathname = decodeURIComponent(url.pathname);
    const base = decodeURIComponent(siteRoot.pathname);
    if (pathname.indexOf(base) === 0) pathname = pathname.slice(base.length);
    pathname = pathname.replace(/^\/+/, "");
    if (pathname && !pathname.endsWith("/") && !/\.[a-z0-9]+$/i.test(pathname)) pathname += "/";
    return pathname;
  }

  function catalogItemByUrl(url) {
    return config && config.catalog.find(function (item) { return item.url === url; });
  }

  function countReasons(items) {
    return items.reduce(function (result, item) {
      result[item.reason] = (result[item.reason] || 0) + 1;
      return result;
    }, {});
  }

  function groupByReason(items) {
    return items.reduce(function (result, item) {
      if (!result[item.reason]) result[item.reason] = [];
      result[item.reason].push(item);
      return result;
    }, {});
  }

  function reasonLabel(reason) {
    return { mastered: "测评认为已经掌握", goal_mismatch: "当前目标不主动推荐", locked: "前置尚未满足", planned: "内容尚未建设" }[reason] || reason;
  }

  function reasonDescription(reason) {
    return {
      mastered: "根据当前能力画像从精简导航收起，可随时加回。",
      goal_mismatch: "不属于当前学习目的的必经内容，仍可自由学习。",
      locked: "建议先完成前置课程或重新测评后再进入。",
      planned: "路线已登记，但正文尚未开放，不伪装为可学习内容。"
    }[reason] || "";
  }

  function infoCard(title, copy) {
    const card = element("article", "be-assessment-fact");
    card.append(element("strong", "", title), element("span", "", copy));
    return card;
  }

  function systemNotice(copy) {
    return element("p", "be-assessment-system", copy);
  }

  function element(tag, className, text) {
    const node = document.createElement(tag);
    if (className) node.className = className;
    if (text !== undefined) node.textContent = text;
    return node;
  }

  function button(label, kind) {
    const node = element("button", "be-assessment-button be-assessment-button--" + kind, label);
    node.type = "button";
    return node;
  }

  function linkButton(label, href, kind) {
    const node = element("a", "be-assessment-button be-assessment-button--" + kind, label);
    node.href = new URL(href, siteRoot).href;
    return node;
  }
})();
