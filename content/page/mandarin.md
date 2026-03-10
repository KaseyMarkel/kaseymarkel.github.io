---
title: "Mandarin"
slug: "mandarin"
socialShare: false
---

{{< rawhtml >}}
<style>
/* Hide header */
.intro-header { display: none !important; }
.header-section.has-img { display: none !important; }
div[role="main"].container { padding-top: 80px !important; margin-top: 0 !important; }

/* Hide page title since we have our own */
.post-heading h1, article header { display: none !important; }

* { box-sizing: border-box; }

.hanzi-app {
  max-width: 500px;
  margin: 0 auto;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  color: #333;
  -webkit-tap-highlight-color: transparent;
  user-select: none;
  padding-bottom: 40px;
}

.hanzi-header {
  text-align: center;
  margin-bottom: 24px;
}

.hanzi-header h1 {
  font-size: 24px;
  color: #0085a1;
  margin: 0 0 4px 0;
}

.hanzi-stats {
  display: flex;
  justify-content: center;
  gap: 20px;
  font-size: 13px;
  color: #888;
}

.hanzi-stats span {
  display: flex;
  align-items: center;
  gap: 4px;
}

/* Card container */
.hanzi-card-area {
  position: relative;
  min-height: 340px;
  margin-bottom: 20px;
}

.hanzi-card {
  background: #fff;
  border: 2px solid #e0e0e0;
  border-radius: 16px;
  padding: 32px 24px;
  text-align: center;
  cursor: pointer;
  transition: border-color 0.2s;
  box-shadow: 0 2px 12px rgba(0,0,0,0.06);
}

.hanzi-card:active {
  border-color: #0085a1;
}

.hanzi-character {
  font-size: 120px;
  line-height: 1.1;
  margin: 8px 0 16px 0;
  font-family: 'Noto Sans SC', 'PingFang SC', 'Heiti SC', sans-serif;
}

.hanzi-pinyin {
  font-size: 24px;
  color: #0085a1;
  margin-bottom: 8px;
  font-weight: 500;
}

.hanzi-meaning {
  font-size: 18px;
  color: #666;
  margin-bottom: 0;
}

.hanzi-tap-hint {
  font-size: 13px;
  color: #bbb;
  margin-top: 16px;
}

/* Answer reveal */
.hanzi-answer {
  max-height: 0;
  overflow: hidden;
  transition: max-height 0.3s ease;
}

.hanzi-card.revealed .hanzi-answer {
  max-height: 200px;
}

.hanzi-card.revealed .hanzi-tap-hint {
  display: none;
}

/* Rating buttons */
.hanzi-rating {
  display: flex;
  gap: 10px;
  justify-content: center;
  opacity: 0;
  transform: translateY(10px);
  transition: opacity 0.3s, transform 0.3s;
  pointer-events: none;
}

.hanzi-rating.visible {
  opacity: 1;
  transform: translateY(0);
  pointer-events: auto;
}

.hanzi-rating button {
  flex: 1;
  padding: 14px 8px;
  border: 2px solid;
  border-radius: 12px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.15s;
  background: #fff;
  max-width: 140px;
}

.hanzi-rating button:active {
  transform: scale(0.96);
}

.hanzi-btn-again {
  border-color: #e74c3c;
  color: #e74c3c;
}
.hanzi-btn-again:active {
  background: #e74c3c;
  color: #fff;
}

.hanzi-btn-hard {
  border-color: #e67e22;
  color: #e67e22;
}
.hanzi-btn-hard:active {
  background: #e67e22;
  color: #fff;
}

.hanzi-btn-good {
  border-color: #27ae60;
  color: #27ae60;
}
.hanzi-btn-good:active {
  background: #27ae60;
  color: #fff;
}

.hanzi-btn-easy {
  border-color: #0085a1;
  color: #0085a1;
}
.hanzi-btn-easy:active {
  background: #0085a1;
  color: #fff;
}

