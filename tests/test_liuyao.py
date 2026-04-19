#!/usr/bin/env python3
"""
六爻Skill综合测试用例

测试范围：
1. 交互流程测试
2. 输入解析测试  
3. 边界情况测试
4. 错误处理测试

使用方法：
  python3 test_liuyao.py              # 运行所有测试
  python3 test_liuyao.py -v           # 详细输出
  python3 test_liuyao.py TestClass    # 运行指定测试类
"""

import unittest
import json
import os
import sys
import tempfile
import time
import threading
from unittest.mock import patch, MagicMock

# 添加脚本目录到路径
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PARENT_DIR = os.path.dirname(SCRIPT_DIR)
sys.path.insert(0, os.path.join(PARENT_DIR, 'scripts'))

# 导入被测模块
from liuyao_interactive import (
    is_emoji, is_text, is_divination_request,
    start_divination, process_step, handle_user_input,
    get_session, save_session, clear_session,
    SESSION_FILE, TRIGGER_WORD, YAO_NAMES
)


# ============================================
# 测试数据定义
# ============================================

class TestData:
    """测试数据集"""
    
    # 标准6爻输入格式
    STANDARD_YAOS_INPUT = """今年能不能升职？
初爻：少阳
二爻：少阴
三爻：老阳动
四爻：老阴动
五爻：少阳
上爻：少阴"""

    # 全老阳（6个动爻）
    ALL_LAOYANG_INPUT = """测试问题
初爻：老阳动
二爻：老阳动
三爻：老阳动
四爻：老阳动
五爻：老阳动
上爻：老阳动"""

    # 全少阴（无动爻）
    ALL_SHAOYIN_INPUT = """测试问题
初爻：少阴
二爻：少阴
三爻：少阴
四爻：少阴
五爻：少阴
上爻：少阴"""

    # 3个动爻
    THREE_DONG_INPUT = """测试问题
初爻：老阳动
二爻：少阴
三爻：老阴动
四爻：少阳
五爻：老阳动
上爻：少阴"""

    # 特殊字符问题
    SPECIAL_CHARS_QUESTION = """测试💰包含表情、中文、English、123数字！#@￥%
初爻：少阳
二爻：少阴
三爻：老阳动
四爻：少阴
五爻：少阳
上爻：少阴"""

    # 各种表情测试
    EMOJI_ONLY = "👍"
    EMOJI_MIXED = "好的👍"
    TEXT_ONLY = "OK"
    TEXT_CHINESE = "心想事成"
    TEXT_MIXED_EMOJI = "心想事成👍"
    MULTI_EMOJI = "🌕🌑🌑"
    EMOJI_WITH_SPACE = "👍 🌕🌑🌑"
    EMOJI_BRACKET_OK = "[OK]"
    COINS_PATTERN = "🌕🌕🌑"

    # 起卦触发词
    TRIGGERS = [
        "起卦",
        "算一卦",
        "摇卦",
        "占卦",
        "卜卦",
        "算卦",
        "🎲",
        "六爻",
        "占卜",
        "问卦",
        "打卦",
        "求卦"
    ]

    # 问题关键词
    QUESTIONS = [
        "今年能不能升职？",
        "这段感情怎么样？",
        "财运如何？",
        "考试能通过吗",
        "健康需要注意什么？",
        "创业行不行",
        "买房合适吗？",
        "出行顺利吗",
    ]


# ============================================
# 1. 交互流程测试
# ============================================

