// Render the pack art from art/src/art.html with the pre-installed Chromium.
//   node art/render.cjs [path/to/in-game-shot.png]
// Writes art/out/: logo.png (transparent), icon.png (512), menu_background.png and title_card.png (1920x1080,
// only when a shot is given). The in-game shot is a real screenshot from the pack (see art/README.md).
const { chromium } = require('playwright');
const path = require('path');
const fs = require('fs');

(async () => {
  const root = __dirname;
  const out = path.join(root, 'out');
  fs.mkdirSync(out, { recursive: true });
  const shot = process.argv[2] ? 'file://' + path.resolve(process.argv[2]) : null;
  const browser = await chromium.launch();
  const jobs = [
    { view: 'logo', w: 1600, h: 700, file: 'logo.png', transparent: true },
    { view: 'icon', w: 512, h: 512, file: 'icon.png' },
  ];
  if (shot) jobs.push({ view: 'menu', w: 1920, h: 1080, file: 'menu_background.png' },
                      { view: 'card', w: 1920, h: 1080, file: 'title_card.png' });
  for (const j of jobs) {
    const page = await browser.newPage({ viewport: { width: j.w, height: j.h } });
    const hash = `view=${j.view}` + (shot ? `&shot=${encodeURIComponent(shot)}` : '');
    await page.goto('file://' + path.join(root, 'src', 'art.html') + '#' + hash);
    await page.evaluate(() => document.fonts.ready);
    await page.waitForTimeout(300);
    await page.locator('#' + j.view).screenshot({ path: path.join(out, j.file), omitBackground: !!j.transparent });
    await page.close();
    console.log('wrote', path.join('art/out', j.file));
  }
  await browser.close();
})();
