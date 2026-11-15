# -*- coding: utf-8 -*-
import random
import re
from typing import Dict, Any, List, Tuple
from data.words import get_words_for_page
from database.db import (
    get_user_settings,
    save_current_session,
    record_answer,
    get_user_stats,
    get_struggling_words
)

def clean_text(text: str) -> str:
    """Tekshirish uchun matnni tozalaydi (kichik harflar, apostroflarni bir xillashtirish)"""
    if not text:
        return ""
    text = text.lower().strip()
    # Har xil apostroflarni bitta standart ' ga aylantiramiz
    text = text.replace("’", "'").replace("‘", "'").replace("`", "'").replace("ʻ", "'").replace("ʼ", "'")
    # Tinish belgilarini soddalashtirish
    text = re.sub(r"[^\w\s\']", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text

def check_written_answer(user_input: str, correct_target: str) -> bool:
    """
    Foydalanuvchi kiritgan matn to'g'riligini tekshiradi.
    Agar tarjimada 'Hudud; maydon' bo'lsa, foydalanuvchi 'hudud' yoki 'maydon' desa ham to'g'ri hisoblanadi.
    """
    cleaned_input = clean_text(user_input)
    if not cleaned_input:
        return False

    cleaned_target = clean_text(correct_target)
    if cleaned_input == cleaned_target:
        return True

    # Sinonimlarni qismlarga ajratamiz (masalan ';' yoki '/' bo'yicha)
    parts = re.split(r"[;/]", correct_target)
    for part in parts:
        cleaned_part = clean_text(part)
        if cleaned_part and cleaned_part == cleaned_input:
            return True
        # Qavs ichidagi izohlarni olib tashlab tekshirish: masalan "Holat; ish (sud ishi)" -> "ish"
        without_parens = re.sub(r"\(.*?\)", "", part)
        cleaned_without_parens = clean_text(without_parens)
        if cleaned_without_parens and cleaned_without_parens == cleaned_input:
            return True
        # Qavs ichidagi so'zni ham tekshirish: masalan "(sud ishi)" -> "sud ishi"
        inside_parens = re.findall(r"\((.*?)\)", part)
        for ip in inside_parens:
            if clean_text(ip) == cleaned_input:
                return True

    return False

def select_word_for_user(user_id: int, only_mistakes: bool = False) -> Tuple[Dict[str, str], List[Dict[str, str]]]:
    """Foydalanuvchi uchun keyingi so'zni tanlaydi."""
    settings = get_user_settings(user_id)
    page = settings.get("page", 1)
    word_list = get_words_for_page(page)

    if not word_list:
        word_list = get_words_for_page(1)

    if only_mistakes:
        struggling = get_struggling_words(user_id, word_list)
        if struggling:
            return random.choice(struggling), word_list

    # 35% ehtimollik bilan oldin xato qilingan so'zlardan beramiz (takrorlash algoritmi)
    if random.random() < 0.35:
        struggling = get_struggling_words(user_id, word_list)
        if struggling:
            return random.choice(struggling), word_list

    # Oddiy tasodifiy tanlash
    selected_word = random.choice(word_list)
    return selected_word, word_list

def prepare_question(user_id: int, only_mistakes: bool = False) -> Dict[str, Any]:
    """
    Joriy foydalanuvchi sozlamalari asosida yangi savolni tayyorlaydi va sessiyani saqlaydi.
    """
    settings = get_user_settings(user_id)
    direction_setting = settings.get("direction", "en_uz")
    mode = settings.get("mode", "quiz")
    page = settings.get("page", 1)

    word, word_list = select_word_for_user(user_id, only_mistakes=only_mistakes)

    # Yo'nalishni aniqlash
    if direction_setting == "mix":
        active_direction = random.choice(["en_uz", "uz_en"])
    else:
        active_direction = direction_setting

    en_word = word["en"]
    uz_word = word["uz"]

    prompt_word = en_word if active_direction == "en_uz" else uz_word
    target_word = uz_word if active_direction == "en_uz" else en_word

    options = []
    correct_idx = -1

    if mode == "quiz":
        # 3 ta noto'g'ri variant tanlaymiz
        other_words = [w for w in word_list if w["en"] != en_word]
        if len(other_words) < 3:
            # Agar sahifada so'z kam bo'lsa (barcha so'zlardan olamiz)
            all_w = get_words_for_page(0)
            other_words = [w for w in all_w if w["en"] != en_word]
            
        distractors = random.sample(other_words, min(3, len(other_words)))
        options_raw = [target_word] + [
            (d["uz"] if active_direction == "en_uz" else d["en"]) for d in distractors
        ]
        
        # Aralashtiramiz
        random.shuffle(options_raw)
        options = options_raw
        correct_idx = options.index(target_word)

    save_current_session(
        user_id=user_id,
        current_en=en_word,
        current_uz=uz_word,
        current_dir=active_direction,
        options=options,
        correct_idx=correct_idx
    )

    return {
        "page": page,
        "mode": mode,
        "direction": active_direction,
        "prompt_word": prompt_word,
        "target_word": target_word,
        "en_word": en_word,
        "uz_word": uz_word,
        "options": options,
        "correct_idx": correct_idx
    }
