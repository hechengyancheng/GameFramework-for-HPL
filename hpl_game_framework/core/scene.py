#!/usr/bin/env python3
"""
场景系统模块
========

管理游戏场景、选择项、条件判断。

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


# ============ 选择项类 ============

class Choice:
    """选择项类"""
    
    def __init__(self, text, target_scene, condition=None, action=None):
        self.text = text              # 显示文本
        self.target_scene = target_scene  # 目标场景ID
        self.condition = condition    # 条件表达式（可选）
        self.action = action          # 执行的动作（可选）
        self.visible = True           # 是否可见
        self.enabled = True           # 是否可用
    
    def check_condition(self, player, game_state):
        """检查条件"""
        if self.condition is None:
            return True
        # 简化条件检查，实际游戏中可以扩展
        return True
    
    def execute_action(self, player, game_state):
        """执行动作"""
        if self.action is None:
            return
        # 执行动作
    
    def get_display_text(self):
        """获取显示文本"""
        if not self.enabled:
            return f"[不可用] {self.text}"
        return self.text


# ============ 场景类 ============

class Scene:
    """场景类"""
    
    def __init__(self, id, name, description):
        self.id = id                  # 场景唯一标识
        self.name = name              # 场景名称
        self.description = description  # 场景描述
        self.choices = []             # 选择项列表
        self.on_enter = None          # 进入场景时执行的动作
        self.on_exit = None           # 离开场景时执行的动作
        self.visited = False          # 是否访问过
        self.items = []               # 场景中的物品
        self.npcs = []                # 场景中的NPC
        self.exits = {}               # 出口 {方向: 场景ID}
    
    def add_choice(self, choice):
        """添加选择项"""
        self.choices.append(choice)
    
    def create_choice(self, text, target, condition=None, action=None):
        """创建并添加选择项"""
        choice = Choice(text, target, condition, action)
        self.add_choice(choice)
        return choice
    
    def add_simple_choice(self, text, target_scene):
        """添加简单选择（无条件）"""
        choice = Choice(text, target_scene, None, None)
        self.add_choice(choice)
        return choice
    
    def add_item(self, item):
        """添加物品到场景"""
        self.items.append(item)
    
    def remove_item(self, index):
        """移除场景中的物品"""
        if index < 0 or index >= len(self.items):
            return None
        return self.items.pop(index)
    
    def add_npc(self, npc):
        """添加NPC"""
        self.npcs.append(npc)
    
    def add_exit(self, direction, scene_id):
        """添加出口"""
        self.exits[direction] = scene_id
    
    def get_available_choices(self, player, game_state):
        """获取可用选择"""
        available = []
        for choice in self.choices:
            if choice.visible and choice.check_condition(player, game_state):
                available.append(choice)
        return available
    
    def display(self, player, game_state):
        """显示场景"""
        # 显示场景名称和描述
        self._show_scene(self.name, self.description)
        
        # 显示场景中的物品
        if len(self.items) > 0:
            print("这里的物品:")
            for item in self.items:
                print(f"  - {item.name}")
        
        # 显示NPC
        if len(self.npcs) > 0:
            print("这里的人:")
            for npc in self.npcs:
                print(f"  - {npc.name}")
        
        # 显示出口
        if len(self.exits) > 0:
            print("出口:")
            directions = []
            # 手动获取所有方向
            if "north" in self.exits:
                directions.append("北")
            if "south" in self.exits:
                directions.append("南")
            if "east" in self.exits:
                directions.append("东")
            if "west" in self.exits:
                directions.append("西")
            if "up" in self.exits:
                directions.append("上")
            if "down" in self.exits:
                directions.append("下")
            print(f"  {directions}")
        
        # 显示选择项
        available = self.get_available_choices(player, game_state)
        if len(available) > 0:
            print("")
            print("你可以:")
            for i, choice in enumerate(available):
                print(f"  [{i + 1}] {choice.get_display_text()}")
        
        return available
    
    def _show_scene(self, location, description):
        """显示场景描述"""
        print("")
        print(f"【{location}】")
        print("-" * 40)
        print(description)
        print("-" * 40)
        print("")
    
    def make_choice(self, choice_index, player, game_state):
        """执行选择"""
        available = self.get_available_choices(player, game_state)
        if choice_index < 0 or choice_index >= len(available):
            return None
        choice = available[choice_index]
        
        # 执行动作
        choice.execute_action(player, game_state)
        
        return choice.target_scene
    
    def enter(self, player, game_state):
        """进入场景"""
        self.visited = True
        player.location = self.id
        
        if self.on_enter is not None:
            self.on_enter(player, game_state)
    
    def exit(self, player, game_state):
        """离开场景"""
        if self.on_exit is not None:
            self.on_exit(player, game_state)


# ============ NPC类 ============

class NPC:
    """NPC类"""
    
    def __init__(self, id, name, description):
        self.id = id
        self.name = name
        self.description = description
        self.dialogues = []           # 对话列表
        self.shop_items = []          # 商店物品（如果是商人）
        self.is_merchant = False      # 是否是商人
        self.quests = []              # 提供的任务
        self.friendly = True          # 是否友好
    
    def add_dialogue(self, text, responses):
        """添加对话"""
        dialogue = {
            "text": text,
            "responses": responses
        }
        self.dialogues.append(dialogue)
    
    def get_greeting(self):
        """获取问候语"""
        if len(self.dialogues) > 0:
            return self.dialogues[0]["text"]
        return f"你好，{self.name}向你打招呼。"
    
    def interact(self, player, game_state):
        """交互"""
        self._show_dialog(self.name, self.get_greeting())
        
        if self.is_merchant:
            # 显示商店选项
            print("1. 购买物品")
            print("2. 出售物品")
            print("3. 离开")
            return
        
        if len(self.quests) > 0:
            print("4. 询问任务")
    
    def _show_dialog(self, speaker, text):
        """显示对话"""
        print("")
        if speaker is not None and len(speaker) > 0:
            print(f"[{speaker}]")
        print(f"\"{text}\"")
        print("")


# ============ 模块级函数 ============

def create_choice(text, target_scene, condition=None, action=None):
    """创建选择项"""
    return Choice(text, target_scene, condition, action)

def create_scene(id, name, description):
    """创建场景"""
    return Scene(id, name, description)

def create_npc(id, name, description):
    """创建NPC"""
    return NPC(id, name, description)

def add_choice(scene, choice):
    """添加选择项到场景"""
    scene.add_choice(choice)


# ============ 模块注册 ============


HPL_MODULE = HPLModule("scene", "场景系统 - 管理游戏场景、选择项、条件判断")

# 注册函数
HPL_MODULE.register_function('create_choice', create_choice, None, '创建选择项')
HPL_MODULE.register_function('create_scene', create_scene, 3, '创建场景')
HPL_MODULE.register_function('create_npc', create_npc, 3, '创建NPC')
HPL_MODULE.register_function('add_choice', add_choice, 2, '添加选择项到场景')


# 注册常量
HPL_MODULE.register_constant('VERSION', "1.0.0", '模块版本')
HPL_MODULE.register_constant('AUTHOR', "HPL Framework Team", '模块作者')
