// Render the pack art from art/src/art.html with the pre-installed Chromium.
//   node art/render.cjs [path/to/in-game-shot.png]
// Writes art/out/: logo.png (transparent), icon_1024.png and icon.png (512, from src/icon.html), menu_background.png, menu_background_dark.png and
// title_card.png (1920x1080, only when a shot is given), and art/out/menu/btn_<entry>_<normal|hover>.png. The in-game shot is a real screenshot from the pack (see art/README.md).
const { chromium } = require('playwright');
const path = require('path');
const fs = require('fs');

(async () => {
  const root = __dirname;
  const out = path.join(root, 'out');
  fs.mkdirSync(path.join(out, 'menu'), { recursive: true });
  const shot = process.argv[2] ? 'file://' + path.resolve(process.argv[2]) : null;
  const browser = await chromium.launch();
  const jobs = [
    { view: 'logo', w: 1600, h: 700, file: 'logo.png', transparent: true },
  ];
  if (shot) jobs.push({ view: 'menu', w: 1920, h: 1080, file: 'menu_background.png' },
                      { view: 'menu2', w: 1920, h: 1080, file: 'menu_background_dark.png' },
                      { view: 'card', w: 1920, h: 1080, file: 'title_card.png' });
  // Title-screen menu entries: each label in its idle and hovered state (transparent, 640x64 = 160x16 GUI at 4x).
  for (const [key, label] of [['singleplayer', 'SINGLEPLAYER'], ['multiplayer', 'MULTIPLAYER'], ['mods', 'MODS'],
                              ['options', 'OPTIONS'], ['quit', 'QUIT GAME']])
    for (const state of ['normal', 'hover'])
      jobs.push({ view: 'btn', w: 640, h: 64, file: `menu/btn_${key}_${state}.png`, transparent: true,
                  extra: `&label=${encodeURIComponent(label)}&state=${state}` });
  for (const j of jobs) {
    const page = await browser.newPage({ viewport: { width: j.w, height: j.h } });
    const hash = `view=${j.view}` + (shot ? `&shot=${encodeURIComponent(shot)}` : '') + (j.extra || '');
    await page.goto('file://' + path.join(root, 'src', 'art.html') + '#' + hash);
    await page.evaluate(() => document.fonts.ready);
    await page.waitForTimeout(300);
    await page.locator('#' + j.view).screenshot({ path: path.join(out, j.file), omitBackground: !!j.transparent });
    await page.close();
    console.log('wrote', path.join('art/out', j.file));
  }
  // The icon (the CurseForge project avatar) is its own page, drawn at 1024 and rendered at full and half scale.
  for (const [scale, file] of [[1, 'icon_1024.png'], [0.5, 'icon.png']]) {
    const page = await browser.newPage({ viewport: { width: 1024, height: 1024 }, deviceScaleFactor: scale });
    await page.goto('file://' + path.join(root, 'src', 'icon.html'));
    await page.evaluate(() => document.fonts.ready);
    await page.waitForTimeout(300);
    await page.locator('#icon').screenshot({ path: path.join(out, file) });
    await page.close();
    console.log('wrote', path.join('art/out', file));
  }
  await browser.close();
})();
