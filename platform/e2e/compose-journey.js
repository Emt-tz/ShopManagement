/* Turns out/journey/ (screen frames with real timestamps + marks) into out/journey.mp4.
 * Layout: a slim top bar with the chapter, the app in the middle, a caption bar below it so nothing ever covers the UI.
 * Motion: intro and outro cards, chapter labels that slide in, captions that fade, five-step progress. All drawn as ASS (anti-aliased, frame-accurate). */
const fs = require('fs'), path = require('path');
const { execFileSync } = require('child_process');
const OUT = path.join(__dirname, 'out'), J = path.join(OUT, 'journey');
const tl = JSON.parse(fs.readFileSync(path.join(J, 'timeline.json')));
const W = 1920, H = 1080, TOP = 56, BOT = 104, VW = Math.round((H - TOP - BOT) * 16 / 9 / 2) * 2, VH = H - TOP - BOT, VX = (W - VW) / 2;
const first = tl.frames[0].ts, skip = Math.max(0, tl.T0 - first - 0.25);
const t = wall => wall - first - skip;                       // seconds in the trimmed video
const dur = t(tl.END) + 1.6;

// 1) frame list with true durations, then constant 30 fps
const lines = [];
tl.frames.forEach((f, i) => {
  const next = i + 1 < tl.frames.length ? tl.frames[i + 1].ts : tl.END + 1.6;
  lines.push(`file '${path.join(J, f.file)}'`, `duration ${Math.max(0.001, next - f.ts).toFixed(4)}`);
});
lines.push(`file '${path.join(J, tl.frames[tl.frames.length - 1].file)}'`);
fs.writeFileSync(path.join(J, 'frames.txt'), lines.join('\n'));

// 2) overlays
const ts = s => { s = Math.max(0, s); const h = Math.floor(s / 3600), m = Math.floor(s % 3600 / 60), x = (s % 60).toFixed(2); return `${h}:${String(m).padStart(2, '0')}:${x.padStart(5, '0')}`; };
const esc = s => s.replace(/[{}\\]/g, '');
const ev = [];
const D = (layer, a, b, style, text) => ev.push(`Dialogue: ${layer},${ts(a)},${ts(b)},${style},,0,0,0,,${text}`);
const rect = (x, y, w, h) => `m ${x} ${y} l ${x + w} ${y} ${x + w} ${y + h} ${x} ${y + h}`;
const chapters = tl.marks.filter(m => m.kind === 'chapter'), caps = tl.marks.filter(m => m.kind === 'cap');

// progress: thin line along the very bottom, growing
D(5, 0, dur, 'Draw', `{\\an7\\pos(0,${H - 5})\\1c&HE37100&\\fscx0\\t(0,${Math.round(dur * 1000)},\\fscx100)\\p1}${rect(0, 0, W, 5)}{\\p0}`);
// top bar: brand left, chapter label (slides in), five steps right
D(5, 0, dur, 'Brand', `{\\an4\\pos(${VX},${TOP / 2})}Emt Shop`);
for (let i = 0; i < 5; i++) {
  const c = chapters.find(x => x.n === i + 1); const a = c ? t(c.at) : dur;
  const sx = W - VX - (5 - i) * 64 + 8;
  D(5, 0, dur, 'Draw', `{\\an7\\pos(${sx},${TOP / 2 - 3})\\1c&H3A3A3C&\\p1}${rect(0, 0, 52, 6)}{\\p0}`);
  if (c) D(6, a, dur, 'Draw', `{\\an7\\pos(${sx},${TOP / 2 - 3})\\1c&HE37100&\\fscx0\\t(0,500,\\fscx100)\\p1}${rect(0, 0, 52, 6)}{\\p0}`);
}
chapters.forEach((c, i) => {
  const a = t(c.at), b = i + 1 < chapters.length ? t(chapters[i + 1].at) : dur - 2;
  D(5, a, b, 'Chap', `{\\an4\\move(${VX + 190},${TOP / 2 + 14},${VX + 190},${TOP / 2},0,380)\\fad(380,300)}${c.n}  ·  ${esc(c.title)}`);
  D(5, a + 0.1, b, 'ChapSub', `{\\an4\\pos(${VX + 190 + 20 + (c.n + '  ·  ' + c.title).length * 17},${TOP / 2 + 1})\\fad(500,300)}${esc(c.sub)}`);
});
// captions in the bar under the app
caps.forEach((c, i) => {
  const a = t(c.at) + 0.05, b = i + 1 < caps.length ? t(caps[i + 1].at) - 0.02 : dur - 2.2;
  if (b - a > 0.4) D(6, a, b, 'Cap', `{\\an5\\move(960,${H - BOT / 2 + 12},960,${H - BOT / 2 - 2},0,280)\\fad(280,220)}${esc(c.txt)}`);
});
// intro / outro
D(8, 0, 3.2, 'Draw', `{\\an7\\pos(0,0)\\1c&H1C1C1E&\\fad(0,700)\\p1}${rect(0, 0, W, H)}{\\p0}`);
D(9, 0.1, 3.2, 'Title', `{\\an5\\pos(960,470)\\fad(500,700)\\fscx90\\fscy90\\t(0,1300,\\fscx100\\fscy100)}Emt Shop`);
D(9, 0.1, 3.2, 'Sub', `{\\an5\\pos(960,566)\\fad(900,700)}From the first sign-up to the first sale`);
D(8, dur - 2.4, dur, 'Draw', `{\\an7\\pos(0,0)\\1c&H1C1C1E&\\fad(900,0)\\p1}${rect(0, 0, W, H)}{\\p0}`);
D(9, dur - 2.1, dur, 'Title', `{\\an5\\pos(960,500)\\fad(800,0)\\fs96}Add stock. Sell. Grow.`);

