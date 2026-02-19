#!/usr/bin/env python3
"""
声明式动作系统测试脚本
"""

import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from hpl_game_framework.core.scene import (
    _Choice, _Scene, 
    _execute_declarative_action,
    register_action_handler,
    _action_handlers
)

# 模拟玩家类
class MockInventory:
    def __init__(self):
        self.gold = 100
        self.items = []
    
    def add_gold(self, amount):
        self.gold += amount
        return self.gold
    
    def add_item(self, item):
        self.items.append(item)
        return True

class MockPlayer:
    def __init__(self):
        self.hp = 100
        self.max_hp = 100
        self.mp = 50
        self.max_mp = 50
        self.inventory = MockInventory()
        self.location = "forest"
    
    def heal(self, amount):
        self.hp = min(self.hp + amount, self.max_hp)
        return self.hp
    
    def gain_exp(self, amount):
        print(f"  [经验] 获得 {amount} 经验值")
        return amount

# 模拟游戏状态
class MockGameState:
    def __init__(self):
        self.items = {
            "herb_001": {"id": "herb_001", "name": "草药", "type": "material", "value": 5},
            "potion_001": {"id": "potion_001", "name": "生命药水", "type": "consumable", "value": 20},
            "sword_001": {"id": "sword_001", "name": "生锈的剑", "type": "weapon", "value": 50},
        }

def test_random_event():
    """测试随机事件动作"""
    print("\n=== 测试 random_event ===")
    player = MockPlayer()
    game_state = MockGameState()
    
    action_def = {
        "type": "random_event",
        "events": [
            {"chance": 30, "message": "发现草药！", "give_items": [{"id": "herb_001", "count": 1}]},
            {"chance": 70, "message": "什么也没找到。"}
        ]
    }
    
    print("执行随机事件（运行3次看不同结果）：")
    for i in range(3):
        print(f"\n  第 {i+1} 次:")
        _execute_declarative_action(action_def, player, game_state)

def test_give_item():
    """测试给予物品动作"""
    print("\n=== 测试 give_item ===")
    player = MockPlayer()
    game_state = MockGameState()
    
    action_def = {
        "type": "give_item",
        "item_id": "potion_001",
        "count": 2,
        "message": "获得生命药水！"
    }
    
    _execute_declarative_action(action_def, player, game_state)
    print(f"  物品栏: {[item.name for item in player.inventory.items]}")

def test_give_gold():
    """测试给予金币动作"""
    print("\n=== 测试 give_gold ===")
    player = MockPlayer()
    game_state = MockGameState()
    
    old_gold = player.inventory.gold
    action_def = {
        "type": "give_gold",
        "amount": 50,
        "message": "发现金币袋！"
    }
    
    _execute_declarative_action(action_def, player, game_state)
    print(f"  金币: {old_gold} -> {player.inventory.gold}")

def test_heal():
    """测试治疗动作"""
    print("\n=== 测试 heal ===")
    player = MockPlayer()
    game_state = MockGameState()
    
    player.hp = 50  # 先扣血
    action_def = {
        "type": "heal",
        "amount": 30,
        "message": "使用治疗药水！"
    }
    
    _execute_declarative_action(action_def, player, game_state)
    print(f"  当前HP: {player.hp}")

def test_damage():
    """测试伤害动作"""
    print("\n=== 测试 damage ===")
    player = MockPlayer()
    game_state = MockGameState()
    
    action_def = {
        "type": "damage",
        "amount": 15,
        "message": "踩到陷阱！"
    }
    
    _execute_declarative_action(action_def, player, game_state)
    print(f"  当前HP: {player.hp}")

def test_show_message():
    """测试显示消息动作"""
    print("\n=== 测试 show_message ===")
    player = MockPlayer()
    game_state = MockGameState()
    
    action_def = {
        "type": "show_message",
        "message": "欢迎来到迷雾森林！",
        "msg_type": "system"
    }
    
    _execute_declarative_action(action_def, player, game_state)

def test_condition():
    """测试条件分支动作"""
    print("\n=== 测试 condition ===")
    player = MockPlayer()
    game_state = MockGameState()
    
    # 测试金币检查
    action_def = {
        "type": "condition",
        "condition_type": "gold_at_least",
        "condition_value": 50,
        "success": {"type": "show_message", "message": "金币充足！"},
        "fail": {"type": "show_message", "message": "金币不足！"}
    }
    
    print("  金币100时:")
    _execute_declarative_action(action_def, player, game_state)
    
    player.inventory.gold = 30
    print("  金币30时:")
    _execute_declarative_action(action_def, player, game_state)

def test_sequence():
    """测试顺序执行动作"""
    print("\n=== 测试 sequence ===")
    player = MockPlayer()
    game_state = MockGameState()
    
    action_def = {
        "type": "sequence",
        "actions": [
            {"type": "show_message", "message": "开始探索..."},
            {"type": "give_gold", "amount": 10},
            {"type": "heal", "amount": 5},
            {"type": "show_message", "message": "探索完成！"}
        ]
    }
    
    _execute_declarative_action(action_def, player, game_state)
    print(f"  最终状态: HP={player.hp}, 金币={player.inventory.gold}")

def test_choice_execute_action():
    """测试 _Choice 类的 execute_action 方法"""
    print("\n=== 测试 _Choice.execute_action ===")
    player = MockPlayer()
    game_state = MockGameState()
    
    # 测试声明式动作
    choice = _Choice("测试选择", None, None, {
        "type": "show_message",
        "message": "通过Choice执行声明式动作"
    })
    choice.execute_action(player, game_state)
    
    # 测试HPL代码块（向后兼容）
    print("\n  测试HPL代码块向后兼容:")
    choice2 = _Choice("测试选择2", None, None, """
print("[HPL代码块] 执行成功！")
    """)
    choice2.execute_action(player, game_state)

def list_action_handlers():
    """列出所有已注册的动作处理器"""
    print("\n=== 已注册的动作处理器 ===")
    for name in _action_handlers:
        print(f"  - {name}")

if __name__ == "__main__":
    print("=" * 50)
    print("声明式动作系统测试")
    print("=" * 50)
    
    list_action_handlers()
    
    test_random_event()
    test_give_item()
    test_give_gold()
    test_heal()
    test_damage()
    test_show_message()
    test_condition()
    test_sequence()
    test_choice_execute_action()
    
    print("\n" + "=" * 50)
    print("所有测试完成！")
    print("=" * 50)
