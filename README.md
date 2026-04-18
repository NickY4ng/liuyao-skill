# 六爻占卜 Skill for OpenClaw

六爻占卜AI助手，基于OpenClaw框架开发。

## 功能

- 六爻起卦（铜钱摇卦）
- 纳甲信息解析
- 世应系统计算
- 六亲推演
- 用神选取
- 吉凶判断
- 六神配置

## 安装

```bash
# 安装依赖
pip install -r requirements.txt

# 或使用 setup.sh
bash setup.sh
```

## 使用

在OpenClaw中配置后，直接输入六爻问题即可。

## 项目结构

```
liuyao-skill/
├── SKILL.md           # Skill定义
├── scripts/           # 核心脚本
│   ├── liuyao_interactive.py   # 交互式占卜
│   ├── interpret.py             # 解读引擎
│   └── ...
├── data/              # 数据文件
│   ├── hexagrams.json          # 64卦数据
│   ├── hexagrams_full.json      # 完整卦象
│   ├── naga.json               # 纳甲数据
│   └── yongshen_rules.json     # 用神规则
└── docs/              # 文档
```

## 依赖

- Python 3.10+
- 其他依赖见 requirements.txt

## License

MIT