/* Intro card for new characters */
.hanzi-intro {
  background: linear-gradient(135deg, #f8f9fa 0%, #fff 100%);
  border: 2px solid #0085a1;
  border-radius: 16px;
  padding: 28px 24px;
  text-align: center;
  box-shadow: 0 2px 12px rgba(0,133,161,0.1);
}

.hanzi-intro-label {
  font-size: 12px;
  text-transform: uppercase;
  letter-spacing: 2px;
  color: #0085a1;
  margin-bottom: 12px;
  font-weight: 600;
}

.hanzi-intro .hanzi-character {
  font-size: 100px;
}

.hanzi-intro .hanzi-pinyin {
  font-size: 28px;
  margin-bottom: 4px;
}

.hanzi-intro .hanzi-meaning {
  font-size: 20px;
  margin-bottom: 16px;
}

.hanzi-story {
  font-size: 15px;
  color: #555;
  line-height: 1.6;
  text-align: left;
  background: #fff;
  padding: 16px;
  border-radius: 10px;
  border: 1px solid #e8e8e8;
  margin-bottom: 20px;
}

.hanzi-story-label {
  font-size: 11px;
  text-transform: uppercase;
  letter-spacing: 1px;
  color: #999;
  margin-bottom: 6px;
  font-weight: 600;
}

.hanzi-intro-btn {
  display: block;
  width: 100%;
  padding: 14px;
  background: #0085a1;
  color: #fff;
  border: none;
  border-radius: 12px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.15s;
}

.hanzi-intro-btn:active {
  background: #006b82;
}

/* Done state */
.hanzi-done {
  text-align: center;
  padding: 60px 24px;
}

.hanzi-done-icon {
  font-size: 48px;
  margin-bottom: 16px;
}

.hanzi-done h2 {
  color: #27ae60;
  margin: 0 0 8px 0;
  font-size: 22px;
}

.hanzi-done p {
  color: #888;
  font-size: 15px;
  margin: 0;
}

/* Progress bar */
.hanzi-progress {
  height: 4px;
  background: #eee;
  border-radius: 2px;
  margin-bottom: 24px;
  overflow: hidden;
}

.hanzi-progress-fill {
  height: 100%;
  background: #0085a1;
  border-radius: 2px;
  transition: width 0.4s ease;
}

/* Reset link */
.hanzi-reset {
  text-align: center;
  margin-top: 24px;
}

.hanzi-reset button {
  background: none;
  border: none;
  color: #bbb;
  font-size: 13px;
  cursor: pointer;
  text-decoration: underline;
  padding: 8px;
}

.hanzi-reset button:hover {
  color: #888;
}
</style>

<div class="hanzi-app" id="hanziApp">
  <div class="hanzi-header">
    <h1>Hanzi</h1>
    <div class="hanzi-stats">
      <span id="statLearned">0 learned</span>
      <span id="statDue">0 due</span>
      <span id="statNew">0 new</span>
    </div>
  </div>
  <div class="hanzi-progress"><div class="hanzi-progress-fill" id="progressFill"></div></div>
  <div class="hanzi-card-area" id="cardArea"></div>
  <div class="hanzi-reset"><button onclick="resetApp()">Reset progress</button></div>
</div>

<script>
(function() {
  // === CHARACTER DATA ===
  const CHARS = [
    {
      char: "\u7684", pinyin: "de", meaning: "possessive particle (like 's)",
      story: "A white (\u767d) ladle (\u52fa) \u2014 imagine scooping up ownership. \"This is the ladle OF the white chef.\" It\u2019s the glue word of Chinese, connecting descriptions to nouns."
    },
    {
      char: "\u4e00", pinyin: "y\u012b", meaning: "one",
      story: "A single brushstroke across the page. One horizon line \u2014 the simplest character there is. Just one clean, horizontal stroke."
    },
    {
      char: "\u662f", pinyin: "sh\u00ec", meaning: "is / to be",
      story: "The sun (\u65e5) stands on solid legs below. The sun simply IS \u2014 it exists, undeniable, a statement of truth anchored to the ground."
    },
    {
      char: "\u4e0d", pinyin: "b\u00f9", meaning: "not / no",
      story: "A flower bud with a line blocking it from opening. It\u2019s NOT going to bloom. The downward strokes push away, negating everything."
    },
    {
      char: "\u4e86", pinyin: "le", meaning: "completed action / changed state",
      story: "A tiny hook that snags the moment something finishes. The fish is caught \u2014 done! Add it after a verb and the action is complete."
    },
    {
      char: "\u4eba", pinyin: "r\u00e9n", meaning: "person / people",
      story: "Two strokes leaning on each other like legs mid-stride. A person walking. One of the most fundamental building blocks \u2014 you\u2019ll see this shape inside dozens of other characters."
    },
    {
      char: "\u6211", pinyin: "w\u01d2", meaning: "I / me",
      story: "A hand (\u624b) gripping a weapon (\u6208). \"I defend myself.\" The ego has a spear. The most personal character \u2014 me, myself."
    },
    {
      char: "\u5728", pinyin: "z\u00e0i", meaning: "at / in / exists",
      story: "A scholar standing on earth (\u571f). Wherever you plant your feet, that\u2019s where you\u2019re AT. Existence grounded in a place."
    },
    {
      char: "\u6709", pinyin: "y\u01d2u", meaning: "have / there is",
      story: "A hand reaching over the moon (\u6708). You HAVE the moon in your grasp. Possession \u2014 something exists in your hands."
    },
    {
      char: "\u4ed6", pinyin: "t\u0101", meaning: "he / him",
      story: "Person radical (\u4ebf) plus \"also\" (\u4e5f). He is ALSO a person \u2014 just someone else standing beside you."
    },
    {
      char: "\u8fd9", pinyin: "zh\u00e8", meaning: "this",
      story: "The walking radical (\u8fb6) approaches something (\u6587). Walking right up to it and pointing: THIS one, right here."
    },
    {
      char: "\u4e2d", pinyin: "zh\u014dng", meaning: "middle / center / China",
      story: "A line piercing straight through the center of a box. Bullseye. China calls itself \u4e2d\u56fd \u2014 the Middle Kingdom."
    },
    {
      char: "\u5927", pinyin: "d\u00e0", meaning: "big / large",
      story: "A person stretching their arms and legs wide. How BIG is it? THIS big! Spread your body as far as it goes."
    },
    {
      char: "\u6765", pinyin: "l\u00e1i", meaning: "come",
      story: "A tree with extra branches waving you over. Come here, come closer! The branches beckon."
    },
    {
      char: "\u4e0a", pinyin: "sh\u00e0ng", meaning: "up / above / on top",
      story: "A vertical stroke reaching above a baseline, with a small dash on top saying \"look UP here!\" The opposite of \u4e0b (down)."
    },
    {
      char: "\u56fd", pinyin: "gu\u00f3", meaning: "country / nation",
      story: "Jade (\u7389) locked inside walls (\u56d7). A country is precious treasure protected within borders."
    },
    {
      char: "\u4e2a", pinyin: "g\u00e8", meaning: "general measure word",
      story: "A tiny umbrella over a person. Used to count individual things \u2014 one of this, three of that. The default counter when no special one applies."
    },
    {
      char: "\u5230", pinyin: "d\u00e0o", meaning: "arrive / reach / to",
      story: "Reaching (\u81f3) with a knife (\u5202) cutting through the last obstacle. You\u2019ve finally ARRIVED at your destination."
    },
    {
      char: "\u8bf4", pinyin: "shu\u014d", meaning: "say / speak",
      story: "The speech radical (\u8ba0) on the left \u2014 an open mouth ready to SPEAK. Words pour out the right side."
    },
    {
      char: "\u4eec", pinyin: "men", meaning: "plural people marker",
      story: "A person (\u4ebf) at a door (\u95e8). Open the door \u2014 there\u2019s not just one, there are MANY of them inside. Add it to make pronouns plural."
    },
    {
      char: "\u4e3a", pinyin: "w\u00e8i", meaning: "for / because / to do",
      story: "A hand doing work with purpose. Everything is done FOR a reason. One of the most versatile words in Chinese."
    },
    {
      char: "\u5b50", pinyin: "z\u01d0", meaning: "child / son / suffix",
      story: "A baby with arms reaching out from swaddling cloth. A little CHILD wanting to be held. Also used as a common suffix on nouns."
    },
    {
      char: "\u548c", pinyin: "h\u00e9", meaning: "and / harmony / peace",
      story: "Grain (\u79be) plus mouth (\u53e3). When there\u2019s food AND mouths to feed, there is harmony. The word for peaceful coexistence."
    },
    {
      char: "\u4f60", pinyin: "n\u01d0", meaning: "you",
      story: "Person radical (\u4ebf) pointing across at another little figure. I\u2019m looking at YOU \u2014 the person across from me."
    },
    {
      char: "\u5730", pinyin: "d\u00ec", meaning: "earth / ground / land",
      story: "Earth radical (\u571f) on the left, \"also\" (\u4e5f) on the right. The ground is ALSO beneath us, always. Solid earth everywhere."
    }
  ];

  const STORAGE_KEY = "hanzi_progress";
  const NEW_PER_DAY = 5;

  // === STATE ===
  let state = loadState();

  function defaultState() {
    return {
      cards: {},        // char -> { interval, ease, due, reps }
      introduced: [],   // array of char indices that have been shown intro
      queue: [],        // indices due for review
      newToday: 0,      // how many new cards introduced today
      lastDate: today(),
      introIdx: null    // index currently being introduced
    };
  }

  function today() {
    return new Date().toISOString().slice(0, 10);
  }

  function loadState() {
    try {
      const raw = localStorage.getItem(STORAGE_KEY);
      if (raw) {
        const s = JSON.parse(raw);
        // Reset daily counter if new day
        if (s.lastDate !== today()) {
          s.newToday = 0;
          s.lastDate = today();
        }
        return s;
      }
    } catch(e) {}
    return defaultState();
  }

  function saveState() {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(state));
  }

  // === SPACED REPETITION (SM-2 simplified) ===
  function scheduleCard(charIdx, quality) {
    // quality: 0=again, 1=hard, 2=good, 3=easy
    const ch = CHARS[charIdx].char;
    let card = state.cards[ch] || { interval: 0, ease: 2.5, due: today(), reps: 0 };

    if (quality === 0) {
      // Again - reset
      card.interval = 0;
      card.reps = 0;
    } else {
      if (card.reps === 0) {
        card.interval = 1;
      } else if (card.reps === 1) {
        card.interval = quality === 3 ? 4 : quality === 2 ? 3 : 2;
      } else {
        let mult = quality === 3 ? 1.5 : quality === 2 ? 1.0 : 0.8;
        card.interval = Math.max(1, Math.round(card.interval * card.ease * mult));
      }
      card.reps++;
      // Adjust ease
      card.ease = Math.max(1.3, card.ease + (quality - 2) * 0.1);
    }

    // Set next due date
    const due = new Date();
    if (card.interval === 0) {
      // Due now (will show again this session)
      card.due = today();
    } else {
      due.setDate(due.getDate() + card.interval);
      card.due = due.toISOString().slice(0, 10);
    }

    state.cards[ch] = card;
    saveState();
  }

  // === QUEUE ===
  function buildQueue() {
    const now = today();
    const due = [];
    for (let i = 0; i < state.introduced.length; i++) {
      const idx = state.introduced[i];
      const card = state.cards[CHARS[idx].char];
      if (card && card.due <= now) {
        due.push({ idx, due: card.due, interval: card.interval });
      }
    }
    // Sort: shortest interval first (hardest cards first), then by due date
    due.sort((a, b) => a.interval - b.interval || a.due.localeCompare(b.due));
    return due.map(d => d.idx);
  }

  // === RENDERING ===
  function render() {
    const queue = buildQueue();
    const totalIntroduced = state.introduced.length;
    const learned = state.introduced.filter(i => {
      const c = state.cards[CHARS[i].char];
      return c && c.interval >= 7;
    }).length;
    const canAddNew = state.newToday < NEW_PER_DAY && totalIntroduced < CHARS.length;
    const nextNewIdx = totalIntroduced < CHARS.length ? totalIntroduced : null;

    // Stats
    document.getElementById("statLearned").textContent = learned + " learned";
    document.getElementById("statDue").textContent = queue.length + " due";
    document.getElementById("statNew").textContent = (CHARS.length - totalIntroduced) + " new";

    // Progress
    const pct = CHARS.length > 0 ? (totalIntroduced / CHARS.length * 100) : 0;
    document.getElementById("progressFill").style.width = pct + "%";

    const area = document.getElementById("cardArea");

    // If there's a pending introduction, show it
    if (state.introIdx !== null) {
      renderIntro(state.introIdx);
      return;
    }

    // If there are due cards, show review
    if (queue.length > 0) {
      renderReview(queue[0]);
      return;
    }

    // If we can introduce a new card
    if (canAddNew && nextNewIdx !== null) {
      state.introIdx = nextNewIdx;
      saveState();
      renderIntro(nextNewIdx);
      return;
    }

    // All done for today
    renderDone();
  }

  function renderIntro(idx) {
    const c = CHARS[idx];
    const area = document.getElementById("cardArea");
    area.innerHTML = `
      <div class="hanzi-intro">
        <div class="hanzi-intro-label">New Character</div>
        <div class="hanzi-character">${c.char}</div>
        <div class="hanzi-pinyin">${c.pinyin}</div>
        <div class="hanzi-meaning">${c.meaning}</div>
        <div class="hanzi-story">
          <div class="hanzi-story-label">Memory story</div>
          ${c.story}
        </div>
        <button class="hanzi-intro-btn" id="introGotIt">Got it</button>
      </div>
    `;
    document.getElementById("introGotIt").addEventListener("click", function() {
      // Mark as introduced
      if (!state.introduced.includes(idx)) {
        state.introduced.push(idx);
        state.newToday++;
      }
      // Create initial card - due now for immediate first review
      state.cards[c.char] = { interval: 0, ease: 2.5, due: today(), reps: 0 };
      state.introIdx = null;
      saveState();
      render();
    });
  }

  function renderReview(idx) {
    const c = CHARS[idx];
    const area = document.getElementById("cardArea");
    area.innerHTML = `
      <div class="hanzi-card" id="reviewCard">
        <div class="hanzi-character">${c.char}</div>
        <div class="hanzi-tap-hint">Tap to reveal</div>
        <div class="hanzi-answer">
          <div class="hanzi-pinyin">${c.pinyin}</div>
          <div class="hanzi-meaning">${c.meaning}</div>
        </div>
      </div>
      <div class="hanzi-rating" id="ratingBtns">
        <button class="hanzi-btn-again" data-q="0">Again</button>
        <button class="hanzi-btn-hard" data-q="1">Hard</button>
        <button class="hanzi-btn-good" data-q="2">Good</button>
        <button class="hanzi-btn-easy" data-q="3">Easy</button>
      </div>
    `;

    const card = document.getElementById("reviewCard");
    const rating = document.getElementById("ratingBtns");

    card.addEventListener("click", function() {
      card.classList.add("revealed");
      // Small delay so reveal animation plays first
      setTimeout(function() { rating.classList.add("visible"); }, 150);
    });

    rating.querySelectorAll("button").forEach(function(btn) {
      btn.addEventListener("click", function() {
        const q = parseInt(btn.getAttribute("data-q"));
        scheduleCard(idx, q);
        render();
      });
    });
  }

  function renderDone() {
    const area = document.getElementById("cardArea");
    const totalIntroduced = state.introduced.length;
    const allDone = totalIntroduced >= CHARS.length;
    area.innerHTML = `
      <div class="hanzi-done">
        <div class="hanzi-done-icon">${allDone ? "\u2728" : "\u2705"}</div>
        <h2>${allDone ? "All characters learned!" : "Done for today!"}</h2>
        <p>${allDone
          ? "You\u2019ve been introduced to all " + CHARS.length + " characters. Come back to review!"
          : "Come back tomorrow for more characters and reviews."
        }</p>
      </div>
    `;
  }

  // === RESET ===
  window.resetApp = function() {
    if (confirm("Reset all progress? This cannot be undone.")) {
      localStorage.removeItem(STORAGE_KEY);
      state = defaultState();
      render();
    }
  };

  // === INIT ===
  render();
})();
</script>
{{< /rawhtml >}}
