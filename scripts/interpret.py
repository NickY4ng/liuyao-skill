#!/usr/bin/env python3
"""
六爻解读脚本
调用 naga.analyze() 获取完整卦象分析，再做用神选取、吉凶判断
"""

from naga import analyze, liushou, BAGUA
from hexagrams import HEXAGRAMS


# ===== HEXAGRAMS反向映射 =====
# naga用(inner_gua, outer_gua)定位卦象，HEXAGRAMS用gua=(inner, outer)作key
_GUA_TO_INFO = {info['gua']: {'full_name': n, 'palace': info['palace']}
                for n, info in HEXAGRAMS.items()}

# naga返回缩写名（如'同人'），HEXAGRAMS用全名（如'火天大有'）
# 通过gua (inner, outer)建立缩写→全名的映射
_NAGA_ABBREV_TO_FULL = {}
for full_name, info in HEXAGRAMS.items():
    inner, outer = info['gua']
    # naga的HEX用(outer, inner)做key，这里用(inner, outer)做反向映射
    _NAGA_ABBREV_TO_FULL[(outer, inner)] = full_name


# ===== 用神选取 =====
YONGSHEN_RULES = [
    (["父母", "父亲", "母亲", "房子", "文书", "证书", "车", "载具", "长辈"], "父母"),
    (["兄弟", "朋友", "竞争", "同事", "合作", "分"], "兄弟"),
    (["子孙", "小孩", "子女", "动物", "娱乐", "技术", "快乐"], "子孙"),
    (["妻", "情人", "桃花", "姻缘", "感情", "婚", "女性"], "妻财"),
    (["官", "工作", "事业", "升职", "老板", "上司", "丈夫", "男"], "官鬼"),
    (["财", "钱", "收入", "财运", "盈利", "投资", "生意"], "妻财"),
]


def get_yongshen(question):
    """根据问题判断用神"""
    if not question:
        return "世爻"
    for keywords, yongshen in YONGSHEN_RULES:
        if any(k in question for k in keywords):
            return yongshen
    return "世爻"


# ===== 旺衰判断 =====
WANGZHUAI = {
    "子": {"木": "死", "火": "休", "土": "囚", "金": "胎", "水": "旺"},
    "丑": {"木": "墓", "火": "养", "土": "旺", "金": "相", "水": "休"},
    "寅": {"木": "旺", "火": "相", "土": "休", "金": "囚", "水": "死"},
    "卯": {"木": "旺", "火": "相", "土": "休", "金": "囚", "水": "死"},
    "辰": {"木": "相", "火": "旺", "土": "旺", "金": "墓", "水": "囚"},
    "巳": {"木": "死", "火": "旺", "土": "相", "金": "休", "水": "囚"},
    "午": {"木": "死", "火": "旺", "土": "相", "金": "休", "水": "囚"},
    "未": {"木": "相", "火": "旺", "土": "旺", "金": "墓", "水": "囚"},
    "申": {"木": "囚", "火": "死", "土": "休", "金": "旺", "水": "相"},
    "酉": {"木": "囚", "火": "死", "土": "休", "金": "旺", "水": "相"},
    "戌": {"木": "休", "火": "囚", "土": "旺", "金": "相", "水": "墓"},
    "亥": {"木": "旺", "火": "死", "土": "胎", "金": "囚", "水": "旺"},
}


def judge_jixiong(result, yongshen):
    """吉凶判断"""
    naga = result["naga"]
    shi_pos = result["shi_position"]
    ying_pos = result["ying_position"]
    moving = result["moving"]
    guige = result["guige"]

    # 找用神爻
    yong_yao = None
    for item in naga:
        if item["liushou"] == yongshen:
            yong_yao = item
            break

    # 找世爻
    shi_yao = naga[shi_pos - 1]

    # 基本逻辑
    jixiong = "平"
    reason = ""
    detail = ""
    advice = ""

    has_dong = len(moving) > 0
    is_liuchong = "六冲卦" in guige if guige else False
    is_youhun = "游魂卦" in guige if guige else False
    is_guihun = "归魂卦" in guige if guige else False

    if yongshen == "世爻":
        # 以世爻为用神
        jixiong = "吉"
        reason = "以世爻为用神，此事由自身决定"
        detail = "此事成败完全取决于自己，宜积极主动。"
        advice = "大胆推进，充分发挥主观能动性。"
    elif yong_yao is None:
        jixiong = "待定"
        reason = "用神不现于卦中"
        detail = "所问之事用神未现，结果不完全取决于常规因素。"
        advice = "此事较特殊，需要结合时运综合判断。"
    elif yong_yao["position"] == shi_pos:
        # 用神持世
        if is_liuchong:
            jixiong = "吉中带凶"
            reason = "用神持世但逢六冲"
            detail = "此事虽与自身相关，但过程多波折，须防变故。"
            advice = "积极推进但做好备选方案，防意外。"
        else:
            jixiong = "吉"
            reason = "用神持世"
            detail = "用神落在世爻位置，此事由自己主导，大方向有利。"
            advice = "放心去做，此事终将有成。"
    elif yong_yao["position"] == ying_pos:
        jixiong = "凶"
        reason = "用神在应爻"
        detail = "用神落在应爻，此事由他人或外在因素主导，结果不在己。"
        advice = "谨慎对待，不可强求，做好变通准备。"
    elif has_dong:
        jixiong = "变化中"
        reason = f"有{len(moving)}个动爻"
        detail = "动爻出现，事情处于变化中，结果未定。"
        if is_youhun:
            detail += "游魂卦，心神不定，适宜变化。"
        if is_guihun:
            detail += "归魂卦，事情有归着，利于回归。"
        advice = "持续观察，等待时机成熟再行动。"
    else:
        jixiong = "平"
        reason = "静卦无动"
        detail = "此卦安静，事态平稳，暂无明显变化。"
        advice = "静待时机，不宜轻举妄动。"

    return {
        "jixiong": jixiong,
        "reason": reason,
        "detail": detail,
        "advice": advice,
    }


