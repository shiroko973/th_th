#!/usr/bin/env python3

import os
import random
import signal
import sys
import json
import subprocess
import time
from pathlib import Path

try:
    import readline
except ImportError:
    pass

from text_discoloration import (
    random_typewriter,
    separator,
    custom_print,
    gradient_text,
    success,
    error,
    info,
    warn,
    progress_bar,
    COLOR_MAP,
    END,
    set_quiet,
    set_verbose,
    RED, YELLOW, GREEN, CYAN, BLUE, PURPLE,
)


CONFIG_PATH = Path.home() / ".th_config.json"
DEFAULT_CONFIG = {
    "loop_mode": True,
    "version": "2.0.1",
    "language": "python",
    "quiet": False,
}


def load_config():
    if CONFIG_PATH.exists():
        try:
            return json.loads(CONFIG_PATH.read_text(encoding='utf-8'))
        except:
            return DEFAULT_CONFIG.copy()
    else:
        info("首次启动，正在初始化配置...")
        for i in range(0, 101, 20):
            progress_bar(i, width=30, color="cyan", auto_end=False)
            time.sleep(0.05)
        print()
        CONFIG_PATH.write_text(json.dumps(DEFAULT_CONFIG, indent=2), encoding='utf-8')
        success("配置文件已创建: ~/.th_config.json")
        return DEFAULT_CONFIG.copy()


def save_config(config):
    CONFIG_PATH.write_text(json.dumps(config, indent=2), encoding='utf-8')


def set_language(lang):
    config = load_config()
    config["language"] = lang
    save_config(config)
    success(f"默认语言已切换为: {lang}")


def set_loop_mode(enabled):
    config = load_config()
    config["loop_mode"] = enabled
    save_config(config)
    status = "开启" if enabled else "关闭"
    success(f"循环模式已{status}")



LANG_CONFIG = {
    "python": {
        "ext": ".py",
        "compile": None,
        "run": "python {file}",
        "template": '# 输入你的 Python 代码\n'
    },
    "c": {
        "ext": ".c",
        "compile": "gcc {file} -o {out}",
        "run": "{out}",
        "template": '#include <stdio.h>\n\nint main() {\n    \n    return 0;\n}\n'
    },
    "cpp": {
        "ext": ".cpp",
        "compile": "g++ {file} -o {out}",
        "run": "{out}",
        "template": '#include <iostream>\n\nint main() {\n    \n    return 0;\n}\n'
    },
    "go": {
        "ext": ".go",
        "compile": "go build -o {out} {file}",
        "run": "{out}",
        "template": 'package main\n\nfunc main() {\n    \n}\n'
    },
    "lua": {
        "ext": ".lua",
        "compile": None,
        "run": "lua {file}",
        "template": '-- 输入你的 Lua 代码\n'
    },
}


tmp_dir = Path.home() / ".th_temp"
tmp_dir.mkdir(exist_ok=True)


def get_temp_file(lang):
    ext = LANG_CONFIG.get(lang, LANG_CONFIG["python"])["ext"]
    return tmp_dir / f"code{ext}"


def clear_temp_files():
    for f in tmp_dir.iterdir():
        try:
            f.unlink()
        except:
            pass



def execute_code(code, lang, debug=False):
    config = LANG_CONFIG.get(lang, LANG_CONFIG["python"])
    ext = config["ext"]
    temp_file = tmp_dir / f"code{ext}"
    
    temp_file.write_text(code, encoding='utf-8')
    
    if config["compile"]:
        out_file = tmp_dir / "program"
        cmd = config["compile"].format(file=temp_file, out=out_file)
        info(f"编译: {cmd}")
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode != 0:
            error("编译失败:")
            print(result.stderr)
            return False
        out_file.chmod(out_file.stat().st_mode | 0o111)
        run_cmd = config["run"].format(out=out_file)
    else:
        run_cmd = config["run"].format(file=temp_file)
    
    if debug:
        info(f"调试模式: {run_cmd}")
        subprocess.run(run_cmd, shell=True)
    else:
        try:
            result = subprocess.run(run_cmd, shell=True, capture_output=True, text=True)
            if result.stdout:
                print(result.stdout, end='')
            if result.stderr:
                print(result.stderr, end='', file=sys.stderr)
        except Exception as e:
            error(f"运行失败: {e}")
            return False
    return True


def run_file(filepath, debug=False):
    p = Path(filepath)
    if not p.exists():
        error(f"文件不存在: {filepath}")
        return
    
    ext = p.suffix
    lang = None
    for l, cfg in LANG_CONFIG.items():
        if cfg["ext"] == ext:
            lang = l
            break
    
    if lang is None:
        error(f"不支持的文件类型: {ext}")
        return
    
    code = p.read_text(encoding='utf-8')
    
    if lang == "python":
        if debug:
            info(f"调试模式: {filepath}")
            import pdb
            pdb.run(code)
        else:
            exec_globals = {
                "__name__": "__main__",
                "__file__": str(p.resolve()),
            }
            exec(code, exec_globals)
    else:
        execute_code(code, lang, debug)


