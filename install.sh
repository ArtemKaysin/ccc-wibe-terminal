#!/usr/bin/env bash
set -euo pipefail

echo "[ccc] Установка начата..."

have_cmd() { command -v "$1" >/dev/null 2>&1; }

PYTHON_BIN="${PYTHON_BIN:-python3}"
if ! have_cmd "$PYTHON_BIN"; then
	if have_cmd python; then
		PYTHON_BIN="python"
	else
		echo "[ccc] Не найден python. Установите Python 3 и повторите."
		exit 1
	fi
fi

if have_cmd pipx; then
	echo "[ccc] Найден pipx. Устанавливаю через pipx..."
	pipx install .
else
	echo "[ccc] pipx не найден. Пытаюсь установить: $PYTHON_BIN -m pip install --user pipx"
	"$PYTHON_BIN" -m pip install --user pipx
	echo "[ccc] Добавляю pipx в PATH (ensurepath)..."
	"$PYTHON_BIN" -m pipx ensurepath || true
	if have_cmd pipx; then
		echo "[ccc] Устанавливаю через pipx..."
		pipx install .
	else
		echo "[ccc] pipx всё ещё недоступен. Пытаюсь установить напрямую: $PYTHON_BIN -m pip install ."
		"$PYTHON_BIN" -m pip install .
	fi
fi

echo "[ccc] Готово. Возможно потребуется перезапустить терминал, чтобы команда 'ccc' появилась в PATH."
echo "[ccc] Проверьте: ccc --version"


