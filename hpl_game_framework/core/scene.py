#!/usr/bin/env python3
"""
场景系统模块
========

管理游戏场景、选择项、条件判断。
所有功能封装为模块级函数，兼容HPL Runtime。

作者: HPL Framework Team
版本: 1.0.0
"""

# ============ 导入 ============
try:
    from hpl_runtime.modules.base import HPLModule
    from hpl_runtime.utils.exceptions import HPLTypeError, HPLValueError, HPLRuntimeError
except ImportError:
    import sys
    import os
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    from hpl_runtime.modules.base import HPLModule
    from hpl_runtime.utils.exceptions import HPLTypeError, HPLValueError, HPLRuntimeError


# ============ 内部类定义 ============

class _Choice:
    """选择项类（内部使用）"""
    
    def __init__(self, text, target_scene, condition=None, action=None):
        self.text = text
        self.target_scene = target_scene
        self.condition = condition
        self.action = action
        self.visible = True
        self.enabled = True
    
    def check_condition(self, player, game_state):
        if self.condition is None:
            return True
        return True
    
    def execute_action(self, player, game_state):
        if self.action is not None:
            # Handle HPLArrowFunction objects from HPL runtime
            if callable(self.action):
                self.action(player, game_state)
            elif hasattr(self.action, 'call') and callable(self.action.call):
                self.action.call(player, game_state)
            elif hasattr(self.action, 'call_function') and callable(self.action.call_function):
                self.action.call_function(player, game_state)

    
    def get_display_text(self):
        if not self.enabled:
            return f"[不可用] {self.text}"
        return self.text


class _Scene:
    """场景类（内部使用）"""
    
    def __init__(self, id, name, description):
        self.id = id
        self.name = name
        self.description = description
        self.choices = []
        self.on_enter = None
        self.on_exit = None
        self.visited = False
        self.items = []
        self.npcs = []
        self.exits = {}
    
    def add_choice(self, choice):
        self.choices.append(choice)
    
    def get_available_choices(self, player, game_state):
        available = []
        for choice in self.choices:
            if choice.visible and choice.check_condition(player, game_state):
                available.append(choice)
        return available
    
    def display(self, player, game_state):
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
        print("")
        print(f"【{location}】")
        print("-" * 40)
        print(description)
        print("-" * 40)
        print("")
    
    def make_choice(self, choice_index, player, game_state):
        available = self.get_available_choices(player, game_state)
        if choice_index < 0 or choice_index >= len(available):
            return None
        choice = available[choice_index]
        choice.execute_action(player, game_state)
        return choice.target_scene
    
    def enter(self, player, game_state):
        self.visited = True
        player.location = self.id
        if self.on_enter is not None:
            self.on_enter(player, game_state)
    
    def exit(self, player, game_state):
        if self.on_exit is not None:
            self.on_exit(player, game_state)


# ============ 对象实例管理 ============

_scenes = {}
_choices = {}

def _get_scene(scene_id):
    """获取场景实例"""
    return _scenes.get(scene_id)

def _set_scene(scene_id, scene):
    """存储场景实例"""
    _scenes[scene_id] = scene

def _get_choice(choice_id):
    """获取选择项实例"""
    return _choices.get(choice_id)

def _set_choice(choice_id, choice):
    """存储选择项实例"""
    _choices[choice_id] = choice


# ============ 模块级函数（HPL可调用的API） ============

def create_scene(id, name, description):
    """创建场景，返回场景ID"""
    scene = _Scene(id, name, description)
    _set_scene(id, scene)
    return scene

def create_choice(text, target_scene, condition=None, action=None):
    """创建选择项，返回选择项对象"""
    choice = _Choice(text, target_scene, condition, action)
    choice_id = f"choice_{id(choice)}"
    _set_choice(choice_id, choice)
    return choice

def add_choice(scene, choice):
    """添加选择项到场景"""
    if isinstance(scene, _Scene):
        scene.add_choice(choice)
    else:
        raise HPLTypeError("First argument must be a scene object")
    return None

def set_scene_description(scene_id, description):
    """设置场景描述"""
    scene = _get_scene(scene_id)
    if scene is None:
        raise HPLValueError(f"Scene not found: {scene_id}")
    scene.description = description
    return None

def add_scene_exit(scene_id, direction, target_scene_id):
    """添加场景出口"""
    scene = _get_scene(scene_id)
    if scene is None:
        raise HPLValueError(f"Scene not found: {scene_id}")
    scene.exits[direction] = target_scene_id
    return None

def get_scene_exits(scene_id):
    """获取场景出口"""
    scene = _get_scene(scene_id)
    if scene is None:
        raise HPLValueError(f"Scene not found: {scene_id}")
    return scene.exits

def set_scene_on_enter(scene_id, callback):
    """设置进入场景时的回调"""
    scene = _get_scene(scene_id)
    if scene is None:
        raise HPLValueError(f"Scene not found: {scene_id}")
    scene.on_enter = callback
    return None

def set_scene_on_exit(scene_id, callback):
    """设置离开场景时的回调"""
    scene = _get_scene(scene_id)
    if scene is None:
        raise HPLValueError(f"Scene not found: {scene_id}")
    scene.on_exit = callback
    return None

def display_scene(scene_id, player, game_state):
    """显示场景"""
    scene = _get_scene(scene_id)
    if scene is None:
        raise HPLValueError(f"Scene not found: {scene_id}")
    return scene.display(player, game_state)

def make_choice(scene_id, choice_index, player, game_state):
    """执行选择"""
    scene = _get_scene(scene_id)
    if scene is None:
        raise HPLValueError(f"Scene not found: {scene_id}")
    return scene.make_choice(choice_index, player, game_state)


# ============ 模块注册 ============

HPL_MODULE = HPLModule("scene", "场景系统 - 管理游戏场景、选择项、条件判断")

# 注册函数
HPL_MODULE.register_function('create_scene', create_scene, 3, '创建场景 (id, name, description)')
HPL_MODULE.register_function('create_choice', create_choice, None, '创建选择项 (text, target_scene, condition?, action?)')
HPL_MODULE.register_function('add_choice', add_choice, 2, '添加选择项到场景 (scene, choice)')
HPL_MODULE.register_function('set_scene_description', set_scene_description, 2, '设置场景描述 (scene_id, description)')
HPL_MODULE.register_function('add_scene_exit', add_scene_exit, 3, '添加场景出口 (scene_id, direction, target_scene_id)')
HPL_MODULE.register_function('get_scene_exits', get_scene_exits, 1, '获取场景出口 (scene_id)')
HPL_MODULE.register_function('set_scene_on_enter', set_scene_on_enter, 2, '设置进入回调 (scene_id, callback)')
HPL_MODULE.register_function('set_scene_on_exit', set_scene_on_exit, 2, '设置离开回调 (scene_id, callback)')
HPL_MODULE.register_function('display_scene', display_scene, 3, '显示场景 (scene_id, player, game_state)')
HPL_MODULE.register_function('make_choice', make_choice, 4, '执行选择 (scene_id, choice_index, player, game_state)')

# 注册常量
HPL_MODULE.register_constant('VERSION', "2.0.0", '模块版本')
HPL_MODULE.register_constant('AUTHOR', "HPL Framework Team", '模块作者')
