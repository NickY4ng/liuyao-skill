#!/usr/bin/env python3
"""
六爻Skill整体逻辑验证脚本 v2
检查内容：
1. hexagrams_full.json 数据完整性
2. naga.json 数据完整性  
3. yongshen_rules.json 数据完整性
4. liuyao_interpret.py get_yongshen() key匹配问题
5. 世应位置一致性
6. 游魂/归魂卦规则一致性
"""

import json
import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(SCRIPT_DIR, "..", "data")

ISSUES = []

def add_issue(level: str, category: str, message: str, detail: str = ""):
    ISSUES.append({"level": level, "category": category, "message": message, "detail": detail})

def load_data():
    with open(os.path.join(DATA_DIR, "hexagrams_full.json"), "r", encoding="utf-8") as f:
        hexagrams = json.load(f)
    with open(os.path.join(DATA_DIR, "naga.json"), "r", encoding="utf-8") as f:
        naga = json.load(f)
    with open(os.path.join(DATA_DIR, "yongshen_rules.json"), "r", encoding="utf-8") as f:
        yongshen = json.load(f)
    return hexagrams, naga, yongshen

def check_hexagrams(hexagrams_data):
    print("=== 检查 hexagrams_full.json ===")
    hexagrams = hexagrams_data.get("hexagrams", {})
    
    if len(hexagrams) != 64:
        add_issue("P0", "数据完整性", f"hexagrams数量={len(hexagrams)}, 期望=64")
    
    # 检查guaxiang_full格式（6位⚊⚋）
    yang, yin = "⚊", "⚋"
    for key, info in hexagrams.items():
        gf = info.get("guaxiang_full", "")
        if len(gf) != 6 or any(c not in (yang, yin) for c in gf):
            add_issue("P0", "数据格式", f"{info.get('name','?')}: guaxiang_full格式错误", f"'{gf}'")
    
    # 检查key与guaxiang_full一致（key是二进制表示）
    for key, info in hexagrams.items():
        expected = "".join(['1' if c == yang else '0' for c in info.get("guaxiang_full", "")])
        if key != expected:
            add_issue("P0", "数据一致性", f"{info.get('name','?')}: key与guaxiang_full不匹配",
                     f"key={key}, expected={expected}")
    
    # 检查八宫（每宫8卦）
    gong_counts = {}
    for k, v in hexagrams.items():
        g = v.get("gong", "未知")
        gong_counts[g] = gong_counts.get(g, 0) + 1
    for g, cnt in gong_counts.items():
        if cnt != 8:
            add_issue("P0", "数据完整性", f"{g}: {cnt}卦, 期望8卦")
    
    if len(gong_counts) != 8:
        add_issue("P0", "数据完整性", f"共{len(gong_counts)}个宫, 期望8宫")
    
    # 检查position分布
    pos_counts = {}
    for k, v in hexagrams.items():
        p = v.get("position", "未知")
        pos_counts[p] = pos_counts.get(p, 0) + 1
    print(f"  各position分布: {pos_counts}")
    
    # 检查本宫首卦的neigua=waigua
    for k, v in hexagrams.items():
        if v.get("position") == "本宫首卦":
            ni = v.get("neigua", "")
            wi = v.get("waigua", "")
            if ni != wi:
                add_issue("P0", "数据一致性", f"本宫首卦{v.get('name','?')}: neigua≠waigua",
                         f"neigua={ni}, waigua={wi}")
    
    print(f"  ✓ hexagrams_full.json 检查完成")

