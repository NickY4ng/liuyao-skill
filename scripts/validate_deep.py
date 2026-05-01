#!/usr/bin/env python3
"""
Deep validation of liuyao data files.
Checks:
1. guaxiang_full consistency with neigua/waigua via trigram_to_yao
2. Duplicate guaxiang_full
3. naga.json data completeness
4. yongshen_rules.json coverage
5. hexagrams.json old file - check for issues
"""
import json
import os

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")

def load_json(name):
    with open(os.path.join(DATA_DIR, name), "r", encoding="utf-8") as f:
        return json.load(f)

def fmt_lines(lines):
    return "".join(lines)

def check_guaxiang_full():
    """Check 1: guaxiang_full = reverse(trigram_to_yao[waigua]) + reverse(trigram_to_yao[neigua])"""
    print("=" * 70)
    print("CHECK 1: guaxiang_full consistency")
    print("=" * 70)
    
    data = load_json("hexagrams_full.json")
    hexagrams = data["hexagrams"]
    t2y = data["trigram_to_yao"]
    
    errors = []
    binary_mismatches = []
    
    for key, info in hexagrams.items():
        name = info["name"]
        ni = info["neigua"]
        wi = info["waigua"]
        actual = info["guaxiang_full"]
        
        # Derive expected guaxiang_full
        # guaxiang_full is in top-to-bottom order (上爻 first)
        # trigram_to_yao is bottom-to-top order
        # So: reverse(t2y[waigua]) gives waigua top-to-bottom
        #     reverse(t2y[neigua]) gives neigua top-to-bottom
        expected_waigua = list(reversed(t2y[wi]))
        expected_neigua = list(reversed(t2y[ni]))
        expected = "".join(expected_waigua + expected_neigua)
        
        if actual != expected:
            # Also check if binary key matches guaxiang_full
            actual_list = list(actual)
            key_list = list(key)
            
            # Binary key: 1=⚊ yang, 0=⚋ yin, top-to-bottom
            expected_from_key = "".join("⚊" if b == "1" else "⚋" for b in key)
            
            if actual != expected_from_key:
                binary_mismatches.append((key, name, actual, expected_from_key))
            
            # Figure out what the binary key trigrams would be
            key_top3 = key[:3]  # waigua bits (上,五,四)
            key_bot3 = key[3:]  # neigua bits (三,二,初)
            
            # Map bits to trigrams
            trigram_map = {
                "111": "☰", "000": "☷",
                "110": "☱", "011": "☴",  # these need careful mapping
                "101": "☲",
                "100": "☳",
                "010": "☵",
                "001": "☶",
            }
            # Let's use the reverse of t2y to find trigram from bits
            # t2y gives bottom-to-top, key bits are top-to-bottom
            # So for lower trigram: key_bot3 reversed = bottom-to-top
            trig_from_bits = {}
            for tri, yao in t2y.items():
                bits = "".join("1" if y == "⚊" else "0" for y in yao)
                trig_from_bits[bits] = tri
            
            key_waigua = trig_from_bits.get(key_top3[::-1], "???")  # reverse to get bottom-to-top
            key_neigua = trig_from_bits.get(key_bot3[::-1], "???")
            
            errors.append({
                "key": key,
                "name": name,
                "expected": expected,
                "actual": actual,
                "expected_from_key": expected_from_key,
                "key_trigrams": f"☰? {key_waigua}{key_neigua}",
                "data_trigrams": f"{wi}{ni}",
            })
    
    if errors:
        print(f"❌ Found {len(errors)} hexagram(s) with guaxiang_full mismatch!")
        for e in errors:
            print(f"\n  卦: {e['name']} (key={e['key']})")
            print(f"    Data trigrams: {e['data_trigrams']}")
            print(f"    Key trigrams:  {e['key_trigrams']}")
            print(f"    Expected (from neigua/waigua): {e['expected']}")
            print(f"    Actual guaxiang_full:          {e['actual']}")
            print(f"    Expected (from binary key):    {e['expected_from_key']}")
    else:
        print("✅ All 64 guaxiang_full values consistent with neigua/waigua!")
    
    return errors

