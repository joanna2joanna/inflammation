const { chromium } = require('playwright');
const [input, output] = process.argv.slice(2);
if (!input || !output) {
  console.error('Usage: node screenshot.js <input.html> <output.png>');
  process.exit(1);
}
(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage();
  await page.setViewportSize({ width: 1080, height: 800 });
  await page.goto(`file://${process.cwd()}/${input}`, { waitUntil: 'networkidle' });
  await page.addStyleTag({ content: '.nav-fixed { display: none !important; }' });
  const height = await page.evaluate(() => document.body.scrollHeight);
  await page.screenshot({ path: output, fullPage: true });
  console.log(`${output}: 1080×${height}`);
  await browser.close();
})();
