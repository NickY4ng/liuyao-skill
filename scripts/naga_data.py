#!/usr/bin/env python3
"""
六爻纳甲规则引擎
每个卦由内卦（下卦）+ 外卦（上卦）组成
初爻到三爻=内卦，四爻到上爻=外卦
"""

from hexagrams import WUXING

TIANGAN = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]
DIZHI = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]

# 八卦宫纳甲表（初爻到上爻）
# 格式：[内卦初爻,内卦二爻,内卦三爻,外卦四爻,外卦五爻,外卦上爻]
# 乾宫：甲子起顺排，隔位进
# 内卦：初爻=甲子，二爻=丙寅，三爻=戊辰
# 外卦：四爻=壬午，五爻=甲申，六爻=丙戌
BAGUANAGA = {
    # 乾宫（金）
    "乾": {
        "gan": ["甲", "丙", "戊", "壬", "甲", "丙"],  # 内3+外3
        "zhi": ["子", "寅", "辰", "午", "申", "戌"],
        "wuxing": "金",
    },
    # 坤宫（土）
    "坤": {
        "gan": ["乙", "丁", "己", "癸", "乙", "丁"],
        "zhi": ["未", "巳", "卯", "亥", "酉", "未"],
        "wuxing": "土",
    },
    # 震宫（木）
    "震": {
        "gan": ["庚", "丙", "甲", "壬", "庚", "丙"],
        "zhi": ["子", "寅", "辰", "午", "申", "戌"],
        "wuxing": "木",
    },
    # 巽宫（木）
    "巽": {
        "gan": ["辛", "壬", "庚", "癸", "辛", "壬"],
        "zhi": ["丑", "亥", "酉", "未", "巳", "卯"],
        "wuxing": "木",
    },
    # 坎宫（水）
    "坎": {
        "gan": ["戊", "丙", "甲", "戊", "丙", "甲"],
        "zhi": ["寅", "辰", "午", "申", "戌", "子"],
        "wuxing": "水",
    },
    # 离宫（火）
    "离": {
        "gan": ["己", "丁", "乙", "己", "丁", "乙"],
        "zhi": ["卯", "丑", "亥", "未", "巳", "酉"],
        "wuxing": "火",
    },
    # 艮宫（土）
    "艮": {
        "gan": ["丙", "戊", "庚", "丙", "戊", "庚"],
        "zhi": ["辰", "午", "申", "戌", "子", "寅"],
        "wuxing": "土",
    },
    # 兑宫（金）
    "兑": {
        "gan": ["丁", "己", "辛", "丁", "己", "辛"],
        "zhi": ["卯", "巳", "未", "酉", "亥", "丑"],
        "wuxing": "金",
    },
}

# 世应位置表
SHI_YING = {
    "乾": {"shi": 5, "ying": 1},
    "兑": {"shi": 5, "ying": 1},
    "离": {"shi": 3, "ying": 1},
    "震": {"shi": 3, "ying": 1},
    "巽": {"shi": 4, "ying": 1},
    "坎": {"shi": 1, "ying": 4},
    "艮": {"shi": 5, "ying": 1},
    "坤": {"shi": 1, "ying": 4},
}


def install_naga(inner_gua, outer_gua, yao_list):
    """
    纳甲装卦
    inner_gua: 内卦名（乾/坤/震/巽/坎/离/艮/兑）
    outer_gua: 外卦名
    yao_list: 6个爻的字符串列表（从初爻到上爻）
    返回：每个爻的 {position, yao, gan, zhi, wuxing, liushou}
    """
    inner = BAGUANAGA.get(inner_gua)
    outer = BAGUANAGA.get(outer_gua)

    if not inner or not outer:
        return None

    result = []
    palace_wuxing = inner["wuxing"]

    for i in range(6):
        if i < 3:
            gan = inner["gan"][i]
            zhi = inner["zhi"][i]
        else:
            gan = outer["gan"][i - 3]
            zhi = outer["zhi"][i - 3]

        wuxing = WUXING.get(gan, "土")
        liushou = get_liushou(palace_wuxing, wuxing)

        result.append({
            "position": i + 1,
            "yao": yao_list[i],
            "gan": gan,
            "zhi": zhi,
            "wuxing": wuxing,
            "liushou": liushou,
        })

    return result


