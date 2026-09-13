"""
Google Translate API Integration Module for BootBridge
Provides lightweight, zero-dependency multi-language translation with local caching.
Supports batch translation in 1 single HTTP request for 0ms lag!
"""

import os
import json
import urllib.request
import urllib.parse
import threading

CACHE_FILE = os.path.expanduser("~/.config/bootbridge/translation_cache.json")
_cache = {}
_cache_lock = threading.Lock()

SUPPORTED_LANGUAGES = [
    ("id", "Bahasa Indonesia"),
    ("en", "English"),
    ("es", "Español (Spanish)"),
    ("fr", "Français (French)"),
    ("de", "Deutsch (German)"),
    ("zh-CN", "简体中文 (Chinese Simplified)"),
    ("ja", "日本語 (Japanese)"),
    ("ko", "한국어 (Korean)"),
    ("ru", "Русский (Russian)"),
    ("ar", "العربية (Arabic)"),
    ("pt", "Português (Portuguese)"),
    ("it", "Italiano (Italian)"),
    ("tr", "Türkçe (Turkish)"),
    ("nl", "Nederlands (Dutch)"),
    ("pl", "Polski (Polish)"),
    ("vi", "Tiếng Việt (Vietnamese)"),
    ("th", "ไทย (Thai)"),
]

def load_cache():
    global _cache
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, "r", encoding="utf-8") as f:
                _cache = json.load(f)
        except Exception:
            _cache = {}

def save_cache():
    with _cache_lock:
        try:
            os.makedirs(os.path.dirname(CACHE_FILE), exist_ok=True)
            with open(CACHE_FILE, "w", encoding="utf-8") as f:
                json.dump(_cache, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"[Translator] Error saving cache: {e}")

load_cache()

def batch_translate_keys(keys_dict, target_lang="en", source_lang="id", callback=None):
    """
    Translates an entire dictionary of keys/values in 1 single batch HTTP request.
    Stores translated strings in local JSON cache.
    """
    if target_lang in ("id", "en"):
        if callback:
            callback(True)
        return

    keys = list(keys_dict.keys())
    values = [keys_dict[k] for k in keys if isinstance(keys_dict[k], str)]

    # Filter out values already cached
    missing_values = []
    for val in values:
        ck = f"{target_lang}:{val}"
        with _cache_lock:
            if ck not in _cache:
                missing_values.append(val)

    if not missing_values:
        if callback:
            callback(True)
        return

    def run_batch():
        DELIMITER = "\n---BB_SEP---\n"
        combined_text = DELIMITER.join(missing_values)
        try:
            q = urllib.parse.quote(combined_text)
            url = f"https://clients5.google.com/translate_a/t?client=dict-chrome-ex&sl={source_lang}&tl={target_lang}&q={q}"
            req = urllib.request.Request(
                url,
                headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
            )
            with urllib.request.urlopen(req, timeout=6) as resp:
                data = json.loads(resp.read().decode('utf-8'))
                translated_blob = ""
                if isinstance(data, list) and len(data) > 0:
                    if isinstance(data[0], list):
                        translated_blob = data[0][0]
                    elif isinstance(data[0], str):
                        translated_blob = data[0]

                parts = [p.strip() for p in translated_blob.split("---BB_SEP---")]
                with _cache_lock:
                    for idx, orig_val in enumerate(missing_values):
                        if idx < len(parts) and parts[idx]:
                            _cache[f"{target_lang}:{orig_val}"] = parts[idx]
                        else:
                            _cache[f"{target_lang}:{orig_val}"] = orig_val
                save_cache()
                if callback:
                    callback(True)
        except Exception as e:
            print(f"[Translator] Batch translation error ({target_lang}): {e}")
            if callback:
                callback(False)

    threading.Thread(target=run_batch, daemon=True).start()

def translate_text(text, target_lang="en", source_lang="id"):
    """Instant in-memory lookup for translated string."""
    if not text or not isinstance(text, str) or target_lang == "id":
        return text

    cache_key = f"{target_lang}:{text}"
    with _cache_lock:
        if cache_key in _cache:
            return _cache[cache_key]

    return text
