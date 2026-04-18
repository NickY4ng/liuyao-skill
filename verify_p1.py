#!/usr/bin/env python3
"""快速验证P1功能"""
import sys
sys.path.insert(0, '/Users/nickyang/.openclaw/skills/liuyao-skill/scripts')

from liuyao_interpret import LiuYaoInterpreter

# 验证六神
print("=== 六神验证 ===")
i = LiuYaoInterpreter()

# 甲日应初爻青龙
i.set_day_gan("甲")
print(f"甲日初爻六神: {i.get_liushou_for_yao(0)} (应为青龙)")

# 壬日应初爻玄武  
i.set_day_gan("壬")
print(f"壬日初爻六神: {i.get_liushou_for_yao(0)} (应为玄武)")

# 验证完整解读
print("\n=== 完整解读验证（前80行）===")
test_input = """我这份工作能做长久吗？
上爻：少阳
五爻：老阳动
四爻：少阴
三爻：少阳
二爻：少阳
初爻：少阴"""

result = i.interpret(test_input)
for line in result.split('\n')[:80]:
    print(line)

print("\n... (截断)")
print("\n=== 验证完成 ===")
