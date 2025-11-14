ccc — умный CLI для выполнения команд из естественного языка
===========================================================

Идея
----
Утилита `ccc` принимает запрос на любом языке (русский, английский и т.д.), отправляет его в OpenAI и получает конкретную команду для вашей оболочки (PowerShell / bash). Команда может быть показана для подтверждения и выполнена в текущем каталоге.

Установка (локально из исходников)
----------------------------------

Рекомендуется `pipx`:

```bash
pipx install .
```

Либо обычный `pip` (добавьте Python Scripts в PATH):

```bash
pip install .
```

После установки команда `ccc` будет доступна в вашей оболочке (также доступно имя `ссс`).

Установка одной командой из папки проекта
----------------------------------------

- Windows (PowerShell):

```powershell
powershell -ExecutionPolicy Bypass -File .\install.ps1
```

- Linux/WSL/macOS:

```bash
bash ./install.sh
```

Скрипт постарается установить `pipx` (если его нет), добавить его в PATH и затем установить `ccc`. При необходимости перезапустите терминал.

Установка на сервер (Ubuntu/Debian)
-----------------------------------

Предусловия:

```bash
sudo apt update
sudo apt install -y git python3 python3-venv python3-pip pipx
```

Вариант A — из клон‑репозитория (рекомендовано для последующего обновления из git):

```bash
git clone https://github.com/ArtemKaysin/ccc-wibe-terminal.git
cd ccc-wibe-terminal
sudo pipx install . --force
ccc --version
```

Обновление на сервере:

```bash
cd /path/to/ccc-wibe-terminal
git pull
sudo pipx install . --force
```

Вариант B — без клона, напрямую из GitHub:

```bash
sudo pipx install "git+https://github.com/ArtemKaysin/ccc-wibe-terminal.git@main#egg=ccc" --force
```

Настройка токена на сервере:

- Токен хранится в конфиге текущего пользователя: `~/.config/ccc/config.json` (или `XDG_CONFIG_HOME`).
- Запустите от имени пользователя, который будет использовать утилиту:

```bash
ccc token sk-...your_openai_token...
```

Альтернатива: задать переменную окружения `OPENAI_API_KEY` (например, через `/etc/environment`), тогда конфиг не обязателен.

Быстрый старт
-------------

1) Сохраните токен OpenAI:

```bash
ccc token sk-...your_openai_token...
```

2) Сформируйте и выполните команду:

```bash
ccc сделай комит с именем "initial setup"
# или
ссс сделай комит с именем "initial setup"
```

Перед выполнением `ccc` покажет команду и попросит подтверждение (если не передан `-y`).

Опции
-----
- `--dry-run` — показать команду, но не выполнять
- `-y/--yes` — не спрашивать подтверждение
- `--shell [auto|powershell|cmd|bash|zsh|sh]` — явно выбрать оболочку (по умолчанию auto)
- `--model <MODEL>` — указать модель OpenAI (по умолчанию `gpt-4o-mini`, можно через переменную окружения `SC_MODEL`)

Примеры
-------
```bash
# Linux/macOS
ccc создай директорию "build" и перейди в неё

# Windows PowerShell
ccc покажи последние 5 коммитов
```

Где хранится токен
------------------
- Windows: `%APPDATA%\ccc\config.json`
- Linux/macOS: `~/.config/ccc/config.json` (или `$XDG_CONFIG_HOME/ccc/config.json`)

Также можно задать токен через переменную окружения `OPENAI_API_KEY` (она имеет приоритет над конфигом).

Безопасность
------------
`ccc` добавляет базовые проверки: пытается обнаружить явно опасные команды (вроде `rm -rf /`, `diskpart`, `mkfs.*`) и требует подтверждение. Тем не менее, вы всегда отвечаете за запуск команд в вашей среде.

Лицензия
--------
MIT


