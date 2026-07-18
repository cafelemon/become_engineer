export const learningStatuses = ["起步中", "按计划推进", "本周已完成"] as const;

export type LearningStatus = (typeof learningStatuses)[number];

export interface LearningSummary {
  learner_id: string;
  learner_name: string;
  description: string;
  completed_lessons: number;
  completed_hours: number;
  status: LearningStatus;
  next_milestone: string;
}

export interface StudySession {
  session_id: number;
  learner_id: string;
  hours: number;
  note: string;
  created_at: string;
}

export interface StudySessionPage {
  items: StudySession[];
  next_after_id: number | null;
}

export interface StudySessionWriteResult {
  session: StudySession;
  replayed: boolean;
}

export interface LearningRecord {
  learnerId: string;
  name: string;
  description: string;
  completedLessons: number;
  hours: number;
  status: LearningStatus;
  nextMilestone: string;
}

export type PageState =
  | { kind: "loading"; message: string }
  | { kind: "success"; message: string; record: LearningRecord }
  | { kind: "empty"; message: string }
  | { kind: "error"; message: string }
  | { kind: "contract-error"; message: string };

export type SessionListState =
  | { kind: "loading"; message: string }
  | { kind: "success"; message: string; page: StudySessionPage }
  | { kind: "empty"; message: string; page: StudySessionPage }
  | { kind: "error"; message: string }
  | { kind: "contract-error"; message: string };

export type WriteState =
  | { kind: "idle"; message: string }
  | { kind: "saving"; message: string }
  | {
      kind: "saved";
      message: string;
      result: StudySessionWriteResult;
      httpStatus: number;
    }
  | { kind: "error"; message: string }
  | { kind: "contract-error"; message: string };

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}

function isLearningStatus(value: unknown): value is LearningStatus {
  return typeof value === "string" && learningStatuses.some((status) => status === value);
}

export function isLearningSummary(value: unknown): value is LearningSummary {
  if (!isRecord(value)) return false;
  return (
    typeof value.learner_id === "string" &&
    typeof value.learner_name === "string" &&
    typeof value.description === "string" &&
    Number.isInteger(value.completed_lessons) &&
    typeof value.completed_hours === "number" &&
    Number.isFinite(value.completed_hours) &&
    isLearningStatus(value.status) &&
    typeof value.next_milestone === "string"
  );
}

export function isStudySession(value: unknown): value is StudySession {
  if (!isRecord(value)) return false;
  return (
    Number.isInteger(value.session_id) &&
    typeof value.learner_id === "string" &&
    typeof value.hours === "number" &&
    Number.isFinite(value.hours) &&
    typeof value.note === "string" &&
    typeof value.created_at === "string"
  );
}

export function isStudySessionPage(value: unknown): value is StudySessionPage {
  if (!isRecord(value) || !Array.isArray(value.items)) return false;
  return (
    value.items.every(isStudySession) &&
    (value.next_after_id === null || Number.isInteger(value.next_after_id))
  );
}

export function isStudySessionWriteResult(
  value: unknown
): value is StudySessionWriteResult {
  if (!isRecord(value)) return false;
  return isStudySession(value.session) && typeof value.replayed === "boolean";
}

export function summaryToRecord(summary: LearningSummary): LearningRecord {
  return {
    learnerId: summary.learner_id,
    name: summary.learner_name,
    description: summary.description,
    completedLessons: summary.completed_lessons,
    hours: summary.completed_hours,
    status: summary.status,
    nextMilestone: summary.next_milestone
  };
}
