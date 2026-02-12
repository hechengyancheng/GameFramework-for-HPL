#!/usr/bin/env python3
"""
游戏工具模块
========

提供随机数生成、文本格式化等功能。

作者: HPL Framework Team
版本: 1.0.0
"""

# ============ 导入 ============
try:
    from hpl_runtime.modules.base import HPLModule
    from hpl_runtime.utils.exceptions import HPLTypeError, HPLValueError, HPLRuntimeError
except ImportError:
    # 备用导入（当模块在 HPL 运行时目录外时）
    import sys
    import os
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    from hpl_runtime.modules.base import HPLModule
    from hpl_runtime.utils.exceptions import HPLTypeError, HPLValueError, HPLRuntimeError

import time
import random


# ============ 随机数生成器 ============

class RandomGenerator:
    """随机数生成器"""
    
    def __init__(self, seed=None):
        if seed is None:
            seed = int(time.time() * 1000)
        self.seed = seed
        self.a = 1103515245
        self.c = 12345
        self.m = 2147483647
    
    def random_int(self, max):
        """生成随机整数 [0, max)"""
        self.seed = (self.a * self.seed + self.c) % self.m
        return (self.seed % max + max) % max
    
    def random_range(self, min, max):
        """生成随机整数 [min, max]"""
        range_val = max - min + 1
        return self.random_int(range_val) + min
    
    def random_choice(self, arr):
        """从数组中随机选择"""
        if len(arr) == 0:
            return None
        index = self.random_int(len(arr))
        return arr[index]
    
    def roll_dice(self, n, d):
        """掷骰子 (n个d面骰子)"""
        total = 0
        for _ in range(n):
            total += self.random_range(1, d)
        return total


# ============ 文本格式化 ============

class TextFormatter:
    """文本格式化类"""
    
    def clear_screen(self):
        """清屏（终端）"""
        # 使用多个换行模拟清屏
        print("\n" * 50)
    
    def print_line(self, char="-", length=50):
        """打印分隔线"""
        if char is None:
            char = "-"
        if length is None:
            length = 50
        line = char * length
        print(line)
    
    def print_title(self, text):
        """打印标题"""
        print("")
        self.print_line("=", 50)
        # 居中显示
        padding = (50 - len(text)) // 2
        left_pad = " " * padding
        print(left_pad + text)
        self.print_line("=", 50)
        print("")
    
    def print_box(self, text):
        """打印带边框的文本"""
        length = len(text) + 4
        border = "+" + "-" * (length - 2) + "+"
        print(border)
        print(f"| {text} |")
        print(border)
    
    def print_list_item(self, index, text):
        """打印列表项"""
        print(f"  [{index}] {text}")
    
    def print_progress(self, current, max, label=None):
        """打印进度条"""
        if label is None:
            label = "Progress"
        percentage = int((current * 100) / max)
        bar_length = 20
        filled = int((current * bar_length) / max)
        bar = "[" + "#" * filled + "-" * (bar_length - filled) + "]"
        print(f"{label}: {bar} {percentage}%")


# ============ 骰子滚动器 ============

class DiceRoller:
    """骰子滚动器"""
    
    def __init__(self):
        self.random_gen = RandomGenerator(int(time.time() * 1000))
    
    def roll(self, expression):
        """解析骰子表达式如 "2d6+3" """
        # 简化实现：直接掷骰子
        # 格式: NdM 或 NdM+K 或 NdM-K
        print(f"Rolling: {expression}")
        return 10  # 默认返回
    
    def ability_check(self, modifier):
        """属性检定 (D20系统)"""
        roll = self.random_gen.random_range(1, 20)
        total = roll + modifier
        print(f"D20 Roll: {roll} + {modifier} = {total}")
        return total
    
    def attack_roll(self, attack_bonus, armor_class):
        """战斗攻击检定"""
        roll = self.random_gen.random_range(1, 20)
        total = roll + attack_bonus
        if roll == 20:
            print("Critical Hit! (Natural 20)")
            return "critical"
        if roll == 1:
            print("Critical Miss! (Natural 1)")
            return "miss"
        if total >= armor_class:
            print(f"Hit! Roll: {roll} + {attack_bonus} >= AC {armor_class}")
            return "hit"
        else:
            print(f"Miss! Roll: {roll} + {attack_bonus} < AC {armor_class}")
            return "miss"
    
    def damage_roll(self, dice_count, dice_sides, bonus=0):
        """伤害骰"""
        if bonus is None:
            bonus = 0
        total = 0
        rolls = []
        for _ in range(dice_count):
            roll = self.random_gen.random_range(1, dice_sides)
            rolls.append(roll)
            total += roll
        total += bonus
        
        print(f"Damage rolls: {rolls} + {bonus} = {total}")
        return total


