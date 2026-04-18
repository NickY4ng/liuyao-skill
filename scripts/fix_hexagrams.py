#!/usr/bin/env python3
"""Fix hexagrams.json to have proper full guaxiang strings"""
import json
import os

script_dir = os.path.dirname(os.path.abspath(__file__))
data_dir = os.path.join(script_dir, "..", "data")

with open(os.path.join(data_dir, "hexagrams.json"), "r", encoding="utf-8") as f:
    d = json.load(f)

# Trigram to yao lines (from top to bottom: 上爻→初爻)
trigram_yao = {
    "☰": ["⚊", "⚊", "⚊"],  # 乾: 3阳
    "☱": ["⚋", "⚊", "⚊"],  # 兑: 少阴
    "☲": ["⚊", "⚋", "⚊"],  # 离: 离中虚
    "☳": ["⚋", "⚋", "⚊"],  # 震: 震仰盂
    "☴": ["⚊", "⚊", "⚋"],  # 巽: 巽下断
    "☶": ["⚋", "⚊", "⚋"],  # 艮: 覆碗
    "☵": ["⚊", "⚋", "⚋"],  # 坎: 中满
    "☷": ["⚋", "⚋", "⚋"],  # 坤: 3阴
}

# Build full 6-line guaxiang for each entry
for k, v in d["hexagrams"].items():
    neigua = v.get("neigua", "?")
    waigua = v.get("waigua", "?")
    if neigua in trigram_yao and waigua in trigram_yao:
        upper = trigram_yao[waigua]   # 上卦: [上爻, 五爻, 四爻]
        lower = trigram_yao[neigua]  # 下卦: [三爻, 二爻, 初爻]
        full = upper + lower  # [上爻, 五爻, 四爻, 三爻, 二爻, 初爻]
        v["guaxiang_full"] = "".join(full)
        v["key_binary"] = "".join(["1" if y == "⚊" else "0" for y in full])

# Show a few
for k, v in list(d["hexagrams"].items())[:5]:
    print(f"key={k} full={v.get('key_binary','?')} name={v['name']}")

print("\nTotal hexagrams:", len(d["hexagrams"]))

# Save
with open(os.path.join(data_dir, "hexagrams.json"), "w", encoding="utf-8") as f:
    json.dump(d, f, ensure_ascii=False, indent=2)
print("Saved!")
