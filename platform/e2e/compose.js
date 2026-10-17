/* Builds out/demo.mp4 from the three recorded browsers: owner iPhone, cashier iPhone, Mac app, with step captions. */
const fs = require('fs');
const path = require('path');
const { execFileSync } = require('child_process');

const OUT = path.join(__dirname, 'out');
const tl = JSON.parse(fs.readFileSync(path.join(OUT, 'timeline.json')));
const W = 2560, H = 1440, FPS = 25;
const base = Math.min(tl.created.phone, tl.created.desktop, tl.created.staff);
const off = k => (tl.created[k] - base) / 1000;
const t0 = (tl.t0 - base) / 1000 + 1.0; // Playwright video lags wall-clock slightly
const last = tl.steps[tl.steps.length - 1];
const duration = Math.ceil(t0 + last.end / 1000 + 3);

const ts = s => { const h = Math.floor(s / 3600), m = Math.floor(s % 3600 / 60), x = (s % 60).toFixed(2); return `${h}:${String(m).padStart(2, '0')}:${x.padStart(5, '0')}`; };
const lines = [];
const style = (name, size, color, bold) => `Style: ${name},DejaVu Sans,${size},${color},&H000000FF,&H00000000,&H64000000,${bold ? -1 : 0},0,0,0,100,100,0,0,1,0,0,7,0,0,0,1`;
// Static labels
const label = (txt, x, y, size, color) => lines.push(`Dialogue: 0,${ts(0)},${ts(duration)},Label,,0,0,0,,{\\pos(${x},${y})\\c${color}&}${txt}`);
// One caption per visible step, held until the next step starts
const visible = tl.steps.filter(s => s.end - s.start > 800);
visible.forEach((s, i) => {
  const a = t0 + s.start / 1000, b = i + 1 < visible.length ? t0 + visible[i + 1].start / 1000 : duration;
  const m = /^(\d+)\.(\d+) (.*)$/.exec(s.name);
  const num = m ? `Flow ${m[1]}.${m[2]}` : '';
  const txt = (m ? m[3] : s.name).replace(/[{}\\]/g, '');
  lines.push(`Dialogue: 1,${ts(a)},${ts(b)},Cap,,0,0,0,,{\\pos(1180,1000)\\c&HFFAA33&\\fs34}${num}`);
  lines.push(`Dialogue: 1,${ts(a)},${ts(b)},Cap,,0,0,0,,{\\pos(1180,1050)\\fs46}${txt}`);
});
label('Emt Shop', 60, 40, 60, '&HFFFFFF');
label('One server, every device, live. Recorded from the real running product.', 330, 62, 34, '&HBBBBBB');
label('Owner · iPhone 15', 60, 120, 32, '&HDDDDDD');
label('Cashier Asha · iPhone 14', 640, 120, 32, '&HDDDDDD');
label('Owner · Mac app', 1210, 120, 32, '&HDDDDDD');

const ass = `[Script Info]
ScriptType: v4.00+
PlayResX: ${W}
PlayResY: ${H}
WrapStyle: 0

[V4+ Styles]
Format: Name,Fontname,Fontsize,PrimaryColour,SecondaryColour,OutlineColour,BackColour,Bold,Italic,Underline,StrikeOut,ScaleX,ScaleY,Spacing,Angle,BorderStyle,Outline,Shadow,Alignment,MarginL,MarginR,MarginV,Encoding
${style('Label', 34, '&H00FFFFFF', false)}
Style: Cap,DejaVu Sans,46,&H00FFFFFF,&H000000FF,&H00000000,&H64000000,0,0,0,0,100,100,0,0,1,0,0,7,1180,80,0,1

[Events]
Format: Layer,Start,End,Style,Name,MarginL,MarginR,MarginV,Effect,Text
${lines.join('\n')}
`;
fs.writeFileSync(path.join(OUT, 'captions.ass'), ass);

const vid = k => tl.videos[k];
const PW = 507, PH = 1097; // 390x844 scaled by 1.3
const frame = (x, y, w, h) => `drawbox=x=${x - 8}:y=${y - 8}:w=${w + 16}:h=${h + 16}:color=0x3a3a3c:t=8`;
const filter = [
  `color=c=0x0d0d10:s=${W}x${H}:r=${FPS}:d=${duration}[bg]`,
  `[0:v]fps=${FPS},scale=${PW}:${PH}:flags=lanczos,setsar=1[p]`,
  `[1:v]fps=${FPS},scale=${PW}:${PH}:flags=lanczos,setsar=1[s]`,
  `[2:v]fps=${FPS},scale=1280:800:flags=lanczos,setsar=1[d]`,
  `[bg]${frame(60, 170, PW, PH)},${frame(640, 170, PW, PH)},${frame(1210, 170, 1280, 800)}[f]`,
  `[f][p]overlay=60:170:eof_action=pass[o1]`,
  `[o1][s]overlay=640:170:eof_action=pass[o2]`,
  `[o2][d]overlay=1210:170:eof_action=pass[o3]`,
  `[o3]ass=${path.join(OUT, 'captions.ass')}:fontsdir=/usr/share/fonts/truetype/dejavu[v]`
].join(';');

const args = [
  '-y', '-hide_banner', '-loglevel', 'error',
  '-itsoffset', String(off('phone')), '-i', vid('phone'),
  '-itsoffset', String(off('staff')), '-i', vid('staff'),
  '-itsoffset', String(off('desktop')), '-i', vid('desktop'),
  '-filter_complex', filter, '-map', '[v]', '-t', String(duration),
  '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '23', '-pix_fmt', 'yuv420p', '-movflags', '+faststart',
  path.join(OUT, 'demo.mp4')
];
console.log(`composing ${duration}s at ${W}x${H}...`);
execFileSync('ffmpeg', args, { stdio: 'inherit' });
console.log('wrote', path.join(OUT, 'demo.mp4'));
