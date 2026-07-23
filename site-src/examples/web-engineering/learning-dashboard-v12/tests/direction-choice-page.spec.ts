import { expect, test } from "@playwright/test";

test("direction choice lesson stays readable across display modes", async ({ page }) => {
  await page.goto("learning-paths/direction-choice/01-first-verifiable-project-direction-trials/");
  await expect(
    page.getByRole("heading", { level: 1, name: "首个可验证项目：从代码证据到方向试学" }),
  ).toBeVisible();
  await expect(page.getByRole("heading", { name: "完成检查" })).toBeVisible();
  await expect(page.locator("[data-context-type=project]")).toBeVisible();
  const hasOverflow = await page.evaluate(
    () => document.documentElement.scrollWidth > document.documentElement.clientWidth,
  );
  expect(hasOverflow).toBe(false);
});
