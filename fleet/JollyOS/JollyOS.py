#!/usr/bin/env python3
"""
JollyOS — the tiniest pirate-friendly micro-OS shell (Python CLI)
Drop this file in a repo, run it, and start adding commands or plugins.

License: MIT
"""

from __future__ import annotations
import os, sys, json, platform, time, shlex, importlib.util, pathlib
from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional

APP_NAME = "JollyOS"
APP_VERSION = "0.1.0"
STATE_DIR = pathlib.Path.home() / ".jollyos"
STATE_FILE = STATE_DIR / "state.json"
PLUGINS_DIR = pathlib.Path("plugins")  # relative to working dir

BANNER = r"""
      _       _ _           _   ____   _____
     | | ___ (_) | ___  ___| | / ___| |  ___|  JollyOS
  _  | |/ _ \| | |/ _ \/ __| | \___ \ | |_      drinker of voltage ⚡
 | |_| | (_) | | |  __/\__ \ |  ___) ||  _|
  \___/ \___/|_|_|\___||___/_| |____(_)_|      v{version}
""".strip("\n")

# ---------- small persistence ----------

def load_state() -> dict:
    try:
        STATE_DIR.mkdir(parents=True, exist_ok=True)
        if STATE_FILE.exists():
            return json.loads(STATE_FILE.read_text())
        return {"tasks": []}
    except Exception as e:
        print(f"[state] failed to load: {e}")
        return {"tasks": []}

def save_state(state: dict) -> None:
    try:
        STATE_DIR.mkdir(parents=True, exist_ok=True)
        STATE_FILE.write_text(json.dumps(state, indent=2))
    except Exception as e:
        print(f"[state] failed to save: {e}")

# ---------- command registry ----------

CommandFn = Callable[[List[str]], None]

@dataclass
class CLI:
    commands: Dict[str, CommandFn] = field(default_factory=dict)
    state: dict = field(default_factory=load_state)
    prompt: str = "JollyOS> "

    def register(self, name: str, fn: CommandFn, help_text: str):
        self.commands[name] = fn
        self.commands[f"{name}.__help__"] = lambda _=None, t=help_text: print(t)

    def help_for(self, name: str) -> Optional[str]:
        h = self.commands.get(f"{name}.__help__")
        if h:
            from io import StringIO
            buf = StringIO()
            # capture printed text
            _stdout = sys.stdout
            try:
                sys.stdout = buf
                h([])
            finally:
                sys.stdout = _stdout
            return buf.getvalue().rstrip()
        return None

    def run_line(self, line: str):
        line = line.strip()
        if not line:
            return
        parts = shlex.split(line)
        cmd, args = parts[0], parts[1:]
        if cmd in ("help", "?"):
            if args:
                txt = self.help_for(args[0]) or f"No help for '{args[0]}'."
                print(txt)
            else:
                self.print_help()
            return
        if cmd in ("exit", "quit"):
            print("Farewell, captain. 🏴‍☠️")
            save_state(self.state)
            raise SystemExit(0)
        fn = self.commands.get(cmd)
        if not fn:
            print(f"Unknown command: {cmd}. Type 'help' to list commands.")
            return
        try:
            fn(args)
        except KeyboardInterrupt:
            print("\n[interrupted]")
        except Exception as e:
            print(f"[error] {e}")

    def print_help(self):
        print("Available commands:")
        names = sorted(k for k in self.commands.keys() if ".__help__" not in k)
        for n in names:
            h = self.help_for(n) or ""
            first_line = h.splitlines()[0] if h else ""
            print(f"  {n:<14} {first_line}")

# ---------- built-in commands ----------

def cmd_banner(cli: CLI):
    def _fn(args: List[str]):
        print(BANNER.format(version=APP_VERSION))
    cli.register(
        "banner",
        _fn,
        "banner\n  Show the JollyOS banner."
    )

def cmd_sysinfo(cli: CLI):
    def _fn(args: List[str]):
        info = {
            "python": sys.version.split()[0],
            "platform": platform.platform(),
            "machine": platform.machine(),
            "processor": platform.processor() or "unknown",
            "pid": os.getpid(),
            "cwd": str(pathlib.Path.cwd()),
        }
        print(json.dumps(info, indent=2))
    cli.register(
        "sysinfo",
        _fn,
        "sysinfo\n  Print basic system information as JSON."
    )

