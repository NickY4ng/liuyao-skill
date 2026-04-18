#!/usr/bin/env python3
"""
六爻Skill P1功能测试脚本
测试：六神系统 + 旺衰判断增强
"""

import sys
sys.path.insert(0, '/Users/nickyang/.openclaw/skills/liuyao-skill/scripts')

from liuyao_interpret import LiuYaoInterpreter

def test_liushou():
    """测试六神系统"""
    print("=" * 50)
    print("【测试1】六神系统")
    print("=" * 50)
    
    interpreter = LiuYaoInterpreter()
    
    # 测试不同天干日的六神起始
    test_cases = [
        ("甲", "青龙起"),
        ("乙", "青龙起"),
        ("丙", "朱雀起"),
        ("丁", "朱雀起"),
        ("戊", "勾陈起"),
        ("己", "螣蛇起"),
        ("庚", "白虎起"),
        ("辛", "白虎起"),
        ("壬", "玄武起"),
        ("癸", "玄武起"),
    ]
    
    print("\n1. 测试天干与六神起始对应：")
    for gan, expected_start in test_cases:
        interpreter.set_day_gan(gan)
        chuyao_liushou = interpreter.get_liushou_for_yao(0)  # 初爻六神
        print(f"   {gan}日 → 初爻{chuyao_liushou}（应{expected_start}）")
        
        # 验证六神顺序
        liushou_list = [interpreter.get_liushou_for_yao(i) for i in range(6)]
        print(f"      六神顺序：{' → '.join(liushou_list)}")
    
    print("\n2. 测试当前日期自动获取天干：")
    gan, zhi = interpreter.get_current_day_gan_zhi()
    print(f"   今天是 {gan}{zhi}日")
    interpreter.set_day_gan(gan)
    print(f"   六神从{interpreter.get_liushou_for_yao(0)}开始")

def test_wangshuai():
    """测试旺衰判断增强"""
    print("\n" + "=" * 50)
    print("【测试2】旺衰判断增强")
    print("=" * 50)
    
    # 测试用例：水地比卦，财爻持世，问财运
    test_input = """我最近财运如何？
上爻：少阳
五爻：少阴
四爻：少阴
三爻：少阴
二爻：少阳动
初爻：少阳动"""
    
    interpreter = LiuYaoInterpreter()
    
    print("\n测试输入：")
    print(test_input)
    print("\n" + "-" * 50)
    
    # 解析输入
    success = interpreter.parse_input(test_input)
    print(f"\n解析结果：{'成功' if success else '失败'}")
    
    if success:
        # 查找卦象
        interpreter.hexagram = interpreter.find_hexagram()
        print(f"卦名：{interpreter.hexagram.get('name', '?')}")
        print(f"卦宫：{interpreter.hexagram.get('gong', '?')}")
        
        # 测试旺衰分析
        wangshuai = interpreter.analyze_wangshuai(interpreter.hexagram)
        
        print(f"\n月令：{wangshuai['month_zhi']}月（{wangshuai['yueling_wangxiang']}）")
        print(f"日建：{wangshuai['day_gan_zhi']}日")
        print(f"用神：{wangshuai['yongshen']}")
        
        print("\n用神旺衰分析：")
        for analysis in wangshuai['yongshen_analysis']:
            print(f"  - {analysis['yao_name']}（{analysis['liuqin']}·{analysis['zhi']}·{analysis['wuxing']}）")
            print(f"    旺衰：{analysis['overall']}")
            print(f"    依据：{analysis['basis']}")
            if analysis.get('is_dong'):
                print(f"    状态：动爻")
        
        print("\n动爻影响：")
        for effect in wangshuai['dong_yao_effects']:
            print(f"  - {effect['effect']}")

def test_full_interpretation():
    """测试完整解读输出"""
    print("\n" + "=" * 50)
    print("【测试3】完整解读输出")
    print("=" * 50)
    
    # 测试用例：火天大有卦，问事业
    test_input = """我这份工作能做长久吗？
上爻：老阳动
五爻：少阳
四爻：少阴
三爻：少阳
二爻：少阳
初爻：少阴"""
    
    interpreter = LiuYaoInterpreter()
    result = interpreter.interpret(test_input)
    
    print(result)

def main():
    print("六爻Skill P1功能测试")
    print("=" * 50)
    
    test_liushou()
    test_wangshuai()
    test_full_interpretation()
    
    print("\n" + "=" * 50)
    print("测试完成！")
    print("=" * 50)

if __name__ == "__main__":
    main()
