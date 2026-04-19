#!/usr/bin/env python3
"""
六爻交互式起卦脚本（修复版）
功能：交互式摇卦流程，支持6次摇卦，自动解读
触发词：起卦、算一卦、摇卦、🎲

优化点：
1. 智能识别起卦请求+问题（一句话触发）
2. 简化流程，快速进入摇卦节奏
3. 严格区分表情和文字输入（修复批量返回问题）

状态记录：~/.openclaw/.liuyao_session.json
"""

import json
import sys
import random
import os
import time
import re
import fcntl
from datetime import datetime
from typing import Dict, List, Optional

# 状态文件路径
SESSION_FILE = os.path.expanduser("~/.openclaw/.liuyao_session.json")
TIMEOUT_SECONDS = 300  # 5分钟超时

# 爻符号映射
YAO_TYPES = {
    ("🌕", "🌕", "🌕"): ("老阳", "⚊", True),   # 老阳动，符号⚊
    ("🌑", "🌑", "🌑"): ("老阴", "⚋", True),   # 老阴动，符号⚋
    ("🌕", "🌕", "🌑"): ("少阳", "⚊", False),  # 少阳
    ("🌕", "🌑", "🌑"): ("少阴", "⚋", False),  # 少阴
}

# 爻位名称（从下到上）
YAO_NAMES = ["初爻", "二爻", "三爻", "四爻", "五爻", "上爻"]

# 起卦触发词（用于智能识别）
DIVINATION_TRIGGERS = [
    "起卦", "算一卦", "摇卦", "占卦", "卜卦", "算卦",
    "🎲", "六爻", "占卜", "问卦", "打卦", "求卦"
]

# 常见问事关键词（用于识别是否包含问题）
QUESTION_KEYWORDS = [
    # 疑问词
    "能不能", "怎么样", "如何", "可否", "是否",
    "会不会", "好不好", "行不行", "可以吗", "能吗",
    "吗", "么", "呢", "如何", "怎么样",
    # 事项
    "工作", "感情", "婚姻", "财运", "事业", "健康",
    "升职", "搬家", "出行", "考试", "面试", "创业",
    "投资", "买房", "结婚", "分手", "复合", "求职",
    "订婚", "怀孕", "生子", "创业", "跳槽",
    # 时间相关
    "今年", "明年", "这个月", "今天", "明天", "最近", "哪天", "什么时候",
    # 开放性问题关键词
    "注意", "需要注意", "可能发生", "会有", "如何", "怎么样",
    "好不好", "能不能", "会不会", "行不行", "是否可以"
]

# 摇卦触发词（每次发送这四个字触发一次摇卦）
TRIGGER_WORD = "心想事成"

