---
name: liuyao-skill
description: "Use when user asks for divination, fortune-telling, I Ching, or Liu Yao (六爻) hexagram reading. Supports interactive coin-toss divination and direct hexagram interpretation."
version: 1.1.0
author: 绽放
license: MIT
metadata:
  hermes:
    tags: [divination, i-ching, liu-yao, chinese-astrology, fortune-telling]
    related_skills: [bazi-master, lunar-calendar, huangli]
---

# 六爻占卜 Skill (Liu Yao Divination)

## Overview

A complete Liu Yao (六爻) divination system for Hermes Agent, supporting interactive coin-toss divination, automatic hexagram interpretation, Six Spirits (六神) arrangement, and pattern analysis.

## When to Use

- User says: "起卦", "算一卦", "摇卦", "来一卦", "卜卦", "六爻", "🎲"
- User asks about fortune, decision-making, or future events
- User wants to consult the I Ching / Book of Changes

## Features

| Feature | Description |
|---------|-------------|
| Interactive Divination | User tosses virtual coins 6 times |
| Auto Interpretation | Full hexagram reading with 64 hexagrams database |
| Six Spirits | Automatic arrangement based on day stem |
| Pattern Analysis | Six Clash, Wandering Soul, Returning Soul detection |
| Beautiful Output | Emoji-based hexagram display, no code blocks |

## Core Rules

### Strict Rule: Never Divinate for User

- Trigger words ("来一卦", "摇一卦") only prompt entry, never auto-toss
- All 6 tosses must be triggered by user saying "心想事成"
- `start_divination` only creates session, never calls `process_one_step`
- Only "心想事成" advances the divination

### Yao Determination

| Coin Result | Yao Name | Symbol | Moving |
|-------------|----------|--------|--------|
| 3 heads | Old Yang | ⚊ | ✓ |
| 3 tails | Old Yin | ⚋ | ✓ |
| 2 heads 1 tail | Young Yang | ⚊ | — |
| 2 tails 1 head | Young Yin | ⚋ | — |

## Usage

### Interactive Mode

```
User: 今年能不能升职？
System: 💭 Your question: 今年能不能升职
        🎲 Please send "心想事成" to start (1/6)

User: 心想事成
System: 1st toss (Bottom Yao): 🌕🌕🌑 → Young Yang ⚊
        🎲 Please send "心想事成" to continue (2/6)
...
(Auto interpretation after 6th toss)
```

### Direct Input Mode

```bash
python3 scripts/liuyao_interpret.py --question "财运如何" --yaos "少阳,少阴,老阳,少阴,少阳,老阴"
```

## Scripts

| Script | Purpose |
|--------|---------|
| `liuyao_interactive.py` | Interactive divination main program |
| `liuyao_interpret.py` | Direct interpretation entry |
| `liuyao.py` | Core Liu Yao logic |
| `hexagrams.py` | 64 hexagrams database |
| `interpret.py` | Interpretation algorithm |
| `wangshuai.py` | Strength/weakness analysis |
| `xunkong.py` | Empty period calculation |
| `pattern.py` | Pattern judgment |
| `naga.py` | Naga method |

## Output Format

```
## 🎯 Liu Yao Divination

### 🔮 Hexagram
Di Huo Ming Yi · Kan Palace · Static
⚋ ⚊ ⚊
⚋ ⚋ ⚊

### 🎲 Six Tosses
1st (Bottom): 🌕🌕🌑 → Young Yang ⚊
2nd: 🌑🌕🌑 → Young Yin ⚋
3rd: 🌑🌑🌑 → Old Yang ⚊ (Moving)
...

### 📜 Hexagram Text
Ming Yi, beneficial to be perseveringly distressed and firm.
Image: Brightness enters the earth. The superior man uses obscurity to be bright.

### ⚖️ Fortune
- God: Official Ghost (Mao Wood)
- Strength: Resting in month, supported by day
- Overall: Moderate, wait for timing

### 🐉 Six Spirits
Top: Black Tortoise
5th: White Tiger
4th: Flying Serpent
3rd: Hooked Chen
2nd: Vermilion Bird
Bottom: Azure Dragon

### 🏷️ Pattern
Static hexagram, no moving lines

### 💡 Advice
- Timing: Not suitable to advance, better to defend
- Advantage: Inner ability ready, wait for external conditions
- Caution: Beware of hidden enemies, keep low profile
- Action: Continue accumulating, hope in autumn
```

## Configuration

### Hermes Agent

Place in `~/.hermes/skills/lifestyle/liuyao/`

### Environment Variables

```bash
export LIUYAO_SESSION_FILE="~/.hermes/.liuyao_session.json"
export LIUYAO_TIMEOUT=300
```

## Common Pitfalls

1. **Auto-tossing on start**: `start_divination` must NOT call `process_one_step`
2. **Step counter drift**: Use `len(session["yaos"])` not `session["step"]`
3. **Pattern matching**: Use substring match for hexagram names
4. **Moving line detection**: Only Old Yang/Old Yin are moving lines
5. **Session file safety**: Use atomic write with temp file + os.replace()

## Verification Checklist

- [ ] "心想事成" exactly matches, no other input accepted
- [ ] 6 tosses complete before interpretation
- [ ] Moving lines correctly identified
- [ ] Six Spirits arranged by day stem
- [ ] Output has no code blocks, emoji-based display
- [ ] Session auto-clears after 5min timeout

## License

MIT © 2026 绽放