def execute_temp_file():
    tmp_path = Path.home() / ".th_temp.py"
    if tmp_path.exists():
        code = tmp_path.read_text(encoding='utf-8')
        exec_globals = {
            "__name__": "__main__",
            "__file__": str(tmp_path.resolve()),
        }
        exec(code, exec_globals)



def exit_handler(sig, frame):
    clear_temp_files()
    tmp_path = Path.home() / ".th_temp.py"
    if tmp_path.exists():
        tmp_path.unlink()
    print()
    success("已退出")
    raise SystemExit


signal.signal(signal.SIGINT, exit_handler)
signal.signal(signal.SIGTERM, exit_handler)



def thv():
    config = load_config()
    print(f"th version {config.get('version', '2.0.1')}")



def rainbow_arrow_fall(speed=0.02, height=8):
    colors = [RED, YELLOW, GREEN, CYAN, BLUE, PURPLE]
    arrows = "↓↓↓"
    
    for i in range(height):
        sys.stdout.write("\r" + " " * i + arrows)
        sys.stdout.flush()
        time.sleep(speed)
    
    for _ in range(3):
        for c in colors:
            sys.stdout.write("\r" + c + arrows + END + " " * 10)
            sys.stdout.flush()
            time.sleep(0.1)
    print()



def main():
    config = load_config()
    if not config.get("quiet", False):
        rainbow_arrow_fall()
    
    lang = config.get("language", "python")
    loop_mode = config.get("loop_mode", True)
    
    if config.get("quiet", False):
        set_quiet()
    
    while True:
        tmp_path = Path.home() / ".th_temp.py"
        if tmp_path.exists():
            tmp_path.unlink()
        
        random_typewriter(f"th-py 多语言编辑器 ({lang})", delay=0.03)
        separator(color="purple")
        info(f"当前语言: {lang}")
        info("输入代码，每行按回车")
        info("输入 end 执行代码")
        info("输入 quit 退出程序")
        info("输入 lang:c 切换语言 (python/c/cpp/go/lua)")
        info("按 Ctrl+C 可选择是否执行")
        if loop_mode:
            info("循环模式: 开启")
        separator(color="purple")
        
        lines = []
        while True:
            try:
                inp = input("> ")
            except EOFError:
                break
            
            if inp == "end":
                break
            elif inp == "quit":
                clear_temp_files()
                if tmp_path.exists():
                    tmp_path.unlink()
                success("已退出")
                separator(color="green")
                return
            elif inp.startswith("lang:"):
                new_lang = inp[5:].strip()
                if new_lang in LANG_CONFIG:
                    lang = new_lang
                    set_language(lang)
                    success(f"切换语言: {lang}")
                else:
                    error(f"不支持的语言: {new_lang}")
                continue
            
            lines.append(inp)
        
        if not lines:
            continue
        
        code = '\n'.join(lines)
        
        if lang == "python":
            tmp_path.write_text(code, encoding='utf-8')
        
        gradient_text("执行结果", (255, 0, 100), (0, 200, 255), delay=0.02)
        separator(color="cyan")
        
        if lang == "python":
            exec_globals = {
                "__name__": "__main__",
                "__file__": str(tmp_path.resolve()),
            }
            exec(code, exec_globals)
        else:
            execute_code(code, lang)
        
        separator(color="green")
        
        if not loop_mode:
            success("循环模式已关闭，程序退出")
            break
        
        again = input("\n是否继续编写代码？(y/N): ").strip().lower()
        if again != 'y':
            success("再见")
            break



if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == "--version" or sys.argv[1] == "-v":
            thv()
        elif sys.argv[1] == "-f" or sys.argv[1] == "--file":
            if len(sys.argv) > 2:
                debug = "--debug" in sys.argv
                run_file(sys.argv[2], debug)
            else:
                error("请指定文件路径")
        elif sys.argv[1] == "set" and len(sys.argv) > 2:
            if sys.argv[2] == "lang" and len(sys.argv) > 3:
                set_language(sys.argv[3])
            elif sys.argv[2] == "while" and len(sys.argv) > 3:
                set_loop_mode(sys.argv[3].lower() == "true")
            else:
                print("用法: th set lang <python|c|cpp|go|lua>")
                print("      th set while true/false")
        elif sys.argv[1] == "care_py_main_python":
            try:
                import care
                print(f"彩蛋位置: {care.__file__}")
            except ImportError:
                print("彩蛋文件未找到，但你正在靠近真相")
        else:
            print(f"未知命令: {sys.argv[1]}")
            print("用法:")
            print("  th              进入交互式编辑器")
            print("  th -f <file>    执行文件")
            print("  th -f <file> --debug  调试模式")
            print("  th set lang <语言>   切换默认语言")
            print("  th --version")
    else:
        main()