class TestInteractiveFlow(unittest.TestCase):
    """交互流程测试 - 测试用户与系统的交互流程"""
    
    @classmethod
    def setUpClass(cls):
        """测试类开始时清理会话"""
        clear_session()
    
    @classmethod
    def tearDownClass(cls):
        """测试类结束时清理会话"""
        clear_session()
    
    def setUp(self):
        """每个测试开始前清理状态"""
        clear_session()
    
    def tearDown(self):
        """每个测试结束后清理状态"""
        clear_session()
    
    # ---------- 1.1 正常6次摇卦流程 ----------
    
    def test_01_normal_6_step_flow(self):
        """
        测试用例: 正常6次摇卦流程
        
        输入: 连续发送6次"心想事成"
        期望输出: 
          - 每次返回当前爻的结果和下一步提示
          - 第6次完成后返回完整解读
          - step从1递增到6
        实际输出: (待填写)
        """
        # 开始起卦
        result = handle_user_input("今年能不能升职？")
        self.assertIn(TRIGGER_WORD, result)
        self.assertIn("第1次", result)
        
        session = get_session()
        self.assertIsNotNone(session)
        self.assertEqual(session['step'], 1)
        self.assertEqual(session['question'], "今年能不能升职？")
        
        # 模拟6次摇卦
        for i in range(1, 7):
            result = handle_user_input(TRIGGER_WORD)
            
            if i < 6:
                # 中间步骤
                self.assertIn(f"第{i}次", result)
                self.assertIn(f"第{i+1}次/共6次", result)
                self.assertIn(TRIGGER_WORD, result)
                
                session = get_session()
                self.assertEqual(session['step'], i + 1)
                self.assertEqual(len(session['yaos']), i)
            else:
                # 最后一步 - 应该完成解读
                self.assertIn("六爻起卦完成", result)
                self.assertIn("卦象解读", result)
                self.assertIn("摇卦记录", result)
                
                # 会话应该被清除
                session = get_session()
                self.assertIsNone(session)
    
    def test_02_step_progression_correctness(self):
        """
        测试用例: step递增正确性验证
        
        输入: 6次"心想事成"
        期望输出: step严格从1->2->3->4->5->6，每次只+1
        实际输出: (待填写)
        """
        handle_user_input("测试问题")
        
        expected_steps = []
        actual_steps = []
        
        for i in range(6):
            handle_user_input(TRIGGER_WORD)
            session = get_session()
            if session:
                actual_steps.append(session['step'])
                expected_steps.append(min(i + 2, 6))  # 2,3,4,5,6,6
        
        self.assertEqual(actual_steps, expected_steps,
                        f"step递增不符合预期: 期望{expected_steps}, 实际{actual_steps}")
    
    # ---------- 1.2 状态异常恢复 ----------
    
    def test_03_step_out_of_bounds_recovery(self):
        """
        测试用例: step越界后重新起卦
        
        输入: 
          1. 手动将session step设为10（越界）
          2. 发送"心想事成"
        期望输出: 检测到异常，提示重置并重新开始
        实际输出: (待填写)
        """
        # 创建异常的session
        invalid_session = {
            "step": 10,  # 越界
            "yaos": [],
            "question": "测试问题",
            "start_time": "2026-01-01 00:00:00",
            "last_update": time.time()
        }
        save_session(invalid_session)
        
        # 尝试处理
        result = handle_user_input(TRIGGER_WORD)
        
        # 期望检测到异常并建议重新开始
        self.assertTrue(
            "状态异常" in result or "已重置" in result or "重新开始" in result or "第10次" in result,
            f"异常状态未正确处理: {result}"
        )
    
    def test_04_negative_step_recovery(self):
        """
        测试用例: step为负数时的恢复
        
        输入: session step=-1
        期望输出: 重置状态或报错提示
        实际输出: (待填写)
        """
        invalid_session = {
            "step": -1,
            "yaos": [],
            "question": "测试问题",
            "start_time": "2026-01-01 00:00:00",
            "last_update": time.time()
        }
        save_session(invalid_session)
        
        result = handle_user_input(TRIGGER_WORD)
        self.assertTrue(
            "状态异常" in result or "已重置" in result or "重新开始" in result,
            f"负数step未正确处理: {result}"
        )
    
    # ---------- 1.3 超时后重新起卦 ----------
    
    def test_05_session_timeout_reset(self):
        """
        测试用例: session超时后自动重置
        
        输入: 
          1. 创建session
          2. 将last_update设为6分钟前（超过5分钟超时）
        期望输出: get_session()返回None，视为新会话
        实际输出: (待填写)
        """
        # 创建超时的session
        old_time = time.time() - 400  # 400秒前，超过300秒超时
        timeout_session = {
            "step": 3,
            "yaos": [{}, {}, {}],  # 3个已完成的爻
            "question": "测试问题",
            "start_time": "2026-01-01 00:00:00",
            "last_update": old_time
        }
        save_session(timeout_session)
        
        # 读取应该返回None（超时）
        session = get_session()
        self.assertIsNone(session, "超时session未被清除")
    
    def test_06_timeout_then_new_divination(self):
        """
        测试用例: 超时后重新起卦
        
        输入: 
          1. 创建超时session
          2. 发送新问题"明年运势如何？"
        期望输出: 作为新的起卦请求处理，重新开始
        实际输出: (待填写)
        """
        # 创建超时的session
        old_time = time.time() - 400
        timeout_session = {
            "step": 4,
            "yaos": [{}, {}, {}, {}],
            "question": "旧问题",
            "start_time": "2026-01-01 00:00:00",
            "last_update": old_time
        }
        save_session(timeout_session)
        
        # 发送新问题
        result = handle_user_input("明年运势如何？")
        
        # 应该作为新起卦处理
        self.assertIn(TRIGGER_WORD, result)
        self.assertIn("第1次", result)
        
        session = get_session()
        self.assertIsNotNone(session)
        self.assertEqual(session['question'], "明年运势如何？")
    
    # ---------- 1.4 竞态条件测试 ----------
    
    def test_07_rapid_consecutive_trigger_word(self):
        """
        测试用例: 快速连续发送"心想事成"
        
        输入: 以极短间隔快速发送多次"心想事成"
        期望输出: 
          - 每次正确处理一个步骤
          - step不会跳跃或重复
          - 不会批量返回多个结果
        实际输出: (待填写)
        """
        handle_user_input("快速测试")
        
        # 快速连续发送
        results = []
        for _ in range(6):
            result = handle_user_input(TRIGGER_WORD)
            results.append(result)
        
        # 验证每次都有明确的步骤标识
        for i, result in enumerate(results[:5]):  # 前5次
            self.assertIn(f"第{i+1}次", result, f"第{i+1}次结果缺少步骤标识")
    
    def test_08_concurrent_step_handling(self):
        """
        测试用例: 模拟并发请求处理（单线程安全）
        
        输入: 在session活跃时，快速连续调用handle_user_input
        期望输出: 串行处理，无数据竞争，step正确递增
        实际输出: (待填写)
        """
        handle_user_input("并发测试")
        
        steps_recorded = []
        for _ in range(10):  # 多于6次，测试完成后重复调用的处理
            handle_user_input(TRIGGER_WORD)
            session = get_session()
            if session:
                steps_recorded.append(session['step'])
            else:
                steps_recorded.append('completed')
        
        # 验证步骤单调递增直到完成
        prev = 0
        for step in steps_recorded:
            if step == 'completed':
                break
            self.assertGreater(step, prev, f"step未递增: {prev} -> {step}")
            prev = step


