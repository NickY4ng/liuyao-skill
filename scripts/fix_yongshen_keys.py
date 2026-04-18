#!/usr/bin/env python3
"""
修复 liuyao_interpret.py 中的 get_yongshen() 函数

问题：get_yongshen() 使用了 yongshen_rules.json 中不存在的 keys
导致大量问题类型返回错误的用神（fallback 到官鬼爻）

修复：使用 yongshen_rules.json 中实际存在的 keys
"""

import json
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(SCRIPT_DIR, "..", "data")
INTERPRET_PATH = os.path.join(SCRIPT_DIR, "liuyao_interpret.py")

def load_rules():
    with open(os.path.join(DATA_DIR, "yongshen_rules.json"), "r", encoding="utf-8") as f:
        return json.load(f)["yongshen_lookup"]

def get_fix():
    """
    返回修复后的 get_yongshen 函数代码
    """
    fix = '''    def get_yongshen(self) -> Dict:
        """获取用神
        
        根据问题类型匹配最合适的用神规则
        """
        question = self.question
        rules = self.yongshen_rules.get("yongshen_lookup", {})
        
        # 优先精确匹配（含关键词最多的）
        # 如果精确匹配失败，再使用模糊匹配
        
        # 1. 测婚姻（男占财，女占官）- 用"婚姻-问婚姻状况"兜底
        if any(k in question for k in ["婚", "感情", "恋爱", "对象", "复合", "离婚"]):
            if "复合" in question:
                return rules.get("婚姻-问复合", rules.get("婚姻-问婚期", {}))
            elif "离婚" in question:
                return rules.get("婚姻-问离婚", {})
            elif "对象" in question or "恋爱" in question:
                return rules.get("婚姻-问对象", rules.get("婚姻-问婚期", {}))
            elif "感情纠葛" in question:
                return rules.get("感情-感情纠葛", {})
            elif "感情" in question:
                return rules.get("感情-恋爱发展", rules.get("婚姻-问婚姻状况", {}))
            else:
                return rules.get("婚姻-问婚姻状况", {})
        
        # 2. 测健康/疾病
        if any(k in question for k in ["健康", "疾病", "身体", "病", "康复", "体检"]):
            if "体检" in question:
                return rules.get("健康-问体检", {})
            elif "康复" in question:
                return rules.get("健康-问康复", {})
            elif "疾病" in question or "病" in question:
                return rules.get("健康-问疾病", {})
            else:
                return rules.get("健康-问疾病", {})
        
        # 3. 测考试/学业
        if any(k in question for k in ["考试", "学业", "学习", "升学", "选课"]):
            if "升学" in question:
                return rules.get("学业-升学", {})
            elif "选课" in question:
                return rules.get("学业-选课", {})
            elif "学业" in question or "学习" in question:
                return rules.get("学业-考试", {})
            else:
                return rules.get("学业-考试", {})
        
        # 4. 测出行
        if any(k in question for k in ["出行", "旅游", "出差", "旅行"]):
            return rules.get("出行", {})
        
        # 5. 测官司诉讼
        if any(k in question for k in ["官司", "诉讼"]):
            return rules.get("官司诉讼", {})
        
        # 6. 测房屋住宅
        if any(k in question for k in ["买房", "卖房", "房子", "住宅", "租房", "装修"]):
            if "租" in question:
                return rules.get("房屋-租房", {})
            elif "装修" in question:
                return rules.get("房屋-装修", {})
            elif "买" in question:
                return rules.get("房屋-买房", {})
            else:
                return rules.get("房屋-买房", {})
        
        # 7. 测父母
        if any(k in question for k in ["父母", "爸", "妈", "父亲", "母亲", "长辈"]):
            return rules.get("测父母", {})
        
        # 8. 测子嗣/子女
        if any(k in question for k in ["子女", "孩子", "儿", "孙", "生子", "怀孕"]):
            return rules.get("测子嗣", {})
        
        # 9. 求财生意（核心财运类）
        if any(k in question for k in ["财", "生意", "赚钱", "收入", "工资", "投资", "借贷", "讨债"]):
            if "投资" in question:
                return rules.get("求财-投资求财", {})
            elif "工资" in question or "收入" in question:
                return rules.get("求财-工资收入", {})
            elif "生意" in question or "买卖" in question:
                return rules.get("求财-生意买卖", {})
            elif "借贷" in question or "讨债" in question:
                return rules.get("求财-借贷讨债", {})
            else:
                return rules.get("求财-财运走势", {})
        
        # 10. 测工作/官运
        if any(k in question for k in ["工作", "事业", "官运", "晋升", "求职", "跳槽", "创业", "离职"]):
            if "求职" in question:
                return rules.get("工作-求职", {})
            elif "跳槽" in question:
                return rules.get("工作-跳槽", {})
            elif "晋升" in question or "升职" in question:
                return rules.get("工作-晋升", {})
            elif "创业" in question:
                return rules.get("工作-创业", {})
            elif "离职" in question:
                return rules.get("工作-离职", {})
            elif "职场" in question or "人际" in question:
                return rules.get("工作-职场人际", {})
            elif "官运" in question or "仕途" in question:
                return rules.get("工作-官运仕途", {})
            else:
                return rules.get("工作-官运仕途", {})
        
        # 11. 测流年运势
        if any(k in question for k in ["流年", "运势", "今年运气", "明年运气"]):
            return rules.get("测流年运势", {})
        
        # 12. 测合作
        if any(k in question for k in ["合作", "合伙"]):
            return rules.get("测合作", {})
        
        # 13. 测竞争
        if any(k in question for k in ["竞争", "竞争对手"]):
            return rules.get("测竞争", {})
        
        # 14. 失物
        if any(k in question for k in ["失物", "丢东西", "丢失", "寻物"]):
            if "人" in question or "宠物" in question:
                return rules.get("失物-寻人或宠物", {})
            else:
                return rules.get("失物-寻物", {})
        
        # 15. 天气
        if any(k in question for k in ["天气", "下雨", "晴天", "气温"]):
            return rules.get("天气", {})
        
        # 默认：测工作官运（最常见场景）
        return rules.get("工作-官运仕途", {"primary": "官鬼爻", "secondary": [], "note": ""})
'''

    return fix

