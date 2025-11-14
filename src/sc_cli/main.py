import argparse
import os
import sys
import platform
from typing import List

from . import __version__
from .config import get_token, set_token, get_model
from .llm import generate_command_from_nl
from .runner import detect_shell, run_command, is_dangerous_command, seems_multi_command


def _build_root_parser() -> argparse.ArgumentParser:
	parser = argparse.ArgumentParser(
		prog="ccc",
		description="ccc — утилита для преобразования естественного языка в команды оболочки (OpenAI).",
	)
	parser.add_argument("-y", "--yes", action="store_true", help="Не спрашивать подтверждение, сразу выполнять.")
	parser.add_argument("--dry-run", action="store_true", help="Только показать команду, не выполнять.")
	parser.add_argument(
		"--shell",
		choices=["auto", "powershell", "cmd", "bash", "zsh", "sh"],
		default="auto",
		help="Целевая оболочка. По умолчанию определяется автоматически.",
	)
	parser.add_argument(
		"--model",
		default=None,
		help=f"Модель OpenAI (по умолчанию {get_model()}). Можно также задать через переменную окружения SC_MODEL.",
	)
	parser.add_argument(
		"--version",
		action="version",
		version=f"ccc {__version__}",
	)
	# Остаток командной строки — это текстовый запрос
	parser.add_argument("prompt", nargs=argparse.REMAINDER, help="Запрос на естественном языке.")
	return parser


def _build_token_parser() -> argparse.ArgumentParser:
	parser = argparse.ArgumentParser(
		prog="ccc token",
		description="Сохранить токен OpenAI в конфигурации.",
	)
	parser.add_argument("value", help="Токен OpenAI (sk-...)")
	return parser


def _confirm(prompt: str) -> bool:
	try:
		ans = input(prompt).strip().lower()
	except (EOFError, KeyboardInterrupt):
		return False
	if ans == "":
		return True
	if ans in ("y", "yes", "д", "да"):
		return True
	if ans in ("n", "no", "н", "нет"):
		return False
	return False


def _run_token_subcommand(argv: List[str]) -> int:
	parser = _build_token_parser()
	args = parser.parse_args(argv)
	set_token(args.value)
	print("Токен сохранён.")
	return 0


def _run_generate_and_execute(argv: List[str]) -> int:
	parser = _build_root_parser()
	args = parser.parse_args(argv)

	if not args.prompt:
		parser.print_help()
		return 1

	nl_query = " ".join(args.prompt).strip()
	api_key = get_token()
	if not api_key:
		print("Ошибка: токен OpenAI не задан. Установите его командой:\n  ccc token <YOUR_OPENAI_TOKEN>")
		return 2

	shell_name = detect_shell(args.shell)
	model = args.model or get_model()

	try:
		command = generate_command_from_nl(
			nl_request=nl_query,
			api_key=api_key,
			model=model,
			target_shell=shell_name,
		)
	except Exception as e:
		print(f"Ошибка генерации команды: {e}")
		return 3

	print(f"Команда: {command}")

	danger, reason = is_dangerous_command(command)
	if danger:
		print(f"ВНИМАНИЕ: потенциально опасная команда. {reason}")
		if not args.yes:
			if not _confirm("Выполнить всё равно? [Y/n]: "):
				return 4

	if seems_multi_command(command) and not args.yes:
		if not _confirm("Обнаружены составные команды (&&, ; или новые строки). Выполнить? [Y/n]: "):
			return 5

	if args.dry_run:
		return 0

	if not args.yes:
		if not _confirm("Выполнить команду? [Y/n]: "):
			return 6

	rc = run_command(command, shell_name)
	return rc


def cli(argv: List[str] = None) -> int:
	argv = list(sys.argv[1:] if argv is None else argv)
	if len(argv) > 0 and argv[0] == "token":
		return _run_token_subcommand(argv[1:])
	return _run_generate_and_execute(argv)


if __name__ == "__main__":
	sys.exit(cli())


