# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [v1.0.0] - 2026-04-19

### Added
- 初始开源版本
- 完整的六爻占卜功能（交互式起卦 + 直接输入）
- 64卦数据库（卦名、卦辞、象辞）
- 纳甲、世应、六亲、六神完整实现
- 47个测试用例覆盖核心功能
- 支持多种触发词（起卦、算一卦、摇卦、六爻、占卦）
- "心想事成" 摇卦流程
- 动爻识别与变卦计算
- 完整的解卦输出（用神、旺衰、吉凶判断）

### Fixed
- 状态异常死循环问题
- subprocess超时问题
- 动爻解析漏洞
- 重复匹配bug

### Technical
- Python 3.10+ 支持
- OpenClaw Skill 架构
- 模块化设计（交互式 + 解释器分离）
- 完整的错误处理和边界情况处理

## [Unreleased]

### Planned
- 流日/流月分析功能
- 更多起卦方式（铜钱、时间、数字）
- Web界面支持
- 多语言支持
