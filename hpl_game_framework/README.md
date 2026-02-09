# HPL 文字游戏框架

一个基于HPL（H Programming Language）的完整文字游戏开发框架，提供场景管理、角色系统、战斗机制、存档功能等核心功能。

## 框架结构

```
hpl_game_framework/
├── core/                   # 核心系统
│   ├── game_engine.hpl    # 游戏引擎（主循环、存档）
│   ├── scene.hpl          # 场景系统
│   └── player.hpl         # 玩家角色系统
├── utils/                  # 工具模块
│   ├── game_utils.hpl     # 随机数、格式化、骰子
│   └── interaction.hpl    # 输入处理、菜单、对话
├── examples/               # 示例游戏
│   └── simple_adventure.hpl  # 简单冒险游戏
└── README.md              # 本文档
```

## 核心功能

### 1. 游戏引擎 (GameEngine)
- 游戏主循环管理
- 场景切换和状态管理
- 存档/读档系统（JSON格式）
- 游戏时间追踪

### 2. 场景系统 (Scene)
- 场景描述和选择项
- 条件判断（基于玩家状态）
- 物品和NPC管理
- 出口系统（方向导航）

### 3. 玩家系统 (Player)
- 属性系统（力量、敏捷、智力、体质）
- 生命值/魔法值管理
- 经验值和升级系统
- 背包和装备系统
- 任务追踪

### 4. 交互系统
- 输入验证和处理
- 菜单显示和分页
- 对话系统
- 战斗信息显示

### 5. 工具类
- 随机数生成器
- 文本格式化（标题、边框、进度条）
- 骰子系统（D20检定、伤害骰）

## 快速开始

### 创建新游戏

```yaml
includes:
  - hpl_game_framework/core/game_engine.hpl
  - hpl_game_framework/core/scene.hpl
  - hpl_game_framework/core/player.hpl
  - hpl_game_framework/utils/interaction.hpl
  - hpl_game_framework/utils/game_utils.hpl

classes:
  MyGame:
    init: () => {
        this.engine = GameEngine()
        this.create_scenes()
      }
    
    create_scenes: () => {
        # 创建场景
        start = Scene("start", "起始地点", "这是你的冒险开始的地方...")
        
        # 添加选择项
        start.add_simple_choice("向北走", "north")
        start.add_simple_choice("向南走", "south")
        
        # 注册场景
        this.engine.register_scene(start)
        this.engine.set_start_scene("start")
      }
    
    start: () => {
        # 初始化
        this.engine.initialize("玩家名字")
        
        # 运行游戏
        this.engine.run()
      }

objects:
  my_game: MyGame()

main: () => {
    my_game.start()
  }

call: main()
```

### 场景管理

```yaml
# 创建场景
scene = Scene("forest", "森林", "一片茂密的森林...")

# 添加选择项
scene.add_simple_choice("进入森林", "deep_forest")
scene.add_simple_choice("返回", "village")

# 带条件的选择
choice = Choice("打开宝箱", "chest_open", "has_key", null)
scene.add_choice(choice)

# 添加物品
sword = Item("sword", "长剑", "锋利的剑", "weapon", 50)
sword.set_stat("attack", 5)
scene.add_item(sword)

# 添加NPC
npc = NPC("merchant", "商人", "一个旅行商人")
npc.is_merchant = true
scene.add_npc(npc)
```

### 玩家操作

```yaml
# 创建玩家
player = Player("勇者")

# 显示状态
player.show_status()

# 显示背包
player.show_inventory()

# 治疗
player.heal(20)

# 受到伤害
player.take_damage(10)

# 获得经验
player.gain_exp(50)

# 添加物品
potion = Item("potion", "药水", "恢复药水", "consumable", 10)
player.inventory.add_item(potion)

# 装备武器
player.inventory.equip_item(0)
```

### 存档系统

```yaml
# 自动保存
# 游戏中按 S 键保存

# 手动保存
engine.save_manager.save(1)  # 保存到存档1

# 加载游戏
engine.save_manager.load(1)  # 从存档1加载

# 列出存档
saves = engine.save_manager.list_saves()
```

