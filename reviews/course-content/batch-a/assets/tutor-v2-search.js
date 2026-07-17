(function (root, factory) {
  const api = factory();
  if (typeof module === "object" && module.exports) module.exports = api;
  else root.BeSampleTutorSearch = api;
})(typeof globalThis !== "undefined" ? globalThis : this, function () {
  "use strict";

  const punctuation = /[\s，。！？；：、“”‘’（）()【】\[\]《》<>·,.!?;:'"`~@#$%^&*_=+|\\/\-]+/g;
  const allowedTypes = new Set([
    "overview", "concept", "example", "reproduce", "modify",
    "troubleshoot", "project", "deepen", "career"
  ]);

  function normalize(value) {
    return String(value || "").toLocaleLowerCase("zh-CN").replace(punctuation, "");
  }

  function scoreCard(query, card, context) {
    const q = normalize(query);
    if (!q) return 0;
    const question = normalize(card.question);
    const aliases = (card.aliases || []).map(normalize);
    const keywords = (card.keywords || []).map(normalize).filter(Boolean);
    let score = 0;
    if (q === question) score += 140;
    if (aliases.includes(q)) score += 120;
    if (question.includes(q)) score += 65;
    if (q.includes(question)) score += 55;
    for (const alias of aliases) {
      if (alias.includes(q) || q.includes(alias)) score += 52;
    }
    for (const keyword of keywords) {
      if (q.includes(keyword)) score += Math.max(14, Math.min(28, keyword.length * 5));
    }
    if (!score) return 0;
    if (context && card.lesson_id === context.lessonId) score += 8;
    if (context && card.context_id === context.contextId) score += 20;
    return score;
  }

  function search(query, cards, context, options) {
    const settings = Object.assign({ limit: 3, threshold: 24 }, options || {});
    return (cards || [])
      .map(function (card) { return { card: card, score: scoreCard(query, card, context || {}) }; })
      .filter(function (candidate) { return candidate.score >= settings.threshold; })
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
    const contexts = new Map();
    for (const context of data.contexts || []) {
      if (!context.id || !context.type || !context.title || !context.anchor) {
        errors.push("每个 context 必须包含 id、type、title 和 anchor");
        continue;
      }
      if (contexts.has(context.id)) errors.push("context id 重复: " + context.id);
      if (!allowedTypes.has(context.type)) errors.push("未知 context type: " + context.type);
      if (context.anchor !== "#" + context.id) errors.push(context.id + " anchor 必须指向自身锚点");
      contexts.set(context.id, context);
    }
    const cardIds = new Set();
    const required = [
      "id", "lesson_id", "context_id", "question", "aliases", "keywords",
      "diagnostic", "hints", "example", "answer", "source", "updated_at"
    ];
    for (const card of data.cards || []) {
      for (const field of required) {
        if (!(field in card)) errors.push((card.id || "未知卡片") + " 缺少字段 " + field);
      }
      if (cardIds.has(card.id)) errors.push("card id 重复: " + card.id);
      cardIds.add(card.id);
      if (data.lesson && card.lesson_id !== data.lesson.id) errors.push(card.id + " lesson_id 不匹配");
      if (!contexts.has(card.context_id)) errors.push(card.id + " 引用了未知 context_id");
      if (!Array.isArray(card.aliases) || card.aliases.length === 0) errors.push(card.id + " aliases 不能为空");
      if (!Array.isArray(card.keywords) || card.keywords.length === 0) errors.push(card.id + " keywords 不能为空");
      if (!Array.isArray(card.hints) || card.hints.length < 2) errors.push(card.id + " 至少需要两层 hints");
      if (!card.source || !card.source.label || !card.source.href) errors.push(card.id + " source 必须包含 label 和 href");
      if (card.source && card.source.href !== "#" + card.context_id) errors.push(card.id + " source 必须指向所属语义上下文");
      if (!/^\d{4}-\d{2}-\d{2}$/.test(card.updated_at || "")) errors.push(card.id + " updated_at 格式错误");
    }
    if (!Array.isArray(data.contexts) || data.contexts.length === 0) errors.push("contexts 不能为空");
    if (!Array.isArray(data.cards) || data.cards.length < 8) errors.push("cards 至少需要 8 张");
    return errors;
  }

  return { normalize, scoreCard, search, validateKnowledgeBase, allowedTypes };
});