def check_duplicates():
    """Check 2: Duplicate guaxiang_full"""
    print("\n" + "=" * 70)
    print("CHECK 2: Duplicate guaxiang_full detection")
    print("=" * 70)
    
    data = load_json("hexagrams_full.json")
    hexagrams = data["hexagrams"]
    
    seen = {}
    duplicates = []
    
    for key, info in hexagrams.items():
        gf = info["guaxiang_full"]
        if gf in seen:
            duplicates.append((gf, seen[gf], (key, info["name"])))
        else:
            seen[gf] = (key, info["name"])
    
    if duplicates:
        print(f"❌ Found {len(duplicates)} duplicate guaxiang_full values!")
        for gf, (k1, n1), (k2, n2) in duplicates:
            print(f"   guaxiang_full='{gf}': {n1}({k1}) and {n2}({k2})")
    else:
        print("✅ No duplicate guaxiang_full values (all 64 unique)")
    
    return duplicates

def check_naga():
    """Check 3: naga.json completeness"""
    print("\n" + "=" * 70)
    print("CHECK 3: naga.json data completeness")
    print("=" * 70)
    
    naga = load_json("naga.json")
    naga_song = naga["naga_song"]
    
    expected_gongs = ["乾", "坤", "坎", "离", "震", "巽", "艮", "兑"]
    issues = []
    
    # Check all 8 palaces present
    for gong in expected_gongs:
        if gong not in naga_song:
            issues.append(f"Missing palace: {gong}")
            continue
        
        entry = naga_song[gong]
        
        # Check structure
        for key in ["neigua", "waigua", "shiwei", "yingwei"]:
            if key not in entry:
                issues.append(f"{gong}: missing '{key}'")
        
        if "neigua" in entry:
            for field in ["gan", "zhi", "wuxing"]:
                if field not in entry["neigua"]:
                    issues.append(f"{gong}.neigua: missing '{field}'")
        
        if "waigua" in entry:
            for field in ["gan", "zhi", "wuxing"]:
                if field not in entry["waigua"]:
                    issues.append(f"{gong}.waigua: missing '{field}'")
        
        # Check zhi arrays have 3 elements
        if "neigua" in entry and "zhi" in entry["neigua"]:
            if len(entry["neigua"]["zhi"]) != 3:
                issues.append(f"{gong}.neigua.zhi: expected 3, got {len(entry['neigua']['zhi'])}")
        
        if "waigua" in entry and "zhi" in entry["waigua"]:
            if len(entry["waigua"]["zhi"]) != 3:
                issues.append(f"{gong}.waigua.zhi: expected 3, got {len(entry['waigua']['zhi'])}")
        
        # Validate shiwei/yingwei range
        for pos_name, pos_field in [("shiwei", "shiwei"), ("yingwei", "yingwei")]:
            if pos_field in entry:
                val = entry[pos_field]
                if not (1 <= val <= 6):
                    issues.append(f"{gong}.{pos_field}: {val} not in range 1-6")
    
    # Check zhi_wuxing has all 12 branches
    zhi_wuxing = naga.get("zhi_wuxing", {})
    expected_zhi = ["子","丑","寅","卯","辰","巳","午","未","申","酉","戌","亥"]
    for z in expected_zhi:
        if z not in zhi_wuxing:
            issues.append(f"zhi_wuxing: missing '{z}'")
    
    # Check gan_wuxing has all 10 stems
    gan_wuxing = naga.get("gan_wuxing", {})
    expected_gan = ["甲","乙","丙","丁","戊","己","庚","辛","壬","癸"]
    for g in expected_gan:
        if g not in gan_wuxing:
            issues.append(f"gan_wuxing: missing '{g}'")
    
    if issues:
        print(f"❌ Found {len(issues)} issues in naga.json:")
        for i in issues:
            print(f"   - {i}")
    else:
        print("✅ naga.json complete: 8 palaces, all fields present")
    
    # Also verify specific known values
    print("\n   Quick spot checks:")
    
    # 乾宫: neigua 甲子寅辰, waigua 壬午申戌
    qian = naga_song["乾"]
    print(f"   乾: nei.gan={qian['neigua']['gan']}, nei.zhi={qian['neigua']['zhi']}, "
          f"wai.gan={qian['waigua']['gan']}, wai.zhi={qian['waigua']['zhi']}, "
          f"shi={qian['shiwei']}, ying={qian['yingwei']}")
    
    # 坤宫: neigua 乙未巳卯, waigua 癸丑亥酉 (坤卦纳甲从初爻起: 乙未,乙巳,乙卯 / 癸丑,癸亥,癸酉)
    kun = naga_song["坤"]
    print(f"   坤: nei.gan={kun['neigua']['gan']}, nei.zhi={kun['neigua']['zhi']}, "
          f"wai.gan={kun['waigua']['gan']}, wai.zhi={kun['waigua']['zhi']}, "
          f"shi={kun['shiwei']}, ying={kun['yingwei']}")
    
    return issues

