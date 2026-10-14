import { existsSync } from "node:fs";
import { chromium } from "../site-src/examples/web-engineering/learning-dashboard-v12/node_modules/playwright/index.mjs";

const fallback = "/Users/jiafei/Library/Caches/ms-playwright/chromium_headless_shell-1223/chrome-headless-shell-mac-arm64/chrome-headless-shell";
const executablePath = process.env.PLAYWRIGHT_CHROMIUM_EXECUTABLE || fallback;
if (!existsSync(executablePath)) throw new Error("Chromium executable not found; set PLAYWRIGHT_CHROMIUM_EXECUTABLE");

const browser = await chromium.launch({ headless: true, executablePath });
const base = process.env.SITE_BASE_URL || "http://127.0.0.1:8765";
const root = `${base}/learning-paths/ai-foundation/nlp-transformer`;
const slugs = [
  "01-text-data-contract-splits-metrics",
  "02-tokenization-tfidf-linear-baseline",
  "03-vocabulary-embedding-pooling-network",
  "04-rnn-cnn-sequence-baselines",
  "05-scaled-dot-product-attention-mask-position",
  "06-transformer-encoder-classification-ablation",
  "07-pretrained-path-unified-evaluation-model-card",
];
const profiles = ["零基础兴趣", "有基础兴趣", "零基础求职", "有基础求职"];
const modes = [
  { name: "desktop-light", viewport: { width: 1440, height: 900 }, colorScheme: "light", reducedMotion: "no-preference", javaScriptEnabled: true },
  { name: "mobile-dark-reduced", viewport: { width: 390, height: 844 }, colorScheme: "dark", reducedMotion: "reduce", javaScriptEnabled: true },
  { name: "mobile-no-js", viewport: { width: 390, height: 844 }, colorScheme: "light", reducedMotion: "reduce", javaScriptEnabled: false },
];

let checks = 0;
try {
  for (const mode of modes) {
    const context = await browser.newContext(mode);
    for (const slug of slugs) {
      const page = await context.newPage();
      const response = await page.goto(`${root}/${slug}/`, { waitUntil: "domcontentloaded" });
      const audit = await page.evaluate((requiredProfiles) => ({
        title: document.querySelector("h1")?.textContent?.trim(),
        overflow: document.documentElement.scrollWidth > document.documentElement.clientWidth,
        profiles: requiredProfiles.every((name) => document.body.innerText.includes(name)),
        project: document.body.innerText.includes("文本分类模型演进"),
        command: document.body.innerText.includes("python"),
        noJsReadable: document.body.innerText.includes("来源与版本") && document.body.innerText.includes("下一步"),
      }), profiles);
      if (response?.status() !== 200 || !audit.title || audit.overflow || !audit.profiles || !audit.project || !audit.command || !audit.noJsReadable) {
        throw new Error(`${mode.name} ${slug}: status=${response?.status()} ${JSON.stringify(audit)}`);
      }
      checks += 1;
      await page.close();
    }
    await context.close();
  }

  const context = await browser.newContext({ viewport: { width: 1440, height: 900 } });
  const page = await context.newPage();
  await page.goto(`${root}/${slugs.at(-1)}/`, { waitUntil: "networkidle" });
  const launcher = page.locator('button[aria-label="打开学习助教"]');
  await launcher.focus();
  await page.keyboard.press("Enter");
  await page.locator('.be-tutor-panel[role="dialog"]').waitFor({ state: "visible" });
  await page.keyboard.press("Escape");
  const focused = await page.evaluate(() => document.activeElement?.getAttribute("aria-label") || "");
  if (focused !== "打开学习助教") throw new Error(`keyboard focus did not return: ${focused}`);
  await context.close();
  console.log(JSON.stringify({ valid: true, page_checks: checks, modes: modes.map((mode) => mode.name), keyboard_focus: focused }, null, 2));
} finally {
  await browser.close();
}
