import os
import platform
from typing import Optional

from .config import get_model

_HAS_NEW_CLIENT = False
_OPENAI_CLIENT = None
_OPENAI_LEGACY = None

# Lazy import forms to work with both OpenAI SDK 1.x and legacy 0.x if present
try:
	from openai import OpenAI  # type: ignore
	_HAS_NEW_CLIENT = True
except Exception:
	_HAS_NEW_CLIENT = False

if not _HAS_NEW_CLIENT:
	try:
		import openai as _OPENAI_LEGACY  # type: ignore
	except Exception:
		_OPENAI_LEGACY = None


def _build_system_prompt() -> str:
	return (
		"Ты система синтеза команд оболочки. "
		"Получая запрос на любом естественном языке, генерируй ОДНУ однострочную команду "
		"для указанной ОС и оболочки. "
		"Строго выведи только команду: без пояснений, без кавычек вокруг, без бэктиков и без форматирования кода. "
		"Для Windows используй синтаксис PowerShell. Для Linux/macOS — bash. "
		"Избегай деструктивных действий, не используй команды форматирования дисков и т.п. "
		"Если запрос двусмысленный — выбери наиболее вероятную безопасную интерпретацию."
	)


def _strip_fences(text: str) -> str:
	t = text.strip()
	# Удаляем блоки ```...```
	if t.startswith("```"):
		# удалим первую строку с ```... и последнюю ```
		lines = t.splitlines()
		# убираем первую и последнюю, если последняя тоже ```
		if lines and lines[0].startswith("```"):
			lines = lines[1:]
		if lines and lines[-1].strip() == "```":
			lines = lines[:-1]
		t = "\n".join(lines).strip()
	# Иногда LLM добавляет кавычки вокруг всей команды
	if (t.startswith('"') and t.endswith('"')) or (t.startswith("'") and t.endswith("'")):
		t = t[1:-1].strip()
	# Оставим первую непустую строку (на случай многострочного вывода)
	for line in t.splitlines():
		line = line.strip()
		if line:
			return line
	return t


def generate_command_from_nl(
	nl_request: str,
	api_key: str,
	model: Optional[str] = None,
	target_shell: Optional[str] = None,
) -> str:
	"""
	Преобразует запрос на естественном языке в команду оболочки.
	"""
	if not api_key:
		raise RuntimeError("Токен OpenAI не задан.")

	model_name = model or get_model()
	os_name = platform.system()
	cwd = os.getcwd()
	shell_name = target_shell or "auto"

	system_prompt = _build_system_prompt()
	user_prompt = (
		f"ОС: {os_name}\n"
		f"Оболочка: {shell_name}\n"
		f"Текущая директория: {cwd}\n"
		f"Запрос: {nl_request}\n\n"
		f"Выведи только одну команду."
	)

	# Новый клиент (OpenAI SDK 1.x)
	if _HAS_NEW_CLIENT:
		client = OpenAI(api_key=api_key)
		resp = client.chat.completions.create(
			model=model_name,
			messages=[
				{"role": "system", "content": system_prompt},
				{"role": "user", "content": user_prompt},
			],
			temperature=0.2,
		)
		raw = resp.choices[0].message.content or ""
		return _strip_fences(raw)

	# Легаси клиент (0.x), если установлен
	if _OPENAI_LEGACY is not None:
		_OPENAI_LEGACY.api_key = api_key
		resp = _OPENAI_LEGACY.ChatCompletion.create(
			model=model_name,
			messages=[
				{"role": "system", "content": system_prompt},
				{"role": "user", "content": user_prompt},
			],
			temperature=0.2,
		)
		raw = resp.choices[0].message["content"] or ""
		return _strip_fences(raw)

	raise RuntimeError("Библиотека OpenAI не установлена. Установите пакет `openai`.")


