#!/usr/bin/env python3
"""
游戏引擎核心模块
========

管理游戏主循环、场景切换、存档系统。

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

import json
import time
import os

# ============ 游戏状态管理 ============

class GameState:
    """游戏状态管理类"""
    
    def __init__(self):
        self.scenes = {}              # 场景字典 {id: Scene}
        self.current_scene_id = None
        self.player = None
        self.game_over = False
        self.victory = False
        self.variables = {}           # 游戏变量
        self.flags = {}               # 游戏标志
        self.play_time = 0            # 游戏时间（秒）
        self.start_time = time.time()
        self.save_slot = 1
    
    def register_scene(self, scene):
        """注册场景"""
        self.scenes[scene.id] = scene
    
    def get_scene(self, scene_id):
        """获取场景"""
        if scene_id in self.scenes:
            return self.scenes[scene_id]
        return None
    
    def change_scene(self, scene_id):
        """切换场景"""
        if scene_id not in self.scenes:
            print(f"错误：场景 '{scene_id}' 不存在")
            return False
        
        # 离开当前场景
        if self.current_scene_id is not None:
            current = self.get_scene(self.current_scene_id)
            if current is not None:
                current.exit(self.player, self)
        
        # 切换场景
        self.current_scene_id = scene_id
        new_scene = self.get_scene(scene_id)
        
        # 进入新场景
        new_scene.enter(self.player, self)
        
        return True
    
    def set_var(self, key, value):
        """设置变量"""
        self.variables[key] = value
    
    def get_var(self, key, default_val=None):
        """获取变量"""
        if key in self.variables:
            return self.variables[key]
        return default_val
    
    def set_flag(self, flag, value=None):
        """设置标志"""
        if value is None:
            value = True
        self.flags[flag] = value
    
    def check_flag(self, flag):
        """检查标志"""
        if flag in self.flags:
            return self.flags[flag]
        return False
    
    def get_play_time(self):
        """获取游戏时间"""
        current = time.time()
        elapsed = current - self.start_time
        return elapsed
    
    def format_play_time(self):
        """格式化游戏时间"""
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


# ============ 存档管理器 ============

class SaveManager:
    """存档管理器"""
    
    def __init__(self, game_state):
        self.game_state = game_state
        self.save_dir = "saves"
    
    def create_save_data(self):
        """创建存档数据"""
        player = self.game_state.player
        
        # 保存玩家数据
        save_data = {
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
        
        return save_data
    
    def save(self, slot=None):
        """保存游戏"""
        if slot is None:
            slot = self.game_state.save_slot
        
        try:
            save_data = self.create_save_data()
            filename = f"save_{slot}.json"
            
            # 确保存档目录存在
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
        """加载游戏"""
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
            
            # 恢复游戏状态
            self.restore_save_data(save_data)
            
            print(f"游戏已从存档 {slot} 加载")
            return True
        except Exception as e:
            print(f"加载失败: {e}")
            return False
    
    def restore_save_data(self, save_data):
        """恢复存档数据"""
        # 恢复玩家数据
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
        
        # 恢复游戏状态
        self.game_state.current_scene_id = save_data["current_scene"]
        self.game_state.variables = save_data["variables"]
        self.game_state.flags = save_data["flags"]
        self.game_state.start_time = time.time() - save_data["play_time"]
    
    def list_saves(self):
        """列出所有存档"""
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


# ============ 游戏引擎 ============

class GameEngine:
    """游戏引擎主类"""
    
    def __init__(self):
        self.game_state = GameState()
        self.save_manager = SaveManager(self.game_state)
        self.running = False
        self.debug_mode = False
    
    def initialize(self, player_name):
        """初始化游戏"""
        # 创建玩家（需要从player模块导入）
        from .player import Player
        player = Player(player_name)
        self.game_state.player = player
        
        print("")
        print(f"欢迎, {player_name}!")
        print("你的冒险即将开始...")
        print("")
        
        input("按回车键继续...")
    
    def register_scene(self, scene):
        """注册场景"""
        self.game_state.register_scene(scene)
    
    def set_start_scene(self, scene_id):
        """设置起始场景"""
        self.game_state.change_scene(scene_id)
    
    def run(self):
        """游戏主循环"""
        self.running = True
        
        while self.running:
            # 检查游戏结束条件
            if self.game_state.game_over:
                self.show_game_over()
                break
            
            if self.game_state.victory:
                self.show_victory()
                break
            
            # 获取当前场景
            current_scene = self.game_state.get_scene(self.game_state.current_scene_id)
            if current_scene is None:
                print("错误：当前场景无效")
                break
            
            # 显示场景
            self.clear_screen()
            available_choices = current_scene.display(self.game_state.player, self.game_state)
            
            # 显示玩家状态栏
            self.show_status_bar()
            
            # 获取玩家选择
            print("")
            print("请输入选项编号 (或输入 S保存 L加载 I背包 Q退出): ")
            input_str = input()
            
            # 处理特殊命令
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
                self.show_load_menu()
                continue
            
            if input_str.upper() == "I":
                self.game_state.player.show_inventory()
                input("按回车键继续...")
                continue
            
            # 处理场景选择
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
    
    def clear_screen(self):
        """清屏"""
        # 使用多个换行模拟清屏
        print("\n" * 50)
    
    def show_status_bar(self):
        """显示状态栏"""
        player = self.game_state.player
        print("")
        print(f"[{player.name} | Lv.{player.level} | HP:{player.hp}/{player.max_hp} | MP:{player.mp}/{player.max_mp} | 金币:{player.inventory.gold}]")
        print("[命令: S保存 L加载 I背包 Q退出]")
    
    def show_game_over(self):
        """显示游戏结束"""
        self.clear_screen()
        self.print_title("游 戏 结 束")
        print("")
        print("你的冒险到此结束...")
        print("")
        print(f"游戏时间: {self.game_state.format_play_time()}")
        print("")
        input("按回车键退出...")
    
    def show_victory(self):
        """显示胜利画面"""
        self.clear_screen()
        self.print_title("🎉 胜 利 🎉")
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
    
    def print_title(self, text):
        """打印标题"""
        print("")
        print("=" * 50)
        # 居中显示
        padding = (50 - len(text)) // 2
        left_pad = " " * padding
        print(left_pad + text)
        print("=" * 50)
        print("")
    
    def show_load_menu(self):
        """显示加载菜单"""
        self.clear_screen()
        self.print_title("加 载 游 戏")
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
    
    def show_main_menu(self):
        """显示主菜单"""
        while True:
            self.clear_screen()
            self.print_title("HPL 文字游戏框架")
            print("")
            print("  [1] 开始新游戏")
            print("  [2] 加载游戏")
            print("  [3] 退出")
            print("")
            
            try:
                choice = int(input("请选择: "))
                if choice == 1:
                    return "new"
                elif choice == 2:
                    return "load"
                elif choice == 3:
                    return "exit"
            except ValueError:
                print("请输入有效的数字")
    
    def continue_from_save(self, slot):
        """从存档继续游戏"""
        if self.save_manager.load(slot):
            # 恢复后继续游戏循环
            self.run()
            return True
        return False


# ============ 模块级函数 ============

def create_game_engine():
    """创建游戏引擎实例"""
    return GameEngine()

def create_game_state():
    """创建游戏状态实例"""
    return GameState()

def create_save_manager(game_state):
    """创建存档管理器实例"""
    return SaveManager(game_state)


# ============ 模块注册 ============

HPL_MODULE = HPLModule("game_engine", "游戏引擎核心 - 管理游戏主循环、场景切换、存档系统")

# 注册函数
HPL_MODULE.register_function('create_game_engine', create_game_engine, 0, '创建游戏引擎实例')
HPL_MODULE.register_function('create_game_state', create_game_state, 0, '创建游戏状态实例')
HPL_MODULE.register_function('create_save_manager', create_save_manager, 1, '创建存档管理器实例')

# 注册常量
HPL_MODULE.register_constant('VERSION', "1.0.0", '模块版本')
HPL_MODULE.register_constant('AUTHOR', "HPL Framework Team", '模块作者')
