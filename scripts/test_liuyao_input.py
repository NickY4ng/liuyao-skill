#!/usr/bin/env python3
"""
六爻交互式起卦 - 测试用例
测试表情/文字识别逻辑
"""

import sys
import os

# 添加脚本目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from liuyao_interactive import is_emoji, is_text, clear_session

# 测试用例
test_cases = [
    # (输入, 期望is_emoji结果, 期望is_text结果, 说明)
    
    # 纯表情 - 应继续摇卦
    ("👍", True, False, "单一emoji"),
    ("🌕", True, False, "月亮emoji（阳）"),
    ("🌑", True, False, "月亮emoji（阴）"),
    ("🌕🌑🌑", True, False, "多个emoji连续"),
    ("🌕 🌑 🌑", True, False, "多个emoji带空格"),
    ("🎲", True, False, "骰子emoji"),
    ("👆", True, False, "手指emoji"),
    ("✅", True, False, "对勾emoji"),
    ("❤️", True, False, "心形emoji"),
    ("😀", True, False, "笑脸emoji"),
    ("🙏", True, False, "双手emoji"),
    ("☀️", True, False, "太阳emoji"),
    ("⭐️", True, False, "星星emoji"),
    
    # 纯文字 - 应打断流程
    ("OK", False, True, "英文OK"),
    ("好的", False, True, "中文"),
    ("开始", False, True, "中文"),
    ("继续", False, True, "中文"),
    ("[OK]", False, True, "带括号的OK"),
    ("yes", False, True, "英文yes"),
    ("YES", False, True, "英文YES"),
    ("1", False, True, "数字"),
    ("123", False, True, "多个数字"),
    ("第3次", False, True, "中文+数字"),
    ("起卦", False, True, "触发词"),
    ("算一卦", False, True, "触发词"),
    
    # 混合内容 - 应视为文字（打断流程）
    ("好的👍", False, True, "中文+emoji（混合）"),
    ("👍好的", False, True, "emoji+中文（混合）"),
    ("OK👍", False, True, "英文+emoji（混合）"),
    ("👍OK", False, True, "emoji+英文（混合）"),
    ("继续🎲", False, True, "中文+emoji（混合）"),
    ("🌕开始", False, True, "emoji+中文（混合）"),
    
    # 边界情况
    ("", False, False, "空字符串"),
    ("   ", False, False, "纯空格"),
    ("  👍  ", True, False, "emoji带前后空格"),
    ("  OK  ", False, True, "文字带前后空格"),
]

def run_tests():
    """运行测试"""
    print("=" * 60)
    print("六爻交互式起卦 - 输入识别测试")
    print("=" * 60)
    print()
    
    passed = 0
    failed = 0
    
    for text, expected_emoji, expected_text, description in test_cases:
        result_emoji = is_emoji(text)
        result_text = is_text(text)
        
        emoji_ok = result_emoji == expected_emoji
        text_ok = result_text == expected_text
        
        status = "✅ PASS" if (emoji_ok and text_ok) else "❌ FAIL"
        
        if not (emoji_ok and text_ok):
            failed += 1
            print(f"{status} | {description}")
            print(f"       输入: '{text}'")
            print(f"       期望: is_emoji={expected_emoji}, is_text={expected_text}")
            print(f"       实际: is_emoji={result_emoji}, is_text={result_text}")
            print()
        else:
            passed += 1
            # print(f"{status} | {description}: '{text}'")  # 静默模式，只显示失败
    
    print("-" * 60)
    print(f"测试结果: {passed} 通过, {failed} 失败")
    print("-" * 60)
    
    if failed > 0:
        print("❌ 测试未通过，请检查修复逻辑")
        return 1
    else:
        print("✅ 所有测试通过！")
        return 0

def test_flow_interruption():
    """测试流程打断场景"""
    print()
    print("=" * 60)
    print("流程打断场景测试")
    print("=" * 60)
    print()
    
    # 模拟场景
    scenarios = [
        ("用户发 [OK]", "[OK]", "应打断"),
        ("用户发 好的", "好的", "应打断"),
        ("用户发 👍", "👍", "应继续"),
        ("用户发 好的👍", "好的👍", "应打断"),
        ("用户发 🌕🌕🌕", "🌕🌕🌕", "应继续"),
    ]
    
    for desc, text, expected in scenarios:
        is_e = is_emoji(text)
        is_t = is_text(text)
        action = "继续摇卦" if is_e else "打断流程"
        match = "✅" if (is_e and "继续" in expected) or (is_t and "打断" in expected) else "❌"
        print(f"{match} {desc} → {action} (期望: {expected})")
    
    print()

if __name__ == "__main__":
    # 先清空前次会话状态
    clear_session()
    
    # 运行测试
    exit_code = run_tests()
    test_flow_interruption()
    
    sys.exit(exit_code)
