export const learningStatuses = ["起步中", "按计划推进", "本周已完成"];
function isRecord(value) {
    return typeof value === "object" && value !== null && !Array.isArray(value);
}
function isLearningStatus(value) {
    return typeof value === "string" && learningStatuses.some((status) => status === value);
}
export function isLearningSummary(value) {
    if (!isRecord(value))
        return false;
    return (typeof value.learner_id === "string" &&
        typeof value.learner_name === "string" &&
        typeof value.description === "string" &&
        Number.isInteger(value.completed_lessons) &&
        typeof value.completed_hours === "number" &&
        Number.isFinite(value.completed_hours) &&
        isLearningStatus(value.status) &&
        typeof value.next_milestone === "string");
}
export function summaryToRecord(summary) {
    return {
        name: summary.learner_name,
        description: summary.description,
        completedLessons: summary.completed_lessons,
        hours: summary.completed_hours,
        status: summary.status,
        nextMilestone: summary.next_milestone
    };
}