const ass = `[Script Info]
ScriptType: v4.00+
PlayResX: ${W}
PlayResY: ${H}
WrapStyle: 0
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name,Fontname,Fontsize,PrimaryColour,SecondaryColour,OutlineColour,BackColour,Bold,Italic,Underline,StrikeOut,ScaleX,ScaleY,Spacing,Angle,BorderStyle,Outline,Shadow,Alignment,MarginL,MarginR,MarginV,Encoding
Style: Draw,DejaVu Sans,20,&H00FFFFFF,&H000000FF,&H00000000,&H00000000,0,0,0,0,100,100,0,0,1,0,0,7,0,0,0,1
Style: Brand,DejaVu Sans,26,&H00FFFFFF,&H000000FF,&H00000000,&H00000000,-1,0,0,0,100,100,0,0,1,0,0,4,0,0,0,1
Style: Chap,DejaVu Sans,26,&H00FFAA33,&H000000FF,&H00000000,&H00000000,-1,0,0,0,100,100,0,0,1,0,0,4,0,0,0,1
Style: ChapSub,DejaVu Sans,22,&H00A0A0A8,&H000000FF,&H00000000,&H00000000,0,0,0,0,100,100,0,0,1,0,0,4,0,0,0,1
Style: Title,DejaVu Sans,120,&H00FFFFFF,&H000000FF,&H00000000,&H00000000,-1,0,0,0,100,100,0,0,1,0,0,5,0,0,0,1
Style: Sub,DejaVu Sans,44,&H00BBBBBB,&H000000FF,&H00000000,&H00000000,0,0,0,0,100,100,0,0,1,0,0,5,0,0,0,1
Style: Cap,DejaVu Sans,35,&H00FFFFFF,&H000000FF,&H00000000,&H00000000,0,0,0,0,100,100,0,0,1,0,0,5,170,170,0,1

[Events]
Format: Layer,Start,End,Style,Name,MarginL,MarginR,MarginV,Effect,Text
${ev.join('\n')}
`;
fs.writeFileSync(path.join(J, 'journey.ass'), ass);

const f = [
  `[0:v]fps=30,scale=${VW}:${VH}:flags=lanczos,setsar=1[a]`,
  `color=c=0x111114:s=${W}x${H}:r=30:d=${dur.toFixed(2)}[bg]`,
  `[bg][a]overlay=${VX}:${TOP}:eof_action=repeat[b]`,
  `[b]drawbox=x=${VX - 1}:y=${TOP - 1}:w=${VW + 2}:h=${VH + 2}:color=0x2c2c31:t=1[c]`,
  `[c]ass=${path.join(J, 'journey.ass')}:fontsdir=/usr/share/fonts/truetype/dejavu,fade=t=in:st=0:d=0.4[v]`
].join(';');
console.log(`composing ${dur.toFixed(1)}s (${tl.frames.length} frames) ...`);
execFileSync('ffmpeg', ['-y', '-hide_banner', '-loglevel', 'error', '-ss', String(skip), '-f', 'concat', '-safe', '0', '-i', path.join(J, 'frames.txt'), '-filter_complex', f, '-map', '[v]', '-t', String(dur),
  '-c:v', 'libx264', '-preset', 'medium', '-crf', '19', '-pix_fmt', 'yuv420p', '-movflags', '+faststart', path.join(OUT, 'journey.mp4')], { stdio: 'inherit' });
console.log('wrote out/journey.mp4');
