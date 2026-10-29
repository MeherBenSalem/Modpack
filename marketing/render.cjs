// Render the CurseForge/Modrinth page images: every entry of marketing/src/images.json -> marketing/images/<name>.png.
//   node marketing/render.cjs [name ...]
// Uses the pre-installed Chromium (Playwright). Dividers and headers are transparent PNGs, like the other NightBeam pages.
const { chromium } = require('playwright');
const fs = require('fs'), path = require('path');
(async () => {
  const here = __dirname;
  const specs = JSON.parse(fs.readFileSync(path.join(here, 'src', 'images.json')));
  const only = process.argv.slice(2);
  fs.mkdirSync(path.join(here, 'images'), { recursive: true });
  const sizes = { banner: [1800, 600], divider: [1400, 40], header: [1400, 120], card: [1600, 900], trailer: [1600, 900] };
  const browser = await chromium.launch();
  for (const [name, spec] of Object.entries(specs)) {
    if (only.length && !only.includes(name)) continue;
    const [w, h] = sizes[spec.kind];
    const page = await browser.newPage({ viewport: { width: w, height: h } });
    await page.goto('file://' + path.join(here, 'src', 'marketing.html') + '#' + encodeURIComponent(JSON.stringify(spec)));
    await page.evaluate(() => document.fonts.ready);
    await page.waitForTimeout(250);
    const transparent = spec.kind === 'divider' || spec.kind === 'header';
    await page.locator('#root').screenshot({ path: path.join(here, 'images', name + '.png'), omitBackground: transparent });
    await page.close();
    console.log('wrote marketing/images/' + name + '.png');
  }
  await browser.close();
})();
