#!/usr/bin/env python3
"""
游戏引擎核心模块
========

管理游戏主循环、场景切换、存档系统。
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

import json
import time
import os

# ============ 内部类定义 ============

class _GameState:
    """游戏状态管理类（内部使用）"""
    
    def __init__(self):
        self.scenes = {}
        self.current_scene_id = None
        self.player = None
        self.game_over = False
        self.victory = False
        self.variables = {}
        self.flags = {}
        self.play_time = 0
        self.start_time = time.time()
        self.save_slot = 1
    
    def register_scene(self, scene):
        self.scenes[scene.id] = scene
    
    def get_scene(self, scene_id):
        return self.scenes.get(scene_id)
    
    def change_scene(self, scene_id):
        if scene_id not in self.scenes:
            print(f"错误：场景 '{scene_id}' 不存在")
            return False
        
        if self.current_scene_id is not None:
            current = self.get_scene(self.current_scene_id)
            if current is not None:
                current.exit(self.player, self)
        
        self.current_scene_id = scene_id
        new_scene = self.get_scene(scene_id)
        new_scene.enter(self.player, self)
        return True
    
    def set_var(self, key, value):
        self.variables[key] = value
    
    def get_var(self, key, default_val=None):
        return self.variables.get(key, default_val)
    
    def set_flag(self, flag, value=None):
        self.flags[flag] = value if value is not None else True
    
    def check_flag(self, flag):
        return self.flags.get(flag, False)
    
    def get_play_time(self):
        return time.time() - self.start_time
    
    def format_play_time(self):
        total_seconds = self.get_play_time()
        hours = int(total_seconds / 3600)
        minutes = int((total_seconds % 3600) / 60)
        seconds = int(total_seconds % 60)
        
        result = ""
        if hours > 0:
            result += f"{hours}小时"
        if minutes > 0 or hours > 0:
            result += f"{minutes}分钟"
        result += f"{seconds}秒"
        return result


class _SaveManager:
    """存档管理器（内部使用）"""
    
    def __init__(self, game_state):
        self.game_state = game_state
        self.save_dir = "saves"
    
    def create_save_data(self):
        player = self.game_state.player
        return {
            "player": {
                "name": player.name,
                "level": player.level,
                "exp": player.exp,
                "exp_to_next": player.exp_to_next,
                "hp": player.hp,
                "max_hp": player.max_hp,
                "mp": player.mp,
                "max_mp": player.max_mp,
                "strength": player.strength,
                "agility": player.agility,
                "intelligence": player.intelligence,
                "vitality": player.vitality,
                "status": player.status,
                "location": player.location,
                "inventory_gold": player.inventory.gold,
                "stats": player.stats
            },
            "current_scene": self.game_state.current_scene_id,
            "variables": self.game_state.variables,
            "flags": self.game_state.flags,
            "play_time": self.game_state.get_play_time(),
            "timestamp": time.time()
        }
    
    def save(self, slot=None):
        if slot is None:
            slot = self.game_state.save_slot
        
        try:
            save_data = self.create_save_data()
            filename = f"save_{slot}.json"
            
            if not os.path.exists(self.save_dir):
                os.makedirs(self.save_dir)
            
            filepath = os.path.join(self.save_dir, filename)
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(save_data, f, indent=2, ensure_ascii=False)
            
            print(f"游戏已保存到存档 {slot}")
            return True
        except Exception as e:
            print(f"保存失败: {e}")
            return False
    
    def load(self, slot=None):
        if slot is None:
            slot = 1
        
        try:
            filename = f"save_{slot}.json"
            filepath = os.path.join(self.save_dir, filename)
            
            if not os.path.exists(filepath):
                print(f"存档 {slot} 不存在")
                return False
            
            with open(filepath, 'r', encoding='utf-8') as f:
                save_data = json.load(f)
            
            self.restore_save_data(save_data)
            print(f"游戏已从存档 {slot} 加载")
            return True
        except Exception as e:
            print(f"加载失败: {e}")
            return False
    
    def restore_save_data(self, save_data):
        player_data = save_data["player"]
        player = self.game_state.player
        
        player.name = player_data["name"]
        player.level = player_data["level"]
        player.exp = player_data["exp"]
        player.exp_to_next = player_data["exp_to_next"]
        player.hp = player_data["hp"]
        player.max_hp = player_data["max_hp"]
        player.mp = player_data["mp"]
        player.max_mp = player_data["max_mp"]
        player.strength = player_data["strength"]
        player.agility = player_data["agility"]
        player.intelligence = player_data["intelligence"]
        player.vitality = player_data["vitality"]
        player.status = player_data["status"]
        player.location = player_data["location"]
        player.inventory.gold = player_data["inventory_gold"]
        player.stats = player_data["stats"]
        
        self.game_state.current_scene_id = save_data["current_scene"]
        self.game_state.variables = save_data["variables"]
        self.game_state.flags = save_data["flags"]
        self.game_state.start_time = time.time() - save_data["play_time"]
    
    def list_saves(self):
        saves = []
        for slot in range(1, 6):
            filename = f"save_{slot}.json"
            filepath = os.path.join(self.save_dir, filename)
            if os.path.exists(filepath):
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        save_data = json.load(f)
                    timestamp = save_data["timestamp"]
                    formatted_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(timestamp))
                    saves.append(f"存档 {slot}: {formatted_time} - {save_data['player']['name']} (Lv.{save_data['player']['level']})")
                except Exception:
                    saves.append(f"存档 {slot}: [损坏]")
            else:
                saves.append(f"存档 {slot}: [空]")
        return saves


class _GameEngine:
    """游戏引擎主类（内部使用）"""
    
    def __init__(self):
        self.game_state = _GameState()
        self.save_manager = _SaveManager(self.game_state)
        self.running = False
        self.debug_mode = False
    
    def initialize(self, player_name, player_module):
        """初始化游戏"""
        player = player_module.create_player(player_name)
        self.game_state.player = player
        
        print("")
        print(f"欢迎, {player_name}!")
        print("你的冒险即将开始...")
        print("")
        
        input("按回车键继续...")
    
    def register_scene(self, scene):
        self.game_state.register_scene(scene)
    
    def set_start_scene(self, scene_id):
        self.game_state.change_scene(scene_id)
    
    def run(self):
        self.running = True
        
        while self.running:
            if self.game_state.game_over:
                self._show_game_over()
                break
            
            if self.game_state.victory:
                self._show_victory()
                break
            
            current_scene = self.game_state.get_scene(self.game_state.current_scene_id)
            if current_scene is None:
                print("错误：当前场景无效")
                break
            
            self._clear_screen()
            available_choices = current_scene.display(self.game_state.player, self.game_state)
            self._show_status_bar()
            
            print("")
            print("请输入选项编号 (或输入 S保存 L加载 I背包 Q退出): ")
            input_str = input()
            
            if input_str.upper() == "Q":
                confirm = input("确定要退出游戏吗? (Y/N): ")
                if confirm.upper() == "Y":
                    self.running = False
                    break
                continue
            
            if input_str.upper() == "S":
                self.save_manager.save(None)
                input("按回车键继续...")
                continue
            
            if input_str.upper() == "L":
                self._show_load_menu()
                continue
            
            if input_str.upper() == "I":
                self.game_state.player.show_inventory()
                input("按回车键继续...")
                continue
            
            try:
                choice_num = int(input_str)
                if 1 <= choice_num <= len(available_choices):
                    target_scene = current_scene.make_choice(choice_num - 1, self.game_state.player, self.game_state)
                    if target_scene is not None:
                        self.game_state.change_scene(target_scene)
                else:
                    print("无效选项")
            except ValueError:
                print("请输入有效的数字或命令")
            
            input("按回车键继续...")
        
        print("")
        print("感谢游玩！")
        print(f"游戏时间: {self.game_state.format_play_time()}")
    
    def _clear_screen(self):
        print("\n" * 50)
    
    def _show_status_bar(self):
        player = self.game_state.player
        print("")
        print(f"[{player.name} | Lv.{player.level} | HP:{player.hp}/{player.max_hp} | MP:{player.mp}/{player.max_mp} | 金币:{player.inventory.gold}]")
        print("[命令: S保存 L加载 I背包 Q退出]")
    
    def _show_game_over(self):
        self._clear_screen()
        self._print_title("游 戏 结 束")
        print("")
        print("你的冒险到此结束...")
        print("")
        print(f"游戏时间: {self.game_state.format_play_time()}")
        print("")
        input("按回车键退出...")
    
    def _show_victory(self):
        self._clear_screen()
        self._print_title("🎉 胜 利 🎉")
        print("")
        print("恭喜你完成了冒险！")
        print("")
        player = self.game_state.player
        print("最终状态:")
        player.show_status()
        print("")
        print(f"游戏时间: {self.game_state.format_play_time()}")
        print("")
        input("按回车键退出...")
    
    def _print_title(self, text):
        print("")
        print("=" * 50)
        padding = (50 - len(text)) // 2
        left_pad = " " * padding
        print(left_pad + text)
        print("=" * 50)
        print("")
    
    def _show_load_menu(self):
        self._clear_screen()
        self._print_title("加 载 游 戏")
        print("")
        
        saves = self.save_manager.list_saves()
        for i, save in enumerate(saves):
            print(f"  {save}")
        
        print("")
        print("  [0] 返回")
        print("")
        
        try:
            slot = int(input("请选择要加载的存档 (0-5): "))
            if 0 <= slot <= 5:
                if slot > 0:
                    self.save_manager.load(slot)
        except ValueError:
            print("请输入有效的数字")


# ============ 引擎实例管理 ============

_engines = {}

def _get_engine(engine_id):
    """获取引擎实例"""
    return _engines.get(engine_id)

def _set_engine(engine_id, engine):
    """存储引擎实例"""
    _engines[engine_id] = engine


# ============ 模块级函数（HPL可调用的API） ============

def create_game_engine():
    """创建游戏引擎实例"""
    engine = _GameEngine()
    engine_id = f"engine_{id(engine)}"
    _set_engine(engine_id, engine)
    return engine_id

def initialize_game(engine_id, player_name, player_module):
    """初始化游戏引擎"""
    engine = _get_engine(engine_id)
    if engine is None:
        raise HPLValueError(f"Invalid engine ID: {engine_id}")
    
    # 处理 HPLModule 对象或普通 Python 模块
    if hasattr(player_module, 'call_function'):
        # HPLModule 对象，使用 call_function 调用 create_player
        player = player_module.call_function('create_player', [player_name])
    else:
        # 普通 Python 模块
        player = player_module.create_player(player_name)
    
    engine.game_state.player = player
    
    print("")
    print(f"欢迎, {player_name}!")
    print("你的冒险即将开始...")
    print("")
    
    input("按回车键继续...")
    return None


def register_scene(engine_id, scene):
    """注册场景"""
    engine = _get_engine(engine_id)
    if engine is None:
        raise HPLValueError(f"Invalid engine ID: {engine_id}")
    engine.register_scene(scene)
    return None

def set_start_scene(engine_id, scene_id):
    """设置起始场景"""
    engine = _get_engine(engine_id)
    if engine is None:
        raise HPLValueError(f"Invalid engine ID: {engine_id}")
    engine.set_start_scene(scene_id)
    return None

def run_game(engine_id):
    """运行游戏"""
    engine = _get_engine(engine_id)
    if engine is None:
        raise HPLValueError(f"Invalid engine ID: {engine_id}")
    engine.run()
    return None

def get_game_state(engine_id):
    """获取游戏状态"""
    engine = _get_engine(engine_id)
    if engine is None:
        raise HPLValueError(f"Invalid engine ID: {engine_id}")
    return engine.game_state

def get_player(engine_id):
    """获取玩家对象"""
    engine = _get_engine(engine_id)
    if engine is None:
        raise HPLValueError(f"Invalid engine ID: {engine_id}")
    return engine.game_state.player

def save_game(engine_id, slot=None):
    """保存游戏"""
    engine = _get_engine(engine_id)
    if engine is None:
        raise HPLValueError(f"Invalid engine ID: {engine_id}")
    return engine.save_manager.save(slot)

def load_game(engine_id, slot=None):
    """加载游戏"""
    engine = _get_engine(engine_id)
    if engine is None:
        raise HPLValueError(f"Invalid engine ID: {engine_id}")
    return engine.save_manager.load(slot)


# ============ 模块注册 ============

HPL_MODULE = HPLModule("game_engine", "游戏引擎核心 - 管理游戏主循环、场景切换、存档系统")

# 注册函数
HPL_MODULE.register_function('create_game_engine', create_game_engine, 0, '创建游戏引擎实例，返回引擎ID')
HPL_MODULE.register_function('initialize_game', initialize_game, 3, '初始化游戏引擎 (engine_id, player_name, player_module)')
HPL_MODULE.register_function('register_scene', register_scene, 2, '注册场景 (engine_id, scene)')
HPL_MODULE.register_function('set_start_scene', set_start_scene, 2, '设置起始场景 (engine_id, scene_id)')
HPL_MODULE.register_function('run_game', run_game, 1, '运行游戏 (engine_id)')
HPL_MODULE.register_function('get_game_state', get_game_state, 1, '获取游戏状态 (engine_id)')
HPL_MODULE.register_function('get_player', get_player, 1, '获取玩家对象 (engine_id)')
HPL_MODULE.register_function('save_game', save_game, None, '保存游戏 (engine_id, slot?)')
HPL_MODULE.register_function('load_game', load_game, None, '加载游戏 (engine_id, slot?)')

# 注册常量
HPL_MODULE.register_constant('VERSION', "2.0.0", '模块版本')
HPL_MODULE.register_constant('AUTHOR', "HPL Framework Team", '模块作者')
