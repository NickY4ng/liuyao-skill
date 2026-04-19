# 六爻Skill测试用例说明

## 测试文件位置
`~/.openclaw/skills/liuyao-skill/tests/test_liuyao.py`

## 测试概览

测试用例总数：**47个**

| 类别 | 用例数 | 说明 |
|------|--------|------|
| 交互流程测试 | 8个 | 测试摇卦流程、状态恢复、竞态条件 |
| 输入解析测试 | 16个 | 测试表情识别、文本识别、起卦请求识别 |
| 边界情况测试 | 8个 | 测试全动爻、静卦、特殊字符、超长输入 |
| 错误处理测试 | 9个 | 测试文件损坏、超时、格式错误、权限问题 |
| 综合场景测试 | 6个 | 测试完整流程、中断恢复、重置等 |

## 运行测试

```bash
# 运行所有测试
python3 test_liuyao.py

# 详细输出
python3 test_liuyao.py -v

# 运行指定测试类
python3 test_liuyao.py TestInteractiveFlow
python3 test_liuyao.py TestInputParsing
python3 test_liuyao.py TestBoundaryCases
python3 test_liuyao.py TestErrorHandling
python3 test_liuyao.py TestComprehensiveScenarios

# 运行单个测试用例
python3 test_liuyao.py TestInteractiveFlow.test_01_normal_6_step_flow
```

## 测试数据结构

测试数据集中定义在 `TestData` 类中：

### 输入格式测试数据
- `STANDARD_YAOS_INPUT`: 标准6爻输入
- `ALL_LAOYANG_INPUT`: 全老阳（6动爻）
- `ALL_SHAOYIN_INPUT`: 全少阴（0动爻）
- `THREE_DONG_INPUT`: 3个动爻
- `SPECIAL_CHARS_QUESTION`: 特殊字符问题

### 表情/文本测试数据
- `EMOJI_ONLY`: "👍"
- `EMOJI_MIXED`: "好的👍"
- `TEXT_ONLY`: "OK"
- `TEXT_CHINESE`: "心想事成"
- `COINS_PATTERN`: "🌕🌕🌑"
- `EMOJI_BRACKET_OK`: "[OK]"

## 测试用例详细列表

### 1. 交互流程测试 (TestInteractiveFlow)

| ID | 用例名称 | 描述 |
|----|----------|------|
| 01 | test_01_normal_6_step_flow | 正常6次摇卦流程 |
| 02 | test_02_step_progression_correctness | step递增正确性 |
| 03 | test_03_step_out_of_bounds_recovery | step越界恢复 |
| 04 | test_04_negative_step_recovery | 负数step恢复 |
| 05 | test_05_session_timeout_reset | session超时重置 |
| 06 | test_06_timeout_then_new_divination | 超时后新起卦 |
| 07 | test_07_rapid_consecutive_trigger_word | 快速连续发送 |
| 08 | test_08_concurrent_step_handling | 并发处理测试 |

### 2. 输入解析测试 (TestInputParsing)

| ID | 用例名称 | 描述 |
|----|----------|------|
| 09 | test_09_standard_yao_format | 标准6爻格式 |
| 10 | test_10_yao_position_mapping | 爻位映射 |
| 11 | test_11_emoji_only_true | 纯表情识别 |
| 12 | test_12_emoji_coins_pattern | 硬币图案识别 |
| 13 | test_13_text_only_false | 纯文字识别 |
| 14 | test_14_chinese_text | 中文识别 |
| 15 | test_15_mixed_emoji_text | 混合内容识别 |
| 16 | test_16_trigger_with_emoji | 触发词+表情 |
| 17 | test_17_bracket_ok_not_emoji | [OK]不是表情 |
| 18 | test_18_emoji_with_space | 表情带空格 |
| 19 | test_19_empty_string | 空字符串 |
| 20 | test_20_whitespace_only | 仅空白字符 |
| 21 | test_21_trigger_words_recognition | 触发词识别 |
| 22 | test_22_trigger_with_question | 触发词+问题 |
| 23 | test_23_question_without_trigger | 无触发词问题 |
| 24 | test_24_normal_text_not_divination | 普通文本 |

### 3. 边界情况测试 (TestBoundaryCases)

| ID | 用例名称 | 描述 |
|----|----------|------|
| 25 | test_25_all_laoyang_six_dong | 全老阳6动爻 |
| 26 | test_26_all_laoyang_bian_gua | 全老阳变卦 |
| 27 | test_27_all_shaoyin_no_dong | 全少阴无动爻 |
| 28 | test_28_no_dong_jing_gua_interpretation | 静卦解读 |
| 29 | test_29_three_dong_yao | 3个动爻 |
| 30 | test_30_special_chars_in_question | 特殊字符 |
| 31 | test_31_very_long_question | 超长问题 |
| 32 | test_32_unicode_edge_cases | Unicode边界 |

### 4. 错误处理测试 (TestErrorHandling)

| ID | 用例名称 | 描述 |
|----|----------|------|
| 33 | test_33_corrupted_session_file | session文件损坏 |
| 34 | test_34_empty_session_file | 空session文件 |
| 35 | test_35_missing_session_fields | 缺少必要字段 |
| 36 | test_36_interpret_script_timeout | 解读脚本超时 |
| 37 | test_37_interpret_script_error | 解读脚本错误 |
| 38 | test_38_insufficient_yao_count | 爻数量不足 |
| 39 | test_39_invalid_yao_type | 无效爻类型 |
| 40 | test_40_missing_question | 缺少问题 |
| 41 | test_41_session_read_permission_denied | 权限问题 |

### 5. 综合场景测试 (TestComprehensiveScenarios)

| ID | 用例名称 | 描述 |
|----|----------|------|
| 42 | test_42_full_divination_workflow | 完整流程 |
| 43 | test_43_interrupt_and_resume | 中断继续 |
| 44 | test_44_restart_during_active_session | 活跃会话重启 |
| 45 | test_45_wrong_emoji_during_divination | 错误表情 |
| 46 | test_46_status_check_during_divination | 状态检查 |
| 47 | test_47_clear_during_divination | 重置测试 |

## 测试结果记录

运行测试后，结果会保存在 `test_report.txt` 中。

每个测试用例包含：
- **输入**: 测试输入数据
- **期望输出**: 预期的正确输出
- **实际输出**: 运行测试后的实际结果（待填写）

## 修复验证流程

1. **修复前**: 运行测试，记录失败的测试用例
2. **修复后**: 重新运行测试，验证失败的用例是否通过
3. **回归测试**: 确保修复没有引入新的问题

## 注意事项

1. 测试会修改 `~/.openclaw/.liuyao_session.json` 文件
2. 运行测试前会自动清理session状态
3. 部分测试（如权限测试）在Windows上会跳过
4. 解读脚本超时测试使用了mock，可能需要根据实际实现调整
