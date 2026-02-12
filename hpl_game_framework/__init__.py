#!/usr/bin/env python3
"""
HPL 游戏框架 - Python 模块版本
========

这是一个用于 HPL (High-level Programming Language) 的文字游戏框架，
提供了完整的游戏开发功能，包括：
- 游戏引擎核心（场景管理、存档系统）
- 玩家角色系统（属性、背包、任务）
- 场景系统（场景、选择、NPC）
- 游戏工具（随机数、文本格式化、骰子）
- 交互系统（输入处理、菜单、对话）

作者: HPL Framework Team
版本: 1.0.0
"""

# ============ 版本信息 ============
__version__ = "1.0.0"
__author__ = "HPL Framework Team"
__description__ = "HPL 游戏框架 - Python 模块版本"

# ============ 导入核心模块 ============
try:
    from .core.game_engine import (
        GameEngine,
        GameState,
        SaveManager,
        create_game_engine,
        create_game_state,
        create_save_manager,
        HPL_MODULE as game_engine_module
    )
    
    from .core.player import (
        Player,
        Item,
        Inventory,
        create_player,
        create_item,
        create_inventory,
        HPL_MODULE as player_module
    )
    
    from .core.scene import (
        Scene,
        Choice,
        NPC,
        create_scene,
        create_choice,
        create_npc,
        HPL_MODULE as scene_module
    )
    
    from .utils.game_utils import (
        RandomGenerator,
        TextFormatter,
        DiceRoller,
        create_random_generator,
        create_text_formatter,
        create_dice_roller,
        random_int,
        random_range,
        random_choice,
        roll_dice,
        clear_screen,
        print_line,
        print_title,
        print_box,
        print_progress,
        HPL_MODULE as game_utils_module
    )
    
    from .utils.interaction import (
        InputHandler,
        MenuSystem,
        DialogSystem,
        create_input_handler,
        create_menu_system,
        create_dialog_system,
        get_int,
        get_string,
        get_confirm,
        get_choice,
        pause,
        show_menu,
        show_dialog,
        show_narration,
        show_scene,
        show_system,
        show_combat,
        show_loot,
        show_stat_change,
        HPL_MODULE as interaction_module
    )
    
    # ============ 便捷访问 ============
    # 核心类
    GameEngine = GameEngine
    GameState = GameState
    SaveManager = SaveManager
    Player = Player
    Item = Item
    Inventory = Inventory
    Scene = Scene
    Choice = Choice
    NPC = NPC
    
    # 工具类
    RandomGenerator = RandomGenerator
    TextFormatter = TextFormatter
    DiceRoller = DiceRoller
    InputHandler = InputHandler
    MenuSystem = MenuSystem
    DialogSystem = DialogSystem
    
    # HPL 模块
    HPL_MODULES = {
        'game_engine': game_engine_module,
        'player': player_module,
        'scene': scene_module,
        'game_utils': game_utils_module,
        'interaction': interaction_module
    }
    
    # ============ 自动接口（可选） ============
    # 如果不想使用 HPLModule 显式接口，可以直接暴露这些函数
    def get_all_functions():
        """获取所有可用的函数"""
        functions = {}
        
        # 从各个模块收集函数
        for module_name, module in HPL_MODULES.items():
            if hasattr(module, 'list_functions'):
                funcs = module.list_functions()
                for func_name in funcs:
                    functions[f"{module_name}.{func_name}"] = getattr(module, func_name, None)
        
        return functions
    
    def get_all_constants():
        """获取所有可用的常量"""
        constants = {}
        
        # 从各个模块收集常量
        for module_name, module in HPL_MODULES.items():
            if hasattr(module, 'list_constants'):
                consts = module.list_constants()
                for const_name in consts:
                    constants[f"{module_name}.{const_name}"] = module.get_constant(const_name)
        
        return constants

except ImportError as e:
    # 如果导入失败，可能是 HPL 运行时不可用
    # 在这种情况下，我们仍然可以独立使用这些类
    print(f"警告: 无法导入 HPL 运行时模块: {e}")
    print("框架类仍然可用，但 HPL 集成功能将受限。")


# ============ 便捷函数 ============

def create_simple_game(player_name, start_scene_id):
    """
    创建一个简单的游戏实例
    
    Args:
        player_name: 玩家名称
        start_scene_id: 起始场景ID
    
    Returns:
        GameEngine 实例
    """
    engine = create_game_engine()
    engine.initialize(player_name)
    return engine


def quick_start(player_name):
    """
    快速开始一个新游戏
    
    Args:
        player_name: 玩家名称
    
    Returns:
        (GameEngine, Player) 元组
    """
    engine = create_game_engine()
    engine.initialize(player_name)
    return engine, engine.game_state.player


# ============ 模块信息 ============

def get_framework_info():
    """获取框架信息"""
    return {
        "name": "HPL Game Framework",
        "version": __version__,
        "author": __author__,
        "description": __description__,
        "modules": list(HPL_MODULES.keys()) if 'HPL_MODULES' in dir() else [],
        "python_version": "3.6+"
    }


# ============ 打印欢迎信息 ============

def print_welcome():
    """打印框架欢迎信息"""
    print("=" * 50)
    print("    HPL 游戏框架 - Python 模块版本")
    print(f"    版本: {__version__}")
    print("=" * 50)
    print("")
    print("可用模块:")
    if 'HPL_MODULES' in dir():
        for name in HPL_MODULES.keys():
            print(f"  - {name}")
    print("")
    print("快速开始:")
    print("  from hpl_game_framework import create_simple_game")
    print("  engine = create_simple_game('玩家名', 'start_scene')")
    print("  engine.run()")
    print("")


# 如果直接运行此文件，显示欢迎信息
if __name__ == "__main__":
    print_welcome()
