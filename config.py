# -*- coding: utf-8 -*-
import os

# Agar python-dotenv o'rnatilgan bo'lsa, undan foydalanamiz
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # Aks holda standart python orqali .env faylni o'qiymiz
    env_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
    if os.path.exists(env_file):
        with open(env_file, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, val = line.split("=", 1)
                    os.environ.setdefault(key.strip(), val.strip())

BOT_TOKEN = os.getenv("BOT_TOKEN", "").strip()

if not BOT_TOKEN:
    print("OGOHLANTIRISH: BOT_TOKEN topilmadi! .env faylida BOT_TOKEN=... ni ko'rsating yoki muhit o'zgaruvchisi sifatida bering.")