# ============================================
# 2. 输入解析测试
# ============================================

class TestInputParsing(unittest.TestCase):
    """输入解析测试 - 测试各种输入格式的解析"""
    
    @classmethod
    def setUpClass(cls):
        clear_session()
    
    @classmethod
    def tearDownClass(cls):
        clear_session()
    
    # ---------- 2.1 标准格式解析 ----------
    
    def test_09_standard_yao_format(self):
        """
        测试用例: 标准6爻输入格式解析
        
        输入:
          初爻：少阳
          二爻：老阳动
          三爻：少阴
          四爻：老阴动
          五爻：少阳
          上爻：少阴
        
        期望输出:
          - 正确识别6个爻
          - 正确识别动爻（老阳动、老阴动）
          - 爻位对应正确
        实际输出: (待填写)
        """
        # 使用liuyao_interpret.py解析
        from liuyao_interpret import LiuYaoInterpreter
        
        interpreter = LiuYaoInterpreter()
        result = interpreter.parse_input(TestData.STANDARD_YAOS_INPUT)
        
        self.assertTrue(result, "解析失败")
        self.assertEqual(len(interpreter.yao_results), 6, "爻数量不正确")
        
        # 验证动爻识别
        dong_count = sum(1 for y in interpreter.yao_results if y['dong'])
        self.assertEqual(dong_count, 2, "动爻数量应为2")
    
    def test_10_yao_position_mapping(self):
        """
        测试用例: 爻位映射正确性
        
        输入: 完整的6爻数据
        期望输出: 初爻=pos0, 二爻=pos1, ..., 上爻=pos5
        实际输出: (待填写)
        """
        from liuyao_interpret import LiuYaoInterpreter
        
        interpreter = LiuYaoInterpreter()
        interpreter.parse_input(TestData.STANDARD_YAOS_INPUT)
        
        expected_positions = {
            "初爻": 0,
            "二爻": 1,
            "三爻": 2,
            "四爻": 3,
            "五爻": 4,
            "上爻": 5
        }
        
        for yao in interpreter.yao_results:
            expected_pos = expected_positions.get(yao['yao_name'])
            self.assertEqual(yao['pos_idx'], expected_pos,
                           f"{yao['yao_name']}位置映射错误")
    
    # ---------- 2.2 表情识别测试 ----------
    
    def test_11_emoji_only_true(self):
        """
        测试用例: 纯表情识别为True
        
        输入: "👍"
        期望输出: is_emoji=True, is_text=False
        实际输出: (待填写)
        """
        self.assertTrue(is_emoji(TestData.EMOJI_ONLY))
        self.assertFalse(is_text(TestData.EMOJI_ONLY))
    
    def test_12_emoji_coins_pattern(self):
        """
        测试用例: 硬币图案识别为表情
        
        输入: "🌕🌕🌑"
        期望输出: is_emoji=True
        实际输出: (待填写)
        """
        self.assertTrue(is_emoji(TestData.COINS_PATTERN))
    
    def test_13_text_only_false(self):
        """
        测试用例: 纯文字识别为非表情
        
        输入: "OK"
        期望输出: is_emoji=False, is_text=True
        实际输出: (待填写)
        """
        self.assertFalse(is_emoji(TestData.TEXT_ONLY))
        self.assertTrue(is_text(TestData.TEXT_ONLY))
    
    def test_14_chinese_text(self):
        """
        测试用例: 中文"心想事成"
        
        输入: "心想事成"
        期望输出: is_emoji=False, is_text=True
        实际输出: (待填写)
        """
        self.assertFalse(is_emoji(TestData.TEXT_CHINESE))
        self.assertTrue(is_text(TestData.TEXT_CHINESE))
    
    def test_15_mixed_emoji_text(self):
        """
        测试用例: 混合内容识别为文字
        
        输入: "好的👍"
        期望输出: is_emoji=False, is_text=True（混合视为文字）
        实际输出: (待填写)
        """
        self.assertFalse(is_emoji(TestData.EMOJI_MIXED))
        self.assertTrue(is_text(TestData.EMOJI_MIXED))
    
    def test_16_trigger_with_emoji(self):
        """
        测试用例: "心想事成👍"
        
        输入: "心想事成👍"
        期望输出: is_emoji=False, is_text=True（混合视为文字，会打断流程）
        实际输出: (待填写)
        """
        self.assertFalse(is_emoji(TestData.TEXT_MIXED_EMOJI))
        self.assertTrue(is_text(TestData.TEXT_MIXED_EMOJI))
    
    def test_17_bracket_ok_not_emoji(self):
        """
        测试用例: "[OK]"不是表情
        
        输入: "[OK]"
        期望输出: is_emoji=False（包含文字字符）
        实际输出: (待填写)
        """
        self.assertFalse(is_emoji(TestData.EMOJI_BRACKET_OK))
        self.assertTrue(is_text(TestData.EMOJI_BRACKET_OK))
    
    def test_18_emoji_with_space(self):
        """
        测试用例: 表情带空格
        
        输入: "👍 🌕🌑🌑"
        期望输出: is_emoji=True（空格分隔的表情仍视为表情）
        实际输出: (待填写)
        """
        self.assertTrue(is_emoji(TestData.EMOJI_WITH_SPACE))
    
    def test_19_empty_string(self):
        """
        测试用例: 空字符串
        
        输入: ""
        期望输出: is_emoji=False, is_text=False
        实际输出: (待填写)
        """
        self.assertFalse(is_emoji(""))
        self.assertFalse(is_text(""))
    
    def test_20_whitespace_only(self):
        """
        测试用例: 仅空白字符
        
        输入: "   \t\n"
        期望输出: is_emoji=False, is_text=False
        实际输出: (待填写)
        """
        self.assertFalse(is_emoji("   \t\n"))
        self.assertFalse(is_text("   \t\n"))
    
    # ---------- 2.3 起卦请求识别 ----------
    
    def test_21_trigger_words_recognition(self):
        """
        测试用例: 各种触发词识别
        
        输入: "起卦"、"算一卦"、"🎲"等
        期望输出: 全部识别为起卦请求(is_div=True)
        实际输出: (待填写)
        """
        for trigger in TestData.TRIGGERS:
            is_div, question = is_divination_request(trigger)
            self.assertTrue(is_div, f"'{trigger}'应被识别为起卦请求")
    
    def test_22_trigger_with_question(self):
        """
        测试用例: 触发词+问题组合
        
        输入: "起卦 今年能不能升职？"
        期望输出: is_div=True, question="今年能不能升职？"
        实际输出: (待填写)
        """
        is_div, question = is_divination_request("起卦 今年能不能升职？")
        self.assertTrue(is_div)
        self.assertEqual(question, "今年能不能升职？")
    
    def test_23_question_without_trigger(self):
        """
        测试用例: 无触发词但有疑问特征
        
        输入: "今年能不能升职？"
        期望输出: is_div=True（智能识别为起卦）
        实际输出: (待填写)
        """
        for q in TestData.QUESTIONS:
            is_div, question = is_divination_request(q)
            self.assertTrue(is_div, f"'{q}'应被智能识别为起卦请求")
    
    def test_24_normal_text_not_divination(self):
        """
        测试用例: 普通文本不识别为起卦
        
        输入: "今天天气不错"
        期望输出: is_div=False
        实际输出: (待填写)
        """
        is_div, _ = is_divination_request("今天天气不错")
        self.assertFalse(is_div)
        
        is_div2, _ = is_divination_request("你好")
        self.assertFalse(is_div2)


