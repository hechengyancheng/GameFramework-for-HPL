#!/usr/bin/env python3
"""
玩家角色系统模块
========

管理玩家属性、背包、状态。

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


# ============ 物品类 ============

class Item:
    """物品类"""
    
    def __init__(self, id, name, description, item_type, value):
        self.id = id
        self.name = name
        self.description = description
        self.type = item_type  # weapon, armor, consumable, key, misc
        self.value = value
        self.quantity = 1
        self.equipped = False
        self.stats = {}  # 额外属性如攻击力、防御力等
    
    def set_stat(self, key, value):
        """设置物品属性"""
        self.stats[key] = value
    
    def get_stat(self, key, default_val=None):
        """获取物品属性"""
        if key in self.stats:
            return self.stats[key]
        return default_val
    
    def get_info(self):
        """显示物品信息"""
        info = self.name
        if self.quantity > 1:
            info += f" x{self.quantity}"
        if self.equipped:
            info += " [已装备]"
        return info


# ============ 背包系统 ============

class Inventory:
    """背包系统"""
    
    def __init__(self, capacity=20):
        self.capacity = capacity
        self.items = []
        self.gold = 0
    
    def add_item(self, item):
        """添加物品"""
        # 检查是否可堆叠
        if item.type in ["consumable", "misc"]:
            for existing in self.items:
                if existing.id == item.id:
                    existing.quantity += item.quantity
                    return True
        
        # 检查容量
        if len(self.items) >= self.capacity:
            return False
        
        self.items.append(item)
        return True
    
    def remove_item(self, index, quantity=1):
        """移除物品"""
        if index < 0 or index >= len(self.items):
            return None
        item = self.items[index]
        if item.quantity <= quantity:
            # 移除整个物品
            return self.items.pop(index)
        else:
            # 减少数量
            item.quantity -= quantity
            # 创建副本返回
            copy = Item(item.id, item.name, item.description, item.type, item.value)
            copy.quantity = quantity
            return copy
    
    def get_item(self, index):
        """获取物品"""
        if index < 0 or index >= len(self.items):
            return None
        return self.items[index]
    
    def find_item(self, item_id):
        """查找物品"""
        for i, item in enumerate(self.items):
            if item.id == item_id:
                return i
        return -1
    
    def has_item(self, item_id):
        """检查是否有物品"""
        return self.find_item(item_id) >= 0
    
    def get_item_list(self):
        """获取物品列表"""
        result = []
        for i, item in enumerate(self.items):
            result.append(f"{i + 1}. {item.get_info()}")
        return result
    
    def get_equipped_weapon(self):
        """获取已装备武器"""
        for item in self.items:
            if item.type == "weapon" and item.equipped:
                return item
        return None
    
    def get_equipped_armor(self):
        """获取已装备防具"""
        for item in self.items:
            if item.type == "armor" and item.equipped:
                return item
        return None
    
    def equip_item(self, index):
        """装备物品"""
        if index < 0 or index >= len(self.items):
            return False
        item = self.items[index]
        
        # 取消同类型其他装备的装备状态
        if item.type in ["weapon", "armor"]:
            for other in self.items:
                if other.type == item.type:
                    other.equipped = False
        
        item.equipped = True
        return True
    
    def unequip_item(self, index):
        """卸下装备"""
        if index < 0 or index >= len(self.items):
            return False
        self.items[index].equipped = False
        return True
    
    def add_gold(self, amount):
        """添加金币"""
        self.gold += amount
        return self.gold
    
    def spend_gold(self, amount):
        """消费金币"""
        if self.gold < amount:
            return False
        self.gold -= amount
        return True


# ============ 玩家角色 ============

class Player:
    """玩家角色"""
    
    def __init__(self, name):
        self.name = name
        self.level = 1
        self.exp = 0
        self.exp_to_next = 100
        
        # 基础属性
        self.max_hp = 100
        self.hp = 100
        self.max_mp = 50
        self.mp = 50
        
        # 战斗属性
        self.strength = 10  # 力量，影响物理攻击
        self.agility = 10   # 敏捷，影响速度和闪避
        self.intelligence = 10  # 智力，影响魔法攻击和MP
        self.vitality = 10  # 体质，影响HP和防御
        
        # 状态
        self.status = "normal"  # normal, poisoned, paralyzed, etc.
        self.location = "start"
        
        # 背包
        self.inventory = Inventory(20)
        
        # 任务记录
        self.quests = []
        self.completed_quests = []
        
        # 游戏统计
        self.stats = {
            "monsters_killed": 0,
            "deaths": 0,
            "items_found": 0,
            "gold_earned": 0,
            "play_time": 0
        }
    
    def get_attack(self):
        """计算属性值（包含装备加成）"""
        base = self.strength
        weapon = self.inventory.get_equipped_weapon()
        if weapon is not None:
            bonus = weapon.get_stat("attack", 0)
            base += bonus
        return base
    
    def get_defense(self):
        """计算防御力"""
        base = self.vitality / 2
        armor = self.inventory.get_equipped_armor()
        if armor is not None:
            bonus = armor.get_stat("defense", 0)
            base += bonus
        return int(base)
    
    def get_speed(self):
        """计算速度"""
        return self.agility
    
    def heal(self, amount):
        """生命值管理"""
        self.hp += amount
        if self.hp > self.max_hp:
            self.hp = self.max_hp
        return self.hp
    
    def take_damage(self, amount):
        """受到伤害"""
        self.hp -= amount
        if self.hp < 0:
            self.hp = 0
        return self.hp
    
    def is_alive(self):
        """是否存活"""
        return self.hp > 0
    
    def use_mp(self, amount):
        """使用魔法值"""
        if self.mp < amount:
            return False
        self.mp -= amount
        return True
    
    def restore_mp(self, amount):
        """恢复魔法值"""
        self.mp += amount
        if self.mp > self.max_mp:
            self.mp = self.max_mp
        return self.mp
    
    def gain_exp(self, amount):
        """获得经验值"""
        self.exp += amount
        if self.exp >= self.exp_to_next:
            self.level_up()
    
    def level_up(self):
        """升级"""
        self.level += 1
        self.exp -= self.exp_to_next
        self.exp_to_next = int(self.exp_to_next * 1.5)
        
        # 属性成长
        hp_growth = 10 + self.vitality // 5
        mp_growth = 5 + self.intelligence // 5
        
        self.max_hp += hp_growth
        self.max_mp += mp_growth
        self.hp = self.max_hp
        self.mp = self.max_mp
        
        print(f"🎉 升级了！等级提升到 {self.level}")
        print(f"   最大HP: +{hp_growth}  最大MP: +{mp_growth}")
    
    def show_status(self):
        """显示状态"""
        print("")
        print("========== 角色状态 ==========")
        print(f"姓名: {self.name}")
        print(f"等级: {self.level}  (经验: {self.exp}/{self.exp_to_next})")
        print("")
        print(f"生命值: {self.hp}/{self.max_hp}")
        print(f"魔法值: {self.mp}/{self.max_mp}")
        print("")
        print(f"力量: {self.strength}  敏捷: {self.agility}")
        print(f"智力: {self.intelligence}  体质: {self.vitality}")
        print("")
        print(f"攻击力: {self.get_attack()}  防御力: {self.get_defense()}")
        print(f"速度: {self.get_speed()}")
        print("")
        print(f"金币: {self.inventory.gold}")
        print(f"状态: {self.status}")
        print("============================")
    
    def show_inventory(self):
        """显示背包"""
        print("")
        print("========== 背包 ==========")
        print(f"金币: {self.inventory.gold}")
        print(f"容量: {len(self.inventory.items)}/{self.inventory.capacity}")
        print("")
        items = self.inventory.get_item_list()
        if len(items) == 0:
            print("背包是空的")
        else:
            for item in items:
                print(item)
        print("==========================")
    
    def add_quest(self, quest_id, quest_name, description):
        """添加任务"""
        quest = {
            "id": quest_id,
            "name": quest_name,
            "description": description,
            "completed": False,
            "objectives": []
        }
        self.quests.append(quest)
        print(f"📜 接受任务: {quest_name}")
    
    def complete_quest(self, quest_id):
        """完成任务"""
        for quest in self.quests:
            if quest["id"] == quest_id:
                quest["completed"] = True
                self.completed_quests.append(quest)
                print(f"✅ 完成任务: {quest['name']}")
                return True
        return False
    
    def get_active_quests(self):
        """获取进行中的任务"""
        active = []
        for quest in self.quests:
            if not quest["completed"]:
                active.append(quest)
        return active


# ============ 模块级函数 ============

def create_player(name):
    """创建玩家实例"""
    return Player(name)

def create_item(id, name, description, item_type, value):
    """创建物品实例"""
    return Item(id, name, description, item_type, value)

def create_inventory(capacity=20):
    """创建背包实例"""
    return Inventory(capacity)


# ============ 模块注册 ============

HPL_MODULE = HPLModule("player", "玩家角色系统 - 管理玩家属性、背包、状态")

# 注册函数
HPL_MODULE.register_function('create_player', create_player, 1, '创建玩家实例')
HPL_MODULE.register_function('create_item', create_item, 5, '创建物品实例')
HPL_MODULE.register_function('create_inventory', create_inventory, None, '创建背包实例')

# 注册常量
HPL_MODULE.register_constant('VERSION', "1.0.0", '模块版本')
HPL_MODULE.register_constant('AUTHOR', "HPL Framework Team", '模块作者')
