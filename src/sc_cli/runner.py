import os
import shutil
import subprocess
import sys
from typing import Optional, Tuple
import platform
import re


def detect_shell(preferred: str = "auto") -> str:
	if preferred and preferred != "auto":
		return preferred
	system = platform.system().lower()
	if "windows" in system:
		return "powershell"
	# POSIX
	if shutil.which("bash"):
		return "bash"
	if shutil.which("zsh"):
		return "zsh"
	return "sh"


def run_command(command: str, shell_name: str) -> int:
	system = platform.system().lower()
	if shell_name == "powershell" or ("windows" in system and shell_name == "auto"):
		exe = shutil.which("pwsh") or shutil.which("powershell") or "powershell"
		proc = subprocess.run(
			[exe, "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", command],
			text=True,
		)
		return proc.returncode

	if shell_name == "cmd":
		exe = shutil.which("cmd") or "cmd"
		proc = subprocess.run([exe, "/C", command], text=True)
		return proc.returncode

	# POSIX shells
	if shell_name == "bash":
		exe = shutil.which("bash") or "bash"
		proc = subprocess.run([exe, "-lc", command], text=True)
		return proc.returncode
	if shell_name == "zsh":
		exe = shutil.which("zsh") or "zsh"
		proc = subprocess.run([exe, "-lc", command], text=True)
		return proc.returncode
	# default sh
	exe = shutil.which("sh") or "sh"
	proc = subprocess.run([exe, "-lc", command], text=True)
	return proc.returncode


_DANGER_PATTERNS = [
	r"\brm\s+-rf\s+/\s*$",  # rm -rf /
	r"\brm\s+-rf\s+/\*",    # rm -rf /*
	r"\bmkfs(\.|_|-)",      # mkfs.*
	r"\bdd\s+if=.*\s+of=/dev/sd[a-z]",  # dd writing to disks
	r"\bshutdown\b",
	r"\breboot\b",
	r"\bhalt\b",
	r":\s*\(\)\s*\{\s*:\s*\|\s*:\s*&\s*\};\s*:",  # fork bomb
	r"\bformat\b",
	r"\bdiskpart\b",
	r"\bdel\s+/s\s+/q\s+C:\\",  # windows dangerous delete
	r"\brd\s+/s\s+/q\s+C:\\",
	r"\bRemove-Item\s+-Recurse\s+-Force\s+C:\\",
]


def is_dangerous_command(command: str) -> Tuple[bool, Optional[str]]:
	text = command.strip()
	lower = text.lower()
	for pat in _DANGER_PATTERNS:
		if re.search(pat, lower, flags=re.IGNORECASE):
			return True, f"Команда совпала с опасным шаблоном: {pat}"
	return False, None


def seems_multi_command(command: str) -> bool:
	# Грубая эвристика: многострочность или явные цепочки
	if "\n" in command:
		return True
	if "&&" in command or "||" in command or ";" in command:
		return True
	return False