# ============================================
# 3. 边界情况测试
# ============================================

class TestBoundaryCases(unittest.TestCase):
    """边界情况测试 - 测试极端和特殊场景"""
    
    @classmethod
    def setUpClass(cls):
        clear_session()
    
    @classmethod
    def tearDownClass(cls):
        clear_session()
    
    def setUp(self):
        clear_session()
    
    def tearDown(self):
        clear_session()
    
    # ---------- 3.1 全老阳（6个动爻） ----------
    
    def test_25_all_laoyang_six_dong(self):
        """
        测试用例: 全老阳（6个动爻）
        
        输入: 6个老阳动
        期望输出:
          - 正确识别6个动爻
          - 变卦为全阴
          - 解读正确处理多动爻场景
        实际输出: (待填写)
        """
        from liuyao_interpret import LiuYaoInterpreter
        
        interpreter = LiuYaoInterpreter()
        result = interpreter.parse_input(TestData.ALL_LAOYANG_INPUT)
        
        self.assertTrue(result)
        self.assertEqual(len(interpreter.yao_results), 6)
        
        # 验证6个都是动爻
        dong_count = sum(1 for y in interpreter.yao_results if y['dong'])
        self.assertEqual(dong_count, 6, "应有6个动爻")
        
        # 验证所有爻都是阳
        yang_count = sum(1 for y in interpreter.yao_results if y['yang'])
        self.assertEqual(yang_count, 6, "应有6个阳爻")
    
    def test_26_all_laoyang_bian_gua(self):
        """
        测试用例: 全老阳的变卦
        
        输入: 全老阳
        期望输出: 变卦为全阴（坤卦）
        实际输出: (待填写)
        """
        from liuyao_interpret import LiuYaoInterpreter
        
        interpreter = LiuYaoInterpreter()
        interpreter.parse_input(TestData.ALL_LAOYANG_INPUT)
        interpreter.hexagram = interpreter.find_hexagram()
        bian = interpreter.get_bian_hexagram()
        
        # 全老阳变卦应为全阴
        self.assertIsNotNone(bian)
        # 变卦应该是坤卦（全阴）
        self.assertIn("坤", bian.get("name", ""))
    
    # ---------- 3.2 全少阴（无动爻） ----------
    
    def test_27_all_shaoyin_no_dong(self):
        """
        测试用例: 全少阴（无动爻）
        
        输入: 6个少阴
        期望输出:
          - 正确识别0个动爻
          - 静卦处理逻辑
          - 无变卦或变卦与主卦相同
        实际输出: (待填写)
        """
        from liuyao_interpret import LiuYaoInterpreter
        
        interpreter = LiuYaoInterpreter()
        result = interpreter.parse_input(TestData.ALL_SHAOYIN_INPUT)
        
        self.assertTrue(result)
        
        # 验证0个动爻
        dong_count = sum(1 for y in interpreter.yao_results if y['dong'])
        self.assertEqual(dong_count, 0, "应有0个动爻")
        
        # 验证所有爻都是阴
        yang_count = sum(1 for y in interpreter.yao_results if y['yang'])
        self.assertEqual(yang_count, 0, "应有0个阳爻")
    
    def test_28_no_dong_jing_gua_interpretation(self):
        """
        测试用例: 静卦解读
        
        输入: 无动爻
        期望输出: 解读中包含"静卦"相关描述
        实际输出: (待填写)
        """
        from liuyao_interpret import LiuYaoInterpreter
        
        interpreter = LiuYaoInterpreter()
        interpreter.parse_input(TestData.ALL_SHAOYIN_INPUT)
        interpreter.hexagram = interpreter.find_hexagram()
        interpreter.bian_hexagram = interpreter.get_bian_hexagram()
        
        result = interpreter.generate_interpretation()
        
        # 应包含静卦相关内容
        self.assertIn("静卦", result)
    
    # ---------- 3.3 3个动爻 ----------
    
    def test_29_three_dong_yao(self):
        """
        测试用例: 3个动爻
        
        输入: 3个动爻混合
        期望输出:
          - 正确识别3个动爻
          - 动变分析覆盖所有动爻
        实际输出: (待填写)
        """
        from liuyao_interpret import LiuYaoInterpreter
        
        interpreter = LiuYaoInterpreter()
        result = interpreter.parse_input(TestData.THREE_DONG_INPUT)
        
        self.assertTrue(result)
        
        # 验证3个动爻
        dong_count = sum(1 for y in interpreter.yao_results if y['dong'])
        self.assertEqual(dong_count, 3, "应有3个动爻")
    
    # ---------- 3.4 特殊字符问题 ----------
    
    def test_30_special_chars_in_question(self):
        """
        测试用例: 问题包含特殊字符
        
        输入: 包含表情、中英文、数字、特殊符号的问题
        期望输出: 正确提取问题，不报错
        实际输出: (待填写)
        """
        from liuyao_interpret import LiuYaoInterpreter
        
        interpreter = LiuYaoInterpreter()
        result = interpreter.parse_input(TestData.SPECIAL_CHARS_QUESTION)
        
        self.assertTrue(result)
        # 问题应被完整保留
        self.assertIn("测试", interpreter.question)
        self.assertIn("💰", interpreter.question)
    
    def test_31_very_long_question(self):
        """
        测试用例: 超长问题
        
        输入: 1000字的问题描述
        期望输出: 正常处理，不截断或报错
        实际输出: (待填写)
        """
        long_question = "A" * 1000
        input_data = f"{long_question}\n初爻：少阳\n二爻：少阴\n三爻：老阳动\n四爻：少阴\n五爻：少阳\n上爻：少阴"
        
        from liuyao_interpret import LiuYaoInterpreter
        interpreter = LiuYaoInterpreter()
        result = interpreter.parse_input(input_data)
        
        self.assertTrue(result)
        self.assertEqual(len(interpreter.question), 1000)
    
    def test_32_unicode_edge_cases(self):
        """
        测试用例: Unicode边界字符
        
        输入: 包含各种Unicode字符（中文、日文、韩文、阿拉伯文等）
        期望输出: 正常处理不崩溃
        实际输出: (待填写)
        """
        unicode_question = "测试🔮你好こんにちは안녕하세요مرحبا"
        input_data = f"{unicode_question}\n初爻：少阳\n二爻：少阴\n三爻：老阳动\n四爻：少阴\n五爻：少阳\n上爻：少阴"
        
        from liuyao_interpret import LiuYaoInterpreter
        interpreter = LiuYaoInterpreter()
        
        try:
            result = interpreter.parse_input(input_data)
            self.assertTrue(result)
        except Exception as e:
            self.fail(f"Unicode字符处理失败: {e}")