### 随机数和骰子

```yaml
# 随机整数 [0, 100)
num = random_gen.random_int(100)

# 范围随机 [1, 20]
d20 = random_gen.random_range(1, 20)

# 从数组选择
item = random_gen.random_choice(["剑", "盾", "药水"])

# 掷骰子 2d6+3
damage = dice.damage_roll(2, 6, 3)

# D20检定
result = dice.attack_roll(attack_bonus, armor_class)
# 返回: "hit", "miss", "critical"
```

### 交互功能

```yaml
# 获取整数输入
num = input_handler.get_int("请输入数字: ", 1, 10)

# 获取字符串
name = input_handler.get_string("请输入名字: ", false)

# 确认对话框
confirm = input_handler.get_confirm("确定吗? (Y/N): ")

# 显示菜单
choice = menu_system.show_menu("主菜单", ["开始游戏", "设置", "退出"])

# 显示对话
dialog_system.show_dialog("NPC名字", "对话内容...")

# 显示场景
dialog_system.show_scene("场景名", "场景描述...")

# 显示获得物品
dialog_system.show_loot("金币", 100)

# 显示属性变化
dialog_system.show_stat_change("生命值", 80, 100)
```

## 游戏命令

在游戏中，玩家可以使用以下命令：

| 命令 | 功能 |
|------|------|
| `S` | 保存游戏 |
| `L` | 加载游戏 |
| `I` | 查看背包 |
| `Q` | 退出游戏 |
| 数字 | 选择选项 |

## 示例游戏

运行示例游戏：

```bash
cd hpl_game_framework/examples
python -m hpl_runtime.interpreter simple_adventure.hpl
```

## 扩展框架

### 添加新功能

1. **创建新模块**
   ```yaml
   # my_module.hpl
   classes:
     MySystem:
       my_method: () => {
           # 实现
         }
   objects:
     my_system: MySystem()
   ```

2. **继承和扩展**
   ```yaml
   classes:
     CustomPlayer:
       parent: Player
       special_ability: () => {
           # 新能力
         }
   ```

3. **自定义场景逻辑**
   ```yaml
   # 在场景中使用条件
   choice = Choice("进入密室", "secret_room", "has_key", null)
   # 条件: has_key 标志必须为true
   ```

## 最佳实践

1. **模块化设计**：将不同功能分离到不同文件
2. **使用includes**：复用框架组件
3. **场景规划**：先设计场景流程图再实现
4. **平衡性测试**：调整战斗数值确保游戏平衡
5. **存档点**：在关键位置自动保存

## 高级功能

### 条件系统

```yaml
# 基于玩家属性
choice = Choice("推开巨石", "cave", "strength >= 15", null)

# 基于游戏标志
choice = Choice("进入城堡", "castle", "quest_completed", null)

# 基于物品
choice = Choice("使用钥匙", "treasure", "has_item:golden_key", null)
```

### 战斗系统扩展

```yaml
# 创建敌人
enemy = {
  "name": "哥布林",
  "hp": 25,
  "attack": 8,
  "defense": 3,
  "exp_reward": 15,
  "gold_reward": 10
}

# 战斗循环
while (enemy.hp > 0 && player.is_alive()) :
  # 玩家回合
  damage = player.get_attack() - enemy.defense
  enemy.hp = enemy.hp - damage
  
  # 敌人回合
  if (enemy.hp > 0) {
    damage = enemy.attack - player.get_defense()
    player.take_damage(damage)
  }
```

### 任务系统

```yaml
# 添加任务
player.add_quest("find_sword", "寻找圣剑", "在古老的神庙中找到传说中的圣剑")

# 完成任务
player.complete_quest("find_sword")

# 检查进行中的任务
active = player.get_active_quests()
```

## 技术支持

- **HPL版本**: 1.0+
- **依赖**: time, json, io 标准库模块
- **存档位置**: `saves/save_1.json` 等

## 许可

本框架基于HPL语言开发，遵循开源协议。

---

**开始创建你的文字游戏吧！** 🎮