def get_liushou(palace_wuxing, yao_wuxing):
    """六亲生克：卦宫五行 + 爻五行"""
    shengke = {
        ("木", "木"): "兄弟", ("木", "火"): "子孙", ("木", "土"): "妻财", ("木", "金"): "官鬼", ("木", "水"): "父母",
        ("火", "木"): "父母", ("火", "火"): "兄弟", ("火", "土"): "子孙", ("火", "金"): "妻财", ("火", "水"): "官鬼",
        ("土", "木"): "官鬼", ("土", "火"): "父母", ("土", "土"): "兄弟", ("土", "金"): "子孙", ("土", "水"): "妻财",
        ("金", "木"): "妻财", ("金", "火"): "官鬼", ("金", "土"): "父母", ("金", "金"): "兄弟", ("金", "水"): "子孙",
        ("水", "木"): "子孙", ("水", "火"): "妻财", ("水", "土"): "官鬼", ("水", "金"): "父母", ("水", "水"): "兄弟",
    }
    return shengke.get((palace_wuxing, yao_wuxing), "兄弟")


def get_palace(inner_gua):
    """以内卦定卦宫"""
    palace_map = {
        "乾": "乾宫", "兑": "乾宫",
        "离": "离宫",
        "震": "震宫", "巽": "震宫",
        "坎": "坎宫",
        "艮": "艮宫",
        "坤": "坤宫",
    }
    return palace_map.get(inner_gua, "乾宫")


def get_shi_ying(inner_gua):
    """世应位置"""
    return SHI_YING.get(inner_gua, {"shi": 5, "ying": 1})


def is_moving(yao_str):
    return yao_str in ("老阳", "老阴", "动")


def get_biangua_yaos(yao_list):
    """动爻阴阳互换，生成变卦的6个爻"""
    biangua = []
    for y in yao_list:
        if y == "老阳":
            biangua.append("少阴")
        elif y == "老阴":
            biangua.append("少阳")
        else:
            biangua.append(y)
    return biangua


# 三爻卦符号映射
TRIGRAM_FROM_3 = {
    "⚊⚊⚊": "乾", "⚋⚋⚋": "坤",
    "⚊⚋⚋": "震", "⚋⚊⚋": "巽",
    "⚋⚊⚊": "坎", "⚊⚋⚊": "离",
    "⚊⚊⚋": "艮", "⚋⚋⚊": "兑",
}


def analyze(yao_list):
    """
    六爻分析主函数
    yao_list: ["少阳","老阳","少阴","少阴","老阴","少阳"]（从初爻到上爻）
    """
    from hexagrams import HEXAGRAMS_FULL

    sym_map = {"少阳": "⚊", "老阳": "☰", "少阴": "⚋", "老阴": "☱"}
    hex_id = "".join(sym_map.get(y, "⚊") for y in yao_list)

    # 内外卦（从爻符号反推）
    # 初二三爻构成内卦（上爻为最上，故反序）
    inner_3 = hex_id[2] + hex_id[1] + hex_id[0]  # 三爻·二爻·初爻
    outer_3 = hex_id[5] + hex_id[4] + hex_id[3]  # 上爻·五爻·四爻
    inner_gua = TRIGRAM_FROM_3.get(inner_3, "乾")
    outer_gua = TRIGRAM_FROM_3.get(outer_3, "乾")

    # 卦名（通过内外卦查）
    hex_name = get_hex_name(outer_gua, inner_gua)
    hex_data = HEXAGRAMS_FULL.get(hex_name, {})

    # 纳甲
    naga = install_naga(inner_gua, outer_gua, yao_list)
    palace = get_palace(inner_gua)
    palace_wuxing = BAGUANAGA.get(inner_gua, {}).get("wuxing", "金")

    # 世应
    se = get_shi_ying(inner_gua)

    # 动爻
    moving_indices = [i for i, y in enumerate(yao_list) if is_moving(y)]

    # 变卦
    biangua_yaos = get_biangua_yaos(yao_list)
    biangua_id = "".join(sym_map.get(y, "⚊") for y in biangua_yaos)
    bian_inner_3 = biangua_id[2] + biangua_id[1] + biangua_id[0]
    bian_outer_3 = biangua_id[5] + biangua_id[4] + biangua_id[3]
    bian_inner_gua = TRIGRAM_FROM_3.get(bian_inner_3, "乾")
    bian_outer_gua = TRIGRAM_FROM_3.get(bian_outer_3, "乾")
    bian_name = get_hex_name(bian_outer_gua, bian_inner_gua)

    # 格局
    guige = []
    if hex_name in ("乾", "坤", "震", "巽", "坎", "离", "艮", "兑", "否", "泰", "大壮", "无妄", "大过"):
        guige.append("六冲卦")
    if hex_name in ("蛊", "丰", "旅", "咸", "小过", "晋", "睽", "中孚", "节", "需", "大壮"):
        guige.append("游魂卦")
    if hex_name in ("随", "渐", "旅", "咸", "小过", "晋", "睽", "中孚", "节", "需", "讼"):
        guige.append("归魂卦")

    return {
        "hexagram_name": hex_name,
        "hex_data": hex_data,
        "hex_id": hex_id,
        "inner_gua": inner_gua,
        "outer_gua": outer_gua,
        "palace": palace,
        "palace_wuxing": palace_wuxing,
        "naga": naga,
        "shi_position": se["shi"],
        "ying_position": se["ying"],
        "moving_indices": moving_indices,
        "biangua_name": bian_name,
        "biangua_id": biangua_id,
        "guige": guige,
        "yao_list": yao_list,
    }


