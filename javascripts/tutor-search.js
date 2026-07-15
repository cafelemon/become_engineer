(function (root, factory) {
  const api = factory();
  if (typeof module === "object" && module.exports) {
    module.exports = api;
  } else {
    root.BeTutorSearch = api;
  }
})(typeof globalThis !== "undefined" ? globalThis : this, function () {
  "use strict";

  const punctuation = /[\s，。！？；：、“”‘’（）()【】\[\]《》<>·,.!?;:'"`~@#$%^&*_=+|\\/\-]+/g;

  function normalize(value) {
    return String(value || "").toLocaleLowerCase("zh-CN").replace(punctuation, "");
  }

  function scoreCard(query, card, context) {
    const normalizedQuery = normalize(query);
    if (!normalizedQuery) return 0;

    const normalizedQuestion = normalize(card.question);
    const aliases = (card.aliases || []).map(normalize);
    const keywords = (card.keywords || []).map(normalize).filter(Boolean);
    let score = 0;

    if (normalizedQuery === normalizedQuestion) score += 140;
    if (aliases.includes(normalizedQuery)) score += 120;
    if (normalizedQuestion.includes(normalizedQuery)) score += 65;
    if (normalizedQuery.includes(normalizedQuestion)) score += 55;

    for (const alias of aliases) {
      if (alias.includes(normalizedQuery) || normalizedQuery.includes(alias)) score += 52;
    }

    for (const keyword of keywords) {
      if (normalizedQuery.includes(keyword)) score += Math.max(14, Math.min(28, keyword.length * 5));
    }

    if (score === 0) return 0;
    if (context && card.lesson_id === context.lessonId) score += 8;
    if (context && card.step_id === context.stepId) score += 18;
    return score;
  }

  function search(query, cards, context, options) {
    const settings = Object.assign({ limit: 3, threshold: 24 }, options || {});
    return (cards || [])
      .map(function (card) {
        return { card: card, score: scoreCard(query, card, context || {}) };
      })
      .filter(function (candidate) {
        return candidate.score >= settings.threshold;
      })
      .sort(function (left, right) {
        if (right.score !== left.score) return right.score - left.score;
        return left.card.question.localeCompare(right.card.question, "zh-CN");
      })
      .slice(0, settings.limit);
  }

  function validateKnowledgeBase(data) {
    const errors = [];
    if (!data || typeof data !== "object") return ["知识库根节点必须是对象"];
    if (!data.lesson || !data.lesson.id || !data.lesson.title || !data.lesson.path) {
      errors.push("lesson 必须包含 id、title 和 path");
    }

    const stepIds = new Set();
    for (const step of data.steps || []) {
      if (!step.id || !step.title) errors.push("每个 step 必须包含 id 和 title");
      if (stepIds.has(step.id)) errors.push("step id 重复: " + step.id);
      stepIds.add(step.id);
    }

    const cardIds = new Set();
    const required = ["id", "lesson_id", "step_id", "question", "aliases", "keywords", "diagnostic", "hints", "example", "answer", "source", "updated_at"];
    for (const card of data.cards || []) {
      for (const field of required) {
        if (!(field in card)) errors.push((card.id || "未知卡片") + " 缺少字段 " + field);
      }
      if (cardIds.has(card.id)) errors.push("card id 重复: " + card.id);
      cardIds.add(card.id);
      if (data.lesson && card.lesson_id !== data.lesson.id) errors.push(card.id + " lesson_id 不匹配");
      if (!stepIds.has(card.step_id)) errors.push(card.id + " 引用了未知 step_id");
      if (!Array.isArray(card.aliases) || card.aliases.length === 0) errors.push(card.id + " aliases 不能为空");
      if (!Array.isArray(card.keywords) || card.keywords.length === 0) errors.push(card.id + " keywords 不能为空");
      if (!Array.isArray(card.hints) || card.hints.length < 2) errors.push(card.id + " 至少需要两层 hints");
      if (!card.source || !card.source.label || !card.source.href) errors.push(card.id + " source 必须包含 label 和 href");
      if (!/^#step-[1-7]$/.test(card.source && card.source.href || "")) errors.push(card.id + " source 必须指向任务步骤锚点");
      if (!/^\d{4}-\d{2}-\d{2}$/.test(card.updated_at || "")) errors.push(card.id + " updated_at 格式错误");
    }
    if (!Array.isArray(data.cards) || data.cards.length === 0) errors.push("cards 不能为空");
    return errors;
  }

  return {
    normalize: normalize,
    scoreCard: scoreCard,
    search: search,
    validateKnowledgeBase: validateKnowledgeBase
  };
});
