"""
Google Translate API Integration Module for BootBridge
Provides lightweight, zero-dependency multi-language translation with local caching.
Uses official Chrome extension Google Translate endpoint for fast, reliable translations.
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

def translate_text(text, target_lang="en", source_lang="auto"):
    """
    Translates text to target_lang using Google Translate API endpoint.
    Uses local JSON caching to ensure instant responses for repeated phrases.
    """
    if not text or not isinstance(text, str) or target_lang == "id":
        return text

    cache_key = f"{target_lang}:{text}"
    with _cache_lock:
        if cache_key in _cache:
            return _cache[cache_key]

    try:
        q = urllib.parse.quote(text)
        url = f"https://clients5.google.com/translate_a/t?client=dict-chrome-ex&sl={source_lang}&tl={target_lang}&q={q}"
        req = urllib.request.Request(
            url,
            headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}
        )
        with urllib.request.urlopen(req, timeout=4) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            result = text
            if isinstance(data, list) and len(data) > 0:
                if isinstance(data[0], list):
                    result = data[0][0]
                elif isinstance(data[0], str):
                    result = data[0]

            with _cache_lock:
                _cache[cache_key] = result
            save_cache()
            return result
    except Exception as e:
        print(f"[Translator] Translation fallback for '{text[:20]}...' ({target_lang}): {e}")

    return text
