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

import random



# ============ 声明式动作处理器注册表 ============
_action_handlers = {}

def register_action_handler(action_type):
    """装饰器：注册声明式动作处理器"""
    def decorator(func):
        _action_handlers[action_type] = func
        return func
    return decorator

def _execute_declarative_action(action_def, player, game_state):
    """执行声明式动作"""
    action_type = action_def.get('type')
    handler = _action_handlers.get(action_type)
    if handler:
        return handler(action_def, player, game_state)
    else:
        print(f"[警告] 未知的声明式动作类型: {action_type}")
        return None


# ============ 常用声明式动作处理器 ============

@register_action_handler('random_event')
def _handle_random_event(action_def, player, game_state):
    """处理随机事件动作"""
    import random
    events = action_def.get('events', [])
    
    # 计算总概率
    total_chance = sum(e.get('chance', 0) for e in events)
    if total_chance == 0:
        return
    
    # 随机选择事件
    roll = random.randint(1, total_chance)
    cumulative = 0
    
    for event in events:
        cumulative += event.get('chance', 0)
        if roll <= cumulative:
            # 执行该事件
            _execute_event_effects(event, player, game_state)
            break

@register_action_handler('give_item')
def _handle_give_item(action_def, player, game_state):
    """处理给予物品动作"""
    item_id = action_def.get('item_id')
    count = action_def.get('count', 1)
    message = action_def.get('message')
    
    if message:
        print(f"[系统] {message}")
    
    # 通过 game_state 获取物品数据
    if hasattr(game_state, 'items') and item_id in game_state.items:
        item_data = game_state.items[item_id]
        for _ in range(count):
            player.inventory.add_item(_create_item_from_data(item_data))
        print(f"[获得] {item_data.get('name', item_id)} x{count}")

@register_action_handler('give_gold')
def _handle_give_gold(action_def, player, game_state):
    """处理给予金币动作"""
    amount = action_def.get('amount', 0)
    message = action_def.get('message')
    
    if message:
        print(f"[系统] {message}")
    
    player.inventory.add_gold(amount)
    print(f"[获得] {amount} 金币")

@register_action_handler('heal')
def _handle_heal(action_def, player, game_state):
    """处理治疗动作"""
    amount = action_def.get('amount', 0)
    message = action_def.get('message')
    cost = action_def.get('cost', 0)
    
    if message:
        print(f"[系统] {message}")
    
    if cost > 0:
        if player.inventory.gold < cost:
            print("[系统] 金币不足！")
            return
        player.inventory.gold -= cost
    
    old_hp = player.hp
    player.heal(amount)
    print(f"[恢复] HP: {old_hp} -> {player.hp}")

@register_action_handler('damage')
def _handle_damage(action_def, player, game_state):
    """处理伤害动作"""
    amount = action_def.get('amount', 0)
    message = action_def.get('message')
    
    if message:
        print(f"[系统] {message}")
    
    player.hp -= amount
    if player.hp < 0:
        player.hp = 0
    print(f"[伤害] 失去 {amount} HP，当前 HP: {player.hp}")

@register_action_handler('show_message')
def _handle_show_message(action_def, player, game_state):
    """处理显示消息动作"""
    message = action_def.get('message', '')
    msg_type = action_def.get('msg_type', 'system')  # system, dialog, combat, narration
    
    prefixes = {
        'system': '[系统]',
        'dialog': '[对话]',
        'combat': '[战斗]',
        'narration': '[旁白]',
        'loot': '[获得]'
    }
    prefix = prefixes.get(msg_type, '[系统]')
    print(f"{prefix} {message}")

@register_action_handler('require_item')
def _handle_require_item(action_def, player, game_state):
    """处理物品需求检查"""
    item_id = action_def.get('item_id')
    success = action_def.get('success', {})
    fail = action_def.get('fail', {})
    
    # 检查物品
    has_item = any(item.id == item_id for item in player.inventory.items)
    
    if has_item:
        _execute_nested_action(success, player, game_state)
    else:
        _execute_nested_action(fail, player, game_state)

@register_action_handler('sequence')
def _handle_sequence(action_def, player, game_state):
    """处理顺序执行多个动作"""
    actions = action_def.get('actions', [])
    for action in actions:
        _execute_nested_action(action, player, game_state)