def check_naga(naga_data):
    print("\n=== 检查 naga.json ===")
    naga_song = naga_data.get("naga_song", {})
    
    expected = {"乾", "坤", "震", "巽", "坎", "离", "艮", "兑"}
    actual = set(naga_song.keys())
    if expected != actual:
        add_issue("P0", "数据完整性", "naga.json八卦不全",
                 f"缺少: {expected-actual}, 多余: {actual-expected}")
    
    for bagua, info in naga_song.items():
        for side in ["neigua", "waigua"]:
            data = info.get(side, {})
            gan = data.get("gan", "")
            zhi_list = data.get("zhi", [])
            if not gan or len(zhi_list) != 3:
                add_issue("P1", "数据格式", f"naga.json {bagua}[{side}]数据不完整",
                         f"gan={gan}, zhi={zhi_list}")
    
    # 检查shiwei/yingwei
    for bagua, info in naga_song.items():
        sw = info.get("shiwei", -1)
        yw = info.get("yingwei", -1)
        if sw != 5 or yw != 2:
            add_issue("P1", "世应位置", f"naga.json {bagua}: shiwei={sw}, yingwei={yw}, 期望5,2", "")
    
    print(f"  ✓ naga.json 检查完成")

def check_yongshen_rules(yongshen_data):
    print("\n=== 检查 yongshen_rules.json ===")
    lookup = yongshen_data.get("yongshen_lookup", {})
    
    if not lookup:
        add_issue("P0", "数据完整性", "yongshen_lookup为空")
        return
    
    print(f"  共{len(lookup)}条规则")
    
    # 检查get_yongshen()函数中使用的keys是否都存在
    code_path = os.path.join(SCRIPT_DIR, "liuyao_interpret.py")
    with open(code_path, "r", encoding="utf-8") as f:
        code = f.read()
    
    # 从代码中提取rules.get()调用
    import re
    key_pattern = re.findall(r'return rules\.get\("([^"]+)"', code)
    
    for key in key_pattern:
        if key not in lookup:
            add_issue("P1", "代码Bug", f"get_yongshen()中使用了不存在的rules key: '{key}'",
                     "当关键词匹配时会fallback到default_yongshen，导致用神判断错误")
    print(f"  ✓ yongshen_rules.json 检查完成")

def check_yongshen_logic(hexagrams_data, yongshen_data):
    print("\n=== 检查用神逻辑正确性 ===")
    lookup = yongshen_data.get("yongshen_lookup", {})
    
    # 测试一些常见问题
    test_cases = [
        ("我想投资生意", "妻财爻"),
        ("最近财运怎么样", "妻财爻"),
        ("问下婚姻状况", "妻财爻"),
        ("工作怎么样", "官鬼爻"),  # 工作官运
        ("身体健康吗", "官鬼爻"),
        ("孩子的情况", "子孙爻"),
        ("考试能过吗", "父母爻"),
        ("出行注意事项", "世爻"),
    ]
    
    # 加载interpret模块动态测试
    sys.path.insert(0, SCRIPT_DIR)
    try:
        import liuyao_interpret
        interp = liuyao_interpret.LiuYaoInterpreter()
        
        errors = []
        for question, expected_primary in test_cases:
            interp.question = question
            result = interp.get_yongshen()
            actual = result.get("primary", "")
            if expected_primary not in actual:
                errors.append(f"  '{question}' → 期望含'{expected_primary}', 实际='{actual}'")
        
        if errors:
            print("  ⚠ 用神判断错误:")
            for e in errors:
                print(e)
            add_issue("P1", "代码Bug", "get_yongshen()存在多个判断错误", 
                     "\n".join(errors[:5]))
        else:
            print("  ✓ 用神判断逻辑正确")
    except Exception as e:
        add_issue("P1", "测试失败", f"无法导入liuyao_interpret: {e}")
    
    print(f"  ✓ 用神逻辑检查完成")

