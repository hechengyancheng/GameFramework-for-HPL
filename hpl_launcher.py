#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HPL 游戏启动器
=============
让用户交互式地选择并运行 hpl_game_framework/examples/ 目录下的 HPL 脚本。

使用方法:
    python hpl_launcher.py              # 交互式模式
    python hpl_launcher.py --list       # 仅列出可用脚本
    python hpl_launcher.py <脚本名>      # 直接运行指定脚本
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path
from typing import List, Optional, Tuple


# 配置
EXAMPLES_DIR = Path("hpl_game_framework/examples")
HPL_RUNTIME_MODULE = "hpl_runtime.interpreter"  # HPL运行时入口


class Colors:
    """终端颜色代码"""
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'


def print_header(text: str) -> None:
    """打印带格式的标题"""
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*50}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{text.center(50)}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'='*50}{Colors.ENDC}\n")


def print_success(text: str) -> None:
    """打印成功消息"""
    print(f"{Colors.GREEN}✓ {text}{Colors.ENDC}")


def print_error(text: str) -> None:
    """打印错误消息"""
    print(f"{Colors.RED}✗ {text}{Colors.ENDC}", file=sys.stderr)


def print_info(text: str) -> None:
    """打印信息消息"""
    print(f"{Colors.CYAN}ℹ {text}{Colors.ENDC}")


def print_warning(text: str) -> None:
    """打印警告消息"""
    print(f"{Colors.YELLOW}⚠ {text}{Colors.ENDC}")


def get_hpl_scripts() -> List[Tuple[str, Path]]:
    """
    扫描examples目录，获取所有.hpl脚本文件
    
    Returns:
        列表，包含 (脚本名称, 完整路径) 元组
    """
    scripts = []
    
    if not EXAMPLES_DIR.exists():
        print_error(f"示例目录不存在: {EXAMPLES_DIR}")
        return scripts
    
    for hpl_file in sorted(EXAMPLES_DIR.glob("*.hpl")):
        # 获取脚本名称（不含扩展名）
        script_name = hpl_file.stem
        scripts.append((script_name, hpl_file))
    
    return scripts


def display_scripts(scripts: List[Tuple[str, Path]]) -> None:
    """
    显示可用的HPL脚本列表
    
    Args:
        scripts: 脚本列表，包含 (脚本名称, 完整路径) 元组
    """
    if not scripts:
        print_warning("未找到任何HPL脚本文件")
        return
    
    print_header("可用的 HPL 游戏脚本")
    
    for idx, (name, path) in enumerate(scripts, 1):
        # 尝试读取文件的第一行注释作为描述
        description = get_script_description(path)
        desc_text = f" - {description}" if description else ""
        
        print(f"{Colors.CYAN}[{idx}]{Colors.ENDC} {Colors.BOLD}{name}{Colors.ENDC}{desc_text}")
        print(f"    路径: {path}")
        print()
    
    print(f"{Colors.YELLOW}[0]{Colors.ENDC} {Colors.BOLD}退出{Colors.ENDC}")
    print()


def get_script_description(path: Path) -> Optional[str]:
    """
    从HPL文件中提取描述（第一行注释）
    
    Args:
        path: HPL文件路径
    
    Returns:
        描述字符串，如果没有则返回None
    """
    try:
        with open(path, 'r', encoding='utf-8') as f:
            first_line = f.readline().strip()
            # 检查是否是注释行
            if first_line.startswith('#'):
                return first_line[1:].strip()
    except Exception:
        pass
    return None


def run_hpl_script(script_path: Path) -> int:
    """
    运行指定的HPL脚本
    
    Args:
        script_path: HPL文件的完整路径
    
    Returns:
        返回码（0表示成功）
    """
    print_header(f"正在运行: {script_path.name}")
    
    # 检查hpl_runtime是否可用
    try:
        # 尝试导入hpl_runtime
        result = subprocess.run(
            [sys.executable, "-c", "import hpl_runtime"],
            capture_output=True,
            text=True
        )
        if result.returncode != 0:
            print_error("HPL运行时未安装或不可用")
            print_info("请确保hpl_runtime模块已正确安装")
            print_info("错误信息:", result.stderr)
            return 1
    except Exception as e:
        print_error(f"检查HPL运行时时出错: {e}")
        return 1
    
    # 运行脚本
    try:
        print_info(f"执行命令: python -m {HPL_RUNTIME_MODULE} {script_path}")
        print("-" * 50)
        
        # 使用subprocess运行，实时输出
        process = subprocess.Popen(
            [sys.executable, "-m", HPL_RUNTIME_MODULE, str(script_path)],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding='utf-8',
            errors='replace'
        )
        
        # 实时输出
        for line in process.stdout:
            print(line, end='')
        
        process.wait()
        
        print("-" * 50)
        
        if process.returncode == 0:
            print_success("脚本执行完成")
        else:
            print_error(f"脚本执行失败（返回码: {process.returncode}）")
        
        return process.returncode
        
    except FileNotFoundError:
        print_error(f"找不到HPL运行时模块: {HPL_RUNTIME_MODULE}")
        print_info("请确保hpl_runtime已正确安装")
        return 1
    except Exception as e:
        print_error(f"运行脚本时出错: {e}")
        return 1


