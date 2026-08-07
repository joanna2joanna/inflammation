const { chromium } = require('playwright');
const path = require('path');

// 检查 HTML 里的孤字换行：行末不得出现单字、字+标点掉到下一行
// 用法: node check_orphan.js issues/issue-77.html issues/issue-78.html
//       或  node check_orphan.js issues/issue-7*.html

// 标点净化：去掉这些字符后若一行只剩 ≤1 个有效字符，即判定为孤行
// 正则用源码字符串传入浏览器（playwright 序列化会把 RegExp 对象搞坏）
const PUNCT_SOURCE = '[\\s。，、；：！？,.；：—–…【】「」""\'\'（）()]';

// 要检查的文本块
const SELECTORS = [
  '.hero h1',
  '.hero .flip',
  '.why-card p',
  '.action-list .what',
  '.action-list .why',
];

async function checkFile(file) {
  const browser = await chromium.launch();
  try {
    const page = await browser.newPage();
    await page.setViewportSize({ width: 1080, height: 800 });
    await page.goto(`file://${path.resolve(file)}`, { waitUntil: 'networkidle' });
    const orphans = await page.evaluate(({ sels, punctSource }) => {
      const punct = new RegExp(punctSource, 'g');
      const results = [];
      sels.forEach(sel => {
        document.querySelectorAll(sel).forEach(el => {
          const lines = {};
          const walker = document.createTreeWalker(el, NodeFilter.SHOW_TEXT);
          while (walker.nextNode()) {
            const node = walker.currentNode;
            for (let i = 0; i < node.textContent.length; i++) {
              const range = document.createRange();
              range.setStart(node, i);
              range.setEnd(node, i + 1);
              const r = range.getClientRects()[0];
              if (r) {
                const top = Math.round(r.top);
                (lines[top] ||= []).push(node.textContent[i]);
              }
            }
          }
          Object.values(lines).forEach(arr => {
            const str = arr.join('');
            if (str.replace(punct, '').length <= 1 && str.length > 0) {
              results.push({ block: sel, orphan: str });
            }
          });
        });
      });
      return results;
    }, { sels: SELECTORS, punctSource: PUNCT_SOURCE });
    console.log(orphans.length
      ? `✗ ${file}: ${orphans.map(o => `${o.block}「${o.orphan}」`).join('; ')}`
      : `✓ ${file}: 无孤字`);
    return orphans.length;
  } finally {
    await browser.close();
  }
}

(async () => {
  const files = process.argv.slice(2);
  if (!files.length) {
    console.error('用法: node check_orphan.js <file.html> [more...]');
    process.exit(1);
  }
  let bad = 0;
  for (const f of files) {
    bad += await checkFile(f);
  }
  process.exit(bad ? 1 : 0);
})();