@register_action_handler('condition')
def _handle_condition(action_def, player, game_state):
    """处理条件分支动作"""
    # 支持的条件类型
    condition_type = action_def.get('condition_type')
    condition_value = action_def.get('condition_value')
    success = action_def.get('success', {})
    fail = action_def.get('fail', {})
    
    result = False
    
    if condition_type == 'has_item':
        result = any(item.id == condition_value for item in player.inventory.items)
    elif condition_type == 'gold_at_least':
        result = player.inventory.gold >= condition_value
    elif condition_type == 'hp_above':
        result = player.hp > condition_value
    elif condition_type == 'random':
        import random
        result = random.randint(1, 100) <= condition_value
    
    if result:
        _execute_nested_action(success, player, game_state)
    else:
        _execute_nested_action(fail, player, game_state)

def _execute_event_effects(event_def, player, game_state):
    """执行事件效果"""
    # 显示消息
    message = event_def.get('message')
    if message:
        print(f"[事件] {message}")
    
    # 给予物品
    give_items = event_def.get('give_items', [])
    for item_info in give_items:
        if isinstance(item_info, dict):
            item_id = item_info.get('id')
            count = item_info.get('count', 1)
        else:
            item_id = item_info
            count = 1
        
        if hasattr(game_state, 'items') and item_id in game_state.items:
            item_data = game_state.items[item_id]
            for _ in range(count):
                player.inventory.add_item(_create_item_from_data(item_data))
            print(f"[获得] {item_data.get('name', item_id)} x{count}")
    
    # 给予金币
    give_gold = event_def.get('give_gold', 0)
    if give_gold > 0:
        player.inventory.add_gold(give_gold)
        print(f"[获得] {give_gold} 金币")
    
    # 造成伤害
    damage = event_def.get('damage', 0)
    if damage > 0:
        player.hp -= damage
        if player.hp < 0:
            player.hp = 0
        print(f"[伤害] 失去 {damage} HP，当前 HP: {player.hp}")
    
    # 治疗
    heal = event_def.get('heal', 0)
    if heal > 0:
        old_hp = player.hp
        player.heal(heal)
        print(f"[恢复] HP: {old_hp} -> {player.hp}")
    
    # 获得经验
    exp = event_def.get('exp', 0)
    if exp > 0:
        player.gain_exp(exp)
        print(f"[经验] 获得 {exp} 经验值")

def _execute_nested_action(action_def, player, game_state):
    """执行嵌套动作（用于 success/fail/actions 等）"""
    if isinstance(action_def, dict):
        action_type = action_def.get('type')
        handler = _action_handlers.get(action_type)
        if handler:
            handler(action_def, player, game_state)
    elif isinstance(action_def, str):
        # 简单的字符串消息
        print(f"[系统] {action_def}")

def _create_item_from_data(item_data):
    """从数据创建物品对象"""
    try:
        from hpl_game_framework.core import player as player_module
        return player_module.create_item(
            item_data.get('id', 'unknown'),
            item_data.get('name', 'Unknown'),
            item_data.get('description', ''),
            item_data.get('type', 'misc'),
            item_data.get('value', 0)
        )
    except ImportError:
        # 简化版本，如果导入失败
        class SimpleItem:
            def __init__(self, id, name, desc, type_, value):
                self.id = id
                self.name = name
                self.description = desc
                self.type = type_
                self.value = value
        return SimpleItem(
            item_data.get('id', 'unknown'),
            item_data.get('name', 'Unknown'),
            item_data.get('description', ''),
            item_data.get('type', 'misc'),
            item_data.get('value', 0)
        )


# ============ 内部类定义 ============