# Emoji Unicode 范围 - 严格定义常见emoji
# 注意：不包含汉字、中文标点等
COMMON_EMOJIS = set([
    # 笑脸/表情
    '😀', '😃', '😄', '😁', '😆', '😅', '🤣', '😂', '🙂', '🙃', '😉', '😊', 
    '😇', '🥰', '😍', '🤩', '😘', '😗', '😚', '😙', '😋', '😛', '😜', '🤪',
    '😝', '🤑', '🤗', '🤭', '🤫', '🤔', '🤐', '🤨', '😐', '😑', '😶', '😏',
    '😒', '🙄', '😬', '🤥', '😌', '😔', '😪', '🤤', '😴', '😷', '🤒', '🤕',
    '🤢', '🤮', '🤧', '🥵', '🥶', '🥴', '😵', '🤯', '🤠', '🥳', '😎', '🤓',
    '🧐', '😕', '😟', '🙁', '☹️', '😮', '😯', '😲', '😳', '🥺', '😦', '😧',
    '😨', '😰', '😥', '😢', '😭', '😱', '😖', '😣', '😞', '😓', '😩', '😫',
    '😤', '😡', '😠', '🤬', '😈', '👿', '💀', '☠️', '💩', '🤡', '👹', '👺',
    '👻', '👽', '👾', '🤖', '😺', '😸', '😹', '😻', '😼', '😽', '🙀', '😿',
    '😾',
    # 手势
    '👋', '🤚', '🖐', '✋', '🖖', '👌', '🤌', '🤏', '✌️', '🤞', '🤟', '🤘',
    '🤙', '👈', '👉', '👆', '🖕', '👇', '☝️', '👍', '👎', '✊', '👊', '🤛',
    '🤜', '👏', '🙌', '👐', '🤲', '🤝', '🙏', '✍️', '💪', '🦾', '🦿', '🦵',
    '🦶', '👂', '🦻', '👃', '🧠', '🫀', '🫁', '🦷', '🦴', '👀', '👁', '👅',
    '👄', '💋', '🩸',
    # 人
    '👶', '👧', '🧒', '👦', '👩', '🧑', '👨', '👩‍🦱', '👨‍🦱', '👩‍🦰', '👨‍🦰', '👱‍♀️',
    '👱‍♂️', '👩‍🦳', '👨‍🦳', '👩‍🦲', '👨‍🦲', '🧔', '👵', '🧓', '👴', '👲', '👳‍♀️',
    '👳‍♂️', '🧕', '👮‍♀️', '👮‍♂️', '👷‍♀️', '👷‍♂️', '💂‍♀️', '💂‍♂️', '🕵️‍♀️', '🕵️‍♂️',
    # 动物
    '🐵', '🐒', '🦍', '🦧', '🐶', '🐕', '🦮', '🐕‍🦺', '🐩', '🐺', '🦊', '🦝',
    '🐱', '🐈', '🐈‍⬛', '🦁', '🐯', '🐅', '🐆', '🐴', '🐎', '🦄', '🦓', '🦌',
    '🦬', '🐮', '🐂', '🐃', '🐄', '🐷', '🐖', '🐗', '🐽', '🐏', '🐑', '🐐',
    '🐪', '🐫', '🦙', '🦒', '🐘', '🦣', '🦏', '🦛', '🐭', '🐁', '🐀', '🐹',
    '🐰', '🐇', '🐿', '🦫', '🦔', '🦇', '🐻', '🐻‍❄️', '🐨', '🐼', '🦥', '🦦',
    '🦨', '🦘', '🦡', '🐾', '🦃', '🐔', '🐓', '🐣', '🐤', '🐥', '🐦', '🐧',
    '🕊', '🦅', '🦆', '🦢', '🦉', '🦤', '🪶', '🦩', '🦚', '🦜', '🐸', '🐊',
    '🐢', '🦎', '🐍', '🐲', '🐉', '🦕', '🦖', '🐳', '🐋', '🐬', '🦭', '🐟',
    '🐠', '🐡', '🦈', '🐙', '🐚', '🐌', '🦋', '🐛', '🐜', '🐝', '🪲', '🐞',
    '🦗', '🪳', '🕷', '🕸', '🦂', '🦟', '🪰', '🪱', '🦠', '💐', '🌸', '💮',
    '🏵', '🌹', '🥀', '🌺', '🌻', '🌼', '🌷', '🌱', '🪴', '🌲', '🌳', '🌴',
    '🌵', '🌾', '🌿', '☘️', '🍀', '🍁', '🍂', '🍃',
    # 食物
    '🍇', '🍈', '🍉', '🍊', '🍋', '🍌', '🍍', '🥭', '🍎', '🍏', '🍐', '🍑',
    '🍒', '🍓', '🫐', '🥝', '🍅', '🫒', '🥥', '🥑', '🍆', '🥔', '🥕', '🌽',
    '🌶', '🫑', '🥒', '🥬', '🥦', '🧄', '🧅', '🍄', '🥜', '🌰', '🍞', '🥐',
    '🥖', '🫓', '🥨', '🥯', '🥞', '🧇', '🧀', '🍖', '🍗', '🥩', '🥓', '🍔',
    '🍟', '🍕', '🌭', '🥪', '🌮', '🌯', '🫔', '🥙', '🧆', '🥚', '🍳', '🥘',
    '🍲', '🫕', '🥣', '🥗', '🍿', '🧈', '🧂', '🥫', '🍱', '🍘', '🍙', '🍚',
    '🍛', '🍜', '🍝', '🍠', '🍢', '🍣', '🍤', '🍥', '🍡', '🥟', '🥠', '🥡',
    '🦀', '🦞', '🦐', '🦑', '🦪', '🍦', '🍧', '🍨', '🍩', '🍪', '🎂', '🍰',
    '🧁', '🥧', '🍫', '🍬', '🍭', '🍮', '🍯', '🍼', '🥛', '☕️', '🫖', '🍵',
    '🍶', '🍾', '🍷', '🍸', '🍹', '🍺', '🍻', '🥂', '🥃', '🥤', '🧋', '🧃',
    '🧉', '🧊',
    # 运动/活动
    '⚽️', '🏀', '🏈', '⚾️', '🥎', '🎾', '🏐', '🏉', '🥏', '🎱', '🪀', '🏓',
    '🏸', '🏒', '🏑', '🥍', '🏏', '🥅', '⛳️', '🪁', '🏹', '🎣', '🤿', '🥊',
    '🥋', '🎽', '🛹', '🛼', '🛷', '⛸', '🥌', '🎿', '⛷', '🏂', '🪂', '🏋️',
    '🤼', '🤸', '⛹️', '🤺', '🤾', '🏌️', '🏇', '🧘', '🏄', '🏊', '🚣', '🧗',
    '🚴', '🚵', '🎪', '🤹', '🎭', '🩰', '🎨', '🎬', '🎤', '🎧', '🎼', '🎹',
    '🥁', '🎷', '🎺', '🎸', '🪕', '🎻', '🎲', '🎯', '🎳', '🎮', '🎰', '🧩',
    # 交通/地点
    '🚗', '🚕', '🚙', '🚌', '🚎', '🏎', '🚓', '🚑', '🚒', '🚐', '🛻', '🚚',
    '🚛', '🚜', '🦯', '🦽', '🦼', '🛴', '🚲', '🛵', '🏍', '🛺', '🚨', '🚔',
    '🚍', '🚘', '🚖', '🚡', '🚠', '🚟', '🚃', '🚋', '🚞', '🚝', '🚄', '🚅',
    '🚈', '🚂', '🚆', '🚇', '🚊', '🚉', '✈️', '🛫', '🛬', '🛩', '💺', '🛰',
    '🚀', '🛸', '🚁', '🛶', '⛵️', '🚤', '🛥', '🛳', '⛴', '🚢', '⚓️', '⛽️',
    '🚧', '🚦', '🚥', '🚏', '🗺', '🗿', '🗽', '🗼', '🏰', '🏯', '🏟', '🎡',
    '🎢', '🎠', '⛲️', '⛱', '🏖', '🏝', '🏜', '🌋', '⛰', '🏔', '🗻', '🏕',
    '⛺️', '🛖', '🏠', '🏡', '🏘', '🏚', '🏗', '🏭', '🏢', '🏬', '🏣', '🏤',
    '🏥', '🏦', '🏨', '🏪', '🏫', '🏩', '💒', '🏛', '⛪️', '🕌', '🕍', '🛕',
    '🕋', '⛩', '🛤', '🛣', '🗾', '🎑', '🏞', '🌅', '🌄', '🌠', '🎇', '🎆',
    '🌇', '🌆', '🏙', '🌃', '🌌', '🌉', '🌁',
    # 物品
    '⌚️', '📱', '📲', '💻', '⌨️', '🖥', '🖨', '🖱', '🖲', '🕹', '🗜', '💽',
    '💾', '💿', '📀', '📼', '📷', '📸', '📹', '🎥', '📽', '🎞', '📞', '☎️',
    '📟', '📠', '📺', '📻', '🎙', '🎚', '🎛', '🧭', '⏱', '⏲', '⏰', '🕰',
    '⌛️', '⏳', '📡', '🔋', '🔌', '💡', '🔦', '🕯', '🪔', '🧯', '🛢', '💸',
    '💵', '💴', '💶', '💷', '🪙', '💰', '💳', '💎', '⚖️', '🪜', '🧰', '🪛',
    '🔧', '🔨', '⚒', '🛠', '⛏', '🪚', '🔩', '⚙️', '🪤', '🧱', '⛓', '🧲',
    '🔫', '💣', '🧨', '🪓', '🔪', '🗡', '⚔️', '🛡', '🚬', '⚰️', '🪦', '⚱️',
    '🏺', '🔮', '📿', '🧿', '💎', '🔔', '🔕', '📯', '🎙', '📢', '📣', '📯',
    '🔔', '🔕', '🎼', '🎵', '🎶', '🎙', '📻', '🎸', '🎷', '🎺', '🎻', '🥁',
    '🎹', '🎛', '🎚', '🎙', '🎤', '🎧', '📻', '📱', '📲', '☎️', '📞', '📟',
    '📠', '🔋', '🔌', '💻', '💽', '💾', '💿', '📀', '🧮', '🎥', '📸', '📷',
    '📹', '📼', '🔍', '🔎', '🕯', '💡', '🔦', '🏮', '📔', '📕', '📖', '📗',
    '📘', '📙', '📚', '📓', '📒', '📃', '📜', '📄', '📰', '🗞', '📑', '🔖',
    '🏷', '💰', '💴', '💵', '💶', '💷', '💸', '💳', '🧾', '💹', '✉️', '📧',
    '📨', '📩', '📤', '📥', '📦', '📫', '📪', '📬', '📭', '📮', '🗳', '✏️',
    '✒️', '🖋', '🖊', '🖌', '🖍', '📝', '💼', '📁', '📂', '🗂', '📅', '📆',
    '🗒', '🗓', '📇', '📈', '📉', '📊', '📋', '📌', '📍', '📎', '🖇', '📏',
    '📐', '✂️', '🗃', '🗄', '🗑', '🔒', '🔓', '🔏', '🔐', '🔑', '🗝', '🔨',
    '⛏', '⚒', '🛠', '🗡', '⚔️', '🔫', '🏹', '🛡', '🔧', '🔩', '⚙️', '🗜',
    '⚖️', '🔗', '⛓', '🧰', '🧲', '🔭', '🔬', '🩺', '🩹', '💊', '💉', '🩸',
    '🧬', '🦠', '🧫', '🧪', '🌡', '🧹', '🧺', '🧻', '🚽', '🚰', '🚿', '🛁',
    '🛀', '🧴', '🧷', '🧹', '🧺', '🧻', '🚽', '🚰', '🚿', '🛁', '🛀', '🧴',
    '🧷', '🧼', '🧽', '🧯', '🛒', '🚬', '⚰️', '🪦', '🧿', '🧸', '🧵', '🧶',
    # 符号
    '❤️', '🧡', '💛', '💚', '💙', '💜', '🖤', '🤍', '🤎', '💔', '❣️', '💕',
    '💞', '💓', '💗', '💖', '💘', '💝', '💟', '☮️', '✝️', '☪️', '🕉', '☸️',
    '✡️', '🔯', '🕎', '☯️', '☦️', '🛐', '⛎', '♈️', '♉️', '♊️', '♋️', '♌️',
    '♍️', '♎️', '♏️', '♐️', '♑️', '♒️', '♓️', '🆔', '⚛️', '🉑', '☢️', '☣️',
    '📴', '📳', '🈶', '🈚️', '🈸', '🈺', '🈷️', '✴️', '🆚', '💮', '🉐', '㊙️',
    '㊗️', '🈴', '🈵', '🈹', '🈲', '🅰️', '🅱️', '🆎', '🆑', '🅾️', '🅿️', '🈳',
    '㊗️', '🈴', '🈵', '🈹', '🈲', '🅰️', '🅱️', '🆎', '🆑', '🅾️', '🅿️', '🈳',
    '㊂', '㊀', '㊁', '🈁', '🈂️', '🛗', '🈳', '🈂️', '🛗', '🈳', '🈳', '🈂️',
    '♀️', '♂️', '⚧️', '✖️', '➕', '➖', '➗', '♾', '‼️', '⁉️', '❓', '❔',
    '❕', '❗️', '〰️', '💱', '💲', '⚕️', '♻️', '⚜️', '🔱', '📛', '🔰', '⭕️',
    '✅', '☑️', '✔️', '❌', '❎', '➰', '➿', '〽️', '✳️', '✴️', '❇️', '©️',
    '®️', '™️', '#️⃣', '*️⃣', '0️⃣', '1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣', '6️⃣',
    '7️⃣', '8️⃣', '9️⃣', '🔟', '🔠', '🔡', '🔢', '🔣', '🔤', '🅰️', '🆎',
    '🅱️', '🆑', '🆒', '🆓', 'ℹ️', '🆔', 'Ⓜ️', '🆕', '🆖', '🆗', '🆘', '🆙',
    '🆚', '🈁', '🈂️', '🈷️', '🈶', '🈯️', '🉐', '🈹', '🈚️', '🈲', '🉑',
    '🈸', '🈴', '🈳', '㊗️', '㊙️', '🈺', '🈵', '▪️', '▫️', '◻️', '◼️', '◽️',
    '◾️', '⬛️', '⬜️', '🔶', '🔷', '🔸', '🔹', '🔺', '🔻', '💠', '🔘', '🔲',
    '🔳', '⚪️', '⚫️', '🔴', '🟠', '🟡', '🟢', '🔵', '🟣', '🟤', '⚪️', '⚫️',
    '🟥', '🟦', '🟧', '🟨', '🟩', '🟪', '⬛️', '⬜️', '◼️', '◻️', '◾️', '◽️',
    '▪️', '▫️', '🔲', '🔳', '💠', '🔘', '🔵', '🟣', '⚫️', '🟤', '🔴', '🟠',
    '🟡', '🟢', '⚪️',
    # 月亮（起卦专用）
    '🌕', '🌑',
    # 旗帜
    '🏳️', '🏴', '🏴‍☠️', '🏁', '🚩', '🏳️‍🌈', '🏳️‍⚧️', '🇺🇳',
    # 其他特殊符号
    '⬆️', '↗️', '➡️', '↘️', '⬇️', '↙️', '⬅️', '↖️', '↕️', '↔️', '↩️', '↪️',
    '⤴️', '⤵️', '🔃', '🔄', '🔙', '🔚', '🔛', '🔜', '🔝', '🛐', '⚛️', '🕉',
    '✡️', '☸️', '☯️', '✝️', '☦️', '☪️', '☮️', '🕎', '🔯', '♈️', '♉️', '♊️',
    '♋️', '♌️', '♍️', '♎️', '♏️', '♐️', '♑️', '♒️', '♓️', '⛎', '🔀', '🔁',
    '🔂', '▶️', '⏩', '⏭', '⏯', '◀️', '⏪', '⏮', '🔼', '⏫', '🔽', '⏬',
    '⏸', '⏹', '⏺', '⏏', '🎦', '🔅', '🔆', '📶', '📳', '📴', '♀️', '♂️',
    '⚧️', '✖️', '➕', '➖', '➗', '♾', '‼️', '⁉️', '❓', '❔', '❕', '❗️',
    '〰️', '💱', '💲', '⚕️', '♻️', '⚜️', '🔱', '📛', '🔰', '⭕️', '✅', '☑️',
    '✔️', '❌', '❎', '➰', '➿', '〽️', '✳️', '✴️', '❇️', '©️', '®️', '™️',
    # 关键测试用例
    '✓', '✔', '☑',
])

