(function (root, factory) {
  const api = factory();
  if (typeof module === "object" && module.exports) module.exports = api;
  else root.BePersonalization = api;
})(typeof globalThis !== "undefined" ? globalThis : this, function () {
  "use strict";

  function validateConfig(config) {
    const errors = [];
    if (!config || typeof config !== "object") return ["个性化配置必须是对象"];
    if (config.version !== 1) errors.push("配置 version 必须为 1");
    if (!config.assessment || !Array.isArray(config.assessment.questions)) errors.push("assessment.questions 必须是数组");
    if (!config.profiles || typeof config.profiles !== "object") errors.push("profiles 必须是对象");
    if (!Array.isArray(config.catalog)) errors.push("catalog 必须是数组");

    const dimensions = new Set((config.assessment && config.assessment.dimensions || []).map(function (item) { return item.id; }));
    const questionIds = new Set();
    for (const question of config.assessment && config.assessment.questions || []) {
      if (!question.id || questionIds.has(question.id)) errors.push("测评题 id 缺失或重复: " + (question.id || "未知"));
      questionIds.add(question.id);
      if (!dimensions.has(question.dimension)) errors.push(question.id + " 引用了未知能力维度");
      if (!Array.isArray(question.options) || question.options.length < 3) errors.push(question.id + " 至少需要三个选项");
      for (const option of question.options || []) {
        if (!option.id || !Number.isInteger(option.score) || option.score < 0 || option.score > 2 || !option.evidence) {
          errors.push(question.id + " 的选项必须包含 id、0-2 分 score 和 evidence");
        }
      }
    }

    const catalogIds = new Set();
    const urls = new Set();
    for (const item of config.catalog || []) {
      if (!item.id || catalogIds.has(item.id)) errors.push("课程目录 id 缺失或重复: " + (item.id || "未知"));
      catalogIds.add(item.id);
      if (!item.title || !item.status || !item.selection) errors.push((item.id || "未知目录项") + " 缺少 title、status 或 selection");
      if (item.status === "ready") {
        if (!item.url) errors.push(item.id + " 已开放但缺少 url");
        if (urls.has(item.url)) errors.push("课程 URL 重复: " + item.url);
        urls.add(item.url);
      }
      if (item.dimension && !dimensions.has(item.dimension)) errors.push(item.id + " 引用了未知能力维度");
    }
    return errors;
  }

  function scoreAssessment(config, answers) {
    const purpose = answers && answers.purpose === "career" ? "career" : "interest";
    const dimensions = {};
    const evidence = {};
    for (const dimension of config.assessment.dimensions) {
      dimensions[dimension.id] = 0;
      evidence[dimension.id] = [];
    }

    const totals = {};
    const counts = {};
    for (const question of config.assessment.questions) {
      const optionId = answers && answers[question.id];
      const option = question.options.find(function (candidate) { return candidate.id === optionId; }) || question.options[0];
      totals[question.dimension] = (totals[question.dimension] || 0) + option.score;
      counts[question.dimension] = (counts[question.dimension] || 0) + 1;
      evidence[question.dimension].push(option.evidence);
    }
    for (const dimension of config.assessment.dimensions) {
      dimensions[dimension.id] = Math.max(0, Math.min(2, Math.round((totals[dimension.id] || 0) / Math.max(1, counts[dimension.id] || 0))));
    }

    const experience = dimensions.programming >= 1 ? "experienced" : "beginner";
    const profileKey = experience + "-" + purpose;
    const profile = {
      version: 1,
      purpose: purpose,
      profileKey: profileKey,
      dimensions: dimensions,
      evidence: evidence,
      confirmed: false,
      view: "personalized",
      includedOverrides: []
    };
    return Object.assign(profile, buildRoute(config, profile, []));
  }

  function buildRoute(config, profile, overrides) {
    const overrideSet = new Set(overrides || profile.includedOverrides || []);
    const includedIds = [];
    const hidden = [];

    for (const item of config.catalog) {
      if (item.status !== "ready") {
        hidden.push(hiddenItem(item, "planned"));
        continue;
      }
      if (overrideSet.has(item.id)) {
        includedIds.push(item.id);
        continue;
      }
      if (item.audience === "career" && profile.purpose !== "career") {
        hidden.push(hiddenItem(item, "goal_mismatch"));
        continue;
      }

      if (item.selection === "always") {
        includedIds.push(item.id);
      } else if (item.selection === "career") {
        if (profile.purpose === "career") includedIds.push(item.id);
        else hidden.push(hiddenItem(item, "goal_mismatch"));
      } else if (item.selection === "beginner-or-gap") {
        const isBeginner = profile.profileKey.indexOf("beginner-") === 0;
        if (isBeginner || Number(profile.dimensions[item.dimension] || 0) < 2) includedIds.push(item.id);
        else hidden.push(hiddenItem(item, "mastered"));
      } else if (item.selection === "prerequisite") {
        if (Number(profile.dimensions[item.dimension] || 0) >= Number(item.minLevel || 1)) includedIds.push(item.id);
        else hidden.push(hiddenItem(item, "locked"));
      }
    }

    const first = config.catalog.find(function (item) {
      return item.status === "ready" && item.url && includedIds.includes(item.id) && item.kind === "course";
    });
    return {
      includedIds: includedIds,
      hidden: hidden,
      startUrl: first ? first.url : config.fallbackStartUrl
    };
  }

  function hiddenItem(item, reason) {
    return {
      id: item.id,
      title: item.title,
      url: item.url || "",
      group: item.group,
      reason: reason,
      canInclude: item.status === "ready" && Boolean(item.url)
    };
  }

  function toStoredProfile(profile) {
    return {
      version: 1,
      purpose: profile.purpose,
      profileKey: profile.profileKey,
      dimensions: profile.dimensions,
      confirmed: profile.confirmed === true,
      view: profile.view === "full" ? "full" : "personalized",
      includedOverrides: Array.isArray(profile.includedOverrides) ? profile.includedOverrides : []
    };
  }

  return {
    validateConfig: validateConfig,
    scoreAssessment: scoreAssessment,
    buildRoute: buildRoute,
    toStoredProfile: toStoredProfile
  };
});
