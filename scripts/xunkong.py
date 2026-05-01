#!/usr/bin/env python3
"""
旬空判断模块
根据日干支计算旬空地支

旬空规则：
- 甲子旬：戌亥空
- 甲戌旬：申酉空
- 甲申旬：午未空
- 甲午旬：辰巳空
- 甲辰旬：寅卯空
- 甲寅旬：子丑空

天干地支组合以60甲子循环，每10个天干配一轮地支，每旬10组干支，每旬都有两个地支没有天干相配，称为旬空。
"""

# 旬空规则字典
XUNKONG_RULES = {
    # 旬首: [空亡地支1, 空亡地支2]
    "甲子": ["戌", "亥"],  # 甲子旬
    "甲戌": ["申", "酉"],  # 甲戌旬
    "甲申": ["午", "未"],  # 甲申旬
    "甲午": ["辰", "巳"],  # 甲午旬
    "甲辰": ["寅", "卯"],  # 甲辰旬
    "甲寅": ["子", "丑"],  # 甲寅旬
}

# 60甲子完整列表（按旬分组）
# 每旬以甲开头，共6旬
JIAZI_CYCLE = {
    "甲子": ["甲子", "乙丑", "丙寅", "丁卯", "戊辰", "己巳", "庚午", "辛未", "壬申", "癸酉"],
    "甲戌": ["甲戌", "乙亥", "丙子", "丁丑", "戊寅", "己卯", "庚辰", "辛巳", "壬午", "癸未"],
    "甲申": ["甲申", "乙酉", "丙戌", "丁亥", "戊子", "己丑", "庚寅", "辛卯", "壬辰", "癸巳"],
    "甲午": ["甲午", "乙未", "丙申", "丁酉", "戊戌", "己亥", "庚子", "辛丑", "壬寅", "癸卯"],
    "甲辰": ["甲辰", "乙巳", "丙午", "丁未", "戊申", "己酉", "庚戌", "辛亥", "壬子", "癸丑"],
    "甲寅": ["甲寅", "乙卯", "丙辰", "丁巳", "戊午", "己未", "庚申", "辛酉", "壬戌", "癸亥"],
}


def get_xunkong(day_gan: str, day_zhi: str) -> list:
    """
    根据日干支计算旬空地支
    
    Args:
        day_gan: 日干（甲、乙、丙、丁、戊、己、庚、辛、壬、癸）
        day_zhi: 日支（子、丑、寅、卯、辰、巳、午、未、申、酉、戌、亥）
    
    Returns:
        包含两个空亡地支的列表，如 ["戌", "亥"]
    """
    day_ganzhi = day_gan + day_zhi
    
    # 查找日干支所在的旬
    for xunshou, ganzhi_list in JIAZI_CYCLE.items():
        if day_ganzhi in ganzhi_list:
            return XUNKONG_RULES.get(xunshou, ["?", "?"])
    
    return ["?", "?"]


def get_xunkong_by_ganzhi(day_ganzhi: str) -> list:
    """
    根据日干支（组合字符串）计算旬空地支
    
    Args:
        day_ganzhi: 日干支，如"甲子"
    
    Returns:
        包含两个空亡地支的列表
    """
    # 查找日干支所在的旬
    for xunshou, ganzhi_list in JIAZI_CYCLE.items():
        if day_ganzhi in ganzhi_list:
            return XUNKONG_RULES.get(xunshou, ["?", "?"])
    
    return ["?", "?"]


def get_xunshou(day_gan: str, day_zhi: str) -> str:
    """
    获取日干支所在的旬首
    
    Args:
        day_gan: 日干
        day_zhi: 日支
    
    Returns:
        旬首名称，如"甲子"
    """
    day_ganzhi = day_gan + day_zhi
    
    for xunshou, ganzhi_list in JIAZI_CYCLE.items():
        if day_ganzhi in ganzhi_list:
            return xunshou
    
    return "?"


def format_xunkong(xunkong: list) -> str:
    """
    格式化旬空输出
    
    Args:
        xunkong: 空亡地支列表
    
    Returns:
        格式化字符串，如"戌亥空"
    """
    if len(xunkong) >= 2:
        return f"{xunkong[0]}{xunkong[1]}空"
    return "未知"


# 测试函数
if __name__ == "__main__":
    # 测试各种干支组合
    test_cases = [
        ("甲", "子"),  # 甲子旬：戌亥空
        ("乙", "丑"),  # 甲子旬：戌亥空
        ("甲", "戌"),  # 甲戌旬：申酉空
        ("甲", "申"),  # 甲申旬：午未空
        ("甲", "午"),  # 甲午旬：辰巳空
        ("甲", "辰"),  # 甲辰旬：寅卯空
        ("甲", "寅"),  # 甲寅旬：子丑空
        ("丙", "戌"),  # 甲戌旬：申酉空
        ("戊", "子"),  # 甲申旬：午未空
    ]
    
    print("旬空测试：")
    for gan, zhi in test_cases:
        xunkong = get_xunkong(gan, zhi)
        xunshou = get_xunshou(gan, zhi)
        print(f"  {gan}{zhi}日 → {xunshou}旬 → 旬空：{format_xunkong(xunkong)}")
