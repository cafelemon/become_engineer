import { expect, test } from "@playwright/test";

const lessons = [
  {
    path: "learning-paths/career-algorithm/01-fixed-io-local-judge-contract/",
    title: "固定输入输出与本机判题契约",
  },
  {
    path: "learning-paths/career-algorithm/02-timed-rehearsal-strategy-log/",
    title: "限时模拟、策略选择与过程记录",
  },
  {
    path: "learning-paths/career-algorithm/03-failure-categories-minimal-counterexamples-regression/",
    title: "错因分类、最小反例与回归复盘",
  },
];

test("algorithm career lessons stay readable across display modes", async ({ page }) => {
  for (const lesson of lessons) {
    await page.goto(lesson.path);
    await expect(page.getByRole("heading", { level: 1, name: lesson.title })).toBeVisible();
    await expect(page.getByRole("heading", { name: "完成检查" })).toBeVisible();
    await expect(page.locator("[data-context-type=project]")).toBeVisible();
    const hasOverflow = await page.evaluate(
      () => document.documentElement.scrollWidth > document.documentElement.clientWidth,
    );
    expect(hasOverflow, `${lesson.path} should not overflow horizontally`).toBe(false);
  }
});
