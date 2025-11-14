import json
import os
import pathlib
from typing import Any, Dict, Optional


CONFIG_DIR_PRIMARY = "ccc"
CONFIG_DIR_LEGACY = "sc"
CONFIG_FILE_NAME = "config.json"


def _config_base_dir(dir_name: str) -> pathlib.Path:
	# Windows
	if os.name == "nt":
		appdata = os.environ.get("APPDATA")
		if appdata:
			return pathlib.Path(appdata) / dir_name
		# Fallback to home if APPDATA is not set
		return pathlib.Path.home() / dir_name

	# POSIX
	xdg = os.environ.get("XDG_CONFIG_HOME")
	if xdg:
		return pathlib.Path(xdg) / dir_name
	return pathlib.Path.home() / ".config" / dir_name


def _config_path(dir_name: str) -> pathlib.Path:
	return _config_base_dir(dir_name) / CONFIG_FILE_NAME


def _load_config_from(dir_name: str) -> Dict[str, Any]:
	path = _config_path(dir_name)
	if not path.exists():
		return {}
	try:
		with path.open("r", encoding="utf-8") as f:
			return json.load(f)
	except Exception:
		# Corrupted or unreadable, treat as empty
		return {}


def load_config() -> Dict[str, Any]:
	# Try primary location
	cfg = _load_config_from(CONFIG_DIR_PRIMARY)
	if cfg:
		return cfg
	# Fallback to legacy location
	legacy = _load_config_from(CONFIG_DIR_LEGACY)
	if legacy:
		# Migrate by saving to primary
		try:
			save_config(legacy)
		except Exception:
			pass
		return legacy
	return {}


def save_config(cfg: Dict[str, Any]) -> None:
	path = _config_path(CONFIG_DIR_PRIMARY)
	path.parent.mkdir(parents=True, exist_ok=True)
	with path.open("w", encoding="utf-8") as f:
		json.dump(cfg, f, ensure_ascii=False, indent=2)


def set_token(token: str) -> None:
	cfg = load_config()
	cfg["openai_api_key"] = token.strip()
	save_config(cfg)


def get_token() -> Optional[str]:
	# Priority 1: explicit env var OPENAI_API_KEY
	env_token = (
		os.environ.get("OPENAI_API_KEY")
		or os.environ.get("CCC_OPENAI_API_KEY")
		or os.environ.get("SC_OPENAI_API_KEY")
	)
	if env_token:
		return env_token.strip()

	# Priority 2: config file
	cfg = load_config()
	token = cfg.get("openai_api_key")
	if token:
		return str(token).strip()

	return None


def get_model(default_model: str = "gpt-4.1") -> str:
	# Priority 1: explicit env var
	env_model = os.environ.get("CCC_MODEL") or os.environ.get("SC_MODEL")
	if env_model:
		return env_model.strip()

	# Priority 2: config file
	cfg = load_config()
	model = cfg.get("model")
	if model:
		return str(model).strip()

	return default_model


def set_model(model: str) -> None:
	cfg = load_config()
	cfg["model"] = model.strip()
	save_config(cfg)


