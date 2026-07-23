import { existsSync } from "node:fs";
import { chromium } from "../site-src/examples/web-engineering/learning-dashboard-v12/node_modules/playwright/index.mjs";

const defaultExecutable = "/Users/jiafei/Library/Caches/ms-playwright/chromium_headless_shell-1223/chrome-headless-shell-mac-arm64/chrome-headless-shell";
const executablePath = process.env.PLAYWRIGHT_CHROMIUM_EXECUTABLE || defaultExecutable;
if (!existsSync(executablePath)) {
  throw new Error("Chromium executable not found; set PLAYWRIGHT_CHROMIUM_EXECUTABLE");
}

const browser = await chromium.launch({ headless: true, executablePath });
const base = process.env.SITE_BASE_URL || "http://127.0.0.1:8765";
const lessonRoot = `${base}/learning-paths/ai-foundation/deep-learning`;
const slugs = [
  "01-tensor-shape-dtype-device-contract",
  "02-linear-layer-activation-parameters-forward-graph",
  "03-cross-entropy-autograd-backprop-gradient-check",
  "04-mini-batch-sgd-learning-rate-training-loop",
  "05-validation-curves-overfitting-weight-decay-dropout",
  "06-initialization-activation-gradient-diagnostics-clipping",
  "07-checkpoint-rng-resume-exact-training",
  "08-eval-inference-schema-manifest-delivery",
];
const modes = [
  { name: "desktop-light", viewport: { width: 1440, height: 900 }, colorScheme: "light", reducedMotion: "no-preference", javaScriptEnabled: true },
  { name: "mobile-dark-reduced", viewport: { width: 390, height: 844 }, colorScheme: "dark", reducedMotion: "reduce", javaScriptEnabled: true },
  { name: "mobile-no-js", viewport: { width: 390, height: 844 }, colorScheme: "light", reducedMotion: "reduce", javaScriptEnabled: false },
];

let pageChecks = 0;
for (const mode of modes) {
  const context = await browser.newContext(mode);
  for (const slug of slugs) {
    const page = await context.newPage();
    await page.goto(`${lessonRoot}/${slug}/`, { waitUntil: "domcontentloaded" });
    const audit = await page.evaluate(() => ({
      title: document.querySelector("h1")?.textContent?.trim(),
      overflow: document.documentElement.scrollWidth > document.documentElement.clientWidth,
      overflowElements: [...document.querySelectorAll("body *")]
        .filter((element) => element.getBoundingClientRect().right > document.documentElement.clientWidth + 1)
        .slice(0, 8)
        .map((element) => ({
          tag: element.tagName,
          className: element.className,
          text: element.textContent?.trim().slice(0, 80),
          right: Math.round(element.getBoundingClientRect().right),
        })),
      profiles: ["零基础兴趣", "有基础兴趣", "零基础求职", "有基础求职"].every((text) => document.body.innerText.includes(text)),
      project: document.body.innerText.includes("可诊断神经网络训练系统"),
      command: document.body.innerText.includes(".venv/bin/python"),
      source: document.body.innerText.includes("PyTorch"),
    }));
    if (!audit.title || audit.overflow || !audit.profiles || !audit.project || !audit.command || !audit.source) {
      throw new Error(`${mode.name} ${slug}: ${JSON.stringify(audit)}`);
    }
    pageChecks += 1;
    await page.close();
  }
  await context.close();
}

const keyboard = await browser.newContext({ viewport: { width: 1440, height: 900 } });
const page = await keyboard.newPage();
await page.goto(`${lessonRoot}/${slugs.at(-1)}/`, { waitUntil: "networkidle" });
const launcher = page.locator('button[aria-label="打开学习助教"]');
await launcher.focus();
await page.keyboard.press("Enter");
await page.locator('.be-tutor-panel[role="dialog"]').waitFor({ state: "visible" });
await page.keyboard.press("Escape");
const focused = await page.evaluate(() => document.activeElement?.getAttribute("aria-label") || "");
if (focused !== "打开学习助教") {
  throw new Error(`keyboard focus did not return: ${focused}`);
}
await keyboard.close();
await browser.close();

console.log(JSON.stringify({
  valid: true,
  page_checks: pageChecks,
  modes: modes.map((mode) => mode.name),
  keyboard_focus: focused,
}, null, 2));
