// Render the pack art from art/src/art.html with the pre-installed Chromium.
//   node art/render.cjs [path/to/in-game-shot.png]
// Writes art/out/: logo.png (transparent), icon_1024.png and icon.png (512, from src/icon.html), menu_background.png, menu_background_dark.png and
// title_card.png (1920x1080, only when a shot is given), and art/out/menu/btn_<entry>_normal.png + btn_<entry>_hover.apng. The in-game shot is a real screenshot from the pack (see art/README.md).
const { chromium } = require('playwright');
const path = require('path');
const fs = require('fs');
const zlib = require('zlib');

// A minimal APNG writer: every frame is a full-size RGBA PNG of the same size; frame i shows for delays[i] ms.
function pngChunks(buf) {
  const out = [];
  for (let o = 8; o < buf.length;) {
    const len = buf.readUInt32BE(o);
    out.push({ type: buf.toString('ascii', o + 4, o + 8), data: buf.subarray(o + 8, o + 8 + len) });
    o += 12 + len;
  }
  return out;
}
function pngChunk(type, data) {
  const len = Buffer.alloc(4), crc = Buffer.alloc(4), body = Buffer.concat([Buffer.from(type, 'ascii'), data]);
  len.writeUInt32BE(data.length); crc.writeUInt32BE(zlib.crc32(body));
  return Buffer.concat([len, body, crc]);
}
function apng(frames, delays, plays) {
  const ihdr = pngChunks(frames[0]).find(c => c.type === 'IHDR').data;
  const actl = Buffer.alloc(8); actl.writeUInt32BE(frames.length, 0); actl.writeUInt32BE(plays, 4);
  const parts = [frames[0].subarray(0, 8), pngChunk('IHDR', ihdr), pngChunk('acTL', actl)];
  let seq = 0;
  frames.forEach((f, i) => {
    const fctl = Buffer.alloc(26);
    fctl.writeUInt32BE(seq++, 0); fctl.writeUInt32BE(ihdr.readUInt32BE(0), 4); fctl.writeUInt32BE(ihdr.readUInt32BE(4), 8);
    fctl.writeUInt16BE(delays[i], 20); fctl.writeUInt16BE(1000, 22);   // dispose none, blend source (bytes 24-25 = 0)
    parts.push(pngChunk('fcTL', fctl));
    for (const c of pngChunks(f).filter(c => c.type === 'IDAT')) {
      if (i === 0) { parts.push(pngChunk('IDAT', c.data)); continue; }
      const s = Buffer.alloc(4); s.writeUInt32BE(seq++);
      parts.push(pngChunk('fdAT', Buffer.concat([s, c.data])));
    }
  });
  parts.push(pngChunk('IEND', Buffer.alloc(0)));
  return Buffer.concat(parts);
}

(async () => {
  const root = __dirname;
  const out = path.join(root, 'out');
  fs.mkdirSync(path.join(out, 'menu'), { recursive: true });
  const shotArg = process.argv.slice(2).find(a => !a.startsWith('--'));
  const shot = shotArg ? 'file://' + path.resolve(shotArg) : null;
  const browser = await chromium.launch();
  const jobs = [
    { view: 'logo', w: 1600, h: 700, file: 'logo.png', transparent: true },
  ];
  if (shot) jobs.push({ view: 'menu', w: 1920, h: 1080, file: 'menu_background.png' },
                      { view: 'menu2', w: 1920, h: 1080, file: 'menu_background_dark.png' },
                      { view: 'card', w: 1920, h: 1080, file: 'title_card.png' });
  // Title-screen menu entries (transparent, 920x112 = 230x28 GUI units at 4x): the idle label as a PNG, and the hover
  // as an APNG that plays once: the rules grow out from the word and the glow and diamonds fade in over 160 ms.
  const ENTRIES = [['singleplayer', 'SINGLEPLAYER'], ['multiplayer', 'MULTIPLAYER'], ['mods', 'MODS'],
                   ['options', 'OPTIONS'], ['quit', 'QUIT GAME']];
  const HOVER_T = [0.125, 0.25, 0.375, 0.5, 0.625, 0.75, 0.875, 1];
  for (const [key, label] of ENTRIES) {
    jobs.push({ view: 'btn', w: 920, h: 112, file: `menu/btn_${key}_normal.png`, transparent: true,
                extra: `&label=${encodeURIComponent(label)}&state=normal` });
    HOVER_T.forEach((t, i) => jobs.push({ view: 'btn', w: 920, h: 112, file: `menu/.frames/${key}_${i}.png`, transparent: true,
                                          extra: `&label=${encodeURIComponent(label)}&state=hover&t=${t}` }));
  }
  // The sponsor entry (bottom-right of the title screen, 736x120 = 184x30 GUI units at 4x) and the 16x16 mark for the
  // Multiplayer screen's button (64x64). Both show the supplied banner in art/sponsors/ through a window: the cube
  // mark is cropped, never redrawn. `node art/render.cjs --sponsor` renders only these three.
  const SPONSOR = [
    { view: 'sponsor', w: 736, h: 120, file: 'menu/btn_server_normal.png', transparent: true, extra: '&state=normal' },
    { view: 'sponsor', w: 736, h: 120, file: 'menu/btn_server_hover.png', transparent: true, extra: '&state=hover' },
    { view: 'apexicon', w: 64, h: 64, file: 'sponsor/apex_icon.png' },
  ];
  const sponsorOnly = process.argv.includes('--sponsor');
  if (sponsorOnly) jobs.length = 0;
  jobs.push(...SPONSOR);
  for (const j of jobs) {
    const page = await browser.newPage({ viewport: { width: j.w, height: j.h } });
    const hash = `view=${j.view}` + (shot ? `&shot=${encodeURIComponent(shot)}` : '') + (j.extra || '');
    await page.goto('file://' + path.join(root, 'src', 'art.html') + '#' + hash);
    await page.evaluate(() => document.fonts.ready);
    if (j.view === 'btn') await page.waitForSelector('body[data-ready="1"]');
    await page.waitForTimeout(300);
    fs.mkdirSync(path.dirname(path.join(out, j.file)), { recursive: true });
    await page.locator('#' + j.view).screenshot({ path: path.join(out, j.file), omitBackground: !!j.transparent });
    await page.close();
    console.log('wrote', path.join('art/out', j.file));
  }
  if (sponsorOnly) { await browser.close(); return; }
  // Pack each entry's hover frames into one APNG: 20 ms a frame, the last held for a minute, played once.
  for (const [key] of ENTRIES) {
    const frames = HOVER_T.map((_, i) => fs.readFileSync(path.join(out, 'menu', '.frames', `${key}_${i}.png`)));
    fs.writeFileSync(path.join(out, 'menu', `btn_${key}_hover.apng`), apng(frames, HOVER_T.map((_, i) => i === HOVER_T.length - 1 ? 60000 : 20), 1));
    console.log('wrote', `art/out/menu/btn_${key}_hover.apng`);
  }
  fs.rmSync(path.join(out, 'menu', '.frames'), { recursive: true, force: true });

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