def interpret(question, yao_list, month_zhi=None):
    """
    六爻解读主函数
    question: 用户问题
    yao_list: 6个爻（从初爻到上爻）
    month_zhi: 月令地支，默认取当前农历月
    """
    from datetime import datetime

    # 获取当前月令
    if month_zhi is None:
        try:
            from lunarcalendar import Converter, Lunar
            today = datetime.now()
            lunar = Converter.Solar2Lunar(today.year, today.month, today.day)
            month_map = {1: "寅", 2: "卯", 3: "辰", 4: "巳", 5: "午",
                         6: "未", 7: "申", 8: "酉", 9: "戌", 10: "亥", 11: "子", 12: "丑"}
            month_zhi = month_map.get(lunar.lunar_month, "辰")
        except:
            month_zhi = "辰"

    # 1. 纳甲分析
    result = analyze(yao_list)

    # 2. 用神
    yongshen = get_yongshen(question)

    # 3. 吉凶判断
    jix = judge_jixiong(result, yongshen)

    # 4. 组装输出
    output = []
    output.append(f"{'='*46}")
    output.append(f"  六爻卦象解读")
    output.append(f"{'='*46}")
    output.append(f"  所问：{question or '吉凶如何'}")
    # 卦名和卦宫：naga返回缩写名和inner/outer，用GUA映射查完整名和卦宫
    hex_info = _GUA_TO_INFO.get((result['inner_gua'], result['outer_gua']), {'full_name': result['hex_name'], 'palace': '未知'})
    output.append(f"  卦名：{hex_info['full_name']}  卦宫：{hex_info['palace']}")
    output.append(f"  卦象：{result['hex_id']}（{result['inner_gua']}内 · {result['outer_gua']}外）")
    output.append(f"  月令：{month_zhi}月")
    output.append("")

    # 爻表
    yao_cn = ["初爻", "二爻", "三爻", "四爻", "五爻", "上爻"]
    for i, item in enumerate(result["naga"]):
        se = ""
        if i + 1 == result["shi_position"]:
            se = "【世】"
        elif i + 1 == result["ying_position"]:
            se = "【应】"
        m = " ←动" if i in result["moving"] else ""
        tag = " ←用神" if item["liushou"] == yongshen else ""
        output.append(f"  {yao_cn[i]}：{item['gan']}{item['zhi']} {item['liushou']}{se}{m}{tag}")

    output.append("")
    output.append(f"  用神：{yongshen}")
    if result["guige"]:
        output.append(f"  格局：{'、'.join(result['guige'])}")
    if result["moving"]:
        output.append(f"  动爻：{', '.join([yao_cn[i] for i in result['moving']])}")
        # 变卦：用bian_hex_id重建变卦的inner/outer，再查全名
        _bian_id = result['bian_hex_id']
        from naga import TRIGRAM, YAO_SYM as YAO_SYM_SRC
        _binr = TRIGRAM.get(_bian_id[0]+_bian_id[1]+_bian_id[2], '乾')
        _boutr = TRIGRAM.get(_bian_id[3]+_bian_id[4]+_bian_id[5], '乾')
        _bian_full = _NAGA_ABBREV_TO_FULL.get((_boutr, _binr), result['bian_name'])
        output.append(f"  变卦：{_bian_full}（{result['bian_hex_id']}）")

    output.append("")
    output.append(f"{'='*46}")
    output.append(f"  吉凶：{jix['jixiong']}")
    output.append(f"{'='*46}")
    output.append(f"  {jix['detail']}")
    if jix['advice']:
        output.append(f"  建议：{jix['advice']}")

    return "\n".join(output)


if __name__ == "__main__":
    # 测试：问财运，动爻在妻财爻
    # 假设：初爻少阳，二爻老阳动，三爻少阴，四爻少阳，五爻少阴，上爻少阳
    # 这是一个天风姤卦（乾宫）
    test_yao = ["少阳", "老阳", "少阴", "少阴", "少阴", "少阳"]
    print(interpret("最近财运如何", test_yao))
