import csv
import json
import sys
import re
import os

def is_header_row(row):
    q, a = row[0].strip().lower(), row[1].strip().lower()
    header_keywords = {"question", "answer", "q", "a", "front", "back", "term", "definition"}
    return q in header_keywords or a in header_keywords

def load_cards(csv_path):
    cards = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.reader(f)
        for i, row in enumerate(reader):
            if len(row) < 2:
                continue
            if i == 0 and is_header_row(row):
                continue
            q = row[0].strip()
            a = row[1].strip()
            if q and a:
                cards.append({"q": q, "a": a})
    return cards

def build_html(cards):
    cards_json = json.dumps(cards, ensure_ascii=False)
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Flashcards</title>
<script src="https://cdnjs.cloudflare.com/ajax/libs/mathjax/3.2.2/es5/tex-chtml.min.js"></script>
<style>
  *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}

  :root {{
    --bg: #0f0f13;
    --surface: #1a1a22;
    --surface2: #22222e;
    --border: rgba(255,255,255,0.08);
    --border2: rgba(255,255,255,0.15);
    --text: #f0eeff;
    --text2: #9893b8;
    --text3: #5e5a7a;
    --accent: #7c6af7;
    --accent2: #a98bff;
    --green: #3ecf8e;
    --red: #f87171;
    --amber: #fbbf24;
    --radius: 16px;
    --card-h: clamp(240px, 45vw, 380px);
  }}

  body {{
    background: var(--bg);
    color: var(--text);
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    min-height: 100dvh;
    display: flex;
    flex-direction: column;
    align-items: center;
    padding: 1.5rem 1rem 3rem;
    gap: 1.5rem;
  }}

  header {{
    width: 100%;
    max-width: 680px;
    display: flex;
    align-items: center;
    justify-content: space-between;
  }}

  .logo {{ font-size: 15px; font-weight: 600; color: var(--accent2); letter-spacing: -0.02em; }}

  .stats {{
    display: flex;
    gap: 1.5rem;
    font-size: 13px;
    color: var(--text2);
  }}
  .stats span {{ display: flex; align-items: center; gap: 5px; }}
  .dot {{ width: 7px; height: 7px; border-radius: 50%; display: inline-block; }}
  .dot-green {{ background: var(--green); }}
  .dot-red {{ background: var(--red); }}

  .progress-bar {{
    width: 100%;
    max-width: 680px;
    height: 3px;
    background: var(--surface2);
    border-radius: 99px;
    overflow: hidden;
  }}
  .progress-fill {{
    height: 100%;
    background: linear-gradient(90deg, var(--accent), var(--accent2));
    border-radius: 99px;
    transition: width 0.4s cubic-bezier(.4,0,.2,1);
  }}

  .counter {{
    font-size: 13px;
    color: var(--text3);
    width: 100%;
    max-width: 680px;
    text-align: right;
  }}

  .scene {{
    width: 100%;
    max-width: 680px;
    height: var(--card-h);
    perspective: 1200px;
    cursor: pointer;
  }}

  .card {{
    width: 100%;
    height: 100%;
    position: relative;
    transform-style: preserve-3d;
    transition: transform 0.55s cubic-bezier(.4,0,.2,1);
  }}

  .card.flipped {{ transform: rotateY(180deg); }}

  .face {{
    position: absolute;
    inset: 0;
    backface-visibility: hidden;
    -webkit-backface-visibility: hidden;
    border-radius: var(--radius);
    border: 1px solid var(--border);
    background: var(--surface);
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 2rem 2.5rem;
    text-align: center;
    gap: 1rem;
    overflow: hidden;
  }}

  .face::before {{
    content: '';
    position: absolute;
    inset: 0;
    background: radial-gradient(ellipse 60% 40% at 50% 0%, rgba(124,106,247,0.08), transparent);
    pointer-events: none;
  }}

  .face-back {{
    transform: rotateY(180deg);
    background: var(--surface2);
  }}
  .face-back::before {{
    background: radial-gradient(ellipse 60% 40% at 50% 100%, rgba(62,207,142,0.07), transparent);
  }}

  .face-label {{
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: var(--text3);
    position: absolute;
    top: 1.25rem;
    left: 1.5rem;
  }}

  .face-text {{
    font-size: clamp(14px, 2.5vw, 18px);
    line-height: 1.65;
    color: var(--text);
    max-height: calc(var(--card-h) - 5rem);
    overflow-y: auto;
    scrollbar-width: none;
  }}

  .hint {{
    font-size: 12px;
    color: var(--text3);
    position: absolute;
    bottom: 1.25rem;
    right: 1.5rem;
  }}

  .controls {{
    display: flex;
    gap: 0.75rem;
    width: 100%;
    max-width: 680px;
    justify-content: center;
  }}

  .btn {{
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 6px;
    border: 1px solid var(--border2);
    border-radius: 10px;
    background: var(--surface);
    color: var(--text2);
    font-size: 13px;
    font-weight: 500;
    padding: 0.6rem 1.25rem;
    cursor: pointer;
    transition: background 0.15s, color 0.15s, transform 0.1s;
    white-space: nowrap;
  }}
  .btn:hover {{ background: var(--surface2); color: var(--text); }}
  .btn:active {{ transform: scale(0.97); }}

  .btn-know {{
    flex: 1;
    background: rgba(62,207,142,0.1);
    border-color: rgba(62,207,142,0.25);
    color: var(--green);
  }}
  .btn-know:hover {{ background: rgba(62,207,142,0.18); }}

  .btn-nope {{
    flex: 1;
    background: rgba(248,113,113,0.1);
    border-color: rgba(248,113,113,0.25);
    color: var(--red);
  }}
  .btn-nope:hover {{ background: rgba(248,113,113,0.18); }}

  .btn-shuffle, .btn-restart {{
    background: transparent;
    border-color: var(--border);
  }}

  .result-screen {{
    display: none;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 1.5rem;
    width: 100%;
    max-width: 680px;
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 3rem 2rem;
    text-align: center;
  }}
  .result-screen.visible {{ display: flex; }}

  .result-big {{ font-size: 48px; font-weight: 700; letter-spacing: -0.03em; }}
  .result-sub {{ font-size: 15px; color: var(--text2); }}

  .result-grid {{
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 1rem;
    width: 100%;
    max-width: 320px;
  }}

  .result-stat {{
    background: var(--surface2);
    border-radius: 10px;
    padding: 1rem;
    font-size: 13px;
    color: var(--text2);
  }}
  .result-stat strong {{ display: block; font-size: 22px; font-weight: 600; color: var(--text); margin-bottom: 2px; }}

  @media (max-width: 480px) {{
    body {{ padding: 1rem 0.75rem 2rem; }}
    .face {{ padding: 1.5rem 1.25rem; }}
    .btn {{ padding: 0.6rem 0.9rem; font-size: 12px; }}
  }}