def check_liushou_consistency(hexagrams_data, yongshen_data):
    print("\n=== 检查游魂/归魂卦一致性 ===")
    hexagrams = hexagrams_data.get("hexagrams", {})
    liushou = yongshen_data.get("liushou_patterns", {})
    
    hex_youhun = [v["name"] for k, v in hexagrams.items() if v.get("position") == "游魂卦"]
    hex_guihun = [v["name"] for k, v in hexagrams.items() if v.get("position") == "归魂卦"]
    
    rules_youhun = liushou.get("游魂卦", [])
    rules_guihun = liushou.get("归魂卦", [])
    
    print(f"  hex游魂: {hex_youhun}")
    print(f"  rules游魂: {rules_youhun}")
    print(f"  hex归魂: {hex_guihun}")
    print(f"  rules归魂: {rules_guihun}")
    
    # 检查不匹配
    youhun_diff = set(hex_youhun) ^ set(rules_youhun)
    guihun_diff = set(hex_guihun) ^ set(rules_guihun)
    
    if youhun_diff:
        add_issue("P1", "数据一致性", f"游魂卦不一致: {youhun_diff}",
                 f"hex有但rules无: {set(hex_youhun)-set(rules_youhun)}, "
                 f"rules有但hex无: {set(rules_youhun)-set(hex_youhun)}")
    
    if guihun_diff:
        add_issue("P1", "数据一致性", f"归魂卦不一致: {guihun_diff}",
                 f"hex有但rules无: {set(hex_guihun)-set(rules_guihun)}, "
                 f"rules有但hex无: {set(rules_guihun)-set(hex_guihun)}")
    
    print(f"  ✓ 游魂/归魂一致性检查完成")

def check_interpret_shihua(hexagrams_data, yongshen_data):
    print("\n=== 检查世应位置逻辑 ===")
    hexagrams = hexagrams_data.get("hexagrams", {})
    
    # 正确的世应规则
    SHI_YING_RULES = {
        "本宫首卦": (5, 2),
        "一世卦":   (0, 3),
        "二世卦":   (1, 4),
        "三世卦":   (2, 5),
        "四世卦":   (3, 0),
        "五世卦":   (4, 1),
        "游魂卦":   (3, 0),
        "归魂卦":   (2, 5),
    }
    YAO_NAMES = ["初爻", "二爻", "三爻", "四爻", "五爻", "上爻"]
    
    # 从hexagrams的position字段验证
    for key, info in hexagrams.items():
        pos = info.get("position", "")
        name = info.get("name", "")
        if pos not in SHI_YING_RULES:
            add_issue("P1", "世应位置", f"position='{pos}'不在已知规则中", f"卦名={name}")
    
    # 检查代码中的position_map
    code_path = os.path.join(SCRIPT_DIR, "liuyao_interpret.py")
    with open(code_path, "r", encoding="utf-8") as f:
        code = f.read()
    
    for pos, (shi, ying) in SHI_YING_RULES.items():
        shi_name = YAO_NAMES[shi]
        ying_name = YAO_NAMES[ying]
        expected_str = f'"{pos}": {{"shi": {shi}, "ying": {ying}}}'
        if expected_str not in code:
            add_issue("P1", "代码逻辑", f"get_shi_ying()中{pos}世应位置可能错误",
                     f"期望: {expected_str}")
    
    print(f"  ✓ 世应位置检查完成")

def print_summary():
    print("\n" + "="*60)
    print("问题汇总")
    print("="*60)
    
    total = len(ISSUES)
    print(f"\n总计: {total}个问题")
    
    for level in ["P0", "P1", "P2"]:
        issues = [i for i in ISSUES if i["level"] == level]
        if issues:
            print(f"\n【{level}级】{len(issues)}个:")
            for i, issue in enumerate(issues, 1):
                print(f"  {i}. [{issue['category']}] {issue['message']}")
                if issue["detail"]:
                    lines = issue["detail"].split("\n")
                    for line in lines[:5]:
                        print(f"     → {line[:120]}")
    
    if not ISSUES:
        print("\n✓ 未发现明显问题！")
    
    return total

if __name__ == "__main__":
    hexagrams_data, naga_data, yongshen_data = load_data()
    
    check_hexagrams(hexagrams_data)
    check_naga(naga_data)
    check_yongshen_rules(yongshen_data)
    check_yongshen_logic(hexagrams_data, yongshen_data)
    check_liushou_consistency(hexagrams_data, yongshen_data)
    check_interpret_shihua(hexagrams_data, yongshen_data)
    
    total = print_summary()
    
    # 导出JSON
    out_path = os.path.join(DATA_DIR, "..", "scripts", "validate_issues.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump({"total": total, "issues": ISSUES}, f, ensure_ascii=False, indent=2)
    print(f"\n已导出: {out_path}")
    
    sys.exit(0 if total == 0 else 1)
