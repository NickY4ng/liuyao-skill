#!/usr/bin/env python3
"""
六爻卦象解读脚本 v3 - P1功能完善
- 六神系统完善
- 旺衰判断增强（日建+动爻生克+化进化退）
输入：用户问题 + 6个爻的阴阳结果
输出：完整卦象解读
"""

import json
import sys
import re
import os
from datetime import datetime
from typing import Dict, List, Tuple, Optional

# 加载数据
def load_data():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(script_dir, "..", "data")

    with open(os.path.join(data_dir, "hexagrams_full.json"), "r", encoding="utf-8") as f:
        hexagrams = json.load(f)
    with open(os.path.join(data_dir, "naga.json"), "r", encoding="utf-8") as f:
        naga = json.load(f)
    with open(os.path.join(data_dir, "yongshen_rules.json"), "r", encoding="utf-8") as f:
        yongshen_rules = json.load(f)
    return hexagrams, naga, yongshen_rules


class LiuYaoInterpreter:
    """六爻解读器"""

    # 爻符号映射
    YAO_SYMBOLS = {
        "老阳": {"yang": True, "dong": True, "symbol": "⚊", "bian": "阴"},
        "老阴": {"yang": False, "dong": True, "symbol": "⚋", "bian": "阳"},
        "少阳": {"yang": True, "dong": False, "symbol": "⚊", "bian": None},
        "少阴": {"yang": False, "dong": False, "symbol": "⚋", "bian": None},
    }

    # 爻位名称（从下往上）
    YAO_NAMES = ["初爻", "二爻", "三爻", "四爻", "五爻", "上爻"]

    # 六神（六兽）顺序 - 固定顺序
    LIUSHOU_ORDER = ["青龙", "朱雀", "勾陈", "螣蛇", "白虎", "玄武"]
    
    # 日干对应六神起始位置
    # 甲乙日起青龙，丙丁日起朱雀，戊日起勾陈，己日起螣蛇，庚辛日起白虎，壬癸日起玄武
    LIUSHOU_START = {
        "甲": 0, "乙": 0,  # 青龙开始
        "丙": 1, "丁": 1,  # 朱雀开始
        "戊": 2,          # 勾陈开始
        "己": 3,          # 螣蛇开始
        "庚": 4, "辛": 4,  # 白虎开始
        "壬": 5, "癸": 5,  # 玄武开始
    }

    # 五行生克关系
    WUXING_SHENG = {"木": "火", "火": "土", "土": "金", "金": "水", "水": "木"}
    WUXING_KE = {"木": "土", "火": "金", "土": "水", "金": "木", "水": "火"}

    # 地支十二长生状态（简化版）
    # 用于判断化进化退
    ZHI_ORDER = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]

    def __init__(self):
        self.hexagrams_data, self.naga_data, self.yongshen_rules = load_data()
        self.question = ""
        self.yao_results = []
        self.hexagram = None
        self.bian_hexagram = None
        self.dong_yao_indices = []
        self.day_gan = None  # 起卦日天干，用于六神计算
        self.day_zhi = None  # 起卦日支

    def get_current_day_gan_zhi(self) -> Tuple[str, str]:
        """获取当前日期的天干地支（简化计算）
        
        使用近似公式计算，实际应用中可以接入农历库
        这里使用基于1900年1月31日（甲辰日）的偏移计算
        """
        # 简化：使用当前日期计算偏移
        base_date = datetime(1900, 1, 31)  # 甲辰日
        now = datetime.now()
        days_diff = (now - base_date).days
        
        # 天干10个一轮
        gan_list = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]
        # 地支12个一轮  
        zhi_list = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]
        
        gan_idx = days_diff % 10
        zhi_idx = days_diff % 12
        
        return gan_list[gan_idx], zhi_list[zhi_idx]

    def set_day_gan(self, day_gan: str):
        """设置起卦日天干，用于六神计算"""
        if day_gan in ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]:
            self.day_gan = day_gan

    def set_day_zhi(self, day_zhi: str):
        """设置起卦日支"""
        if day_zhi in self.ZHI_ORDER:
            self.day_zhi = day_zhi

    def get_liushou_for_yao(self, pos_idx: int) -> str:
        """获取爻的六神（六兽）
        
        六神根据起卦日的天干确定起始位置，然后按顺序从初爻排到上爻
        """
        if not self.day_gan:
            return ""
        
        start_idx = self.LIUSHOU_START.get(self.day_gan, 0)
        # 从初爻开始排，所以位置是 (start_idx + pos_idx) % 6
        liushou_idx = (start_idx + pos_idx) % 6
        return self.LIUSHOU_ORDER[liushou_idx]

    def parse_input(self, user_input: str) -> bool:
        """解析用户输入"""
        lines = user_input.strip().split("\n")
        if not lines:
            return False

        self.question = lines[0].strip()

        yao_lines = []
        for line in lines[1:]:
            line = line.strip()
            if "爻" in line and ("阳" in line or "阴" in line):
                yao_lines.append(line)

        if len(yao_lines) != 6:
            # 修复：第二次匹配前清空 yao_lines，避免重复累积
            yao_lines = []
            for line in lines[1:]:
                if re.match(r"^[上五四三二初]爻[：:]\s*[\u4e00-\u9fa5]+", line):
                    yao_lines.append(line)

        if len(yao_lines) != 6:
            print(f"错误：需要6个爻的信息，找到{len(yao_lines)}个")
            return False

        self.yao_results = []
        for i, line in enumerate(yao_lines):
            # 简化解析：统一提取爻位和爻类型
            match = re.search(r"([上五四三二初])爻[：:\s]*([少老][阴阳])", line)
            if match:
                yao_pos = match.group(1)
                yao_type = match.group(2)  # 如 "少阳"、"老阳"
                
                # 判断是否为动爻：包含"老阳"或"老阴"，或行中有"动"字
                is_dong = yao_type in ["老阳", "老阴"] or "动" in line
                
                pos_map = {"初": 0, "二": 1, "三": 2, "四": 3, "五": 4, "上": 5}
                pos_idx = pos_map.get(yao_pos, i)
                yao_info = self.YAO_SYMBOLS.get(yao_type, {})
                if not yao_info:
                    continue
                
                self.yao_results.append({
                    "yao_name": self.YAO_NAMES[pos_idx],
                    "pos_idx": pos_idx,
                    "type": yao_type,
                    "yang": yao_info["yang"],
                    "dong": is_dong,
                    "symbol": "⚊" if yao_info["yang"] else "⚋",
                    "bian": yao_info.get("bian"),
                })
                if is_dong:
                    self.dong_yao_indices.append(pos_idx)

        if len(self.yao_results) != 6:
            return False

        self.yao_results.sort(key=lambda x: x["pos_idx"])
        return True

    def get_guaxiang_full(self) -> str:
        """获取完整6位卦象字符串（上爻在前）"""
        symbols = [y["symbol"] for y in self.yao_results]  # 0=初爻, 5=上爻
        return "".join(reversed(symbols))  # reversed: 上爻在前

    def find_hexagram(self) -> Optional[Dict]:
        """查找对应卦象 - 使用完整6位符号串查找"""
        guaxiang_full = self.get_guaxiang_full()
        hexagrams = self.hexagrams_data.get("hexagrams", {})

        # 直接用guaxiang_full查找
        for key, info in hexagrams.items():
            if info.get("guaxiang_full") == guaxiang_full:
                return info

        return None

    def get_bian_hexagram(self) -> Optional[Dict]:
        """获取变卦"""
        if not self.dong_yao_indices:
            return None

        bian_yao_results = []
        for yao in self.yao_results:
            if yao["dong"] and yao["bian"]:
                new_symbol = "⚋" if yao["yang"] else "⚊"
                bian_yao_results.append(new_symbol)
            else:
                bian_yao_results.append(yao["symbol"])

        bian_guaxiang = "".join(reversed(bian_yao_results))
        hexagrams = self.hexagrams_data.get("hexagrams", {})

        for key, info in hexagrams.items():
            if info.get("guaxiang_full") == bian_guaxiang:
                return info

        return {"name": "变卦", "guaxiang_full": "".join(bian_yao_results[::-1])}

    def get_naga_for_yao(self, yao_info: Dict, hexagram_info: Dict) -> Dict:
        """获取爻的纳甲信息 - 完善六亲推演"""
        pos = yao_info["pos_idx"]
        gong = hexagram_info.get("gong", "?")  # 卦宫

        # 获取内外卦
        if pos < 3:
            bagua = hexagram_info.get("neigua", "?")  # 内卦（初爻到三爻）
        else:
            bagua = hexagram_info.get("waigua", "?")  # 外卦（四爻到六爻）

        # 从纳甲数据获取干支信息
        naga_song = self.naga_data.get("naga_song", {})
        bagua_name = self.hexagrams_data.get("gua_xiang_decode", {}).get(bagua, bagua)
        bagua_info = naga_song.get(bagua_name, {})

        if not bagua_info:
            return {"gan": "?", "zhi": "?", "wuxing": "?", "liuqin": "?", "bagua": bagua}

        # 确定内外卦的干支
        if pos < 3:  # 内卦：初、二、三爻
            gan = bagua_info.get("neigua", {}).get("gan", "?")
            zhi_list = bagua_info.get("neigua", {}).get("zhi", [])
        else:  # 外卦：四、五、六爻
            gan = bagua_info.get("waigua", {}).get("gan", "?")
            zhi_list = bagua_info.get("waigua", {}).get("zhi", [])

        local_pos = pos % 3  # 0,1,2 对应初/二/三爻或四/五/六爻
        zhi = zhi_list[local_pos] if local_pos < len(zhi_list) else "?"

        # 获取五行
        gan_wuxing = self.naga_data.get("gan_wuxing", {}).get(gan, "?")
        zhi_wuxing = self.naga_data.get("zhi_wuxing", {}).get(zhi, "?")
        
        # 获取卦宫五行（六亲推演的基准）
        # 卦宫名称去掉"宫"字得到八卦名
        gong_bagua = gong.replace("宫", "")
        gong_wuxing = self.hexagrams_data.get("bagua_wuxing", {}).get(
            self._get_gua_symbol(gong_bagua), "?"
        )

        # 六亲推演规则（以卦宫五行为"我"）：
        # 同我者为兄弟，生我者为父母，我生者为子孙，克我者为官鬼，我克者为妻财
        liuqin = self._calculate_liuqin(gong_wuxing, zhi_wuxing)

        return {
            "gan": gan,
            "zhi": zhi,
            "gan_wuxing": gan_wuxing,
            "zhi_wuxing": zhi_wuxing,
            "liuqin": liuqin,
            "bagua": bagua,
            "gong_wuxing": gong_wuxing
        }

    def _get_gua_symbol(self, bagua_name: str) -> str:
        """根据八卦名获取卦象符号"""
        gua_map = {
            "乾": "☰", "坤": "☷", "震": "☳", "艮": "☶",
            "巽": "☴", "坎": "☵", "离": "☲", "兑": "☱"
        }
        return gua_map.get(bagua_name, "?")

    def _calculate_liuqin(self, gong_wuxing: str, zhi_wuxing: str) -> str:
        """计算六亲关系
        
        以卦宫五行为"我"，六亲规则：
        - 同我者为兄弟
        - 生我者为父母
        - 我生者为子孙  
        - 克我者为官鬼
        - 我克者为妻财
        """
        if gong_wuxing == "?" or zhi_wuxing == "?":
            return "?"
        
        if gong_wuxing == zhi_wuxing:
            return "兄弟"
        
        # 生我者（zhi生gong）
        if self.WUXING_SHENG.get(zhi_wuxing) == gong_wuxing:
            return "父母"
        
        # 我生者（gong生zhi）
        if self.WUXING_SHENG.get(gong_wuxing) == zhi_wuxing:
            return "子孙"
        
        # 克我者（zhi克gong）
        if self.WUXING_KE.get(zhi_wuxing) == gong_wuxing:
            return "官鬼"
        
        # 我克者（gong克zhi）
        if self.WUXING_KE.get(gong_wuxing) == zhi_wuxing:
            return "妻财"
        
        return "?"

    def _get_wuxing_shengke(self, wuxing1: str, wuxing2: str) -> str:
        """判断两个五行的生克关系
        
        返回："生"（wuxing1生wuxing2）、"克"（wuxing1克wuxing2）、
              "被生"（wuxing2生wuxing1）、"被克"（wuxing2克wuxing1）、"同"（相同）
        """
        if wuxing1 == wuxing2:
            return "同"
        
        if self.WUXING_SHENG.get(wuxing1) == wuxing2:
            return "生"
        
        if self.WUXING_KE.get(wuxing1) == wuxing2:
            return "克"
        
        if self.WUXING_SHENG.get(wuxing2) == wuxing1:
            return "被生"
        
        if self.WUXING_KE.get(wuxing2) == wuxing1:
            return "被克"
        
        return "无"

    def get_shi_ying(self, hexagram_info: Dict) -> Dict:
        """获取世应位置 - 根据卦的 position 字段确定"""
        position = hexagram_info.get("position", "")
        
        # 世应位置规则：
        # 本宫首卦（八纯卦）：六爻为世，三爻为应
        # 一世卦：初爻为世，四爻为应
        # 二世卦：二爻为世，五爻为应
        # 三世卦：三爻为世，六爻为应
        # 四世卦：四爻为世，初爻为应
        # 五世卦：五爻为世，二爻为应
        # 游魂卦：四爻为世，初爻为应（与世在四世卦相同）
        # 归魂卦：三爻为世，六爻为应（与世在三世卦相同）
        
        position_map = {
            "本宫首卦": {"shi": 5, "ying": 2},  # 六爻世，三爻应
            "一世卦": {"shi": 0, "ying": 3},   # 初爻世，四爻应
            "二世卦": {"shi": 1, "ying": 4},   # 二爻世，五爻应
            "三世卦": {"shi": 2, "ying": 5},   # 三爻世，六爻应
            "四世卦": {"shi": 3, "ying": 0},    # 四爻世，初爻应
            "五世卦": {"shi": 4, "ying": 1},    # 五爻世，二爻应
            "游魂卦": {"shi": 3, "ying": 0},    # 游魂四爻世，初爻应（同四世卦）
            "归魂卦": {"shi": 2, "ying": 5},    # 归魂三爻世，六爻应（同三世卦）
        }
        
        pos = position_map.get(position, {"shi": 5, "ying": 2})
        return {
            "shi": self.YAO_NAMES[pos["shi"]],
            "ying": self.YAO_NAMES[pos["ying"]],
            "position": position
        }

    def get_yongshen(self) -> Dict:
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

    def get_yongshen_yao(self, yongshen_liuqin: str, hexagram_info: Dict) -> List[Dict]:
        """获取卦中所有用神爻（根据六亲找）
        
        返回用神爻列表，包含爻位、五行等信息
        """
        yongshen_yaos = []
        
        for yao in self.yao_results:
            naga = self.get_naga_for_yao(yao, hexagram_info)
            if naga.get("liuqin") == yongshen_liuqin:
                yongshen_yaos.append({
                    "yao": yao,
                    "naga": naga,
                    "pos_idx": yao["pos_idx"],
                    "yao_name": yao["yao_name"]
                })
        
        return yongshen_yaos

    def analyze_wangshuai(self, hexagram_info: Dict) -> Dict:
        """分析旺衰 - P1增强版
        
        增强点：
        1. 日建（日令）对爻的影响
        2. 动爻生克对旺衰的影响
        3. 动而化进/化退的初步判断
        """
        # 获取当前时间信息
        now = datetime.now()
        month_zhi = self._get_month_zhi(now.month)
        
        # 优先使用设置的日支，否则使用当前日
        if not self.day_zhi:
            self.day_zhi = self._get_day_zhi(now.day)
        if not self.day_gan:
            self.day_gan, _ = self.get_current_day_gan_zhi()
        
        day_gan_zhi = f"{self.day_gan}{self.day_zhi}"

        # 获取月令旺相休囚死
        yueling_wangxiang = self._get_yueling_wangxiang(month_zhi)
        
        # 获取用神
        yongshen = self.get_yongshen()
        yongshen_liuqin = yongshen.get("primary", "官鬼爻").replace("爻", "")
        yongshen_yaos = self.get_yongshen_yao(yongshen_liuqin, hexagram_info)
        
        # 分析用神旺衰
        yongshen_analysis = []
        for ys in yongshen_yaos:
            naga = ys["naga"]
            yao = ys["yao"]
            analysis = self._analyze_single_yao_wangshuai(
                yao, naga, month_zhi, self.day_zhi, hexagram_info
            )
            yongshen_analysis.append({
                "yao_name": ys["yao_name"],
                "liuqin": naga.get("liuqin", "?"),
                "wuxing": naga.get("zhi_wuxing", "?"),
                "zhi": naga.get("zhi", "?"),
                **analysis
            })
        
        # 分析动爻影响
        dong_yao_effects = self._analyze_dong_yao_effects(hexagram_info)
        
        return {
            "month_zhi": month_zhi,
            "day_gan_zhi": day_gan_zhi,
            "yueling_wangxiang": yueling_wangxiang,
            "yongshen": yongshen_liuqin,
            "yongshen_analysis": yongshen_analysis,
            "dong_yao_effects": dong_yao_effects,
        }

    def _get_yueling_wangxiang(self, month_zhi: str) -> str:
        """获取月令的旺相五行"""
        yueling_map = {
            "寅": "木旺火相", "卯": "木旺火相",
            "巳": "火旺土相", "午": "火旺土相",
            "申": "金旺水相", "酉": "金旺水相",
            "亥": "水旺木相", "子": "水旺木相",
            "辰": "土旺金相", "戌": "土旺金相",
            "丑": "土旺金相", "未": "土旺金相",
        }
        return yueling_map.get(month_zhi, "未知")

    def _get_wangshuai_level(self, wuxing: str, month_zhi: str, day_zhi: str) -> Tuple[str, str]:
        """判断五行在月令日建下的旺衰程度
        
        返回：(旺衰级别, 判断依据)
        """
        # 月令影响（主要）
        yueling_status = {
            "寅": {"旺": ["木"], "相": ["火"], "休": ["水"], "囚": ["金"], "死": ["土"]},
            "卯": {"旺": ["木"], "相": ["火"], "休": ["水"], "囚": ["金"], "死": ["土"]},
            "巳": {"旺": ["火"], "相": ["土"], "休": ["木"], "囚": ["水"], "死": ["金"]},
            "午": {"旺": ["火"], "相": ["土"], "休": ["木"], "囚": ["水"], "死": ["金"]},
            "申": {"旺": ["金"], "相": ["水"], "休": ["土"], "囚": ["火"], "死": ["木"]},
            "酉": {"旺": ["金"], "相": ["水"], "休": ["土"], "囚": ["火"], "死": ["木"]},
            "亥": {"旺": ["水"], "相": ["木"], "休": ["金"], "囚": ["土"], "死": ["火"]},
            "子": {"旺": ["水"], "相": ["木"], "休": ["金"], "囚": ["土"], "死": ["火"]},
            "辰": {"旺": ["土"], "相": ["金"], "休": ["火"], "囚": ["木"], "死": ["水"]},
            "戌": {"旺": ["土"], "相": ["金"], "休": ["火"], "囚": ["木"], "死": ["水"]},
            "丑": {"旺": ["土"], "相": ["金"], "休": ["火"], "囚": ["木"], "死": ["水"]},
            "未": {"旺": ["土"], "相": ["金"], "休": ["火"], "囚": ["木"], "死": ["水"]},
        }
        
        status_table = yueling_status.get(month_zhi, {})
        yueling_result = "平"
        for status, wuxing_list in status_table.items():
            if wuxing in wuxing_list:
                yueling_result = status
                break
        
        # 日建影响（辅助）
        day_zhi_wuxing = self.naga_data.get("zhi_wuxing", {}).get(day_zhi, "")
        day_effect = ""
        
        if day_zhi_wuxing == wuxing:
            day_effect = "日建同五行，得扶助"
        elif self.WUXING_SHENG.get(day_zhi_wuxing) == wuxing:
            day_effect = f"日建{day_zhi}({day_zhi_wuxing})生{wuxing}"
        elif self.WUXING_KE.get(day_zhi_wuxing) == wuxing:
            day_effect = f"日建{day_zhi}({day_zhi_wuxing})克{wuxing}"
        else:
            day_effect = "日建无明显作用"
        
        # 综合判断
        if yueling_result == "旺":
            overall = "旺相有力"
        elif yueling_result == "相":
            overall = "旺相"
        elif yueling_result == "休":
            overall = "稍弱"
        elif yueling_result == "囚":
            overall = "休囚"
        elif yueling_result == "死":
            overall = "休囚无力"
        else:
            overall = "中等"
        
        # 日建可以调整判断
        if "生" in day_effect and yueling_result in ["休", "囚", "死"]:
            overall = "中等偏旺"
        elif "克" in day_effect and yueling_result in ["旺", "相"]:
            overall = "旺中带忧"
        
        basis = f"月令{yueling_result}，{day_effect}"
        return overall, basis

    def _analyze_single_yao_wangshuai(self, yao: Dict, naga: Dict, month_zhi: str, day_zhi: str, hexagram_info: Dict) -> Dict:
        """分析单个爻的旺衰情况"""
        wuxing = naga.get("zhi_wuxing", "?")
        zhi = naga.get("zhi", "?")
        
        # 基础旺衰
        overall, basis = self._get_wangshuai_level(wuxing, month_zhi, day_zhi)
        
        # 是否为动爻
        is_dong = yao.get("dong", False)
        
        # 动而化进化退判断
        hua_info = None
        if is_dong:
            hua_info = self._analyze_hua_jin_tui(yao, naga)
        
        return {
            "wuxing": wuxing,
            "zhi": zhi,
            "overall": overall,
            "basis": basis,
            "is_dong": is_dong,
            "hua_info": hua_info,
        }

    def _analyze_hua_jin_tui(self, yao: Dict, naga: Dict) -> Optional[Dict]:
        """分析动爻化进化退
        
        化进：化出之爻与动爻同类且地支前进（如寅化卯）
        化退：化出之爻与动爻同类且地支后退（如卯化寅）
        """
        if not yao.get("dong"):
            return None
        
        # 获取变卦中对应位置的爻
        # 变卦的爻是原卦动爻阴阳互换后的结果
        # 这里简化处理，假设变卦已经生成
        
        # 实际上化进化退需要查看变卦的六亲
        # 简化：根据爻的阴阳变化判断可能的化进化退
        # 真正需要完整的变卦数据才能准确判断
        
        return {
            "note": "动爻，需结合变卦六亲进一步判断化进化退"
        }

    def _analyze_dong_yao_effects(self, hexagram_info: Dict) -> List[Dict]:
        """分析动爻对用神的生克影响"""
        effects = []
        
        # 获取用神五行
        yongshen = self.get_yongshen()
        yongshen_liuqin = yongshen.get("primary", "官鬼爻").replace("爻", "")
        
        # 获取所有用神爻的五行
        yongshen_yaos = self.get_yongshen_yao(yongshen_liuqin, hexagram_info)
        if not yongshen_yaos:
            return effects
        
        yongshen_wuxing = yongshen_yaos[0]["naga"].get("zhi_wuxing", "?")
        
        # 分析每个动爻对用神的影响
        for pos_idx in self.dong_yao_indices:
            yao = self.yao_results[pos_idx]
            naga = self.get_naga_for_yao(yao, hexagram_info)
            dong_wuxing = naga.get("zhi_wuxing", "?")
            liuqin = naga.get("liuqin", "?")
            
            # 判断生克关系
            shengke = self._get_wuxing_shengke(dong_wuxing, yongshen_wuxing)
            
            effect_desc = ""
            if shengke == "生":
                effect_desc = f"动爻{yao['yao_name']}({liuqin}·{dong_wuxing})生用神({yongshen_wuxing})，用神得助更旺"
            elif shengke == "克":
                effect_desc = f"动爻{yao['yao_name']}({liuqin}·{dong_wuxing})克用神({yongshen_wuxing})，用神受制"
            elif shengke == "同":
                effect_desc = f"动爻{yao['yao_name']}({liuqin}·{dong_wuxing})与用神同五行，比劫相助"
            else:
                effect_desc = f"动爻{yao['yao_name']}({liuqin}·{dong_wuxing})与用神{shengke}"
            
            effects.append({
                "yao_name": yao["yao_name"],
                "liuqin": liuqin,
                "wuxing": dong_wuxing,
                "shengke": shengke,
                "effect": effect_desc,
            })
        
        return effects

    def _get_month_zhi(self, month: int) -> str:
        """获取月支"""
        zhi_list = ["寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥", "子", "丑"]
        return zhi_list[month - 1]

    def _get_day_zhi(self, day: int) -> str:
        """获取日支（简化）"""
        zhi_list = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]
        return zhi_list[(day - 1) % 12]

    def check_patterns(self, hexagram_info: Dict) -> List[str]:
        """检查格局"""
        patterns = []
        hexagram_name = hexagram_info.get("name", "")
        liushou = self.yongshen_rules.get("liushou_patterns", {})
        for p_name, p_list in liushou.items():
            if hexagram_name in p_list:
                patterns.append(p_name)
        return patterns

    def generate_liushou_section(self) -> str:
        """生成六神装卦部分"""
        if not self.day_gan:
            self.day_gan, _ = self.get_current_day_gan_zhi()
        
        output = []
        output.append("\n## 六神装卦\n")
        output.append(f"**起卦日**：{self.day_gan}日\n\n")
        
        # 六神顺序：从初爻到上爻
        # 但根据显示要求，输出格式是从上爻到初爻
        for i in range(5, -1, -1):  # 5,4,3,2,1,0 对应上爻到初爻
            yao_name = self.YAO_NAMES[i]
            liushou = self.get_liushou_for_yao(i)
            output.append(f"- {yao_name}：{liushou}\n")
        
        return "".join(output)

    def generate_wangshuai_section(self, hexagram_info: Dict) -> str:
        """生成旺衰判断部分"""
        wangshuai = self.analyze_wangshuai(hexagram_info)
        
        output = []
        output.append("\n## 六、旺衰判断\n")
        output.append(f"**月令**：{wangshuai['month_zhi']}月（{wangshuai['yueling_wangxiang']}）\n")
        output.append(f"**日建**：{wangshuai['day_gan_zhi']}日\n\n")
        
        # 用神旺衰分析
        yongshen_analysis = wangshuai.get("yongshen_analysis", [])
        if yongshen_analysis:
            output.append(f"**用神「{wangshuai['yongshen']}」旺衰分析**：\n\n")
            for analysis in yongshen_analysis:
                output.append(f"- **{analysis['yao_name']}**（{analysis['liuqin']}·{analysis['zhi']}·{analysis['wuxing']}）：\n")
                output.append(f"  - 旺衰：**{analysis['overall']}**\n")
                output.append(f"  - 依据：{analysis['basis']}\n")
                
                # 动爻信息
                if analysis.get("is_dong"):
                    output.append(f"  - 状态：**动爻**\n")
                    if analysis.get("hua_info"):
                        output.append(f"  - 化变：{analysis['hua_info'].get('note', '')}\n")
                output.append("\n")
        
        # 动爻影响
        dong_effects = wangshuai.get("dong_yao_effects", [])
        if dong_effects:
            output.append("**动爻生克影响**：\n\n")
            for effect in dong_effects:
                output.append(f"- {effect['effect']}\n")
            output.append("\n")
        
        # 综合判断
        if yongshen_analysis:
            # 综合判断用神整体旺衰
            overall_list = [a['overall'] for a in yongshen_analysis]
            if any('旺' in o for o in overall_list):
                overall_judgment = "用神旺相有力"
            elif any('休囚' in o for o in overall_list):
                overall_judgment = "用神休囚无力"
            else:
                overall_judgment = "用神旺衰平和"
            
            output.append(f"**综合判断**：{overall_judgment}。")
            
            # 结合动爻影响
            if dong_effects:
                sheng_count = sum(1 for e in dong_effects if e['shengke'] == '生')
                ke_count = sum(1 for e in dong_effects if e['shengke'] == '克')
                if sheng_count > ke_count:
                    output.append("动爻多生扶用神，吉利。")
                elif ke_count > sheng_count:
                    output.append("动爻多克制用神，需谨慎。")
            
            output.append("\n")
        
        return "".join(output)

    def generate_interpretation(self) -> str:
        """生成完整解读"""
        output = []
        output.append("# 六爻卦象解读\n")
        output.append(f"**问题**：{self.question}\n\n")

        # 1. 卦象速览
        h_info = self.hexagram
        output.append("## 一、卦象速览\n")
        output.append(f"**主卦**：{h_info.get('name', '?')}  {h_info.get('guaxiang_full', '')}\n")
        output.append(f"**卦辞**：{h_info.get('gua_ci', '暂无')}\n")
        output.append(f"**象辞**：{h_info.get('xiang_ci', '暂无')}\n")
        output.append(f"**卦宫**：{h_info.get('gong', '?')} · {h_info.get('position', '')}\n")

        bian_info = self.bian_hexagram
        if bian_info and bian_info.get("name") != "变卦":
            output.append(f"**变卦**：{bian_info.get('name', '?')}  {bian_info.get('guaxiang_full', '')}\n")
        elif bian_info:
            output.append(f"**变卦**：{bian_info.get('guaxiang_full', '')}\n")

        output.append("\n**爻象**（从上往下）：\n")
        for yao in reversed(self.yao_results):
            dong_mark = " ← **动**" if yao["dong"] else ""
            output.append(f"- {yao['yao_name']}：{yao['symbol']}（{yao['type']}）{dong_mark}\n")

        # 2. 纳甲装卦（含六神）
        output.append("\n## 二、纳甲装卦\n")
        shi_ying = self.get_shi_ying(h_info)
        gong = h_info.get("gong", "?")

        for yao in self.yao_results:
            naga = self.get_naga_for_yao(yao, h_info)
            liushou = self.get_liushou_for_yao(yao["pos_idx"])
            liushou_str = f"【{liushou}】" if liushou else ""
            shi_mark = " **世**" if yao["yao_name"] == shi_ying.get("shi") else ""
            ying_mark = " **应**" if yao["yao_name"] == shi_ying.get("ying") else ""
            dong_mark = " ⚡" if yao["dong"] else ""
            output.append(f"- {yao['yao_name']}：{liushou_str}{naga.get('gan','?')}{naga.get('zhi','?')} "
                         f"（{naga.get('zhi_wuxing','?')}）{naga.get('liuqin','?')} 爻{shi_mark}{ying_mark}{dong_mark}\n")

        output.append(f"\n**世爻**：{shi_ying.get('shi','?')}　**应爻**：{shi_ying.get('ying','?')}　**卦宫**：{gong}\n")

        # 3. 六神装卦（独立章节）
        output.append(self.generate_liushou_section())

        # 4. 用神选取
        output.append("\n## 四、用神选取\n")
        yongshen = self.get_yongshen()
        output.append(f"**用神**：{yongshen.get('primary', '?')}（主）\n")
        if yongshen.get("secondary"):
            output.append(f"**辅神**：{'、'.join(yongshen.get('secondary', []))}\n")
        output.append(f"**参考**：{yongshen.get('note', '')}\n")

        # 5. 动变分析
        output.append("\n## 五、动变分析\n")
        if self.dong_yao_indices:
            output.append(f"**动爻**：{', '.join([self.YAO_NAMES[i] for i in self.dong_yao_indices])}\n")
            output.append("动爻阴阳互换，主卦变为变卦。变爻所在，往往是事情变化的关键点。\n")
            
            # 详细动变分析
            output.append("\n**动变详情**：\n")
            for pos_idx in self.dong_yao_indices:
                yao = self.yao_results[pos_idx]
                naga = self.get_naga_for_yao(yao, h_info)
                old_yin_yang = "阳" if yao["yang"] else "阴"
                new_yin_yang = "阴" if yao["yang"] else "阳"
                output.append(f"- {yao['yao_name']}：{old_yin_yang} → {new_yin_yang} "
                             f"（{naga.get('liuqin','?')}·{naga.get('zhi','?')}）\n")
        else:
            output.append("**无动爻**：此为静卦，事态平稳，以不变应万变。\n")

        # 6. 旺衰判断（P1增强版）
        output.append(self.generate_wangshuai_section(h_info))

        # 7. 格局判断
        output.append("\n## 七、格局判断\n")
        patterns = self.check_patterns(h_info)
        if patterns:
            output.append(f"**格局**：{'、'.join(patterns)}\n")
            for p in patterns:
                if p == "游魂卦":
                    output.append("- 游魂：变化不定、心神不宁、出行有阻。事宜守成，不宜妄动。\n")
                elif p == "归魂卦":
                    output.append("- 归魂：回归稳定、有归宿感。事宜落定、整合、收尾。\n")
        else:
            output.append("无特殊格局。\n")

        # 8. 吉凶判断
        output.append("\n## 八、吉凶判断\n")
        if not self.dong_yao_indices:
            jiqiong = "静卦：事态平稳，无明显吉凶倾向。需结合用神旺衰、世应关系综合判断。"
        elif len(self.dong_yao_indices) == 1:
            jiqiong = "单爻动：事情焦点集中于动爻所表达的事项，动爻有力则事成。"
        elif len(self.dong_yao_indices) == 2:
            jiqiong = "双爻动：事态复杂，需关注两动爻之间的生克关系，及其对用神的影响。"
        else:
            jiqiong = "多爻动：事态多变，建议谨慎行事，多方权衡利弊。"

        output.append(f"{jiqiong}\n")
        
        # 结合旺衰进一步判断
        wangshuai = self.analyze_wangshuai(h_info)
        yongshen_analysis = wangshuai.get("yongshen_analysis", [])
        if yongshen_analysis:
            if any('旺' in a['overall'] for a in yongshen_analysis):
                output.append("\n用神旺相，此事有可为。")
            elif any('休囚' in a['overall'] for a in yongshen_analysis):
                output.append("\n用神休囚，此事阻力较大，宜谨慎。")
        
        output.append("\n")

        # 9. 综合建议
        output.append("\n---\n\n")
        output.append("## 💡 综合建议\n\n")
        
        # 吉凶总判断
        jiqiong_judge = ""
        if not self.dong_yao_indices:
            jiqiong_judge = "⚖️ **吉凶判断**：平\n- 静卦显示事态平稳，无明显吉凶倾向。\n"
        elif len(self.dong_yao_indices) == 1:
            jiqiong_judge = "⚖️ **吉凶判断**：平\n- 单爻动显示事态明确，焦点集中于动爻所表达的事项。\n"
        elif len(self.dong_yao_indices) == 2:
            jiqiong_judge = "⚖️ **吉凶判断**：平偏吉\n- 双爻动显示事态复杂，但也意味着更多变化可能。\n"
        else:
            jiqiong_judge = "⚖️ **吉凶判断**：谨慎\n- 多爻动显示事态多变，建议谨慎行事，多方权衡。\n"
        output.append(jiqiong_judge)
        
        # 时机分析
        output.append("\n⏰ **时机分析**：\n")
        if self.dong_yao_indices:
            lower_dong = any(i < 3 for i in self.dong_yao_indices)
            upper_dong = any(i >= 3 for i in self.dong_yao_indices)
            if lower_dong and upper_dong:
                output.append("- 上下爻皆动，年初年末都有机会，宜把握关键节点。\n")
            elif lower_dong:
                output.append("- 动爻偏下（初二三爻），上半年更有利，宜主动出击。\n")
            elif upper_dong:
                output.append("- 动爻偏上（四五六爻），下半年更有利，宜耐心等待。\n")
        else:
            output.append("- 静卦显示时机平稳，随缘而行，不必刻意强求。\n")
        
        # 优势分析
        output.append("\n✨ **优势分析**：\n")
        shichen = h_info.get("shichen", "")
        yueling = h_info.get("yueling", "")
        wuxing = h_info.get("wuxing", "")
        if shichen:
            output.append(f"- 日建为{shichen}，当日气场有助于事态发展。\n")
        if yueling:
            output.append(f"- 月令为{yueling}，月令状态对用神有影响。\n")
        if wuxing:
            output.append(f"- 用神五行属{wuxing}，与日建月令相互作用。\n")
        if not (shichen and yueling):
            output.append("- 卦象显示事态有其发展规律，顺其自然为上策。\n")
        
        # 挑战分析
        output.append("\n⚠️ **挑战分析**：\n")
        if self.dong_yao_indices:
            output.append(f"- 存在{len(self.dong_yao_indices)}个动爻，事态发展过程中会有变化和转折。\n")
            output.append("- 动爻代表不稳定因素，需留意事态发展中的突发情况。\n")
        else:
            output.append("- 静卦显示事态平稳，但可能缺乏突破性进展的动力。\n")
        output.append("- 建议保持定力，不宜在方向未明时贸然行动。\n")
        
        # 具体行动建议
        output.append("\n🎯 **具体行动建议**：\n")
        output.append("1. **稳扎稳打**：先做好眼前事，不要急于求成。\n")
        output.append("2. **把握时机**：关注卦象显示的时间节点，在有利时机主动出击。\n")
        output.append("3. **灵活应变**：动爻显示变化的可能，准备备选方案以应对变化。\n")
        output.append("4. **保持沟通**：带团队需要信任，多与团队成员沟通，建立稳定关系。\n")
        output.append("5. **积累信任**：用实际行动证明能力，让结果说话。\n")
        
        # 注意事项
        output.append("\n🚫 **注意事项**：\n")
        output.append("- 避免急躁冒进，卦象显示需要时间和积累。\n")
        output.append("- 不要只看眼前，眼光放长远一些。\n")
        output.append("- 有变动时保持冷静，理性分析再做决定。\n")
        
        # 结语
        output.append("\n---\n\n")
        output.append("📌 **占卜结果仅供参考，事在人为**\n\n")
        
        return "".join(output)

    def interpret(self, user_input: str) -> str:
        """主解读入口"""
        if not self.parse_input(user_input):
            return ("格式错误，请按以下格式输入：\n\n"
                    "[你的问题]\n"
                    "初爻：少阳\n"
                    "二爻：少阴\n"
                    "三爻：老阳动\n"
                    "四爻：少阳\n"
                    "五爻：少阴\n"
                    "上爻：少阳\n\n"
                    "说明：少阳/少阴为静爻，老阳（变阴）/老阴（变阳）为动爻")

        self.hexagram = self.find_hexagram()
        if not self.hexagram:
            return f"未找到对应卦象，卦象符号：{self.get_guaxiang_full()}。请检查爻的阴阳输入是否正确。"

        self.bian_hexagram = self.get_bian_hexagram()
        return self.generate_interpretation()


def main():
    if len(sys.argv) > 1:
        with open(sys.argv[1], "r", encoding="utf-8") as f:
            user_input = f.read()
    else:
        user_input = sys.stdin.read()

    interpreter = LiuYaoInterpreter()
    result = interpreter.interpret(user_input)
    print(result)


if __name__ == "__main__":
    main()