# 文字字符正则（汉字、字母、数字）
TEXT_CHAR_PATTERN = re.compile(
    r'[\u4e00-\u9fa5a-zA-Z0-9]',  # 汉字、字母、数字
    re.UNICODE
)


def is_emoji(text: str) -> bool:
    """
    判断是否为纯表情（允许空格分隔多个表情）
    
    纯表情示例：
    - "👍" → True
    - "🌕🌑🌑" → True
    - "🎲 🎲 🎲" → True
    - "[OK]" → False (文字)
    - "好的👍" → False (混合)
    
    逻辑：
    1. 移除空格
    2. 检查是否包含文字字符（汉字、字母、数字）
    3. 如果包含文字字符 → 不是纯表情
    4. 如果不包含文字字符，且至少有一个常见emoji → 是纯表情
    """
    if not text or not text.strip():
        return False
    
    text = text.strip()
    
    # 移除所有空格
    text_no_space = text.replace(" ", "").replace("\t", "").replace("\n", "")
    
    # 如果空字符串，不是表情
    if not text_no_space:
        return False
    
    # 检查是否包含任何文字字符（汉字、字母、数字）
    if TEXT_CHAR_PATTERN.search(text_no_space):
        return False
    
    # 不包含有文字字符，检查是否至少有一个emoji
    # 逐字符检查是否在COMMON_EMOJIS中
    for char in text_no_space:
        if char in COMMON_EMOJIS:
            return True
    
    # 如果没有找到常见emoji，但也没有文字字符
    # 可能是特殊符号，保守起见视为非表情
    return False


