import { existsSync } from "node:fs";
import { chromium } from "../../web-engineering/learning-dashboard-v12/node_modules/playwright/index.mjs";
const executablePath=process.env.PLAYWRIGHT_CHROMIUM_EXECUTABLE||"/Users/jiafei/Library/Caches/ms-playwright/chromium_headless_shell-1223/chrome-headless-shell-mac-arm64/chrome-headless-shell";
if(!existsSync(executablePath))throw new Error("Chromium executable not found");
const browser=await chromium.launch({headless:true,executablePath});const base=process.env.RAG_APP_BASE_URL||"http://127.0.0.1:8766";
for(const mode of [{name:"desktop",viewport:{width:1440,height:900},colorScheme:"light",reducedMotion:"no-preference",javaScriptEnabled:true},{name:"mobile-dark-reduced",viewport:{width:390,height:844},colorScheme:"dark",reducedMotion:"reduce",javaScriptEnabled:true}]){
 const context=await browser.newContext(mode);const page=await context.newPage();await page.goto(base,{waitUntil:"networkidle"});
 await page.locator("#upload button").click();await page.locator("#ingestion-status").filter({hasText:"succeeded"}).waitFor();
 await page.locator("#chat button").click();await page.locator("#answer-status").filter({hasText:"ACL"}).waitFor();
 const audit=await page.evaluate(()=>({overflow:document.documentElement.scrollWidth>document.documentElement.clientWidth,citations:document.querySelectorAll("#citations li").length,context:document.querySelector("#retrieval-detail")?.textContent?.includes("prompt_version")}));
 if(audit.overflow||audit.citations!==1||!audit.context)throw new Error(`${mode.name}: ${JSON.stringify(audit)}`);await context.close();
}
const nojs=await browser.newContext({viewport:{width:390,height:844},javaScriptEnabled:false,reducedMotion:"reduce"});const page=await nojs.newPage();await page.goto(base,{waitUntil:"domcontentloaded"});
if(!(await page.locator("noscript").textContent())?.includes("/docs"))throw new Error("no-js instructions missing");await nojs.close();await browser.close();
console.log(JSON.stringify({valid:true,application_checks:3,citations:true,no_js:true},null,2));