def cmd_clear(cli: CLI):
    def _fn(args: List[str]):
        os.system("cls" if os.name == "nt" else "clear")
    cli.register(
        "clear",
        _fn,
        "clear\n  Clear the screen."
    )

def cmd_echo(cli: CLI):
    def _fn(args: List[str]):
        print(" ".join(args))
    cli.register(
        "echo",
        _fn,
        "echo <text>\n  Print text back to you."
    )

def cmd_tasks(cli: CLI):
    def _list():
        tasks = cli.state.get("tasks", [])
        if not tasks:
            print("(no tasks)")
            return
        for i, t in enumerate(tasks):
            mark = "✔" if t.get("done") else "•"
            print(f"{i:02d} {mark} {t['text']}")

    def _fn(args: List[str]):
        if not args:
            _list()
            return
        sub = args[0]
        if sub == "add":
            text = " ".join(args[1:]).strip()
            if not text:
                print("usage: tasks add <text>")
                return
            cli.state.setdefault("tasks", []).append({"text": text, "done": False})
            save_state(cli.state)
            print("added.")
        elif sub in ("done", "rm"):
            if len(args) < 2 or not args[1].isdigit():
                print(f"usage: tasks {sub} <index>")
                return
            idx = int(args[1])
            tasks = cli.state.get("tasks", [])
            if idx < 0 or idx >= len(tasks):
                print("index out of range")
                return
            if sub == "done":
                tasks[idx]["done"] = True
                print("marked done.")
            else:
                tasks.pop(idx)
                print("removed.")
            save_state(cli.state)
        else:
            _list()

    cli.register(
        "tasks",
        _fn,
        "tasks [add <text>|done <i>|rm <i>]\n  Tiny persistent todo list."
    )

def cmd_handshake(cli: CLI):
    def _fn(args: List[str]):
        target = args[0] if args else "pi4.local"
        print(f"[net] sending handshake to {target} ...")
        time.sleep(0.2)
        print(f"[net] SYN -> {target}")
        time.sleep(0.2)
        print(f"[net] ACK <- {target}")
        print("[net] link up (simulated).")
    cli.register(
        "handshake",
        _fn,
        "handshake [host]\n  Simulate a network handshake to a host."
    )

def cmd_lidar_ping(cli: CLI):
    def _fn(args: List[str]):
        port = args[0] if args else "/dev/serial0"
        print(f"[lidar] opening {port} (simulated)")
        for i in range(3):
            time.sleep(0.1)
            print(f"[lidar] sample {i}: {100 + i*3} cm")
        print("[lidar] done.")
    cli.register(
        "lidar:ping",
        _fn,
        "lidar:ping [port]\n  Simulate reading a few LiDAR samples."
    )

# ---------- plugin loader ----------

def load_plugins(cli: CLI):
    if not PLUGINS_DIR.exists():
        return
    for path in PLUGINS_DIR.glob("*.py"):
        try:
            spec = importlib.util.spec_from_file_location(path.stem, path)
            mod = importlib.util.module_from_spec(spec)  # type: ignore
            assert spec and spec.loader
            spec.loader.exec_module(mod)  # type: ignore
            if hasattr(mod, "register"):
                mod.register(cli)
                print(f"[plugin] loaded {path.name}")
        except Exception as e:
            print(f"[plugin] failed {path.name}: {e}")

# ---------- main loop ----------

def main(argv: List[str]):
    cli = CLI()
    # register built-ins
    cmd_banner(cli)
    cmd_sysinfo(cli)
    cmd_clear(cli)
    cmd_echo(cli)
    cmd_tasks(cli)
    cmd_handshake(cli)
    cmd_lidar_ping(cli)

    load_plugins(cli)
    print(BANNER.format(version=APP_VERSION))
    print("Type 'help' to list commands. 'exit' to quit.\n")

    # non-interactive mode (one-shot command)
    if len(argv) > 1:
        cli.run_line(" ".join(argv[1:]))
        save_state(cli.state)
        return

    # REPL
    while True:
        try:
            line = input(cli.prompt)
        except EOFError:
            print()
            break
        cli.run_line(line)

if __name__ == "__main__":
    main(sys.argv)