def get_hex_name(outer_gua, inner_gua):
    """根据内外卦找卦名"""
    # 内外卦组合 → 64卦
    combo = (outer_gua, inner_gua)
    hex_map = {
        ("乾", "乾"): "乾", ("乾", "兑"): "履", ("乾", "离"): "同人", ("乾", "震"): "无妄",
        ("乾", "巽"): "姤", ("乾", "坎"): "讼", ("乾", "艮"): "遁", ("乾", "坤"): "否",
        ("兑", "乾"): "夬", ("兑", "兑"): "兑", ("兑", "离"): "睽", ("兑", "震"): "归妹",
        ("兑", "巽"): "中孚", ("兑", "坎"): "困", ("兑", "艮"): "损", ("兑", "坤"): "临",
        ("离", "乾"): "大有", ("离", "兑"): "革", ("离", "离"): "离", ("离", "震"): "丰",
        ("离", "巽"): "家人", ("离", "坎"): "未济", ("离", "艮"): "贲", ("离", "坤"): "明夷",
        ("震", "乾"): "大壮", ("震", "兑"): "随", ("震", "离"): "噬嗑", ("震", "震"): "震",
        ("震", "巽"): "恒", ("震", "坎"): "解", ("震", "艮"): "颐", ("震", "坤"): "豫",
        ("巽", "乾"): "小畜", ("巽", "兑"): "大过", ("巽", "离"): "鼎", ("巽", "震"): "益",
        ("巽", "巽"): "巽", ("巽", "坎"): "涣", ("巽", "艮"): "蛊", ("巽", "坤"): "观",
        ("坎", "乾"): "需", ("坎", "兑"): "节", ("坎", "离"): "既济", ("坎", "震"): "屯",
        ("坎", "巽"): "井", ("坎", "坎"): "坎", ("坎", "艮"): "蹇", ("坎", "坤"): "师",
        ("艮", "乾"): "大畜", ("艮", "兑"): "睽", ("艮", "离"): "贲", ("艮", "震"): "颐",
        ("艮", "巽"): "蛊", ("艮", "坎"): "蹇", ("艮", "艮"): "艮", ("艮", "坤"): "剥",
        ("坤", "乾"): "泰", ("坤", "兑"): "临", ("坤", "离"): "明夷", ("坤", "震"): "复",
        ("坤", "巽"): "升", ("坤", "坎"): "师", ("坤", "艮"): "谦", ("坤", "坤"): "坤",
    }
    return hex_map.get(combo, "乾")


def print_analysis(result):
    """打印分析结果"""
    print(f"\n{'='*46}")
    print(f"  卦名：{result['hexagram_name']}  卦宫：{result['palace']}（{result['palace_wuxing']}）")
    print(f"  卦象：{result['hex_id']}")
    print(f"  内卦：{result['inner_gua']}  外卦：{result['outer_gua']}")
    print(f"{'='*46}")

    yao_cn = ["初爻", "二爻", "三爻", "四爻", "五爻", "上爻"]
    for i, item in enumerate(result["naga"]):
        se = ""
        if i + 1 == result["shi_position"]:
            se = "【世】"
        elif i + 1 == result["ying_position"]:
            se = "【应】"
        m = " ←动" if i in result["moving_indices"] else ""
        print(f"  {yao_cn[i]}：{item['gan']}{item['zhi']} {item['liushou']}{se}{m}")

    if result["moving_indices"]:
        print(f"\n  变卦：{result['biangua_name']}（{result['biangua_id']}）")

    if result["guige"]:
        print(f"\n  格局：{'、'.join(result['guige'])}")


if __name__ == "__main__":
    # 测试乾宫（内外皆乾）
    print("=== 测试1：乾为天 ===")
    yao = ["少阳", "少阳", "少阳", "少阴", "少阴", "少阴"]
    r = analyze(yao)
    print_analysis(r)
    print("期望装卦：甲子 丙寅 戊辰 壬午 甲申 丙戌")
    for item in r["naga"]:
        print(f"  {item['position']}: {item['gan']}{item['zhi']}")

    print()
    print("=== 测试2：天火同人（离宫）===")
    yao2 = ["少阳", "少阳", "少阳", "少阴", "少阴", "少阴"]  # 实际同人卦需要不同组合
    r2 = analyze(["老阳", "少阳", "少阳", "少阴", "少阴", "少阴"])  # 火天大有同人
    print_analysis(r2)
