# 六爻占卜 Skill

基于传统六爻纳甲法的智能占卜系统，支持交互式起卦和卦象解析。

## 功能特点

- 🎯 **交互式起卦**：通过交互式界面引导用户完成起卦流程
- 📊 **智能解卦**：基于传统六爻理论的多维度卦象分析
- 🏷️ **用神自动提取**：自动识别占卜主题并匹配用神
- 📖 **详细断语**：提供象数理多层次解读

## 安装方法

1. 将本Skill复制到OpenClaw的skills目录：
   ```bash
   cp -r liuyao-skill ~/.openclaw/skills/
   ```

2. 确保Python依赖已安装：
   ```bash
   pip install lunarcalendar
   ```

## 使用说明

在OpenClaw对话中，使用以下触发词启动：
- `起卦` - 开始交互式起卦流程
- `算一卦` - 快速起卦
- `摇卦` - 进入占卜模式
- `🎲` - 快捷触发

## 目录结构

```
liuyao-skill/
├── SKILL.md                    # Skill说明文档
├── README.md                   # 本文件
├── .gitignore                  # Git忽略配置
├── requirements.txt            # Python依赖
├── scripts/                    # 核心脚本
│   ├── __init__.py
│   ├── liuyao_interactive.py   # 交互式起卦主程序（最新版）
│   ├── liuyao_interpret.py     # 卦象解析核心（最新版）
│   ├── naga.py                 # 纳甲系统
│   ├── naga_data.py            # 纳甲数据
│   ├── pattern.py              # 格局分析
│   ├── wangshuai.py            # 旺衰判断
│   ├── xunkong.py              # 旬空计算
│   └── test_liuyao_input.py    # 输入测试
├── tests/                      # 测试套件（47个测试用例）
│   ├── README.md
│   ├── test_liuyao.py          # 主测试文件
│   └── test_report.txt         # 测试报告
├── data/                       # 数据文件
│   └── gua_data.json           # 64卦基础数据
└── docs/                       # 文档资料
    └── liuyao_notes.md         # 六爻笔记
```

## 核心文件说明

### scripts/liuyao_interactive.py
交互式起卦主程序，处理用户输入、生成卦象、调用解析模块。

### scripts/liuyao_interpret.py
卦象解析核心，包含：
- 用神自动提取
- 卦象分析
- 断语生成
- 多维度解读

## 开源协议

MIT License - 详见 [LICENSE](LICENSE) 文件

## 贡献

欢迎提交Issue和PR。请确保：
1. 代码符合Python规范
2. 新增功能附带测试用例
3. 通过全部47个测试

---

*传统智慧，现代呈现*
