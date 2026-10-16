/* Turns out/journey/ (raw recording + marks) into out/journey.mp4: fade in/out, intro card, chapter badges that slide in,
 * captions that fade, a progress bar, all drawn as ASS so they are anti-aliased and frame-accurate. */
const fs = require('fs'), path = require('path');
const { execFileSync } = require('child_process');
const OUT = path.join(__dirname, 'out'), J = path.join(OUT, 'journey');
const tl = JSON.parse(fs.readFileSync(path.join(J, 'timeline.json')));
const W = 1920, H = 1080;
const skip = Math.max(0, tl.lead - 0.4);                 // drop the blank page-load frames at the start
const t = ms => tl.lead + ms / 1000 - skip;              // seconds into the trimmed video
const dur = t(tl.total) + 1.4;
const ts = s => { s = Math.max(0, s); const h = Math.floor(s / 3600), m = Math.floor(s % 3600 / 60), x = (s % 60).toFixed(2); return `${h}:${String(m).padStart(2, '0')}:${x.padStart(5, '0')}`; };
const esc = s => s.replace(/[{}\\]/g, '');
const ev = [];
const D = (layer, a, b, style, text) => ev.push(`Dialogue: ${layer},${ts(a)},${ts(b)},${style},,0,0,0,,${text}`);

// Progress bar: a 1920x6 rectangle that grows from the left across the whole video.
D(5, 0, dur, 'Draw', `{\\an7\\pos(0,${H - 6})\\1c&HE37100&\\fscx0\\t(0,${dur * 1000},\\fscx100)\\p1}m 0 0 l ${W} 0 ${W} 6 0 6{\\p0}`);
// Intro card
D(8, 0, 3.4, 'Draw', `{\\an7\\pos(0,0)\\1c&H1C1C1E&\\fad(0,700)\\p1}m 0 0 l ${W} 0 ${W} ${H} 0 ${H}{\\p0}`);
D(9, 0.1, 3.4, 'Title', `{\\an5\\pos(960,470)\\fad(500,700)\\fscx92\\fscy92\\t(0,1200,\\fscx100\\fscy100)}Emt Shop`);
D(9, 0.1, 3.4, 'Sub', `{\\an5\\pos(960,560)\\fad(900,700)}From the first sign-up to the first sale`);
// Chapter badges
const chapters = tl.marks.filter(m => m.kind === 'chapter');
chapters.forEach((c, i) => {
  const a = t(c.at) + 0.1, b = a + 3.6;
  D(7, a, b, 'Badge', `{\\an7\\move(-420,40,48,40,0,420)\\fad(0,450)}CHAPTER ${c.n}   ${esc(c.title)}`);
  D(7, a + 0.15, b, 'BadgeSub', `{\\an7\\move(-420,98,48,98,0,420)\\fad(0,450)}${esc(c.sub)}`);
});
// Captions
const caps = tl.marks.filter(m => m.kind === 'cap');
caps.forEach((c, i) => {
  const a = t(c.at), nextAt = i + 1 < caps.length ? t(caps[i + 1].at) : dur - 0.8, b = Math.min(nextAt - 0.05, a + 30);
  if (b - a > 0.5) D(6, a, b, 'Cap', `{\\an2\\pos(960,${H - 70})\\fad(260,260)}${esc(c.txt)}`);
});
// Outro
D(8, dur - 2.2, dur, 'Draw', `{\\an7\\pos(0,0)\\1c&H1C1C1E&\\fad(900,0)\\p1}m 0 0 l ${W} 0 ${W} ${H} 0 ${H}{\\p0}`);
D(9, dur - 1.9, dur, 'Title', `{\\an5\\pos(960,500)\\fad(700,0)}Add stock. Sell. Grow.`);

const style = (n, size, col, extra = '') => `Style: ${n},DejaVu Sans,${size},${col},&H000000FF,&H00000000,&H00000000,${extra}`;
const ass = `[Script Info]
ScriptType: v4.00+
PlayResX: ${W}
PlayResY: ${H}
WrapStyle: 2
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name,Fontname,Fontsize,PrimaryColour,SecondaryColour,OutlineColour,BackColour,Bold,Italic,Underline,StrikeOut,ScaleX,ScaleY,Spacing,Angle,BorderStyle,Outline,Shadow,Alignment,MarginL,MarginR,MarginV,Encoding
Style: Draw,DejaVu Sans,20,&H00FFFFFF,&H000000FF,&H00000000,&H00000000,0,0,0,0,100,100,0,0,1,0,0,7,0,0,0,1
Style: Title,DejaVu Sans,120,&H00FFFFFF,&H000000FF,&H00000000,&H00000000,-1,0,0,0,100,100,0,0,1,0,0,5,0,0,0,1
Style: Sub,DejaVu Sans,44,&H00BBBBBB,&H000000FF,&H00000000,&H00000000,0,0,0,0,100,100,0,0,1,0,0,5,0,0,0,1
Style: Badge,DejaVu Sans,34,&H00FFFFFF,&H000000FF,&H00E37100,&H00E37100,-1,0,0,0,100,100,2,0,3,14,0,7,0,0,0,1
Style: BadgeSub,DejaVu Sans,26,&H00FFFFFF,&H000000FF,&H8C000000,&H8C000000,0,0,0,0,100,100,0,0,3,10,0,7,0,0,0,1
Style: Cap,DejaVu Sans,38,&H00FFFFFF,&H000000FF,&H8C1C1C1E,&H8C1C1C1E,0,0,0,0,100,100,0,0,3,18,0,2,0,0,0,1

[Events]
Format: Layer,Start,End,Style,Name,MarginL,MarginR,MarginV,Effect,Text
${ev.join('\n')}
`;
fs.writeFileSync(path.join(J, 'journey.ass'), ass);
const f = [`[0:v]fps=30,scale=${W}:${H}:flags=lanczos,setsar=1,fade=t=in:st=0:d=0.5[v0]`, `[v0]ass=${path.join(J, 'journey.ass')}:fontsdir=/usr/share/fonts/truetype/dejavu[v]`].join(';');
console.log(`composing ${dur.toFixed(1)}s ...`);
execFileSync('ffmpeg', ['-y', '-hide_banner', '-loglevel', 'error', '-ss', String(skip), '-i', tl.video, '-filter_complex', f, '-map', '[v]', '-t', String(dur),
  '-c:v', 'libx264', '-preset', 'medium', '-crf', '20', '-pix_fmt', 'yuv420p', '-movflags', '+faststart', path.join(OUT, 'journey.mp4')], { stdio: 'inherit' });
console.log('wrote out/journey.mp4');
