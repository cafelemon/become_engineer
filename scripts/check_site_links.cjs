const fs = require("node:fs");
const path = require("node:path");

const siteDir = path.resolve(process.argv[2] || "site");
if (!fs.existsSync(siteDir)) throw new Error(`站点目录不存在：${siteDir}`);

function walk(directory) {
  return fs.readdirSync(directory, { withFileTypes: true }).flatMap((entry) => {
    const full = path.join(directory, entry.name);
    return entry.isDirectory() ? walk(full) : [full];
  });
}

const htmlFiles = walk(siteDir).filter((file) => file.endsWith(".html"));
const htmlCache = new Map(htmlFiles.map((file) => [file, fs.readFileSync(file, "utf8")]));
const failures = [];
let checkedLinks = 0;
let checkedAnchors = 0;

function targetFile(fromFile, hrefPath) {
  let decoded;
  try {
    decoded = decodeURI(hrefPath);
  } catch {
    decoded = hrefPath;
  }
  const basePrefix = "/become_engineer/";
  let candidate;
  if (decoded.startsWith(basePrefix)) candidate = path.join(siteDir, decoded.slice(basePrefix.length));
  else if (decoded.startsWith("/")) candidate = path.join(siteDir, decoded.slice(1));
  else candidate = path.resolve(path.dirname(fromFile), decoded || path.basename(fromFile));

  const options = [candidate];
  if (candidate.endsWith(path.sep) || !path.extname(candidate)) options.push(path.join(candidate, "index.html"));
  if (!path.extname(candidate)) options.push(`${candidate}.html`);
  return options.find((item) => fs.existsSync(item) && fs.statSync(item).isFile()) || null;
}

for (const file of htmlFiles) {
  const html = htmlCache.get(file);
  const hrefPattern = /href=["']([^"']+)["']/g;
  for (const match of html.matchAll(hrefPattern)) {
    const href = match[1];
    if (!href || /^(?:https?:|mailto:|tel:|javascript:|data:)/i.test(href)) continue;
    const [rawPath, rawFragment = ""] = href.split("#", 2);
    const cleanPath = rawPath.split("?", 1)[0];
    const target = targetFile(file, cleanPath);
    checkedLinks += 1;
    if (!target) {
      failures.push(`${path.relative(siteDir, file)} -> ${href}（目标不存在）`);
      continue;
    }
    if (rawFragment) {
      let fragment;
      try {
        fragment = decodeURIComponent(rawFragment);
      } catch {
        fragment = rawFragment;
      }
      checkedAnchors += 1;
      const targetHtml = htmlCache.get(target) || fs.readFileSync(target, "utf8");
      const escaped = fragment.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
      if (!new RegExp(`(?:id|name)=["']${escaped}["']`).test(targetHtml)) failures.push(`${path.relative(siteDir, file)} -> ${href}（锚点不存在）`);
    }
  }
}

if (failures.length) {
  console.error(failures.slice(0, 100).join("\n"));
  throw new Error(`站点内部链接检查失败：${failures.length} 项`);
}

console.log(JSON.stringify({ valid: true, html_files: htmlFiles.length, checked_links: checkedLinks, checked_anchors: checkedAnchors }, null, 2));