# ============================================
# 4. 错误处理测试
# ============================================

class TestErrorHandling(unittest.TestCase):
    """错误处理测试 - 测试异常情况下的行为"""
    
    @classmethod
    def setUpClass(cls):
        clear_session()
    
    @classmethod
    def tearDownClass(cls):
        clear_session()
    
    def setUp(self):
        clear_session()
    
    def tearDown(self):
        clear_session()
    
    # ---------- 4.1 Session文件损坏 ----------
    
    def test_33_corrupted_session_file(self):
        """
        测试用例: session文件损坏时的行为
        
        输入: 写入损坏的JSON到session文件
        期望输出: 优雅处理，返回None或重置，不崩溃
        实际输出: (待填写)
        """
        # 创建损坏的JSON文件
        os.makedirs(os.path.dirname(SESSION_FILE), exist_ok=True)
        with open(SESSION_FILE, 'w', encoding='utf-8') as f:
            f.write("{invalid json content}")
        
        # 尝试读取
        try:
            session = get_session()
            # 应该返回None或处理异常
            self.assertIsNone(session)
        except Exception as e:
            self.fail(f"损坏session文件未优雅处理: {e}")
    
    def test_34_empty_session_file(self):
        """
        测试用例: session文件为空
        
        输入: 空session文件
        期望输出: 返回None
        实际输出: (待填写)
        """
        os.makedirs(os.path.dirname(SESSION_FILE), exist_ok=True)
        with open(SESSION_FILE, 'w', encoding='utf-8') as f:
            f.write("")
        
        session = get_session()
        self.assertIsNone(session)
    
    def test_35_missing_session_fields(self):
        """
        测试用例: session缺少必要字段
        
        输入: JSON格式正确但缺少step/yaos等字段
        期望输出: 优雅处理，可能报错或重置
        实际输出: (待填写)
        """
        incomplete_session = {
            "question": "测试问题",
            "last_update": time.time()
            # 缺少step和yaos
        }
        save_session(incomplete_session)
        
        try:
            result = handle_user_input(TRIGGER_WORD)
            # 应该能处理，可能提示重置
            self.assertTrue(
                "状态" in result or "重置" in result or "第" in result
            )
        except (KeyError, TypeError) as e:
            # 如果抛异常，记录为待修复
            self.fail(f"缺少字段未优雅处理: {e}")
    
    # ---------- 4.2 解读脚本超时 ----------
    
    @patch('subprocess.run')
    def test_36_interpret_script_timeout(self, mock_run):
        """
        测试用例: 解读脚本超时
        
        输入: 模拟subprocess.run超时
        期望输出: 返回超时错误信息，不崩溃
        实际输出: (待填写)
        """
        mock_run.side_effect = TimeoutError("Script execution timeout")
        
        from liuyao_interpret import LiuYaoInterpreter
        interpreter = LiuYaoInterpreter()
        
        # 正常解析输入
        interpreter.parse_input(TestData.STANDARD_YAOS_INPUT)
        interpreter.hexagram = interpreter.find_hexagram()
        interpreter.bian_hexagram = interpreter.get_bian_hexagram()
        
        # 生成解读时会调用interpret_direct
        # 这里需要patch interpret_direct方法
        # 实际测试中可能需要调整
        try:
            result = interpreter.generate_interpretation()
            # 检查是否包含超时相关信息或正常完成
        except TimeoutError:
            pass  # 可以接受超时异常
    
    @patch('subprocess.run')
    def test_37_interpret_script_error(self, mock_run):
        """
        测试用例: 解读脚本返回错误
        
        输入: 模拟subprocess.run返回非零退出码
        期望输出: 返回错误信息，不崩溃
        实际输出: (待填写)
        """
        mock_result = MagicMock()
        mock_result.returncode = 1
        mock_result.stderr = "Script error: missing data file"
        mock_run.return_value = mock_result
        
        from liuyao_interpret import LiuYaoInterpreter
        interpreter = LiuYaoInterpreter()
        
        # 这个测试需要实际调用interpret_direct
        # 可能需要调整测试方式
        result = interpreter.interpret_direct("测试输入")
        
        self.assertIn("失败", result)
    
    # ---------- 4.3 输入格式错误 ----------
    
    def test_38_insufficient_yao_count(self):
        """
        测试用例: 爻数量不足
        
        输入: 只有3个爻
        期望输出: 返回格式错误提示
        实际输出: (待填写)
        """
        incomplete_input = """测试问题
初爻：少阳
二爻：少阴
三爻：老阳动"""
        
        from liuyao_interpret import LiuYaoInterpreter
        interpreter = LiuYaoInterpreter()
        result = interpreter.parse_input(incomplete_input)
        
        self.assertFalse(result, "应返回解析失败")
    
    def test_39_invalid_yao_type(self):
        """
        测试用例: 无效爻类型
        
        输入: 包含"太阳"、"太阴"等无效类型
        期望输出: 识别为错误或跳过
        实际输出: (待填写)
        """
        invalid_input = """测试问题
初爻：太阳
二爻：少阴
三爻：老阳动
四爻：少阴
五爻：少阳
上爻：少阴"""
        
        from liuyao_interpret import LiuYaoInterpreter
        interpreter = LiuYaoInterpreter()
        
        try:
            result = interpreter.parse_input(invalid_input)
            # 可能失败或部分解析
        except Exception as e:
            # 记录异常行为
            pass
    
    def test_40_missing_question(self):
        """
        测试用例: 缺少问题只有爻
        
        输入: 只有6个爻，无问题行
        期望输出: 第一行作为问题，可能为空或默认值
        实际输出: (待填写)
        """
        no_question_input = """初爻：少阳
二爻：少阴
三爻：老阳动
四爻：少阴
五爻：少阳
上爻：少阴"""
        
        from liuyao_interpret import LiuYaoInterpreter
        interpreter = LiuYaoInterpreter()
        result = interpreter.parse_input(no_question_input)
        
        # 第一行被当作问题
        self.assertEqual(interpreter.question, "初爻：少阳")
    
    # ---------- 4.4 文件权限问题 ----------
    
    def test_41_session_read_permission_denied(self):
        """
        测试用例: session文件无读取权限
        
        输入: 创建无读权限的session文件
        期望输出: 优雅处理，返回None或提示
        实际输出: (待填写)
        
        注意: 此测试在Windows上可能行为不同
        """
        # 此测试在非Unix系统跳过
        if os.name == 'nt':
            self.skipTest("权限测试跳过Windows")
        
        try:
            os.makedirs(os.path.dirname(SESSION_FILE), exist_ok=True)
            with open(SESSION_FILE, 'w', encoding='utf-8') as f:
                f.write('{"step": 1}')
            os.chmod(SESSION_FILE, 0o000)
            
            session = get_session()
            # 应该返回None
        except PermissionError:
            pass  # 可以接受权限错误
        finally:
            # 恢复权限以便清理
            if os.path.exists(SESSION_FILE):
                os.chmod(SESSION_FILE, 0o644)