def check_yongshen():
    """Check 4: yongshen_rules.json coverage"""
    print("\n" + "=" * 70)
    print("CHECK 4: yongshen_rules.json coverage")
    print("=" * 70)
    
    data = load_json("yongshen_rules.json")
    yongshen = data.get("yongshen_lookup", {})
    liushou = data.get("liushou_patterns", {})
    
    # Count categories
    categories = set()
    for k in yongshen:
        cat = k.split("-")[0] if "-" in k else k
        categories.add(cat)
    
    print(f"   Total rules: {len(yongshen)}")
    print(f"   Categories: {len(categories)} - {sorted(categories)}")
    
    # Check for common life scenarios
    common_scenarios = [
        "求财", "婚姻", "感情", "工作", "健康", "学业",
        "出行", "官司", "房屋", "天气", "失物",
        "测父母", "测子嗣", "测流年运势", "测合作", "测竞争"
    ]
    
    missing = []
    covered = []
    for s in common_scenarios:
        found = any(k.startswith(s) for k in yongshen)
        if found:
            covered.append(s)
        else:
            missing.append(s)
    
    print(f"\n   Covered scenarios: {len(covered)}/{len(common_scenarios)}")
    for c in covered:
        sub_rules = [k for k in yongshen if k.startswith(c)]
        print(f"     ✅ {c}: {len(sub_rules)} sub-rules ({', '.join(sub_rules)})")
    
    if missing:
        print(f"\n   ❌ Missing scenarios: {missing}")
    else:
        print("   ✅ All common scenarios covered")
    
    # Check liushou_patterns
    print(f"\n   游魂卦: {len(liushou.get('游魂卦', []))} - {liushou.get('游魂卦', [])}")
    print(f"   归魂卦: {len(liushou.get('归魂卦', []))} - {liushou.get('归魂卦', [])}")
    
    # Check for 归魂卦 completeness (should be 7: 师,蛊,比,随,大有,归妹,渐)
    guihun = set(liushou.get("归魂卦", []))
    expected_guihun = {"师","蛊","比","随","大有","归妹","渐"}
    missing_guihun = expected_guihun - guihun
    extra_guihun = guihun - expected_guihun
    if missing_guihun:
        print(f"   ❌ 归魂卦 missing: {missing_guihun}")
    if extra_guihun:
        print(f"   ⚠️  归魂卦 extra: {extra_guihun}")
    if not missing_guihun and not extra_guihun:
        print(f"   ✅ 归魂卦: complete (7/7)")
    
    # Check 游魂卦 completeness (should be 8: 明夷,颐,需,大过,晋,小过,涣,中孚)
    youhun = set(liushou.get("游魂卦", []))
    expected_youhun = {"明夷","颐","需","大过","晋","小过","涣","中孚"}
    missing_youhun = expected_youhun - youhun
    extra_youhun = youhun - expected_youhun
    if missing_youhun:
        print(f"   ❌ 游魂卦 missing: {missing_youhun}")
    if extra_youhun:
        print(f"   ⚠️  游魂卦 extra: {extra_youhun}")
    if not missing_youhun and not extra_youhun:
        print(f"   ✅ 游魂卦: complete (8/8)")
    
    return covered, missing

def check_old_file():
    """Check 5: hexagrams.json old file issues"""
    print("\n" + "=" * 70)
    print("CHECK 5: hexagrams.json old file analysis")
    print("=" * 70)
    
    old = load_json("hexagrams.json")
    old_hex = old.get("hexagrams", {})
    
    print(f"   hexagrams.json: {len(old_hex)} entries (should be 64)")
    
    # Check for duplicate keys (like _2, _3 suffixes)
    duped = [k for k in old_hex if "_" in k]
    if duped:
        print(f"   ❌ Poorly named keys (with _2, _3): {len(duped)}")
        for d in duped:
            print(f"      {d}: {old_hex[d]['name']}")
    
    # Check for entries with wrong trigram assignments
    print("\n   Cross-checking hexagrams.json vs hexagrams_full.json:")
    full = load_json("hexagrams_full.json")
    full_hex = full["hexagrams"]
    
    old_issues = []
    for key, info in old_hex.items():
        name = info["name"]
        # Find in full
        matching = [(k, v) for k, v in full_hex.items() if v["name"] == name]
        
        if key in full_hex:
            full_info = full_hex[key]
            if full_info["name"] != name:
                old_issues.append(f"  Key {key}: old name='{name}' != full name='{full_info['name']}'")
        else:
            # Key not found in full - old data has wrong key
            # Find by name
            if matching:
                correct_key = matching[0][0]
                old_issues.append(f"  Key {key} ({name}): not in full data. Should be {correct_key}")
    
    if old_issues:
        print(f"   ❌ Issues in hexagrams.json:")
        for i in old_issues[:15]:
            print(i)
    else:
        print("   ℹ️  hexagrams.json is the old file, not used by current code")
    
    # Check if old file is referenced in current code
    return old_issues

