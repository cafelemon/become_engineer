import { expect, test } from "@playwright/test";

const lessons = [
  ["01-file-descriptors-partial-io-ownership/", "文件描述符、部分 I/O 与所有权"],
  ["02-signals-process-supervision-graceful-shutdown/", "信号、进程监督与优雅停止"],
  ["03-condition-variables-bounded-queue-shutdown/", "条件变量、有界队列与关闭协议"],
  ["04-nonblocking-network-event-loop-backpressure/", "非阻塞网络、事件循环与背压"],
  ["05-latency-distribution-sampling-performance-budget/", "延迟分布、采样分析与性能预算"],
  ["06-fault-injection-resource-leaks-recovery-acceptance/", "故障注入、资源泄漏与恢复验收"],
] as const;

test("systems engineering lessons stay readable across display modes", async ({ page }) => {
  for (const [path, title] of lessons) {
    await page.goto(`learning-paths/systems-engineering/${path}`);
    await expect(page.getByRole("heading", { level: 1, name: title })).toBeVisible();
    await expect(page.getByRole("heading", { name: "完成检查" })).toBeVisible();
    await expect(page.locator("[data-context-type=project]")).toBeVisible();
    await expect(page.locator("main")).toContainText("零基础兴趣");
    await expect(page.locator("main")).toContainText("有基础求职");
    const hasOverflow = await page.evaluate(
      () => document.documentElement.scrollWidth > document.documentElement.clientWidth,
    );
    expect(hasOverflow, `${path} should not overflow horizontally`).toBe(false);
  }
});

test("systems engineering navigation is keyboard reachable", async ({ page, isMobile }) => {
  test.skip(Boolean(isMobile), "desktop keyboard path is checked separately from mobile layout");
  await page.goto("learning-paths/systems-engineering/06-fault-injection-resource-leaks-recovery-acceptance/");
  await page.keyboard.press("Tab");
  const focusedTag = await page.evaluate(() => document.activeElement?.tagName);
  expect(["A", "BUTTON", "INPUT"]).toContain(focusedTag);
});
