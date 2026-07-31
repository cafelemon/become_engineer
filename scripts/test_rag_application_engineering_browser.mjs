import { existsSync } from "node:fs";
import { chromium } from "../site-src/examples/web-engineering/learning-dashboard-v12/node_modules/playwright/index.mjs";

const executablePath = process.env.PLAYWRIGHT_CHROMIUM_EXECUTABLE || "/Users/jiafei/Library/Caches/ms-playwright/chromium_headless_shell-1223/chrome-headless-shell-mac-arm64/chrome-headless-shell";
if (!existsSync(executablePath)) throw new Error("Chromium executable not found; set PLAYWRIGHT_CHROMIUM_EXECUTABLE");
const browser = await chromium.launch({headless:true,executablePath});
const base = process.env.SITE_BASE_URL || "http://127.0.0.1:8765";
const lessonRoot = `${base}/learning-paths/llm-agent/rag-application-engineering`;
const slugs = [
  "01-document-ingestion-parsing-version-index-jobs",
  "02-chunking-models-strategies-comparison",
  "03-embedding-contract-pgvector-index-lifecycle",
  "04-query-understanding-filter-hybrid-routing",
  "05-rerank-semantic-compression-context-selection",
  "06-prompt-citation-admin-chat-release",
];
const modes = [
  {name:"desktop-light",viewport:{width:1440,height:900},colorScheme:"light",reducedMotion:"no-preference",javaScriptEnabled:true},
  {name:"mobile-dark-reduced",viewport:{width:390,height:844},colorScheme:"dark",reducedMotion:"reduce",javaScriptEnabled:true},
  {name:"mobile-no-js",viewport:{width:390,height:844},colorScheme:"light",reducedMotion:"reduce",javaScriptEnabled:false},
];
let pageChecks=0;
for(const mode of modes){
  const context=await browser.newContext(mode);
  for(const slug of slugs){
    const page=await context.newPage();await page.goto(`${lessonRoot}/${slug}/`,{waitUntil:"domcontentloaded"});
    const audit=await page.evaluate(()=>({
      title:document.querySelector("h1")?.textContent?.trim(),
      overflow:document.documentElement.scrollWidth>document.documentElement.clientWidth,
      profiles:["零基础兴趣","有基础兴趣","零基础求职","有基础求职"].every(text=>document.body.innerText.includes(text)),
      project:document.body.innerText.includes("智能学习助手"),command:document.body.innerText.includes("python"),source:document.body.innerText.includes("来源与版本"),
    }));
    if(!audit.title||audit.overflow||!audit.profiles||!audit.project||!audit.command||!audit.source)throw new Error(`${mode.name} ${slug}: ${JSON.stringify(audit)}`);
    pageChecks+=1;await page.close();
  }
  await context.close();
}
const keyboard=await browser.newContext({viewport:{width:1440,height:900}});const page=await keyboard.newPage();
await page.goto(`${lessonRoot}/${slugs.at(-1)}/`,{waitUntil:"networkidle"});const launcher=page.locator('button[aria-label="打开学习助教"]');
await launcher.focus();await page.keyboard.press("Enter");await page.locator('.be-tutor-panel[role="dialog"]').waitFor({state:"visible"});await page.keyboard.press("Escape");
const focused=await page.evaluate(()=>document.activeElement?.getAttribute("aria-label")||"");if(focused!=="打开学习助教")throw new Error(`keyboard focus did not return: ${focused}`);
await keyboard.close();await browser.close();console.log(JSON.stringify({valid:true,page_checks:pageChecks,modes:modes.map(mode=>mode.name),keyboard_focus:focused},null,2));
