#!/usr/bin/env python3
"""
旺衰判断模块
核心逻辑：
1. 月建旺相休囚死
2. 日建生克作用
3. 动变生克关系
"""

# 月令旺相休囚死表
YUELING_TABLE = {
    # 月令 : [旺, 相, 休, 囚, 死]
    "寅": ["木", "火", "水", "金", "土"],
    "卯": ["木", "火", "水", "金", "土"],
    "巳": ["火", "土", "木", "水", "金"],
    "午": ["火", "土", "木", "水", "金"],
    "申": ["金", "水", "土", "火", "木"],
    "酉": ["金", "水", "土", "火", "木"],
    "亥": ["水", "木", "金", "土", "火"],
    "子": ["水", "木", "金", "土", "火"],
    "辰": ["土", "金", "火", "木", "水"],
    "戌": ["土", "金", "火", "木", "水"],
    "丑": ["土", "金", "火", "木", "水"],
    "未": ["土", "金", "火", "木", "水"],
}

# 五行生克关系
WUXING_SHENG = {"木": "火", "火": "土", "土": "金", "金": "水", "水": "木"}
WUXING_KE = {"木": "土", "火": "金", "土": "水", "金": "木", "水": "火"}
WUXING_TONG = {"木": "木", "火": "火", "土": "土", "金": "金", "水": "水"}


def get_yueling_status(yuezhi: str, wuxing: str) -> str:
    """获取月令下五行的状态"""
    if yuezhi not in YUELING_TABLE:
        return "未知"

    table = YUELING_TABLE[yuezhi]
    if wuxing == table[0]:
        return "旺"
    elif wuxing == table[1]:
        return "相"
    elif wuxing == table[2]:
        return "休"
    elif wuxing == table[3]:
        return "囚"
    elif wuxing == table[4]:
        return "死"
    return "平"


def get_shengke(wuxing1: str, wuxing2: str) -> str:
    """判断五行生克关系"""
    if wuxing1 == WUXING_SHENG.get(wuxing2):
        return f"{wuxing2}生{wuxing1}"  # wuxing2生wuxing1
    elif wuxing1 == WUXING_KE.get(wuxing2):
        return f"{wuxing1}克{wuxing2}"
    elif wuxing1 == wuxing2:
        return f"{wuxing1}同{wuxing2}"
    return "无直接关系"


class WangShuaiAnalyzer:
    """旺衰分析器"""

    def __init__(self, yuezhi: str, rizhi: str, nian_zhi: str = None):
        self.yuezhi = yuezhi
        self.rizhi = rizhi
        self.nian_zhi = nian_zhi

    def analyze_yao(self, yao_wuxing: str, yao_zhi: str = None) -> dict:
        """分析单个爻的旺衰"""
        result = {}

        # 月令判断
        result["yueling_status"] = get_yueling_status(self.yuezhi, yao_wuxing)

        # 日建判断（简化：日支与爻支同五行则扶助）
        if yao_zhi:
            # 实际需要更复杂的日建与爻支关系
            if yao_zhi == self.rizhi:
                result["rizhi_status"] = "日建扶助"
            else:
                result["rizhi_status"] = "日建无特殊扶助"

        # 综合评定
        yueling = result.get("yueling_status", "")
        if yueling in ["旺", "相"]:
            result["overall"] = "旺相有力"
        elif yueling in ["休", "囚"]:
            result["overall"] = "偏弱"
        elif yueling == "死":
            result["overall"] = "休囚无力"
        else:
            result["overall"] = "需综合判断"

        return result


def main():
    # 测试
    analyzer = WangShuaiAnalyzer("寅", "子")
    result = analyzer.analyze_yao("木", "寅")
    print(result)


if __name__ == "__main__":
    main()