def is_text(text: str) -> bool:
    """
    判断是否为文字（非纯表情）
    
    只要有任何文字字符（汉字、字母、数字等），就认为是文字
    
    文字示例：
    - "OK" → True
    - "好的" → True
    - "好的👍" → True (混合视为文字)
    - "👍好的" → True (混合视为文字)
    - "123" → True (数字是文字)
    """
    if not text or not text.strip():
        return False
    
    text = text.strip()
    
    # 如果是纯表情，则不是文字
    if is_emoji(text):
        return False
    
    # 检查是否包含文字字符
    if TEXT_CHAR_PATTERN.search(text):
        return True
    
    # 没有文字字符，但有其他内容（如纯标点），也视为文字
    return True


def get_session() -> Optional[Dict]:
    """读取当前起卦会话状态（带文件锁）"""
    if not os.path.exists(SESSION_FILE):
        return None
    try:
        with open(SESSION_FILE, "r", encoding="utf-8") as f:
            # 获取共享锁（允许多读，但阻止写）
            fcntl.flock(f.fileno(), fcntl.LOCK_SH)
            try:
                session = json.load(f)
            finally:
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)
        # 检查是否超时
        last_update = session.get("last_update", 0)
        if time.time() - last_update > TIMEOUT_SECONDS:
            # 超时，重置（带排他锁）
            try:
                with open(SESSION_FILE, "r+", encoding="utf-8") as f:
                    fcntl.flock(f.fileno(), fcntl.LOCK_EX)
                    try:
                        # 重新检查，避免竞态
                        f.seek(0)
                        session_check = json.load(f)
                        if time.time() - session_check.get("last_update", 0) > TIMEOUT_SECONDS:
                            os.remove(SESSION_FILE)
                    finally:
                        fcntl.flock(f.fileno(), fcntl.LOCK_UN)
            except:
                pass
            return None
        # 未超时，更新last_update延长超时时间（带排他锁）
        session["last_update"] = time.time()
        # 检查必要字段是否存在，缺失则初始化默认值
        required_fields = {"step": 1, "yaos": [], "question": "", "start_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
        for field, default_value in required_fields.items():
            if field not in session:
                session[field] = default_value
        save_session(session)
        return session
    except:
        return None


def save_session(session: Dict):
    """保存起卦会话状态（带文件锁）"""
    session["last_update"] = time.time()
    os.makedirs(os.path.dirname(SESSION_FILE), exist_ok=True)
    # 使用临时文件+原子重命名避免竞态
    temp_file = SESSION_FILE + ".tmp"
    with open(temp_file, "w", encoding="utf-8") as f:
        # 获取排他锁
        fcntl.flock(f.fileno(), fcntl.LOCK_EX)
        try:
            json.dump(session, f, ensure_ascii=False)
            f.flush()
            os.fsync(f.fileno())
        finally:
            fcntl.flock(f.fileno(), fcntl.LOCK_UN)
    # 原子重命名
    os.rename(temp_file, SESSION_FILE)


def clear_session():
    """清除会话状态"""
    if os.path.exists(SESSION_FILE):
        os.remove(SESSION_FILE)


def is_divination_request(user_input: str) -> tuple:
    """
    智能识别是否为起卦请求
    返回：(是否是起卦请求, 提取到的问题)
    
    支持的触发方式：
    1. "起卦 今年能不能升职" - 含触发词+问题
    2. "今年能不能升职起卦" - 问题+触发词
    3. "今年能不能升职？" - 直接问事（自动识别为起卦）
    """
    if not user_input:
        return False, ""
    
    user_input = user_input.strip()
    
    # 检查是否包含显式触发词
    has_trigger = any(trigger in user_input for trigger in DIVINATION_TRIGGERS)
    
    if has_trigger:
        # 提取问题部分（移除触发词）
        question = user_input
        for trigger in DIVINATION_TRIGGERS:
            question = question.replace(trigger, "")
        question = question.strip()
        
        # 如果移除触发词后还有内容，就是问题
        if question:
            # 移除常见的标点
            question = question.lstrip("：:").lstrip("，,").strip()
            return True, question
        else:
            # 只有触发词，没有具体问题
            return True, ""
    
    # 检查是否包含问事特征（没有显式触发词，但内容像问题）
    # 判断依据：包含问事关键词 + 以问号结尾 或 包含疑问词
    has_question_keyword = any(kw in user_input for kw in QUESTION_KEYWORDS)
    ends_with_question = user_input.endswith(("?", "？"))
    has_question_word = any(w in user_input for w in ["吗", "么", "呢", "如何", "怎么样", "能不能", "可不可以", "行不行", "好不好", "能否", "可不可以"])
    
    if has_question_keyword and (ends_with_question or has_question_word):
        # 看起来像问事，但没有触发词
        # 返回True，让调用方决定是否自动识别为起卦
        return True, user_input
    
    return False, ""


def shake_coins() -> tuple:
    """摇三枚硬币"""
    coins = [random.choice(["🌕", "🌑"]) for _ in range(3)]
    return tuple(coins)


def get_yao_type(coins: tuple) -> tuple:
    """根据硬币结果获取爻类型"""
    # 统计阳面数量
    yang_count = coins.count("🌕")
    if yang_count == 3:
        return ("老阳", "⚊", True)  # 老阳动
    elif yang_count == 0:
        return ("老阴", "⚋", True)  # 老阴动
    elif yang_count == 2:
        return ("少阳", "⚊", False)  # 少阳
    else:
        return ("少阴", "⚋", False)  # 少阴


def format_coins(coins: tuple) -> str:
    """格式化硬币显示"""
    return "".join(coins)


def start_divination(question: str = ""):
    """
    开始新的起卦流程（优化版）
    简化流程，快速进入摇卦节奏
    """
    # 清除旧会话（防止干扰）
    clear_session()
    
    session = {
        "step": 1,  # 直接设为1，从第一次摇卦开始
        "yaos": [],
        "question": question,
        "start_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    save_session(session)
    
    # 优化后的输出格式，更紧凑，快速进入节奏
    response = ""
    if question:
        response += f"💭 您的问题：{question}\n\n"
    
    response += f"🎲 请发送「{TRIGGER_WORD}」开始摇卦（第1次/共6次）："
    
    return response


def process_one_step(user_input: str, session: Dict) -> tuple:
    """
    处理一次摇卦步骤（核心函数，只处理1步）
    
    返回：(响应文本, 是否完成)
    是否完成：True = 6次已完成，False = 还有更多步骤
    """
    step = session["step"]
    yaos = session["yaos"]
    
    # 安全检查：step范围
    if step < 1 or step > 6:
        clear_session()  # 修复：清理会话避免死循环
        return "状态异常，已重置。请重新开始起卦。", True
    
    # 摇硬币
    coins = shake_coins()
    yao_type, symbol, is_dong = get_yao_type(coins)
    
    # 记录爻
    yao_info = {
        "yao_name": YAO_NAMES[step - 1],
        "type": yao_type,
        "symbol": symbol,
        "dong": is_dong,
        "coins": format_coins(coins)
    }
    yaos.append(yao_info)
    
    # 构建响应（紧凑格式）
    response = f"第{step}次（{YAO_NAMES[step - 1]}）：{format_coins(coins)} → {yao_type} {symbol}"
    
    if is_dong:
        response += " ← 动爻"
    
    if step < 6:
        # 继续下一步
        session["step"] = step + 1
        session["yaos"] = yaos
        save_session(session)
        response += f"\n\n请发送「{TRIGGER_WORD}」继续（第{step + 1}次/共6次）："
        return response, False  # 未完成
    else:
        # 完成，更新session但不清除（complete_divination会清除）
        session["yaos"] = yaos
        save_session(session)
        return response, True  # 已完成


def process_step(user_input: str) -> str:
    """
    处理当前摇卦步骤（对外接口）
    确保每次只处理一步，step正确递增
    
    参数：
        user_input: 用户输入（应该是纯表情）
    
    返回：响应文本
    """
    session = get_session()
    
    if session is None:
        # 没有活跃会话，但用户可能是在尝试继续
        # 尝试智能识别为新的起卦请求
        is_div, question = is_divination_request(user_input)
        if is_div:
            return start_divination(question)
        return "当前没有进行中的起卦。发送「起卦」或您的问题开始新的摇卦。"
    
    # 调用核心处理函数
    response, is_complete = process_one_step(user_input, session)
    
    if is_complete:
        # 完成解读
        return complete_divination(session)
    
    return response


def complete_divination(session: Dict) -> str:
    """完成起卦，调用解读"""
    yaos = session["yaos"]
    question = session.get("question", "")
    
    # 构建解读输入
    output = ["# 🎯 六爻起卦完成\n\n"]
    
    if question:
        output.append(f"**所问之事**：{question}\n\n")
    
    output.append(f"起卦时间：{session.get('start_time', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))}\n\n")
    output.append("## 摇卦记录\n")
    
    for i, yao in enumerate(yaos):
        dong_mark = " ← 动爻" if yao["dong"] else ""
        output.append(f"{yao['yao_name']}：{yao['coins']} → {yao['type']} {yao['symbol']}{dong_mark}\n")
    
    output.append("\n## 卦象\n```")
    # 从下到上显示
    for yao in yaos:
        dong_mark = " (动)" if yao["dong"] else ""
        output.append(f"{yao['yao_name']}：{yao['symbol']}{dong_mark}")
    output.append("```\n")
    
    # 构建给liuyao_interpret.py的输入格式（包含问题）
    interpret_input = build_interpret_input(yaos, question)
    
    # 调用解读脚本
    interpret_result = interpret_direct(interpret_input)
    
    # 清除会话
    clear_session()
    
    result = "".join(output)
    result += "\n---\n\n## 卦象解读\n"
    result += interpret_result
    
    return result


def build_interpret_input(yaos: List[Dict], question: str = "") -> str:
    """构建解读脚本所需的输入格式"""
    lines = []
    
    # 先加问题
    if question:
        lines.append(question)
        lines.append("")
    
    # 爻是从初爻到上爻记录的，输出时从上到下
    for yao in reversed(yaos):
        dong_suffix = "动" if yao["dong"] else ""
        lines.append(f"{yao['yao_name']}：{yao['type']}{dong_suffix}")
    
    return "\n".join(lines)


def get_status() -> str:
    """获取当前起卦状态"""
    session = get_session()
    if session is None:
        return "当前没有进行中的起卦。发送「起卦」或您的问题开始新的摇卦。"
    
    step = session["step"]
    yaos = session["yaos"]
    question = session.get("question", "")
    
    output = []
    if question:
        output.append(f"💭 问题：{question}\n")
    output.append(f"当前进度：第{step}次/共6次\n\n")
    
    if yaos:
        output.append("已记录的爻：\n")
        for yao in yaos:
            dong_mark = " (动)" if yao["dong"] else ""
            output.append(f"  {yao['yao_name']}：{yao['coins']} → {yao['type']}{dong_mark}\n")
        output.append("\n")
    
    output.append(f"请发送「{TRIGGER_WORD}」继续第{step}次摇卦。")
    return "".join(output)


def interpret_direct(user_input: str) -> str:
    """直接解读模式（保留原有功能）"""
    # 调用liuyao_interpret.py进行解读
    import subprocess
    script_dir = os.path.dirname(os.path.abspath(__file__))
    interpret_script = os.path.join(script_dir, "liuyao_interpret.py")
    
    try:
        result = subprocess.run(
            ["python3", interpret_script],
            input=user_input,
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=30  # 修复：添加超时参数防止死锁
        )
        if result.returncode == 0:
            return result.stdout
        else:
            return f"解读失败：{result.stderr}"
    except Exception as e:
        return f"调用解读脚本失败：{e}"


def handle_user_input(user_input: str) -> str:
    """
    智能处理用户输入（核心入口）
    
    输入规则（严格）：
    1. 笑脸表情 😊 → 继续摇卦，每次只处理1步
    2. 其他表情（👍🎉🌕🌑等）→ 提示错误，要求发送😊
    3. 文字输入（包括纯文字、混合内容）→ 打断流程，询问用户意图
    
    场景：
    1. 有活跃会话 + 😊 → 处理1次摇卦
    2. 有活跃会话 + 其他表情 → 提示"请发送笑脸表情😊继续"
    3. 有活跃会话 + 文字输入 → 打断，询问用户意图
    4. 无会话 + 起卦请求 → 开始新起卦
    5. 无会话 + 其他输入 → 返回提示
    """
    user_input = user_input.strip() if user_input else ""
    
    # 检查是否有活跃会话
    session = get_session()
    
    if session is not None:
        # 有活跃会话
        # 关键判断：必须是笑脸表情😊才能继续
        if user_input == TRIGGER_WORD:
            # 心想事成 → 继续摇卦（只处理1步）
            return process_step(user_input)
        elif is_emoji(user_input):
            # 其他表情 → 提示错误
            return f"❌ 请发送「{TRIGGER_WORD}」继续摇卦（每次发这四个字）"
        else:
            # 文字输入（包括混合内容）→ 打断流程
            return f"【打断】检测到文字输入「{user_input}」，已暂停起卦。您想说什么？\n\n如需继续起卦，请发送「{TRIGGER_WORD}」；如要重新开始，发送「起卦」。"
    
    # 无活跃会话，尝试识别为起卦请求
    is_div, question = is_divination_request(user_input)
    
    if is_div:
        return start_divination(question)
    
    # 不是起卦请求，返回提示
    return "发送「起卦」或您想问的问题（如「今年能不能升职？」）开始摇卦。"


def main():
    """主入口"""
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "start":
            # 开始新起卦，可以带问题
            question = sys.argv[2] if len(sys.argv) > 2 else ""
            print(start_divination(question))
        elif command == "step":
            # 处理一步（仅内部使用，不对外暴露）
            user_input = sys.argv[2] if len(sys.argv) > 2 else ""
            print(process_step(user_input))
        elif command == "status":
            print(get_status())
        elif command == "clear":
            clear_session()
            print("已重置起卦状态。")
        elif command == "check":
            # 智能识别输入
            user_input = sys.argv[2] if len(sys.argv) > 2 else ""
            is_div, question = is_divination_request(user_input)
            print(f"是起卦请求: {is_div}")
            print(f"提取的问题: {question}")
        elif command == "test_emoji":
            # 测试表情识别
            user_input = sys.argv[2] if len(sys.argv) > 2 else ""
            print(f"输入: {user_input}")
            print(f"is_emoji: {is_emoji(user_input)}")
            print(f"is_text: {is_text(user_input)}")
        elif command == "handle":
            # 智能处理（推荐入口）
            user_input = sys.argv[2] if len(sys.argv) > 2 else ""
            print(handle_user_input(user_input))
        elif command == "interpret":
            # 直接解读
            if len(sys.argv) > 2:
                with open(sys.argv[2], "r", encoding="utf-8") as f:
                    content = f.read()
                print(interpret_direct(content))
            else:
                content = sys.stdin.read()
                print(interpret_direct(content))
        else:
            # 未知命令，尝试作为用户输入处理
            print(handle_user_input(command))
    else:
        print("六爻交互式起卦（修复版）")
        print("用法：python3 liuyao_interactive.py <command>")
        print("")
        print("命令：")
        print("  start [问题]       - 开始新的起卦")
        print("  status             - 查看当前起卦状态")
        print("  clear              - 重置起卦状态")
        print("  check <输入>       - 测试智能识别")
        print("  test_emoji <输入>  - 测试表情识别")
        print("  handle <输入>      - 智能处理（推荐）")
        print("  interpret          - 直接解读输入")


if __name__ == "__main__":
    main()
