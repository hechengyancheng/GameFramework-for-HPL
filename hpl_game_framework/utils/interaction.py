#!/usr/bin/env python3
"""
交互系统模块
========

处理用户输入、菜单显示、对话系统。

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


# ============ 输入处理器 ============

class InputHandler:
    """输入处理器"""
    
    def get_int(self, prompt=None, min_val=None, max_val=None):
        """获取整数输入，带验证"""
        while True:
            try:
                if prompt is not None:
                    print(prompt)
                input_str = input()
                value = int(input_str)
                if min_val is not None and value < min_val:
                    print(f"请输入大于等于 {min_val} 的数字")
                    continue
                if max_val is not None and value > max_val:
                    print(f"请输入小于等于 {max_val} 的数字")
                    continue
                return value
            except ValueError:
                print("无效输入，请输入一个有效的数字")
    
    def get_string(self, prompt=None, allow_empty=False):
        """获取字符串输入"""
        if allow_empty is None:
            allow_empty = False
        while True:
            if prompt is not None:
                print(prompt)
            value = input()
            if not allow_empty and len(value) == 0:
                print("输入不能为空，请重新输入")
                continue
            return value
    
    def get_confirm(self, prompt=None):
        """获取确认 (Y/N)"""
        if prompt is None:
            prompt = "确认? (Y/N): "
        while True:
            print(prompt)
            value = input()
            value_upper = value.upper()
            if value_upper == "Y":
                return True
            if value_upper == "N":
                return False
            print("请输入 Y 或 N")
    
    def get_choice(self, prompt, options):
        """获取选择项"""
        print(prompt)
        for i, option in enumerate(options):
            print(f"  {i + 1}. {option}")
        
        while True:
            print(f"请输入选项编号 (1-{len(options)}): ")
            input_str = input()
            try:
                choice = int(input_str)
                if 1 <= choice <= len(options):
                    return choice - 1  # 返回0-based索引
                print("无效选项，请重新输入")
            except ValueError:
                print("请输入有效的数字")
    
    def pause(self, message=None):
        """暂停等待用户按键"""
        if message is None:
            message = "按回车键继续..."
        print(message)
        input()


# ============ 菜单系统 ============

class MenuSystem:
    """菜单系统"""
    
    def show_menu(self, title, options):
        """显示菜单并获取选择"""
        print("")
        print(f"========== {title} ==========")
        for i, option in enumerate(options):
            print(f"  [{i + 1}] {option}")
        print("  [0] 返回/退出")
        print("=" * (24 + len(title)))
        
        while True:
            print("请选择: ")
            input_str = input()
            try:
                choice = int(input_str)
                if 0 <= choice <= len(options):
                    return choice
                print("无效选项，请重新输入")
            except ValueError:
                print("请输入有效的数字")
    
    def show_submenu(self, parent_title, submenu_title, options):
        """显示子菜单"""
        full_title = f"{parent_title} > {submenu_title}"
        return self.show_menu(full_title, options)
    
    def show_paged_list(self, title, items, page_size=10):
        """显示分页列表"""
        if page_size is None:
            page_size = 10
        total_pages = (len(items) + page_size - 1) // page_size
        if total_pages < 1:
            total_pages = 1
        current_page = 0
        
        while True:
            start = current_page * page_size
            end = start + page_size
            if end > len(items):
                end = len(items)
            
            print("")
            print(f"========== {title} (第 {current_page + 1}/{total_pages} 页) ==========")
            for i in range(start, end):
                print(f"  [{i + 1}] {items[i]}")
            
            print("")
            print("  [N] 下一页  [P] 上一页  [Q] 退出")
            print("  或直接输入编号选择")
            print("=" * (42 + len(title)))
            
            print("请选择: ")
            choice = input()
            
            # 处理导航命令
            if choice.upper() == "N":
                if current_page < total_pages - 1:
                    current_page += 1
                continue
            if choice.upper() == "P":
                if current_page > 0:
                    current_page -= 1
                continue
            if choice.upper() == "Q":
                return -1
            
            # 尝试解析为数字选择
            try:
                num_choice = int(choice)
                if 1 <= num_choice <= len(items):
                    return num_choice - 1
                print("无效选项")
            except ValueError:
                print("无效输入")


# ============ 对话系统 ============

class DialogSystem:
    """对话系统"""
    
    def show_dialog(self, speaker, text):
        """显示对话"""
        print("")
        if speaker is not None and len(speaker) > 0:
            print(f"[{speaker}]")
        print(f"\"{text}\"")
        print("")
    
    def show_dialog_with_choices(self, speaker, text, choices):
        """显示带选项的对话"""
        self.show_dialog(speaker, text)
        print("你的回应:")
        for i, choice in enumerate(choices):
            print(f"  {i + 1}. {choice}")
        
        # 使用输入处理器获取选择
        handler = InputHandler()
        return handler.get_choice("", choices)
    
    def show_narration(self, text):
        """显示叙述文本"""
        print("")
        print(text)
        print("")
    
    def show_scene(self, location, description):
        """显示场景描述"""
        print("")
        print(f"【{location}】")
        print("-" * 40)
        print(description)
        print("-" * 40)
        print("")
    
    def show_system(self, message):
        """显示系统消息"""
        print(f"[系统] {message}")
    
    def show_combat(self, attacker, action, target, result=None):
        """显示战斗信息"""
        print("")
        print(f"⚔️  {attacker} {action} {target}")
        if result is not None:
            print(f"   结果: {result}")
        print("")
    
    def show_loot(self, item_name, quantity=1):
        """显示获得物品"""
        if quantity is None:
            quantity = 1
        print("")
        print(f"🎁 获得: {item_name} x{quantity}")
        print("")
    
    def show_stat_change(self, stat_name, old_val, new_val):
        """显示属性变化"""
        diff = new_val - old_val
        if diff > 0:
            print(f"📈 {stat_name}: {old_val} → {new_val} (+{diff})")
        elif diff < 0:
            print(f"📉 {stat_name}: {old_val} → {new_val} ({diff})")
        else:
            print(f"📊 {stat_name}: {new_val}")


# ============ 模块级函数 ============

def create_input_handler():
    """创建输入处理器"""
    return InputHandler()

def create_menu_system():
    """创建菜单系统"""
    return MenuSystem()

def create_dialog_system():
    """创建对话系统"""
    return DialogSystem()

def get_int(prompt=None, min_val=None, max_val=None):
    """获取整数输入"""
    handler = InputHandler()
    return handler.get_int(prompt, min_val, max_val)

def get_string(prompt=None, allow_empty=False):
    """获取字符串输入"""
    handler = InputHandler()
    return handler.get_string(prompt, allow_empty)

def get_confirm(prompt=None):
    """获取确认 (Y/N)"""
    handler = InputHandler()
    return handler.get_confirm(prompt)

def get_choice(prompt, options):
    """获取选择项"""
    handler = InputHandler()
    return handler.get_choice(prompt, options)

def pause(message=None):
    """暂停等待用户按键"""
    handler = InputHandler()
    return handler.pause(message)

def show_menu(title, options):
    """显示菜单"""
    menu = MenuSystem()
    return menu.show_menu(title, options)

def show_dialog(speaker, text):
    """显示对话"""
    dialog = DialogSystem()
    return dialog.show_dialog(speaker, text)

def show_narration(text):
    """显示叙述文本"""
    dialog = DialogSystem()
    return dialog.show_narration(text)

def show_scene(location, description):
    """显示场景描述"""
    dialog = DialogSystem()
    return dialog.show_scene(location, description)

def show_system(message):
    """显示系统消息"""
    dialog = DialogSystem()
    return dialog.show_system(message)

def show_combat(attacker, action, target, result=None):
    """显示战斗信息"""
    dialog = DialogSystem()
    return dialog.show_combat(attacker, action, target, result)

def show_loot(item_name, quantity=1):
    """显示获得物品"""
    dialog = DialogSystem()
    return dialog.show_loot(item_name, quantity)

def show_stat_change(stat_name, old_val, new_val):
    """显示属性变化"""
    dialog = DialogSystem()
    return dialog.show_stat_change(stat_name, old_val, new_val)


# ============ 模块注册 ============

HPL_MODULE = HPLModule("interaction", "交互系统 - 处理用户输入、菜单显示、对话系统")

# 注册函数
HPL_MODULE.register_function('create_input_handler', create_input_handler, 0, '创建输入处理器')
HPL_MODULE.register_function('create_menu_system', create_menu_system, 0, '创建菜单系统')
HPL_MODULE.register_function('create_dialog_system', create_dialog_system, 0, '创建对话系统')
HPL_MODULE.register_function('get_int', get_int, None, '获取整数输入')
HPL_MODULE.register_function('get_string', get_string, None, '获取字符串输入')
HPL_MODULE.register_function('get_confirm', get_confirm, None, '获取确认 (Y/N)')
HPL_MODULE.register_function('get_choice', get_choice, 2, '获取选择项')
HPL_MODULE.register_function('pause', pause, None, '暂停等待用户按键')
HPL_MODULE.register_function('show_menu', show_menu, 2, '显示菜单')
HPL_MODULE.register_function('show_dialog', show_dialog, 2, '显示对话')
HPL_MODULE.register_function('show_narration', show_narration, 1, '显示叙述文本')
HPL_MODULE.register_function('show_scene', show_scene, 2, '显示场景描述')
HPL_MODULE.register_function('show_system', show_system, 1, '显示系统消息')
HPL_MODULE.register_function('show_combat', show_combat, None, '显示战斗信息')
HPL_MODULE.register_function('show_loot', show_loot, None, '显示获得物品')
HPL_MODULE.register_function('show_stat_change', show_stat_change, 3, '显示属性变化')

# 注册常量
HPL_MODULE.register_constant('VERSION', "1.0.0", '模块版本')
HPL_MODULE.register_constant('AUTHOR', "HPL Framework Team", '模块作者')
