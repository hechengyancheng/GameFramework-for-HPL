# HPL 游戏框架 - Python 模块版本

## 概述

这是 HPL（High-level Programming Language）游戏框架的 Python 模块版本。所有原有的 HPL 类已被转换为 Python 模块，可以通过 HPL 的 `imports` 语句导入使用。

## 模块结构

```
hpl_game_framework/
├── __init__.py              # 包初始化，提供便捷访问
├── core/                    # 核心模块
│   ├── game_engine.py       # 游戏引擎、状态管理、存档系统
│   ├── player.py            # 玩家角色、物品、背包
│   └── scene.py             # 场景、选择项、NPC
├── utils/                   # 工具模块
│   ├── game_utils.py        # 随机数、文本格式化、骰子
│   └── interaction.py       # 输入处理、菜单、对话
└── examples/                # 示例
    └── simple_adventure_python.hpl  # 使用 Python 模块的示例游戏
```

## 使用方法

### 在 HPL 中导入模块

```hpl
imports:
  - game_engine
  - player
  - scene
  - game_utils
  - interaction
```

### 创建游戏

```hpl
main: () => {
  # 创建游戏引擎
  engine = game_engine.create_game_engine()
  
  # 初始化游戏
  engine.initialize("玩家名称")
  
  # 创建场景
  forest = scene.create_scene("forest", "迷雾森林", "你站在一片神秘的森林入口...")
  
  # 添加选择项
  forest.add_simple_choice("进入洞穴", "cave")
  
  # 注册场景
  engine.register_scene(forest)
  
  # 设置起始场景
  engine.set_start_scene("forest")
  
  # 运行游戏
  engine.run()
}
```

## 模块详情

### game_engine 模块

**主要类：**
- `GameEngine` - 游戏引擎主类
- `GameState` - 游戏状态管理
- `SaveManager` - 存档管理器

**主要函数：**
- `create_game_engine()` - 创建游戏引擎
- `create_game_state()` - 创建游戏状态
- `create_save_manager(game_state)` - 创建存档管理器

### player 模块

**主要类：**
- `Player` - 玩家角色
- `Item` - 物品
- `Inventory` - 背包系统

**主要函数：**
- `create_player(name)` - 创建玩家
- `create_item(id, name, description, type, value)` - 创建物品
- `create_inventory(capacity)` - 创建背包

### scene 模块

**主要类：**
- `Scene` - 场景
- `Choice` - 选择项
- `NPC` - NPC角色

**主要函数：**
- `create_scene(id, name, description)` - 创建场景
- `create_choice(text, target, condition, action)` - 创建选择项
- `create_npc(id, name, description)` - 创建NPC

### game_utils 模块

**主要类：**
- `RandomGenerator` - 随机数生成器
- `TextFormatter` - 文本格式化
- `DiceRoller` - 骰子滚动器

**主要函数：**
- `random_int(max)` - 随机整数 [0, max)
- `random_range(min, max)` - 随机整数 [min, max]
- `random_choice(arr)` - 从数组随机选择
- `roll_dice(n, d)` - 掷骰子
- `clear_screen()` - 清屏
- `print_title(text)` - 打印标题
- `print_box(text)` - 打印带边框文本
- `print_progress(current, max, label)` - 打印进度条

### interaction 模块

**主要类：**
- `InputHandler` - 输入处理
- `MenuSystem` - 菜单系统
- `DialogSystem` - 对话系统

**主要函数：**
- `get_int(prompt, min, max)` - 获取整数输入
- `get_string(prompt, allow_empty)` - 获取字符串输入
- `get_confirm(prompt)` - 获取确认 (Y/N)
- `get_choice(prompt, options)` - 获取选择
- `pause(message)` - 暂停等待按键
- `show_dialog(speaker, text)` - 显示对话
- `show_narration(text)` - 显示叙述
- `show_scene(location, description)` - 显示场景
- `show_combat(attacker, action, target, result)` - 显示战斗
- `show_loot(item, quantity)` - 显示获得物品
- `show_stat_change(stat, old, new)` - 显示属性变化

## 完整示例

参见 `examples/simple_adventure_python.hpl` 文件，展示了如何使用所有模块创建一个完整的文字冒险游戏。

## 与原始 HPL 框架的区别

### 主要变化

1. **语法差异**：
   - HPL: `this.property` → Python: `self.property`
   - HPL: `echo "text"` → Python: `print("text")`
   - HPL: `input()` → Python: `input()`

2. **类实例化**：
   - HPL: `Player(name)` → Python: `player.create_player(name)`

3. **方法调用**：
   - HPL: `player.show_status()` → Python: `player.show_status()`（相同）

4. **模块导入**：
   - HPL: 自动导入 → Python: 需要显式 `imports`

### 优势

1. **性能**：Python 实现通常比 HPL 解释执行更快
2. **生态**：可以利用 Python 丰富的第三方库
3. **调试**：可以使用 Python 的调试工具
4. **扩展**：易于添加新的 Python 功能

## 故障排除

### 模块未找到

确保 `hpl_game_framework` 目录在 Python 路径中，或者使用：
```python
import sys
sys.path.insert(0, '/path/to/hpl_game_framework')
```

### HPL 运行时不可用

如果看到警告 "无法导入 HPL 运行时模块"，框架类仍然可以独立使用，但 HPL 集成功能将受限。

## 版本信息

- **版本**: 1.0.0
- **作者**: HPL Framework Team
- **Python 版本**: 3.6+

## 许可证

与原始 HPL 框架相同。