def apply_fix():
    """应用修复到 liuyao_interpret.py"""
    
    with open(INTERPRET_PATH, "r", encoding="utf-8") as f:
        content = f.read()
    
    # 找到get_yongshen函数的开始和结束
    import re
    
    # 找到旧的get_yongshen函数
    old_func_pattern = r'(    def get_yongshen\(self\) -> Dict:.*?)(?=\n    def \w+\(self)'
    match = re.search(old_func_pattern, content, re.DOTALL)
    
    if not match:
        print("错误：无法找到 get_yongshen 函数")
        return False
    
    old_func = match.group(1)
    new_func = get_fix()
    
    # 替换
    new_content = content.replace(old_func, new_func)
    
    if new_content == content:
        print("错误：替换后内容相同，可能函数已经修复过")
        return False
    
    # 备份
    backup_path = INTERPRET_PATH + ".bak"
    with open(backup_path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"已备份原文件到: {backup_path}")
    
    # 写入修复后的文件
    with open(INTERPRET_PATH, "w", encoding="utf-8") as f:
        f.write(new_content)
    
    print(f"已修复: {INTERPRET_PATH}")
    return True

def test_fix():
    """测试修复后的 get_yongshen"""
    import sys
    sys.path.insert(0, SCRIPT_DIR)
    
    # 重新加载模块
    import importlib
    import liuyao_interpret
    importlib.reload(liuyao_interpret)
    
    interp = liuyao_interpret.LiuYaoInterpreter()
    
    test_cases = [
        ("我想投资生意", "妻财"),
        ("最近财运怎么样", "妻财"),
        ("问下婚姻状况", "妻财"),
        ("工作怎么样", "官鬼"),
        ("身体健康吗", "子孙"),
        ("孩子的情况", "子孙"),
        ("考试能过吗", "父母"),
        ("出行注意事项", "世爻"),
        ("跳槽怎么样", "官鬼"),
        ("创业行不行", "妻财"),
        ("今年运势如何", "世爻"),
    ]
    
    print("\n=== 测试修复后的 get_yongshen ===")
    all_pass = True
    for question, expected_keyword in test_cases:
        interp.question = question
        result = interp.get_yongshen()
        actual_primary = result.get("primary", "")
        ok = expected_keyword in actual_primary
        status = "✓" if ok else "✗"
        if not ok:
            all_pass = False
        print(f"  {status} '{question}' → {actual_primary} (期望含'{expected_keyword}')")
    
    return all_pass

if __name__ == "__main__":
    import sys
    
    print("=== 修复 get_yongshen ===")
    
    if apply_fix():
        print("\n修复成功！")
        if test_fix():
            print("\n✓ 所有测试通过")
            sys.exit(0)
        else:
            print("\n✗ 部分测试失败")
            sys.exit(1)
    else:
        print("\n✗ 修复失败")
        sys.exit(1)