</style>
</head>
<body>

<header>
  <span class="logo">Flashcards</span>
  <div class="stats">
    <span><span class="dot dot-green"></span><span id="known-count">0</span> know</span>
    <span><span class="dot dot-red"></span><span id="nope-count">0</span> review</span>
  </div>
</header>

<div class="progress-bar"><div class="progress-fill" id="progress" style="width:0%"></div></div>
<div class="counter" id="counter">1 / {len(cards)}</div>

<div class="scene" id="scene">
  <div class="card" id="card">
    <div class="face face-front">
      <span class="face-label">Question</span>
      <div class="face-text" id="q-text"></div>
      <span class="hint">tap to reveal</span>
    </div>
    <div class="face face-back">
      <span class="face-label">Answer</span>
      <div class="face-text" id="a-text"></div>
      <span class="hint">tap to flip back</span>
    </div>
  </div>
</div>

<div class="controls" id="controls">
  <button class="btn btn-nope" onclick="rate(false)">✗ Review</button>
  <button class="btn btn-shuffle" onclick="shuffleDeck()">⇌ Shuffle</button>
  <button class="btn btn-know" onclick="rate(true)">✓ Know it</button>
</div>

<div class="result-screen" id="result-screen">
  <div class="result-big" id="result-pct">—</div>
  <div class="result-sub">of cards marked as known</div>
  <div class="result-grid">
    <div class="result-stat"><strong id="r-known">0</strong> Knew it</div>
    <div class="result-stat"><strong id="r-nope">0</strong> Need review</div>
    <div class="result-stat"><strong id="r-total">0</strong> Total cards</div>
    <div class="result-stat"><strong id="r-streak">0</strong> Best streak</div>
  </div>
  <button class="btn btn-restart" onclick="restart()">↺ Restart deck</button>
  <button class="btn btn-nope" onclick="reviewWrong()" id="review-wrong-btn">Review missed cards</button>
</div>

<script>
const CARDS = {cards_json};

let deck = [...CARDS];
let idx = 0;
let known = 0;
let nope = 0;
let flipped = false;
let streak = 0;
let bestStreak = 0;
let wrongCards = [];

function shuffle(arr) {{
  for (let i = arr.length - 1; i > 0; i--) {{
    const j = Math.floor(Math.random() * (i + 1));
    [arr[i], arr[j]] = [arr[j], arr[i]];
  }}
  return arr;
}}

function renderMath(el) {{
  if (window.MathJax) MathJax.typesetPromise([el]);
}}

