import { expect, test } from "@playwright/test";

const lessons = [
  ["01-postgresql-alembic-data-migration", "PostgreSQL、Alembic 与数据迁移"],
  ["02-password-hashing-cookie-sessions-csrf", "密码哈希、Cookie 会话与 CSRF 防护"],
  ["03-resource-ownership-authorization-audit", "资源所有权、角色授权与审计日志"],
  ["04-session-frontend-e2e-ci", "会话前端、端到端测试与持续集成"],
  ["05-containers-config-health-graceful-shutdown", "容器、配置、健康检查与优雅停止"],
  ["06-observability-backup-release-rollback", "指标、备份、发布与回滚演练"]
] as const;

for (const [slug, title] of lessons) {
  test(`${slug} keeps the full lesson readable`, async ({ page }) => {
    await page.goto(`learning-paths/web-fullstack/web-engineering/${slug}/`);
    await expect(page.getByRole("heading", { level: 1, name: title })).toBeVisible();
    await expect(page.getByRole("heading", { name: "完成检查" })).toBeVisible();
    await expect(page.getByRole("heading", { name: "来源与版本" })).toBeVisible();
    await expect(page.locator("[data-context-type=project]")).toBeVisible();
  });
}

test("keyboard focus reaches a visible course link", async ({ page }, testInfo) => {
  test.skip(testInfo.project.name !== "desktop-light", "keyboard path is covered once on the desktop navigation");
  await page.goto("learning-paths/web-fullstack/web-engineering/");
  for (let index = 0; index < 8; index += 1) await page.keyboard.press("Tab");
  await expect(page.locator("a:focus").first()).toBeVisible();
});
