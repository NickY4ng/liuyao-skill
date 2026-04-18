#!/usr/bin/env python3
"""
格局判断模块
包括：游魂卦、归魂卦、三合局、六冲、六合等
"""

import json
from typing import List, Dict


def load_pattern_rules():
    with open("data/yongshen_rules.json", "r", encoding="utf-8") as f:
        return json.load(f)


class PatternAnalyzer:
    """格局分析器"""

    def __init__(self):
        self.rules = load_pattern_rules()

    def check_youhun(self, hexagram_name: str) -> bool:
        """检查是否游魂卦"""
        youhun_list = self.rules.get("liushou_patterns", {}).get("游魂卦", [])
        return hexagram_name in youhun_list

    def check_guihun(self, hexagram_name: str) -> bool:
        """检查是否归魂卦"""
        guihun_list = self.rules.get("liushou_patterns", {}).get("归魂卦", [])
        return hexagram_name in guihun_list

    def get_pattern_meaning(self, pattern: str) -> str:
        """获取格局含义"""
        meanings = {
            "游魂卦": "游魂主变化不定、心神不宁、出行有阻、事物处于游离状态。适宜守成，不宜妄动。",
            "归魂卦": "归魂主回归稳定、有归宿感、事物将有着落。利于回归、结束、整合。",
            "六冲": "六冲主冲动、变化、分离。吉事冲散，凶事冲开。应爻克世则不吉。",
            "六合": "六合主和合、稳定、长久。利于合作、婚恋、签约等事项。",
            "三合局": "三合局成则力量强大，可左右卦象吉凶。需观用神在局中地位。",
            "三刑": "三刑主是非、冲突、损耗。应慎防官非、口舌。",
            "回头生": "动爻变出的卦回头生该动爻，大吉之象。",
            "回头克": "动爻变出的卦回头克该动爻，大凶之象。",
        }
        return meanings.get(pattern, "未知格局")

    def check_sanhe(self, zhi_list: List[str]) -> Dict:
        """检查是否形成三合局"""
        sanhe = self.rules.get("sanhe_banzi", {})

        result = {"formed": False, "pattern": None, "meaning": ""}

        # 检查各三合局
        for banzi, ju in sanhe.items():
            required_zhi = list(banzi)  # ['申', '子', '辰']
            count = sum(1 for z in zhi_list if z in required_zhi)

            if count >= 3:
                # 检查是否真的有这三个地支
                has_all = all(z in zhi_list for z in required_zhi)
                if has_all:
                    result["formed"] = True
                    result["pattern"] = banzi
                    result["meaning"] = f"{banzi}合{ju}，三合局成，力量强大。"
                    return result

        return result

    def check_chong(self, zhi1: str, zhi2: str) -> bool:
        """检查是否相冲"""
        chong_pairs = [
            ("子", "午"), ("丑", "未"), ("寅", "申"), ("卯", "酉"),
            ("辰", "戌"), ("巳", "亥"),
        ]
        return (zhi1, zhi2) in chong_pairs or (zhi2, zhi1) in chong_pairs

    def check_he(self, zhi1: str, zhi2: str) -> bool:
        """检查是否相合"""
        he_pairs = [
            ("子", "丑"), ("寅", "亥"), ("卯", "戌"),
            ("辰", "酉"), ("巳", "申"), ("午", "未"),
        ]
        return (zhi1, zhi2) in he_pairs or (zhi2, zhi1) in he_pairs

    def analyze_patterns(self, hexagram_name: str, yao_zhi_list: List[str]) -> Dict:
        """综合分析格局"""
        results = {
            "patterns": [],
            "meanings": [],
        }

        # 游魂/归魂
        if self.check_youhun(hexagram_name):
            results["patterns"].append("游魂卦")
            results["meanings"].append(self.get_pattern_meaning("游魂卦"))
        elif self.check_guihun(hexagram_name):
            results["patterns"].append("归魂卦")
            results["meanings"].append(self.get_pattern_meaning("归魂卦"))

        # 三合局
        sanhe_result = self.check_sanhe(yao_zhi_list)
        if sanhe_result["formed"]:
            results["patterns"].append(f"三合局（{sanhe_result['pattern']}）")
            results["meanings"].append(sanhe_result["meaning"])

        return results


def main():
    analyzer = PatternAnalyzer()
    result = analyzer.analyze_patterns("火地晋", ["子", "寅", "辰", "午", "申", "戌"])
    print(result)


if __name__ == "__main__":
    main()