def interactive_mode() -> int:
    """
    交互式模式：显示菜单并让用户选择
    
    Returns:
        返回码（0表示成功）
    """
    print_header("HPL 游戏启动器")
    print("欢迎使用HPL文字游戏框架！\n")
    
    while True:
        scripts = get_hpl_scripts()
        
        if not scripts:
            print_error("未找到任何HPL脚本")
            print_info(f"请确保在 {EXAMPLES_DIR} 目录下有.hpl文件")
            return 1
        
        display_scripts(scripts)
        
        try:
            choice = input(f"{Colors.BOLD}请选择要运行的脚本 [0-{len(scripts)}]: {Colors.ENDC}").strip()
            
            # 处理退出
            if choice == '0' or choice.lower() in ('q', 'quit', 'exit'):
                print_info("感谢使用，再见！")
                return 0
            
            # 尝试解析为数字
            try:
                idx = int(choice)
                if 1 <= idx <= len(scripts):
                    _, script_path = scripts[idx - 1]
                    run_hpl_script(script_path)
                    
                    # 询问是否继续
                    print()
                    cont = input(f"{Colors.BOLD}是否继续运行其他脚本？ (y/n): {Colors.ENDC}").strip().lower()
                    if cont not in ('y', 'yes'):
                        print_info("感谢使用，再见！")
                        return 0
                else:
                    print_error(f"无效的选择，请输入 0-{len(scripts)} 之间的数字")
            except ValueError:
                # 尝试作为脚本名称匹配
                matched = False
                for name, path in scripts:
                    if name.lower() == choice.lower():
                        run_hpl_script(path)
                        matched = True
                        
                        # 询问是否继续
                        print()
                        cont = input(f"{Colors.BOLD}是否继续运行其他脚本？ (y/n): {Colors.ENDC}").strip().lower()
                        if cont not in ('y', 'yes'):
                            print_info("感谢使用，再见！")
                            return 0
                        break
                
                if not matched:
                    print_error(f"无效的输入: {choice}")
                    print_info("请输入数字编号或脚本名称")
                    
        except KeyboardInterrupt:
            print("\n")
            print_info("操作已取消")
            return 0
        except EOFError:
            print("\n")
            print_info("输入结束")
            return 0


def list_mode() -> int:
    """
    列表模式：仅显示可用脚本
    
    Returns:
        返回码（0表示成功）
    """
    scripts = get_hpl_scripts()
    display_scripts(scripts)
    return 0 if scripts else 1


def direct_run_mode(script_name: str) -> int:
    """
    直接运行模式：运行指定的脚本
    
    Args:
        script_name: 脚本名称（可以是完整文件名或不含扩展名的名称）
    
    Returns:
        返回码（0表示成功）
    """
    scripts = get_hpl_scripts()
    
    # 查找匹配的脚本
    target_path = None
    
    # 首先尝试精确匹配（不含扩展名）
    for name, path in scripts:
        if name.lower() == script_name.lower():
            target_path = path
            break
    
    # 然后尝试带扩展名匹配
    if target_path is None:
        for name, path in scripts:
            if path.name.lower() == script_name.lower():
                target_path = path
                break
    
    # 最后尝试部分匹配
    if target_path is None:
        matches = [(name, path) for name, path in scripts 
                  if script_name.lower() in name.lower()]
        if len(matches) == 1:
            _, target_path = matches[0]
        elif len(matches) > 1:
            print_error(f"找到多个匹配的脚本:")
            for name, path in matches:
                print(f"  - {name}")
            return 1
    
    if target_path is None:
        print_error(f"未找到脚本: {script_name}")
        print_info("可用的脚本:")
        for name, _ in scripts:
            print(f"  - {name}")
        return 1
    
    return run_hpl_script(target_path)


def main() -> int:
    """
    主入口函数
    
    Returns:
        返回码（0表示成功）
    """
    # 解析命令行参数
    parser = argparse.ArgumentParser(
        description="HPL 游戏启动器 - 选择并运行HPL文字游戏脚本",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python hpl_launcher.py              # 交互式选择并运行脚本
  python hpl_launcher.py --list       # 列出所有可用脚本
  python hpl_launcher.py simple_adventure  # 直接运行指定脚本
        """
    )
    
    parser.add_argument(
        'script',
        nargs='?',
        help='要直接运行的脚本名称（可选）'
    )
    
    parser.add_argument(
        '-l', '--list',
        action='store_true',
        help='仅列出可用脚本，不进入交互模式'
    )
    
    parser.add_argument(
        '--no-color',
        action='store_true',
        help='禁用彩色输出'
    )
    
    args = parser.parse_args()
    
    # 禁用颜色（如果需要）
    if args.no_color or os.environ.get('NO_COLOR'):
        for attr in dir(Colors):
            if not attr.startswith('_'):
                setattr(Colors, attr, '')
    
    # 根据参数选择模式
    if args.list:
        return list_mode()
    elif args.script:
        return direct_run_mode(args.script)
    else:
        return interactive_mode()


if __name__ == "__main__":
    sys.exit(main())
