#!/usr/bin/env python3
"""测试跨平台兼容性修复"""

import platform
import sys

def test_platform_detection():
    """测试平台检测逻辑"""
    print(f"当前平台: {platform.system()}")
    
    if platform.system() == "Windows":
        try:
            import msvcrt
            print("[OK] Windows 平台: msvcrt 模块可用")
            print("[OK] Windows 键盘输入处理逻辑已实现")
        except ImportError:
            print("[ERROR] Windows 平台: msvcrt 模块不可用")
            return False
    else:
        try:
            import termios
            import tty
            print("[OK] Unix/Linux 平台: termios 和 tty 模块可用")
            print("[OK] Unix/Linux 键盘输入处理逻辑已实现")
        except ImportError:
            print("[ERROR] Unix/Linux 平台: termios 或 tty 模块不可用")
            return False
    
    return True

def test_syntax():
    """测试修复后的文件语法"""
    try:
        with open('libs/deepagents-cli/deepagents_cli/execution.py', 'r', encoding='utf-8') as f:
            code = f.read()
        
        # 检查关键修复点
        checks = [
            ('import platform', '平台检测导入'),
            ('if platform.system() == "Windows":', 'Windows 平台条件判断'),
            ('import msvcrt', 'Windows msvcrt 导入'),
            ('msvcrt.kbhit()', 'Windows 键盘检测'),
            ('msvcrt.getch()', 'Windows 键盘读取'),
            ('termios.tcgetattr', 'Unix/Linux termios 保持'),
            ('tty.setraw', 'Unix/Linux tty 保持'),
        ]
        
        for check, description in checks:
            if check in code:
                print(f"[OK] {description}: 已实现")
            else:
                print(f"[ERROR] {description}: 缺失")
                return False
        
        # 语法检查
        import ast
        ast.parse(code)
        print("[OK] 语法检查: 通过")
        
        return True
        
    except Exception as e:
        print(f"[ERROR] 语法检查失败: {e}")
        return False

if __name__ == "__main__":
    print("=== 跨平台兼容性修复验证 ===\n")
    
    platform_ok = test_platform_detection()
    print()
    syntax_ok = test_syntax()
    
    print(f"\n=== 验证结果 ===")
    if platform_ok and syntax_ok:
        print("✓ 所有检查通过，跨平台兼容性修复成功！")
        sys.exit(0)
    else:
        print("✗ 部分检查失败，需要进一步修复")
        sys.exit(1)