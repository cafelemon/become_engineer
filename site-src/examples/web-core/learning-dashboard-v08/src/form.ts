import type { FieldErrors, StudySessionDraft } from "./contracts.js";

export type DraftValidation =
  | { ok: true; draft: StudySessionDraft }
  | { ok: false; errors: FieldErrors };

export function validateSessionDraft(hoursRaw: string, noteRaw: string): DraftValidation {
  const errors: FieldErrors = {};
  const hours = Number(hoursRaw);
  const note = noteRaw.trim();

  if (hoursRaw.trim() === "" || !Number.isFinite(hours)) {
    errors.hours = "请输入可以计算的小时数。";
  } else if (hours <= 0 || hours > 24) {
    errors.hours = "小时数要大于 0，并且不能超过 24。";
  } else if (Math.abs(hours * 4 - Math.round(hours * 4)) > Number.EPSILON * 8) {
    errors.hours = "请按 0.25 小时递增，例如 0.75、1 或 1.25。";
  }

  if (note.length < 2) {
    errors.note = "备注去掉空格后至少写 2 个字符。";
  } else if (note.length > 200) {
    errors.note = "备注最多 200 个字符。";
  }

  if (Object.keys(errors).length > 0) return { ok: false, errors };
  return { ok: true, draft: { hours, note } };
}

export function draftFingerprint(draft: StudySessionDraft): string {
  return JSON.stringify([draft.hours, draft.note]);
}

export interface SubmissionIntent {
  keyFor(draft: StudySessionDraft): string;
  complete(): void;
  currentKey(): string | null;
}

export function createSubmissionIntent(
  keyFactory: () => string = () => crypto.randomUUID()
): SubmissionIntent {
  let current: { fingerprint: string; key: string } | null = null;

  return {
    keyFor(draft) {
      const fingerprint = draftFingerprint(draft);
      if (current?.fingerprint !== fingerprint) {
        current = { fingerprint, key: `lesson-v08-${keyFactory()}` };
      }
      return current.key;
    },
    complete() {
      current = null;
    },
    currentKey() {
      return current?.key ?? null;
    }
  };
}

export class LatestRequestGate {
  private generation = 0;

  start(): number {
    this.generation += 1;
    return this.generation;
  }

  isCurrent(token: number): boolean {
    return token === this.generation;
  }
}
