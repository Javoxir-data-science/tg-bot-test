# -*- coding: utf-8 -*-
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from typing import List, Dict, Any
from data.words import WORDS_BY_PAGE

def get_main_menu_keyboard(settings: Dict[str, Any], has_mistakes: bool = False) -> InlineKeyboardMarkup:
    page = settings.get("page", 1)
    direction = settings.get("direction", "en_uz")
    mode = settings.get("mode", "quiz")

    page_text = f"📄 {page}-sahifa" if page != 0 else "📚 Barcha sahifalar"
    
    dir_map = {
        "en_uz": "🇬🇧 EN ➡️ 🇺🇿 UZ",
        "uz_en": "🇺🇿 UZ ➡️ 🇬🇧 EN",
        "mix": "🔀 Aralash (Mix)"
    }
    dir_text = dir_map.get(direction, "🇬🇧 EN ➡️ 🇺🇿 UZ")

    mode_map = {
        "quiz": "🎯 Test (4 variant)",
        "flashcard": "🎴 Flashcard (Karta)",
        "written": "✍️ Yozma test"
    }
    mode_text = mode_map.get(mode, "🎯 Test")

    buttons = [
        [InlineKeyboardButton(text="🚀 Mashqni boshlash", callback_data="start_training")],
        [
            InlineKeyboardButton(text=f"Sahifa: {page_text}", callback_data="menu_pages"),
        ],
        [
            InlineKeyboardButton(text=f"Yo'nalish: {dir_text}", callback_data="menu_directions"),
        ],
        [
            InlineKeyboardButton(text=f"Rejim: {mode_text}", callback_data="menu_modes"),
        ],
        [
            InlineKeyboardButton(text="📊 Statistika", callback_data="show_stats"),
        ]
    ]

    if has_mistakes:
        buttons.append([InlineKeyboardButton(text="🔁 Xatolar ustida ishlash", callback_data="practice_mistakes")])

    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_pages_keyboard(selected_page: int) -> InlineKeyboardMarkup:
    def mark(p):
        return " ✅" if p == selected_page else ""

    buttons = [
        [
            InlineKeyboardButton(text=f"1-sahifa ({len(WORDS_BY_PAGE[1])} ta){mark(1)}", callback_data="set_page_1"),
            InlineKeyboardButton(text=f"2-sahifa ({len(WORDS_BY_PAGE[2])} ta){mark(2)}", callback_data="set_page_2"),
        ],
        [
            InlineKeyboardButton(text=f"3-sahifa ({len(WORDS_BY_PAGE[3])} ta){mark(3)}", callback_data="set_page_3"),
            InlineKeyboardButton(text=f"4-sahifa ({len(WORDS_BY_PAGE[4])} ta){mark(4)}", callback_data="set_page_4"),
        ],
        [
            InlineKeyboardButton(text=f"5-sahifa ({len(WORDS_BY_PAGE[5])} ta){mark(5)}", callback_data="set_page_5"),
            InlineKeyboardButton(text=f"6-sahifa ({len(WORDS_BY_PAGE[6])} ta){mark(6)}", callback_data="set_page_6"),
        ],
        [
            InlineKeyboardButton(text=f"📚 Barchasi (532 ta so'z){mark(0)}", callback_data="set_page_0"),
        ],
        [
            InlineKeyboardButton(text="🔙 Asosiy menyu", callback_data="back_to_menu")
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_directions_keyboard(selected_dir: str) -> InlineKeyboardMarkup:
    def mark(d):
        return " ✅" if d == selected_dir else ""

    buttons = [
        [InlineKeyboardButton(text=f"🇬🇧 Inglizcha ➡️ 🇺🇿 O'zbekcha{mark('en_uz')}", callback_data="set_dir_en_uz")],
        [InlineKeyboardButton(text=f"🇺🇿 O'zbekcha ➡️ 🇬🇧 Inglizcha{mark('uz_en')}", callback_data="set_dir_uz_en")],
        [InlineKeyboardButton(text=f"🔀 Aralash (Mix){mark('mix')}", callback_data="set_dir_mix")],
        [InlineKeyboardButton(text="🔙 Asosiy menyu", callback_data="back_to_menu")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_modes_keyboard(selected_mode: str) -> InlineKeyboardMarkup:
    def mark(m):
        return " ✅" if m == selected_mode else ""

    buttons = [
        [InlineKeyboardButton(text=f"🎯 Test (4 ta variantli){mark('quiz')}", callback_data="set_mode_quiz")],
        [InlineKeyboardButton(text=f"🎴 Flashcard (Karta usuli){mark('flashcard')}", callback_data="set_mode_flashcard")],
        [InlineKeyboardButton(text=f"✍️ Yozma (So'zni yozib kiritish){mark('written')}", callback_data="set_mode_written")],
        [InlineKeyboardButton(text="🔙 Asosiy menyu", callback_data="back_to_menu")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_quiz_options_keyboard(options: List[str]) -> InlineKeyboardMarkup:
    buttons = []
    # 4 variantni 1 tadan qatorda chiqaramiz, chunki tarjimalar uzun bo'lishi mumkin
    for idx, opt in enumerate(options):
        buttons.append([InlineKeyboardButton(text=opt, callback_data=f"quiz_ans_{idx}")])
    
    buttons.append([
        InlineKeyboardButton(text="⏭ O'tkazib yuborish", callback_data="next_question"),
        InlineKeyboardButton(text="🔙 Menyu", callback_data="back_to_menu")
    ])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_quiz_next_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⏭ Keyingi so'z ➡️", callback_data="next_question")],
        [InlineKeyboardButton(text="🔙 Menyu", callback_data="back_to_menu")]
    ])

def get_flashcard_question_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="👁 Tarjimani ko'rish", callback_data="flash_reveal")],
        [
            InlineKeyboardButton(text="⏭ O'tkazish", callback_data="next_question"),
            InlineKeyboardButton(text="🔙 Menyu", callback_data="back_to_menu")
        ]
    ])

def get_flashcard_answer_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Yodda qoldi", callback_data="flash_known"),
            InlineKeyboardButton(text="❌ Bilmadim / Qaytaring", callback_data="flash_unknown")
        ],
        [InlineKeyboardButton(text="🔙 Menyu", callback_data="back_to_menu")]
    ])

def get_written_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💡 Javobni ko'rish", callback_data="written_reveal")],
        [
            InlineKeyboardButton(text="⏭ Keyingi so'z", callback_data="next_question"),
            InlineKeyboardButton(text="🔙 Menyu", callback_data="back_to_menu")
        ]
    ])

def get_stats_keyboard(page: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🚀 Mashqni davom ettirish", callback_data="start_training")],
        [InlineKeyboardButton(text="🔄 Ushbu sahifani nollash", callback_data=f"reset_stats_{page}")],
        [InlineKeyboardButton(text="🔙 Asosiy menyu", callback_data="back_to_menu")]
    ])
