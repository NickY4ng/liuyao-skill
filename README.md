# 六爻占卜 Skill for Hermes Agent

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

> 一个完整的六爻占卜系统，支持交互式起卦、自动解卦、六神装卦、格局判断。专为 Hermes Agent 设计，也可独立运行。

## ✨ 特性

- 🎲 **交互式起卦**：用户亲手摇卦，模拟三枚铜钱投掷
- 🔮 **自动解卦**：64卦完整卦辞、象曰、吉凶判断
- 🐉 **六神装卦**：根据日干自动排列青龙、朱雀、勾陈、螣蛇、白虎、玄武
- ⚖️ **旺衰分析**：自动判断用神旺衰、世应关系
- 🎯 **格局判断**：六冲、游魂、归魂等格局自动识别
- 📱 **多平台输出**：支持飞书、微信、命令行等多种输出格式
- 🎨 **美观排版**：emoji 卦象一排排展示，无需代码块

## 🚀 快速开始

### 安装

```bash
git clone https://github.com/yourusername/liuyao-skill.git
cd liuyao-skill
pip install -r requirements.txt
```

### 命令行使用

```bash
# 交互式起卦
python3 scripts/liuyao_interactive.py start "今年能不能升职？"

# 直接解卦（输入6个爻）
python3 scripts/liuyao_interpret.py --question "财运如何" --yaos "少阳,少阴,老阳,少阴,少阳,老阴"
```

### 在 Hermes Agent 中使用

1. 将 `lifestyle/liuyao` 目录复制到 `~/.hermes/skills/`
2. 重启 Hermes Agent
3. 说"来一卦"或"算一卦"即可触发

## 📖 使用示例

### 交互式起卦流程

```
用户：今年能不能升职？
系统：💭 您的问题：今年能不能升职

    🎲 请发送「心想事成」开始摇卦（第1次/共6次）

用户：心想事成
系统：第1次（初爻）：🌕🌕🌑 → 少阳 ⚊
    🎲 请发送「心想事成」继续（第2次/共6次）

用户：心想事成
系统：第2次（二爻）：🌑🌕🌑 → 少阴 ⚋
    ...
    
（第6次后自动解卦）
```

### 输出示例

```
## 🎯 六爻起卦

### 🔮 卦象
地火明夷 · 坎宫 · 静卦
⚋ ⚊ ⚊  
⚋ ⚋ ⚊  

### 🎲 六次摇卦
第1次（初爻）：🌕🌕🌑 → 少阳 ⚊
第2次（二爻）：🌑🌕🌑 → 少阴 ⚋
第3次（三爻）：🌑🌑🌑 → 老阳 ⚊（动）
第4次（四爻）：🌕🌕🌑 → 少阳 ⚊
第5次（五爻）：🌑🌕🌑 → 少阴 ⚋
第6次（上爻）：🌕🌕🌑 → 少阳 ⚊

### 📜 卦辞
明夷，利艰贞。
象曰：明入地中，明夷。君子以莅众，用晦而明。

### ⚖️ 吉凶
- 用神：官鬼爻（卯木）
- 旺衰：休囚于月建，得日辰生扶
- 世应：世爻持官鬼，应爻临妻财
- 总体：中平，需待时机

### 🐉 六神装卦
（日干起六神）
上爻：玄武
五爻：白虎
四爻：螣蛇
三爻：勾陈
二爻：朱雀
初爻：青龙

### 🏷️ 格局
静卦，无动爻

### 💡 建议
- 时机：当前不宜冒进，宜守不宜攻
- 优势：内在能力具备，需等待外部条件成熟
- 注意：谨防小人暗算，行事低调
- 行动：继续积累，秋后有望
```

## 🏗️ 项目结构

```
liuyao-skill/
├── SKILL.md                    # Skill 定义文件
├── README.md                   # 本文件
├── LICENSE                     # MIT 许可证
├── requirements.txt            # 依赖
├── scripts/
│   ├── liuyao_interactive.py   # 交互式起卦主程序
│   ├── liuyao_interpret.py   # 解卦入口
│   ├── liuyao.py              # 核心六爻逻辑
│   ├── hexagrams.py           # 64卦数据
│   ├── interpret.py           # 解卦算法
│   ├── wangshuai.py           # 旺衰分析
│   ├── xunkong.py             # 旬空计算
│   ├── pattern.py             # 格局判断
│   ├── naga.py                # 纳甲法
│   └── validate_liuyao.py     # 验证工具
└── tests/
    └── test_liuyao.py         # 测试用例
```

## 🔧 核心算法

### 爻的判定

| 硬币结果 | 爻名 | 符号 | 动爻 |
|----------|------|------|------|
| 3正 | 老阳 | ⚊ | ✓ |
| 3反 | 老阴 | ⚋ | ✓ |
| 2正1反 | 少阳 | ⚊ | — |
| 2反1正 | 少阴 | ⚋ | — |

### 六神排列

根据起卦日天干：
- 甲乙日：青龙起
- 丙丁日：朱雀起
- 戊日：勾陈起
- 己日：螣蛇起
- 庚辛日：白虎起
- 壬癸日：玄武起

## 📝 配置说明

### Hermes Agent 配置

在 `~/.hermes/config.yaml` 中添加：

```yaml
toolsets:
  - hermes-cli

skills:
  external_dirs:
    - ~/.hermes/skills/lifestyle
```

### 环境变量

```bash
export LIUYAO_SESSION_FILE="~/.hermes/.liuyao_session.json"
export LIUYAO_TIMEOUT=300  # 会话超时时间（秒）
```

## 🧪 测试

```bash
# 运行验证工具
python3 scripts/validate_liuyao.py

# 运行测试用例
python3 tests/test_liuyao.py

# 测试输入识别
python3 scripts/test_liuyao_input.py
```

## 🤝 贡献

欢迎提交 Issue 和 PR！

### 贡献指南

1. Fork 本仓库
2. 创建特性分支：`git checkout -b feature/amazing-feature`
3. 提交更改：`git commit -m 'Add amazing feature'`
4. 推送分支：`git push origin feature/amazing-feature`
5. 提交 Pull Request

## 📄 许可证

[MIT](LICENSE) © 2026 绽放

## 🙏 致谢

- 感谢 Hermes Agent 团队提供的 Skill 框架
- 感谢《增删卜易》《卜筮正宗》等经典六爻著作
- 感谢所有测试和反馈的用户

---

> ⚠️ **免责声明**：本工具仅供学习和娱乐使用，占卜结果仅供参考，不构成任何决策建议。
