import { expect, test } from "@playwright/test";

async function login(page) {
  await page.goto("http://127.0.0.1:8792/");
  await expect(page.getByRole("heading", { name: "登录" })).toBeVisible();
  await page.getByRole("button", { name: "登录" }).click();
  await expect(page.getByRole("heading", { name: "学习看板" })).toBeVisible();
}

test.beforeEach(async ({}, testInfo) => {
  test.skip(testInfo.project.name === "no-javascript", "the application interaction requires JavaScript; static course content is checked separately");
});

test("login and refresh restore the server identity", async ({ page }) => {
  await login(page);
  await page.reload();
  await expect(page.getByText("当前主体：u-browser-learner")).toBeVisible();
});

test("the owner can write a study record", async ({ page }) => {
  await login(page);
  await page.getByLabel("学习记录").fill("浏览器真实写入");
  await page.getByRole("button", { name: "保存记录" }).click();
  await expect(page.getByText("已保存：浏览器真实写入")).toBeVisible();
});

test("learner receives a visible explanation for operator-only action", async ({ page }) => {
  await login(page);
  await page.getByRole("button", { name: "运行操作员诊断" }).click();
  await expect(page.getByText("权限不足：诊断仅对操作员开放")).toBeVisible();
});

test("logout clears the identity view", async ({ page }) => {
  await login(page);
  await page.getByRole("button", { name: "退出" }).click();
  await expect(page.getByRole("heading", { name: "登录" })).toBeVisible();
  await expect(page.getByRole("heading", { name: "学习看板" })).toBeHidden();
});