# ============ 模块级函数 ============

def create_random_generator(seed=None):
    """创建随机数生成器"""
    return RandomGenerator(seed)

def create_text_formatter():
    """创建文本格式化器"""
    return TextFormatter()

def create_dice_roller():
    """创建骰子滚动器"""
    return DiceRoller()

def random_int(max_val):
    """生成随机整数 [0, max)"""
    return random.randint(0, max_val - 1)

def random_range(min_val, max_val):
    """生成随机整数 [min, max]"""
    return random.randint(min_val, max_val)

def random_choice(arr):
    """从数组中随机选择"""
    if len(arr) == 0:
        return None
    return random.choice(arr)

def roll_dice(n, d):
    """掷骰子 (n个d面骰子)"""
    total = 0
    for _ in range(n):
        total += random.randint(1, d)
    return total

def clear_screen():
    """清屏"""
    print("\n" * 50)

def print_line(char="-", length=50):
    """打印分隔线"""
    print(char * length)

def print_title(text):
    """打印标题"""
    print("")
    print("=" * 50)
    padding = (50 - len(text)) // 2
    print(" " * padding + text)
    print("=" * 50)
    print("")

def print_box(text):
    """打印带边框的文本"""
    length = len(text) + 4
    border = "+" + "-" * (length - 2) + "+"
    print(border)
    print(f"| {text} |")
    print(border)

def print_progress(current, max_val, label="Progress"):
    """打印进度条"""
    percentage = int((current * 100) / max_val)
    bar_length = 20
    filled = int((current * bar_length) / max_val)
    bar = "[" + "#" * filled + "-" * (bar_length - filled) + "]"
    print(f"{label}: {bar} {percentage}%")


# ============ 模块注册 ============

HPL_MODULE = HPLModule("game_utils", "游戏工具模块 - 提供随机数生成、文本格式化等功能")

# 注册函数
HPL_MODULE.register_function('create_random_generator', create_random_generator, None, '创建随机数生成器')
HPL_MODULE.register_function('create_text_formatter', create_text_formatter, 0, '创建文本格式化器')
HPL_MODULE.register_function('create_dice_roller', create_dice_roller, 0, '创建骰子滚动器')
HPL_MODULE.register_function('random_int', random_int, 1, '生成随机整数 [0, max)')
HPL_MODULE.register_function('random_range', random_range, 2, '生成随机整数 [min, max]')
HPL_MODULE.register_function('random_choice', random_choice, 1, '从数组中随机选择')
HPL_MODULE.register_function('roll_dice', roll_dice, 2, '掷骰子 (n个d面骰子)')
HPL_MODULE.register_function('clear_screen', clear_screen, 0, '清屏')
HPL_MODULE.register_function('print_line', print_line, None, '打印分隔线')
HPL_MODULE.register_function('print_title', print_title, 1, '打印标题')
HPL_MODULE.register_function('print_box', print_box, 1, '打印带边框的文本')
HPL_MODULE.register_function('print_progress', print_progress, None, '打印进度条')

# 注册常量
HPL_MODULE.register_constant('VERSION', "1.0.0", '模块版本')
HPL_MODULE.register_constant('AUTHOR', "HPL Framework Team", '模块作者')
HPL_MODULE.register_constant('PI', 3.14159265359, '圆周率')
HPL_MODULE.register_constant('E', 2.71828182846, '自然常数e')
