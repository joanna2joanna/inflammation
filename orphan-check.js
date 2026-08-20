// 孤字检测：查小红书卡片文本换行后有没有 行尾孤字/字+标点/左括号、行首右括号/右引号
// 用法: NODE_PATH=... node orphan-check.js issues/issue-87.html
const { chromium } = require('playwright');
const file = process.argv[2] || 'issues/issue-87.html';
(async () => {
  const browser = await chromium.launch();
  try {
    const page = await browser.newPage();
    await page.setViewportSize({ width: 1080, height: 800 });
    await page.goto(`file://${process.cwd()}/${file}`, { waitUntil: 'networkidle' });
    const res = await page.evaluate(() => {
      const results = [];
      const selectors = ['.hero h1', '.hero .flip', '.why-card p', '.action-list .what', '.action-list .why', '.source div'];
      for (const sel of selectors) {
        for (const el of document.querySelectorAll(sel)) {
          const walker = document.createTreeWalker(el, NodeFilter.SHOW_TEXT);
          const nodes = [];
          while (walker.nextNode()) nodes.push(walker.currentNode);
          const total = nodes.reduce((s, n) => s + n.nodeValue.length, 0);
          if (!total) continue;
          const pos = (off) => {
            let cum = 0;
            for (const n of nodes) {
              if (off <= cum + n.nodeValue.length) return { n, off: off - cum };
              cum += n.nodeValue.length;
            }
            const n = nodes[nodes.length - 1];
            return { n, off: n.nodeValue.length };
          };
          const textOf = (a, b) => {
            let s = '', cum = 0;
            for (const n of nodes) {
              if (b > cum && a < cum + n.nodeValue.length) s += n.nodeValue.slice(Math.max(0, a - cum), b - cum);
              cum += n.nodeValue.length;
              if (cum >= b) break;
            }
            return s;
          };
          const lineCount = (end) => {
            const r = document.createRange();
            const pa = pos(0), pb = pos(end);
            r.setStart(pa.n, pa.off);
            r.setEnd(pb.n, pb.off);
            // 按行顶 Y 归组，消除 em 等内联盒把同一行切成多块的误报
            const tops = new Set();
            for (const rect of r.getClientRects()) tops.add(Math.round(rect.top));
            return tops.size;
          };
          const breaks = [0];
          let prev = -1;
          for (let i = 1; i <= total; i++) {
            const c = lineCount(i);
            if (c > prev) { if (prev >= 0) breaks.push(i); prev = c; }
          }
          if (breaks[breaks.length - 1] !== total) breaks.push(total);
          const lines = [];
          for (let k = 0; k < breaks.length - 1; k++) lines.push(textOf(breaks[k], breaks[k + 1]));
          const closeStart = /^[）」』】》〉」』〕〉」"”’]/;
          const openEnd = /[（「『【“]$/;
          const problems = [];
          for (const ln of lines) {
            if (closeStart.test(ln)) problems.push(`行首右括号: "${ln}"`);
            if (openEnd.test(ln)) problems.push(`行尾左括号: "${ln}"`);
            const stripped = ln.replace(/[，。、；：！？…""''）】》〉』」」]+$/, '');
            const m = stripped.match(/[一-鿿]+$/);
            if (m && m[0].length === 1) problems.push(`行尾孤字: "${ln}"`);
          }
          if (problems.length) results.push({ sel, lines, problems });
        }
      }
      return results;
    });
    if (res.length === 0) { console.log('✅ 无孤字问题'); }
    else { console.log(JSON.stringify(res, null, 2)); }
  } finally { await browser.close(); }
})();