function showCard() {{
  const c = deck[idx];
  document.getElementById('q-text').textContent = c.q;
  document.getElementById('a-text').textContent = c.a;
  renderMath(document.getElementById('q-text'));
  renderMath(document.getElementById('a-text'));
  document.getElementById('counter').textContent = (idx + 1) + ' / ' + deck.length;
  document.getElementById('progress').style.width = (idx / deck.length * 100) + '%';
  const card = document.getElementById('card');
  card.classList.remove('flipped');
  flipped = false;
}}

function flipCard() {{
  const card = document.getElementById('card');
  card.classList.toggle('flipped');
  flipped = !flipped;
}}

function rate(correct) {{
  if (correct) {{
    known++;
    streak++;
    if (streak > bestStreak) bestStreak = streak;
    document.getElementById('known-count').textContent = known;
  }} else {{
    nope++;
    streak = 0;
    wrongCards.push(deck[idx]);
    document.getElementById('nope-count').textContent = nope;
  }}
  idx++;
  if (idx >= deck.length) {{
    showResult();
  }} else {{
    showCard();
  }}
}}

function showResult() {{
  document.getElementById('scene').style.display = 'none';
  document.getElementById('controls').style.display = 'none';
  document.getElementById('counter').style.display = 'none';
  const rs = document.getElementById('result-screen');
  rs.classList.add('visible');
  const pct = Math.round(known / deck.length * 100);
  document.getElementById('result-pct').textContent = pct + '%';
  document.getElementById('r-known').textContent = known;
  document.getElementById('r-nope').textContent = nope;
  document.getElementById('r-total').textContent = deck.length;
  document.getElementById('r-streak').textContent = bestStreak;
  document.getElementById('review-wrong-btn').style.display = wrongCards.length ? '' : 'none';
  document.getElementById('progress').style.width = '100%';
}}

function restart() {{
  deck = shuffle([...CARDS]);
  idx = 0; known = 0; nope = 0; streak = 0; bestStreak = 0; wrongCards = [];
  document.getElementById('known-count').textContent = 0;
  document.getElementById('nope-count').textContent = 0;
  document.getElementById('result-screen').classList.remove('visible');
  document.getElementById('scene').style.display = '';
  document.getElementById('controls').style.display = '';
  document.getElementById('counter').style.display = '';
  showCard();
}}

function shuffleDeck() {{
  const rest = deck.slice(idx);
  shuffle(rest);
  deck = deck.slice(0, idx).concat(rest);
  showCard();
}}

function reviewWrong() {{
  deck = shuffle([...wrongCards]);
  idx = 0; known = 0; nope = 0; streak = 0; bestStreak = 0; wrongCards = [];
  document.getElementById('known-count').textContent = 0;
  document.getElementById('nope-count').textContent = 0;
  document.getElementById('result-screen').classList.remove('visible');
  document.getElementById('scene').style.display = '';
  document.getElementById('controls').style.display = '';
  document.getElementById('counter').style.display = '';
  showCard();
}}

function navigate(dir) {{
  const newIdx = idx + dir;
  if (newIdx < 0 || newIdx >= deck.length) return;
  idx = newIdx;
  showCard();
}}

document.addEventListener('keydown', e => {{
  if (e.key === ' ') {{ e.preventDefault(); flipCard(); }}
  if (e.key === 'ArrowRight') navigate(1);
  if (e.key === 'ArrowLeft') navigate(-1);
}});

const scene = document.getElementById('scene');
let touchStartX = 0, touchStartY = 0, touchMoved = false;
scene.addEventListener('touchstart', e => {{
  touchStartX = e.touches[0].clientX;
  touchStartY = e.touches[0].clientY;
  touchMoved = false;
}}, {{ passive: true }});
scene.addEventListener('touchmove', e => {{
  if (Math.abs(e.touches[0].clientX - touchStartX) > 8 || Math.abs(e.touches[0].clientY - touchStartY) > 8) touchMoved = true;
}}, {{ passive: true }});
scene.addEventListener('touchend', e => {{
  if (touchMoved) return;
  const rect = scene.getBoundingClientRect();
  const ratio = (touchStartX - rect.left) / rect.width;
  if (ratio < 0.3) navigate(-1);
  else if (ratio > 0.7) navigate(1);
  else flipCard();
}});

showCard();
</script>
</body>
</html>"""

if __name__ == "__main__":
    csv_path = sys.argv[1] if len(sys.argv) > 1 else "flashcards.csv"
    out_path = sys.argv[2] if len(sys.argv) > 2 else "index.html"
    if not os.path.exists(csv_path):
        print(f"Error: {csv_path} not found", file=sys.stderr)
        sys.exit(1)
    cards = load_cards(csv_path)
    if not cards:
        print("Error: no cards parsed from CSV", file=sys.stderr)
        sys.exit(1)
    html = build_html(cards)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"Generated {out_path} with {len(cards)} cards.")