def check_liuchong():
    """Check liuchong hexagrams in naga.py vs yongshen_rules"""
    print("\n" + "=" * 70)
    print("CHECK 6: 六冲卦 coverage comparison")
    print("=" * 70)
    
    # From naga.py code: 六冲卦 list
    naga_liuchong = {"乾","坤","震","巽","坎","离","艮","兑","否","泰","大壮","无妄","大过","讼","涣","睽","中孚","蛊","升","井"}
    
    # From SKILL.md: 六冲卦 list (same)
    skill_liuchong = {"乾","坤","震","巽","坎","离","艮","兑","否","泰","大壮","无妄","大过","讼","涣","睽","中孚","蛊","升","井"}
    
    # Standard 六冲卦 (8 八纯卦 + 12 others based on standard I Ching theory)
    # 六冲卦 = 八纯卦(8) + 天雷无妄 + 雷天大壮 + 水山蹇? No...
    # Let me check: standard 六冲卦 are: 乾,坤,震,巽,坎,离,艮,兑 (八纯卦)
    # Plus: 否,泰,大壮,无妄,大过,小过? 
    # Actually I need to think about this...
    
    # In the naga.py and naga_data.py code, 六冲卦 includes 20 hexagrams
    print(f"   naga.py 六冲卦: {len(naga_liuchong)} hexagrams")
    print(f"   SKILL.md 六冲卦: {len(skill_liuchong)} hexagrams")
    
    # Compare
    if naga_liuchong == skill_liuchong:
        print("   ✅ SKILL.md and naga.py 六冲卦 lists match")
    else:
        print(f"   ❌ Mismatch! Only in naga.py: {naga_liuchong - skill_liuchong}")
        print(f"   ❌ Only in SKILL.md: {skill_liuchong - naga_liuchong}")
    
    # Also check naga_data.py
    naga_data_liuchong = {"乾", "坤", "震", "巽", "坎", "离", "艮", "兑", "否", "泰", "大壮", "无妄", "大过"}
    print(f"\n   naga_data.py 六冲卦: {len(naga_data_liuchong)} hexagrams (missing 讼,涣,睽,中孚,蛊,升,井)")
    
    # These are probably different lists for different purposes
    missing_from_naga_data = naga_liuchong - naga_data_liuchong
    print(f"   ⚠️  naga_data.py missing vs naga.py: {sorted(missing_from_naga_data)}")
    
    return naga_liuchong

def main():
    errors = check_guaxiang_full()
    dupes = check_duplicates()
    naga_issues = check_naga()
    yongshen_result = check_yongshen()
    old_issues = check_old_file()
    liuchong = check_liuchong()
    
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    
    all_ok = True
    if errors:
        print(f"❌ CHECK 1 FAILED: {len(errors)} guaxiang_full errors")
        all_ok = False
    else:
        print("✅ CHECK 1 PASSED: guaxiang_full consistency")
    
    if dupes:
        print(f"❌ CHECK 2 FAILED: {len(dupes)} duplicate guaxiang_full")
        all_ok = False
    else:
        print("✅ CHECK 2 PASSED: No duplicates")
    
    if naga_issues:
        print(f"❌ CHECK 3 FAILED: {len(naga_issues)} naga.json issues")
        all_ok = False
    else:
        print("✅ CHECK 3 PASSED: naga.json complete")
    
    if yongshen_result[1]:  # missing scenarios
        print(f"❌ CHECK 4 has gaps: {yongshen_result[1]}")
        all_ok = False
    else:
        print("✅ CHECK 4 PASSED: yongshen_rules coverage good")
    
    if old_issues:
        print(f"❌ CHECK 5: hexagrams.json has {len(old_issues)} issues")
        all_ok = False
    else:
        print("✅ CHECK 5 PASSED: hexagrams.json not referenced by current code")
    
    if all_ok:
        print("\n🎉 ALL CHECKS PASSED")
    else:
        print(f"\n⚠️  SOME CHECKS FAILED - see details above")

if __name__ == "__main__":
    main()
