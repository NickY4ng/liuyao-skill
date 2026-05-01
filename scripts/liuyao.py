#!/usr/bin/env python3
"""
六爻占卜 Skill 入口
用法：
  python liuyao.py "最近财运如何" "少阳,少阴,老阳动,少阳,少阴,少阳"
  python liuyao.py "我这工作能不能升职" "老阴,少阳,少阳,少阴,老阳,少阴"
"""

import sys
import os

# yao 符号映射
YAO_MAP = {
    "少阳": "少阳", "老阳": "老阳", "少阴": "少阴", "老阴": "老阴",
    "老阳动": "老阳", "老阴动": "老阴", "动": "老阳",
    "阳": "少阳", "阴": "少阴",
    "1": "少阳", "2": "少阴", "3": "老阳", "4": "老阴",
    "1动": "老阳", "2动": "老阴", "3动": "老阳", "4动": "老阴",
    "⚊": "少阳", "☰": "老阳", "⚋": "少阴", "☱": "老阴",
}


def parse_yao(input_str):
    """
    解析爻输入字符串
    支持格式：
    - "少阳,少阴,老阳动,少阳,少阴,少阳"（逗号分隔）
    - "少阳 少阴 老阳动 少阳 少阴 少阳"（空格分隔）
    - "⚊⚋☰⚋⚊⚋"（符号串）
    """
    s = input_str.strip()
    # 如果是纯符号串（6个字符）
    if set(s.replace(" ", "").replace("☰", "阳").replace("☱", "阴").replace("⚊", "阳").replace("⚋", "阴")) <= {"阳", "阴"}:
        sym_to_yao = {"阳": "少阳" if s.count("☰") + s.count("⚊") == s.count("☰") + s.count("⚊") else "少阳",
                      "☰": "老阳", "☱": "老阴", "⚊": "少阳", "⚋": "少阴"}
        yaos = []
        for ch in s:
            if ch in ("☰", "老阳"):
                yaos.append("老阳")
            elif ch in ("☱", "老阴"):
                yaos.append("老阴")
            elif ch in ("⚊", "阳"):
                yaos.append("少阳")
            elif ch in ("⚋", "阴"):
                yaos.append("少阴")
        if len(yaos) == 6:
            return yaos

    # 逗号/空格分隔
    parts = [p.strip() for p in s.replace("，", ",").replace("、", ",").replace(" ", ",").split(",") if p.strip()]
    if len(parts) == 6:
        yaos = []
        for p in parts:
            if p in YAO_MAP:
                yaos.append(YAO_MAP[p])
            else:
                return None
        return yaos
    return None


def main():
    if len(sys.argv) < 3:
        print("用法: python liuyao.py '问题' '六个爻（逗号分隔）'")
        print()
        print("爻的表示：")
        print("  少阳 = 阳爻（不变）    老阳 = 阳爻（动，变阴）")
        print("  少阴 = 阴爻（不变）    老阴 = 阴爻（动，变阳）")
        print("  数字也可：1=少阳  2=少阴  3=老阳  4=老阴")
        print()
        print("示例:")
        print("  python liuyao.py '最近财运如何' '少阳,少阴,老阳,少阳,少阴,少阳'")
        print("  python liuyao.py '这项目能成吗' '1,2,3动,1,2,1'")
        return

    question = sys.argv[1]
    yao_input = sys.argv[2]

    yao_list = parse_yao(yao_input)
    if not yao_list:
        print("爻输入格式错误，请使用：少阳,少阴,老阳动,少阳,少阴,少阳（共6个）")
        return

    # 导入并运行
    script_dir = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, script_dir)

    from interpret import interpret

    try:
        output = interpret(question, yao_list)
        print(output)
    except Exception as e:
        print(f"解读出错：{e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