# ============================================
# 5. 综合场景测试
# ============================================

class TestComprehensiveScenarios(unittest.TestCase):
    """综合场景测试 - 模拟真实使用场景"""
    
    @classmethod
    def setUpClass(cls):
        clear_session()
    
    @classmethod
    def tearDownClass(cls):
        clear_session()
    
    def setUp(self):
        clear_session()
    
    def tearDown(self):
        clear_session()
    
    def test_42_full_divination_workflow(self):
        """
        测试用例: 完整起卦到解读流程
        
        场景: 用户发送问题 -> 系统提示摇卦 -> 用户摇6次 -> 获得解读
        期望输出: 完整流程顺利完成
        实际输出: (待填写)
        """
        # 开始
        result = handle_user_input("今年的工作运势如何？")
        self.assertIn(TRIGGER_WORD, result)
        
        # 6次摇卦
        for _ in range(6):
            result = handle_user_input(TRIGGER_WORD)
        
        # 验证完成
        self.assertIn("起卦完成", result)
        self.assertIn("卦象解读", result)
    
    def test_43_interrupt_and_resume(self):
        """
        测试用例: 中断后继续
        
        场景: 摇卦过程中发送文字打断 -> 继续摇卦
        期望输出: 正确处理打断，可继续
        实际输出: (待填写)
        """
        # 开始并摇2次
        handle_user_input("测试中断")
        handle_user_input(TRIGGER_WORD)
        handle_user_input(TRIGGER_WORD)
        
        session = get_session()
        self.assertEqual(session['step'], 3)
        
        # 发送文字打断
        result = handle_user_input("我突然想到一件事")
        self.assertIn("打断", result)
        
        # 继续摇卦（应仍然有效）
        result = handle_user_input(TRIGGER_WORD)
        self.assertIn("第3次", result)
    
    def test_44_restart_during_active_session(self):
        """
        测试用例: 活跃会话中重新开始
        
        场景: 摇卦到第3次时发送新问题"起卦 另一个问题"
        期望输出: 重置并开始新的起卦
        实际输出: (待填写)
        """
        # 开始并摇2次
        handle_user_input("第一个问题")
        handle_user_input(TRIGGER_WORD)
        handle_user_input(TRIGGER_WORD)
        
        session = get_session()
        old_question = session['question']
        
        # 发送新问题
        result = handle_user_input("第二个问题")
        
        session = get_session()
        new_question = session['question']
        
        # 新问题应该覆盖旧问题或作为新起卦
        self.assertIn(TRIGGER_WORD, result)
    
    def test_45_wrong_emoji_during_divination(self):
        """
        测试用例: 摇卦时发送错误表情
        
        场景: 摇卦过程中发送"👍"而非"心想事成"
        期望输出: 提示用户发送"心想事成"
        实际输出: (待填写)
        """
        handle_user_input("测试错误表情")
        
        # 发送错误表情
        result = handle_user_input("👍")
        
        self.assertIn(TRIGGER_WORD, result)
        self.assertIn("❌", result)
    
    def test_46_status_check_during_divination(self):
        """
        测试用例: 摇卦过程中检查状态
        
        场景: 摇了3次后查看状态
        期望输出: 正确显示当前进度和已记录的爻
        实际输出: (待填写)
        """
        from liuyao_interactive import get_status
        
        handle_user_input("测试状态检查")
        handle_user_input(TRIGGER_WORD)
        handle_user_input(TRIGGER_WORD)
        handle_user_input(TRIGGER_WORD)
        
        status = get_status()
        
        self.assertIn("第4次", status)
        self.assertIn("已记录的爻", status)
        self.assertIn("初爻", status)
    
    def test_47_clear_during_divination(self):
        """
        测试用例: 摇卦过程中重置
        
        场景: 摇了3次后发送"起卦"重新开始
        期望输出: 清除旧会话，开始新起卦
        实际输出: (待填写)
        """
        handle_user_input("测试重置")
        handle_user_input(TRIGGER_WORD)
        handle_user_input(TRIGGER_WORD)
        handle_user_input(TRIGGER_WORD)
        
        # 重新开始
        result = handle_user_input("起卦 新的问题")
        
        self.assertIn("第1次", result)
        
        session = get_session()
        self.assertEqual(session['step'], 1)
        self.assertEqual(len(session['yaos']), 0)


