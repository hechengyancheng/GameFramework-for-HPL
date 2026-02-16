#!/usr/bin/env python3
"""
玩家角色系统模块
========

管理玩家属性、背包、状态。
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

class _Item:
    """物品类（内部使用）"""
    
    def __init__(self, id, name, description, item_type, value):
        self.id = id
        self.name = name
        self.description = description
        self.type = item_type
        self.value = value
        self.quantity = 1
        self.equipped = False
        self.stats = {}
    
    def set_stat(self, key, value):
        self.stats[key] = value
    
    def get_stat(self, key, default_val=None):
        return self.stats.get(key, default_val)


class _Inventory:
    """背包系统（内部使用）"""
    
    def __init__(self, capacity=20):
        self.capacity = capacity
        self.items = []
        self.gold = 0
    
    def add_item(self, item):
        if item.type in ["consumable", "misc"]:
            for existing in self.items:
                if existing.id == item.id:
                    existing.quantity += item.quantity
                    return True
        
        if len(self.items) >= self.capacity:
            return False
        
        self.items.append(item)
        return True
    
    def add_gold(self, amount):
        self.gold += amount
        return self.gold
    
    def get_item_list(self):
        result = []
        for i, item in enumerate(self.items):
            info = item.name
            if item.quantity > 1:
                info += f" x{item.quantity}"
            if item.equipped:
                info += " [已装备]"
            result.append(f"{i + 1}. {info}")
        return result
    
    def get_equipped_weapon(self):
        for item in self.items:
            if item.type == "weapon" and item.equipped:
                return item
        return None


class _Player:
    """玩家角色（内部使用）"""
    
    def __init__(self, name):
        self.name = name
        self.level = 1
        self.exp = 0
        self.exp_to_next = 100
        
        self.max_hp = 100
        self.hp = 100
        self.max_mp = 50
        self.mp = 50
        
        self.strength = 10
        self.agility = 10
        self.intelligence = 10
        self.vitality = 10
        
        self.status = "normal"
        self.location = "start"
        
        self.inventory = _Inventory(20)
        self.stats = {
            "monsters_killed": 0,
            "deaths": 0,
            "items_found": 0,
            "gold_earned": 0,
            "play_time": 0
        }
    
    def get_attack(self):
        base = self.strength
        weapon = self.inventory.get_equipped_weapon()
        if weapon is not None:
            bonus = weapon.get_stat("attack", 0)
            base += bonus
        return base
    
    def heal(self, amount):
        self.hp += amount
        if self.hp > self.max_hp:
            self.hp = self.max_hp
        return self.hp
    
    def gain_exp(self, amount):
        self.exp += amount
        if self.exp >= self.exp_to_next:
            self.level_up()
    
    def level_up(self):
        self.level += 1
        self.exp -= self.exp_to_next
        self.exp_to_next = int(self.exp_to_next * 1.5)
        
        hp_growth = 10 + self.vitality // 5
        mp_growth = 5 + self.intelligence // 5
        
        self.max_hp += hp_growth
        self.max_mp += mp_growth
        self.hp = self.max_hp
        self.mp = self.max_mp
        
        print(f"🎉 升级了！等级提升到 {self.level}")
        print(f"   最大HP: +{hp_growth}  最大MP: +{mp_growth}")
    
    def show_status(self):
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
        print(f"攻击力: {self.get_attack()}")
        print(f"金币: {self.inventory.gold}")
        print(f"状态: {self.status}")
        print("============================")
    
    def show_inventory(self):
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


# ============ 对象实例管理 ============

_players = {}
_items = {}

def _get_player(player_id):
    """获取玩家实例"""
    return _players.get(player_id)

def _set_player(player_id, player):
    """存储玩家实例"""
    _players[player_id] = player

def _get_item(item_id):
    """获取物品实例"""
    return _items.get(item_id)

def _set_item(item_id, item):
    """存储物品实例"""
    _items[item_id] = item


# ============ 模块级函数（HPL可调用的API） ============

def create_player(name):
    """创建玩家实例，返回玩家对象（直接返回，不是ID）"""
    player = _Player(name)
    # 直接返回对象，因为HPL可以存储Python对象作为常量
    return player

def create_item(id, name, description, item_type, value):
    """创建物品实例，返回物品对象"""
    item = _Item(id, name, description, item_type, value)
    return item

def set_item_stat(item, key, value):
    """设置物品属性"""
    if isinstance(item, _Item):
        item.set_stat(key, value)
    else:
        raise HPLTypeError("First argument must be an item object")
    return None

def get_item_stat(item, key, default_val=None):
    """获取物品属性"""
    if isinstance(item, _Item):
        return item.get_stat(key, default_val)
    raise HPLTypeError("First argument must be an item object")

def add_item_to_inventory(player, item):
    """添加物品到玩家背包"""
    if isinstance(player, _Player) and isinstance(item, _Item):
        player.inventory.add_item(item)
    else:
        raise HPLTypeError("Invalid player or item object")
    return None

def add_gold(player, amount):
    """添加金币给玩家"""
    if isinstance(player, _Player):
        player.inventory.add_gold(amount)
    else:
        raise HPLTypeError("First argument must be a player object")
    return None

def heal_player(player, amount):
    """治疗玩家"""
    if isinstance(player, _Player):
        player.heal(amount)
    else:
        raise HPLTypeError("First argument must be a player object")
    return None

def gain_exp(player, amount):
    """玩家获得经验"""
    if isinstance(player, _Player):
        player.gain_exp(amount)
    else:
        raise HPLTypeError("First argument must be a player object")
    return None

def show_player_status(player):
    """显示玩家状态"""
    if isinstance(player, _Player):
        player.show_status()
    else:
        raise HPLTypeError("First argument must be a player object")
    return None

def show_player_inventory(player):
    """显示玩家背包"""
    if isinstance(player, _Player):
        player.show_inventory()
    else:
        raise HPLTypeError("First argument must be a player object")
    return None

def get_player_name(player):
    """获取玩家名称"""
    if isinstance(player, _Player):
        return player.name
    raise HPLTypeError("First argument must be a player object")

def get_player_hp(player):
    """获取玩家当前HP"""
    if isinstance(player, _Player):
        return player.hp
    raise HPLTypeError("First argument must be a player object")

def get_player_max_hp(player):
    """获取玩家最大HP"""
    if isinstance(player, _Player):
        return player.max_hp
    raise HPLTypeError("First argument must be a player object")

def get_player_level(player):
    """获取玩家等级"""
    if isinstance(player, _Player):
        return player.level
    raise HPLTypeError("First argument must be a player object")

def get_player_gold(player):
    """获取玩家金币"""
    if isinstance(player, _Player):
        return player.inventory.gold
    raise HPLTypeError("First argument must be a player object")

def set_player_stat(player, stat_name, value):
    """设置玩家属性"""
    if isinstance(player, _Player):
        if stat_name == "hp":
            player.hp = value
        elif stat_name == "max_hp":
            player.max_hp = value
        elif stat_name == "mp":
            player.mp = value
        elif stat_name == "max_mp":
            player.max_mp = value
        elif stat_name == "gold":
            player.inventory.gold = value
        elif stat_name == "attack":
            player.strength = value
        elif stat_name == "defense":
            player.vitality = value
        elif stat_name == "magic":
            player.intelligence = value
        else:
            # 其他属性存入stats字典
            player.stats[stat_name] = value
    else:
        raise HPLTypeError("First argument must be a player object")
    return None

def get_player_stat(player, stat_name, default_val=None):
    """获取玩家属性"""
    if isinstance(player, _Player):
        if stat_name == "hp":
            return player.hp
        elif stat_name == "max_hp":
            return player.max_hp
        elif stat_name == "mp":
            return player.mp
        elif stat_name == "max_mp":
            return player.max_mp
        elif stat_name == "gold":
            return player.inventory.gold
        elif stat_name == "attack":
            return player.strength
        elif stat_name == "defense":
            return player.vitality
        elif stat_name == "magic":
            return player.intelligence
        else:
            return player.stats.get(stat_name, default_val)
    raise HPLTypeError("First argument must be a player object")

def damage_player(player, amount):
    """对玩家造成伤害"""
    if isinstance(player, _Player):
        player.hp -= amount
        if player.hp < 0:
            player.hp = 0
    else:
        raise HPLTypeError("First argument must be a player object")
    return None

def restore_mp(player, amount):
    """恢复玩家MP"""
    if isinstance(player, _Player):
        player.mp += amount
        if player.mp > player.max_mp:
            player.mp = player.max_mp
    else:
        raise HPLTypeError("First argument must be a player object")
    return None

def deduct_gold(player, amount):
    """扣除玩家金币"""
    if isinstance(player, _Player):
        player.inventory.gold -= amount
        if player.inventory.gold < 0:
            player.inventory.gold = 0
    else:
        raise HPLTypeError("First argument must be a player object")
    return None

def get_inventory(player):
    """获取玩家背包"""
    if isinstance(player, _Player):
        return player.inventory.items
    raise HPLTypeError("First argument must be a player object")


# 公共类别名（在类定义之后）

Player = _Player
Item = _Item
Inventory = _Inventory


# 额外的工厂函数
def create_inventory(capacity=20):
    """创建背包实例"""
    return _Inventory(capacity)


# ============ 模块注册 ============


HPL_MODULE = HPLModule("player", "玩家角色系统 - 管理玩家属性、背包、状态")

# 注册函数
HPL_MODULE.register_function('create_player', create_player, 1, '创建玩家实例 (name)')
HPL_MODULE.register_function('create_item', create_item, 5, '创建物品实例 (id, name, description, type, value)')
HPL_MODULE.register_function('set_item_stat', set_item_stat, 3, '设置物品属性 (item, key, value)')
HPL_MODULE.register_function('get_item_stat', get_item_stat, None, '获取物品属性 (item, key, default?)')
HPL_MODULE.register_function('add_item_to_inventory', add_item_to_inventory, 2, '添加物品到背包 (player, item)')
HPL_MODULE.register_function('add_gold', add_gold, 2, '添加金币 (player, amount)')
HPL_MODULE.register_function('heal_player', heal_player, 2, '治疗玩家 (player, amount)')
HPL_MODULE.register_function('gain_exp', gain_exp, 2, '获得经验 (player, amount)')
HPL_MODULE.register_function('show_player_status', show_player_status, 1, '显示玩家状态 (player)')
HPL_MODULE.register_function('show_player_inventory', show_player_inventory, 1, '显示玩家背包 (player)')
HPL_MODULE.register_function('get_player_name', get_player_name, 1, '获取玩家名称 (player)')
HPL_MODULE.register_function('get_player_hp', get_player_hp, 1, '获取玩家HP (player)')
HPL_MODULE.register_function('get_player_max_hp', get_player_max_hp, 1, '获取玩家最大HP (player)')
HPL_MODULE.register_function('get_player_level', get_player_level, 1, '获取玩家等级 (player)')
HPL_MODULE.register_function('get_player_gold', get_player_gold, 1, '获取玩家金币 (player)')
HPL_MODULE.register_function('set_player_stat', set_player_stat, 3, '设置玩家属性 (player, stat_name, value)')
HPL_MODULE.register_function('get_player_stat', get_player_stat, None, '获取玩家属性 (player, stat_name, default?)')
HPL_MODULE.register_function('damage_player', damage_player, 2, '对玩家造成伤害 (player, amount)')
HPL_MODULE.register_function('restore_mp', restore_mp, 2, '恢复玩家MP (player, amount)')
HPL_MODULE.register_function('deduct_gold', deduct_gold, 2, '扣除玩家金币 (player, amount)')
HPL_MODULE.register_function('get_inventory', get_inventory, 1, '获取玩家背包 (player)')

# 注册常量

HPL_MODULE.register_constant('VERSION', "2.0.0", '模块版本')
HPL_MODULE.register_constant('AUTHOR', "HPL Framework Team", '模块作者')
