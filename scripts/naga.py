#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
六爻纳甲核心引擎 v17 - 最终版
爻符号：少阳⚊(U+268A) 老阳☰(U+2610) 少阴⚋(U+268B) 老阴☱(U+2611)
六爻顺序（从下往上）：初爻、二爻、三爻、四爻、五爻、上爻
内卦 = h[3:6]（四爻+五爻+上爻）
外卦 = h[0:3]（初爻+二爻+三爻）
HEX key = (inner, outer)
"""

YAO_SYM = {
    "少阳": "⚊", "老阳": "☰",
    "少阴": "⚋", "老阴": "☱",
}

# 正确八卦trigram（8个，无重复）
TRIGRAM = {
    "⚊⚊⚊": "乾",
    "⚋⚋⚋": "坤",
    "⚋⚊⚊": "震",
    "⚊⚊⚋": "巽",
    "⚋⚊⚋": "坎",
    "⚊⚋⚊": "离",
    "⚊⚋⚋": "艮",
    "⚋⚋⚊": "兑",
}

# 纳甲（内卦定宫位）
BAGUA = {
    "乾": {"gan": ["甲","丙","戊","壬","甲","丙"], "zhi": ["子","寅","辰","午","申","戌"]},
    "坤": {"gan": ["乙","丁","己","癸","乙","丁"], "zhi": ["未","巳","卯","亥","酉","未"]},
    "震": {"gan": ["庚","丙","甲","壬","庚","丙"], "zhi": ["子","寅","辰","午","申","戌"]},
    "巽": {"gan": ["辛","壬","庚","癸","辛","壬"], "zhi": ["丑","亥","酉","未","巳","卯"]},
    "坎": {"gan": ["戊","丙","甲","戊","丙","甲"], "zhi": ["寅","辰","午","申","戌","子"]},
    "离": {"gan": ["己","丁","乙","己","丁","乙"], "zhi": ["卯","丑","亥","未","巳","酉"]},
    "艮": {"gan": ["丙","戊","庚","丙","戊","庚"], "zhi": ["辰","午","申","戌","子","寅"]},
    "兑": {"gan": ["丁","己","辛","丁","己","辛"], "zhi": ["卯","巳","未","酉","亥","丑"]},
}

# 世应（内卦定）
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

WXG = {"甲":"木","乙":"木","丙":"火","丁":"火","戊":"土","己":"土","庚":"金","辛":"金","壬":"水","癸":"水"}

def liushou(p, g):
    pw = {"乾":"金","兑":"金","离":"火","震":"木","巽":"木","坎":"水","艮":"土","坤":"土"}[p]
    gw = WXG.get(g, "土")
    t = {
        ("金","金"):"兄弟",("金","火"):"官鬼",("金","土"):"父母",("金","水"):"子孙",("金","木"):"妻财",
        ("火","金"):"妻财",("火","火"):"兄弟",("火","土"):"官鬼",("火","水"):"父母",("火","木"):"子孙",
        ("土","金"):"子孙",("土","火"):"妻财",("土","土"):"兄弟",("土","水"):"官鬼",("土","木"):"父母",
        ("水","金"):"父母",("水","火"):"子孙",("水","土"):"妻财",("水","水"):"兄弟",("水","木"):"官鬼",
        ("木","金"):"官鬼",("木","火"):"父母",("木","土"):"子孙",("木","水"):"妻财",("木","木"):"兄弟",
    }
    return t.get((pw, gw), "兄弟")

# 64卦表：key = (inner, outer) - 注意：key是(内卦,外卦)顺序
HEX = {
    ("乾","乾"):"乾", ("兑","乾"):"履", ("离","乾"):"同人", ("震","乾"):"无妄",
    ("巽","乾"):"小畜", ("坎","乾"):"讼", ("艮","乾"):"遁", ("坤","乾"):"否",
    ("乾","兑"):"夬", ("兑","兑"):"兑", ("离","兑"):"睽", ("震","兑"):"归妹",
    ("巽","兑"):"中孚", ("坎","兑"):"困", ("艮","兑"):"损", ("坤","兑"):"临",
    ("乾","离"):"大有", ("兑","离"):"革", ("离","离"):"离", ("震","离"):"丰",
    ("巽","离"):"家人", ("坎","离"):"既济", ("艮","离"):"贲", ("坤","离"):"明夷",
    ("乾","震"):"大壮", ("兑","震"):"随", ("离","震"):"噬嗑", ("震","震"):"震",
    ("巽","震"):"恒", ("坎","震"):"解", ("艮","震"):"颐", ("坤","震"):"豫",
    ("乾","巽"):"姤", ("兑","巽"):"大过", ("离","巽"):"鼎", ("震","巽"):"益",
    ("巽","巽"):"巽", ("坎","巽"):"涣", ("艮","巽"):"渐", ("坤","巽"):"观",
    ("乾","坎"):"需", ("兑","坎"):"节", ("离","坎"):"未济", ("震","坎"):"屯",
    ("巽","坎"):"井", ("坎","坎"):"坎", ("艮","坎"):"蹇", ("坤","坎"):"师",
    ("乾","艮"):"大畜", ("兑","艮"):"睽", ("离","艮"):"贲", ("震","艮"):"颐",
    ("巽","艮"):"蛊", ("坎","艮"):"蹇", ("艮","艮"):"艮", ("坤","艮"):"剥",
    ("乾","坤"):"泰", ("兑","坤"):"临", ("离","坤"):"明夷", ("震","坤"):"复",
    ("巽","坤"):"升", ("坎","坤"):"师", ("艮","坤"):"谦", ("坤","坤"):"坤",
}

def _normalize_yao_for_trigram(yao):
    """将爻转换为三爻卦符号，用于查找内卦/外卦
    老阳/老阴要归一化为基础阴阳爻（动爻变后就是另一个卦的爻）"""
    if yao in ("老阳", "☰"):
        return "⚊"
    if yao in ("老阴", "☱"):
        return "⚋"
    if yao == "少阳":
        return "⚊"
    if yao == "少阴":
        return "⚋"
    return "⚊"  # fallback

def analyze(yao_list):
    """分析六爻卦象"""
    h = "".join(YAO_SYM.get(y, "⚊") for y in yao_list)
    # 用于三爻卦查找时，老阳/老阴要转为基础阴阳爻
    h_inner = "".join(_normalize_yao_for_trigram(y) for y in yao_list[3:])
    h_outer = "".join(_normalize_yao_for_trigram(y) for y in yao_list[:3])
    inner = TRIGRAM.get(h_inner, "乾")
    outer = TRIGRAM.get(h_outer, "乾")
    # HEX 字典的 key 是 (outer, inner)
    name = HEX.get((outer, inner), "乾")
    nd = BAGUA.get(inner, {"gan": ["甲"]*6, "zhi": ["子"]*6})
    gl, zl = nd["gan"], nd["zhi"]
    naga = []
    for i in range(6):
        g = gl[i] if i < len(gl) else "甲"
        z = zl[i] if i < len(zl) else "子"
        naga.append({
            "position": i+1, "yao": yao_list[i], "gan": g, "zhi": z,
            "wuxing": WXG.get(g, "土"),
            "liushou": liushou(inner, g),
        })
    se = SHI_YING.get(inner, {"shi": 5, "ying": 1})
    moving = [i for i, y in enumerate(yao_list) if y in ("老阳", "老阴", "动")]
    bian = ["少阴" if y=="老阳" else "少阳" if y=="老阴" else y for y in yao_list]
    bh = "".join(YAO_SYM.get(b, "⚊") for b in bian)
    # 变换卦同样需要先归一化老阳/老阴
    bh_inner = "".join(_normalize_yao_for_trigram(y) for y in bian[:3])
    bh_outer = "".join(_normalize_yao_for_trigram(y) for y in bian[3:])
    binr = TRIGRAM.get(bh_inner, "乾")
    boutr = TRIGRAM.get(bh_outer, "乾")
    bname = HEX.get((binr, boutr), "乾")
    guige = []
    if name in ("乾","坤","震","巽","坎","离","艮","兑","否","泰","大壮","无妄","大过","讼","涣","睽","中孚","蛊","升","井"):
        guige.append("六冲卦")
    if name in ("明夷","颐","需","大过","晋","小过","涣","中孚"):
        guige.append("游魂卦")
    if name in ("随","渐","旅","咸","小过","晋","睽","中孚","节","需","师","比","大有","归妹","蛊"):
        guige.append("归魂卦")
    return {
        "hex_name": name, "hex_id": h, "inner_gua": inner, "outer_gua": outer,
        "naga": naga, "shi_position": se["shi"], "ying_position": se["ying"],
        "moving": moving, "bian_name": bname, "bian_hex_id": bh, "guige": guige,
    }

def print_result(r):
    yc = ["初爻","二爻","三爻","四爻","五爻","上爻"]
    print("\n" + "="*46)
    print("  " + r["hex_name"] + "  " + r["inner_gua"] + "内 · " + r["outer_gua"] + "外")
    print("  卦象：" + r["hex_id"])
    print("="*46)
    for i, item in enumerate(r["naga"]):
        se = "【世】" if i+1 == r["shi_position"] else "【应】" if i+1 == r["ying_position"] else ""
        m = " <-动" if i in r["moving"] else ""
        print("  " + yc[i] + "：" + item["gan"]+item["zhi"] + " " + item["liushou"] + se + m)
    if r["moving"]:
        print("\n  变卦：" + r["bian_name"] + "（" + r["bian_hex_id"] + "）")
    if r["guige"]:
        print("  格局：" + "、".join(r["guige"]))

if __name__ == "__main__":
    print("TRIGRAM:", len(TRIGRAM), "entries (should be 8)")
    print("HEX:", len(HEX), "entries (should be 64)")
    print()

    # 核心验证：8个纯卦/本宫卦
    YAOSYM_INV = {"⚊": "少阳", "☰": "老阳", "⚋": "少阴", "☱": "老阴"}
    # 正确的8个本宫卦：内外卦相同，只有纯少阳/少阴
    # 乾⚊⚊⚊、坤⚋⚋⚋、震⚋⚊⚊、巽⚊⚊⚋、坎⚋⚊⚋、离⚊⚋⚊、艮⚊⚋⚋、兑⚋⚋⚊
    CORE_TESTS = [
        ("乾",   ["少阳"]*6, "乾", "乾"),
        ("坤",   ["少阴"]*6, "坤", "坤"),
        ("震",   ["少阴","少阳","少阳","少阴","少阳","少阳"], "震", "震"),
        ("巽",   ["少阳","少阳","少阴","少阳","少阳","少阴"], "巽", "巽"),
        ("坎",   ["少阴","少阳","少阴","少阴","少阳","少阴"], "坎", "坎"),
        ("离",   ["少阳","少阴","少阳","少阳","少阴","少阳"], "离", "离"),
        ("艮",   ["少阳","少阴","少阴","少阳","少阴","少阴"], "艮", "艮"),
        ("兑",   ["少阴","少阴","少阳","少阴","少阴","少阳"], "兑", "兑"),
    ]
    print("=== 八卦本宫卦验证 ===")
    oks = 0
    for name, yao_list, exp_inner, exp_outer in CORE_TESTS:
        r = analyze(yao_list)
        ok = (r["hex_name"] == name and r["inner_gua"] == exp_inner and r["outer_gua"] == exp_outer)
        if ok:
            print(f"OK {name}")
            oks += 1
        else:
            print(f"FAIL {name}: got {r['hex_name']}|内{r['inner_gua']}外{r['outer_gua']}, exp {name}|内{exp_inner}外{exp_outer}")
    print(f"\n{oks}/{len(CORE_TESTS)} passed")

    # 演示
    print("\n=== 演示 ===")
    r = analyze(["少阳"]*6)
    print_result(r)