def _convert_hpl_to_python(hpl_code):

    """将HPL语法转换为有效的Python语法"""
    import re
    
    lines = hpl_code.split('\n')
    result_lines = []
    
    for line in lines:
        original_line = line
        # 去除行首空格用于分析
        stripped = line.lstrip()
        indent = line[:len(line) - len(stripped)]
        
        # 转换 if (condition) : -> if condition:
        if stripped.startswith('if ('):
            # 匹配 if (condition) : 格式
            match = re.match(r'if\s*\((.*?)\)\s*:', stripped)
            if match:
                condition = match.group(1)
                stripped = f'if {condition}:'
                line = indent + stripped
        
        # 转换 elif (condition) : -> elif condition:
        elif stripped.startswith('elif ('):
            match = re.match(r'elif\s*\((.*?)\)\s*:', stripped)
            if match:
                condition = match.group(1)
                stripped = f'elif {condition}:'
                line = indent + stripped
        
        # 转换 for (var in iterable) : -> for var in iterable:
        elif stripped.startswith('for ('):
            match = re.match(r'for\s*\((.*?)\)\s*:', stripped)
            if match:
                loop_expr = match.group(1)
                stripped = f'for {loop_expr}:'
                line = indent + stripped
        
        # 转换 while (condition) : -> while condition:
        elif stripped.startswith('while ('):
            match = re.match(r'while\s*\((.*?)\)\s*:', stripped)
            if match:
                condition = match.group(1)
                stripped = f'while {condition}:'
                line = indent + stripped
        
        # 转换 catch (err) : -> except Exception as err:
        elif stripped.startswith('catch ('):
            match = re.match(r'catch\s*\((.*?)\)\s*:', stripped)
            if match:
                var_name = match.group(1)
                stripped = f'except Exception as {var_name}:'
                line = indent + stripped
        
        # 转换 try : -> try:
        elif stripped.startswith('try :'):
            stripped = 'try:'
            line = indent + stripped
        
        # 转换 else : -> else:
        elif stripped.startswith('else :'):
            stripped = 'else:'
            line = indent + stripped
        
        # 转换 false -> False, true -> True, null -> None
        # 使用单词边界确保只替换完整的标识符
        import re as re_module
        line = re_module.sub(r'\bfalse\b', 'False', line)
        line = re_module.sub(r'\btrue\b', 'True', line)
        line = re_module.sub(r'\bnull\b', 'None', line)
        
        # 转换 || -> or, && -> and (HPL逻辑运算符转Python)
        line = re_module.sub(r'\|\|', 'or', line)
        line = re_module.sub(r'&&', 'and', line)
        
        result_lines.append(line)

    
    return '\n'.join(result_lines)


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
        if self.action is None:
            return
        
        # 处理字典类型的声明式动作
        if isinstance(self.action, dict):
            _execute_declarative_action(self.action, player, game_state)
            return
        
        # 处理字符串类型的动作（HPL代码块）
        if isinstance(self.action, str):
            # 转换HPL语法为Python语法
            python_code = _convert_hpl_to_python(self.action)

            # 导入执行上下文所需的模块
            try:
                from hpl_game_framework.utils import interaction as ui
            except ImportError:
                ui = None
            
            # 创建模拟引擎对象，直接返回玩家对象
            class MockEngine:
                @staticmethod
                def get_player(engine_id):
                    return player
            mock_engine = MockEngine()
            
            # 创建玩家模块包装器，用于与玩家对象交互
            class PlayerModuleWrapper:
                def __init__(self, player_obj):
                    self._player = player_obj
                
                def show_player_status(self, p=None):
                    if p is None:
                        p = self._player
                    return p.show_status()
                
                def get_player_hp(self, p=None):
                    if p is None:
                        p = self._player
                    return p.hp
                
                def heal_player(self, p=None, amount=0):
                    if p is None:
                        p = self._player
                    return p.heal(amount)
                
                def add_gold(self, p=None, amount=0):
                    if p is None:
                        p = self._player
                    return p.inventory.add_gold(amount)
                
                def gain_exp(self, p=None, amount=0):
                    if p is None:
                        p = self._player
                    return p.gain_exp(amount)
                
                def add_item_to_inventory(self, p=None, item=None):
                    if p is None:
                        p = self._player
                    if item is not None:
                        return p.inventory.add_item(item)
                    return False
                
                def damage_player(self, p=None, amount=0):
                    if p is None:
                        p = self._player
                    p.hp -= amount
                    if p.hp < 0:
                        p.hp = 0
                    return p.hp
                
                def get_player_gold(self, p=None):
                    if p is None:
                        p = self._player
                    return p.inventory.gold
                
                def get_inventory(self, p=None):
                    if p is None:
                        p = self._player
                    return p.inventory.items
                
                def restore_mp(self, p=None, amount=0):
                    if p is None:
                        p = self._player
                    p.mp += amount
                    if p.mp > p.max_mp:
                        p.mp = p.max_mp
                    return p.mp
                
                def deduct_gold(self, p=None, amount=0):
                    if p is None:
                        p = self._player
                    p.inventory.gold -= amount
                    if p.inventory.gold < 0:
                        p.inventory.gold = 0
                    return p.inventory.gold
                
                def get_player_mp(self, p=None):
                    if p is None:
                        p = self._player
                    return p.mp
            
            player_wrapper = PlayerModuleWrapper(player)
            
            # 创建物品容器，用于通过ID访问物品
            class ItemsContainer:
                def __getattr__(self, item_id):
                    try:
                        from hpl_game_framework.core import player as player_module
                    except ImportError:
                        import player as player_module
                    if hasattr(game_state, 'items') and item_id in game_state.items:
                        item_data = game_state.items[item_id]
                        return player_module.create_item(
                            item_data.get('id', item_id),
                            item_data.get('name', 'Unknown'),
                            item_data.get('description', ''),
                            item_data.get('type', 'misc'),
                            item_data.get('value', 0)
                        )
                    return player_module.create_item(item_id, item_id, '', 'misc', 0)
            
            items_container = ItemsContainer()
            
            # 创建包含常用变量的执行上下文
            context = {
                'player_obj': player,
                'game_state': game_state,
                'print': print,
                'input': input,
                'len': len,
                'range': range,
                'enumerate': enumerate,
                'int': int,
                'str': str,
                'float': float,
                'bool': bool,
                'list': list,
                'dict': dict,
                'set': set,
                'tuple': tuple,
                'random': random,
                'ui': ui,
                'engine': mock_engine,
                'engine_id': 'mock_engine_id',
                'player': player_wrapper,
                'items': items_container,
            }
            
            try:
                exec(python_code, context)
            except Exception as e:
                print(f"[动作执行错误] {e}")
            return
        
        # 处理来自HPL运行时的HPLArrowFunction对象
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
            # 处理字符串类型的回调（HPL代码块）
            if isinstance(self.on_enter, str):
                # 转换HPL语法为Python语法
                python_code = _convert_hpl_to_python(self.on_enter)
                
                # 导入UI模块用于执行上下文
                try:
                    from hpl_game_framework.utils import interaction as ui
                except ImportError:
                    ui = None

                context = {
                    'player': player,
                    'game_state': game_state,
                    'print': print,
                    'input': input,
                    'ui': ui,
                }
                try:
                    exec(python_code, context)
                except Exception as e:
                    print(f"[on_enter执行错误] {e}")
            elif callable(self.on_enter):
                self.on_enter(player, game_state)

    
    def exit(self, player, game_state):
        if self.on_exit is not None:
            # 处理字符串类型的回调（HPL代码块）
            if isinstance(self.on_exit, str):
                # 转换HPL语法为Python语法
                python_code = _convert_hpl_to_python(self.on_exit)
                
                # 导入UI模块用于执行上下文
                try:
                    from hpl_game_framework.utils import interaction as ui
                except ImportError:
                    ui = None

                context = {
                    'player': player,
                    'game_state': game_state,
                    'print': print,
                    'input': input,
                    'ui': ui,
                }
                try:
                    exec(python_code, context)
                except Exception as e:
                    print(f"[on_exit执行错误] {e}")
            elif callable(self.on_exit):
                self.on_exit(player, game_state)