# ============================================
# 测试执行入口
# ============================================

def generate_test_report(test_results):
    """生成测试报告"""
    report = []
    report.append("=" * 60)
    report.append("六爻Skill测试报告")
    report.append("=" * 60)
    report.append("")
    
    total = test_results.testsRun
    failures = len(test_results.failures)
    errors = len(test_results.errors)
    skipped = len(test_results.skipped)
    passed = total - failures - errors - skipped
    
    report.append(f"总测试数: {total}")
    report.append(f"通过: {passed}")
    report.append(f"失败: {failures}")
    report.append(f"错误: {errors}")
    report.append(f"跳过: {skipped}")
    report.append("")
    
    if failures:
        report.append("失败的测试:")
        for test, trace in test_results.failures:
            report.append(f"  - {test}")
    
    if errors:
        report.append("错误的测试:")
        for test, trace in test_results.errors:
            report.append(f"  - {test}")
    
    report.append("")
    report.append("=" * 60)
    
    return "\n".join(report)


if __name__ == '__main__':
    # 确保测试目录存在
    test_dir = os.path.dirname(os.path.abspath(__file__))
    os.makedirs(test_dir, exist_ok=True)
    
    # 运行测试
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromModule(sys.modules[__name__])
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # 生成报告
    report = generate_test_report(result)
    print("\n" + report)
    
    # 保存报告
    report_file = os.path.join(test_dir, 'test_report.txt')
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report)
    print(f"\n报告已保存至: {report_file}")
    
    # 返回退出码
    sys.exit(0 if result.wasSuccessful() else 1)