class _NPC:
    """NPC类（内部使用）"""
    
    def __init__(self, id, name, description):
        self.id = id
        self.name = name
        self.description = description
        self.dialog = None
    
    def set_dialog(self, dialog):
        self.dialog = dialog
    
    def talk(self, player, game_state):
        if self.dialog is not None:
            print(f"{self.name}: {self.dialog}")
        else:
            print(f"{self.name}: ...")


# 公共类别名（在类定义之后）
Scene = _Scene
Choice = _Choice
NPC = _NPC


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

def create_npc(id, name, description):
    """创建NPC，返回NPC对象"""
    npc = _NPC(id, name, description)
    return npc


def add_choice(scene, choice):
    """添加选择项到场景"""
    if isinstance(scene, _Scene):
        scene.add_choice(choice)
    else:
        raise HPLTypeError("第一个参数必须是场景对象")
    return None


def set_scene_description(scene_id, description):
    """设置场景描述"""
    scene = _get_scene(scene_id)
    if scene is None:
        raise HPLValueError(f"场景未找到: {scene_id}")
    scene.description = description
    return None


def add_scene_exit(scene_id, direction, target_scene_id):
    """添加场景出口"""
    scene = _get_scene(scene_id)
    if scene is None:
        raise HPLValueError(f"场景未找到: {scene_id}")
    scene.exits[direction] = target_scene_id
    return None


def get_scene_exits(scene_id):
    """获取场景出口"""
    scene = _get_scene(scene_id)
    if scene is None:
        raise HPLValueError(f"场景未找到: {scene_id}")
    return scene.exits


def set_scene_on_enter(scene_id, callback):
    """设置进入场景时的回调"""
    scene = _get_scene(scene_id)
    if scene is None:
        raise HPLValueError(f"场景未找到: {scene_id}")
    scene.on_enter = callback
    return None


def set_scene_on_exit(scene_id, callback):
    """设置离开场景时的回调"""
    scene = _get_scene(scene_id)
    if scene is None:
        raise HPLValueError(f"场景未找到: {scene_id}")
    scene.on_exit = callback
    return None


def display_scene(scene_id, player, game_state):
    """显示场景"""
    scene = _get_scene(scene_id)
    if scene is None:
        raise HPLValueError(f"场景未找到: {scene_id}")
    return scene.display(player, game_state)


def make_choice(scene_id, choice_index, player, game_state):
    """执行选择"""
    scene = _get_scene(scene_id)
    if scene is None:
        raise HPLValueError(f"场景未找到: {scene_id}")
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
