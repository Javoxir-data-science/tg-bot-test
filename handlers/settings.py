# -*- coding: utf-8 -*-
from aiogram import Router, F
from aiogram.types import CallbackQuery
from database.db import get_user_settings, update_user_setting, get_struggling_words
from data.words import get_words_for_page
from keyboards.inline import (
    get_pages_keyboard,
    get_directions_keyboard,
    get_modes_keyboard,
    get_main_menu_keyboard
)

router = Router()

# ==================== SAHIFA TANLASH ====================
@router.callback_query(F.data == "menu_pages")
async def cb_menu_pages(call: CallbackQuery):
    user_id = call.from_user.id
    settings = get_user_settings(user_id)
    current_page = settings.get("page", 1)

    text = (
        "📄 <b>Kerakli sahifani tanlang:</b>\n\n"
        "Faqat siz tanlagan sahifadagi so'zlar mashg'ulotda beriladi."
    )
    await call.message.edit_text(text, reply_markup=get_pages_keyboard(current_page), parse_mode="HTML")
    await call.answer()

@router.callback_query(F.data.startswith("set_page_"))
async def cb_set_page(call: CallbackQuery):
    user_id = call.from_user.id
    page_num = int(call.data.replace("set_page_", ""))
    update_user_setting(user_id, "page", page_num)

    page_text = f"{page_num}-sahifa" if page_num != 0 else "Barcha sahifalar"
    await call.answer(f"✅ {page_text} tanlandi!", show_alert=False)

    # Menuga qaytish
    settings = get_user_settings(user_id)
    word_list = get_words_for_page(page_num)
    struggling = get_struggling_words(user_id, word_list)
    from handlers.start import get_welcome_text
    await call.message.edit_text(
        get_welcome_text(user_id),
        reply_markup=get_main_menu_keyboard(settings, has_mistakes=bool(struggling)),
        parse_mode="HTML"
    )

# ==================== YO'NALISH TANLASH ====================
@router.callback_query(F.data == "menu_directions")
async def cb_menu_directions(call: CallbackQuery):
    user_id = call.from_user.id
    settings = get_user_settings(user_id)
    current_dir = settings.get("direction", "en_uz")

    text = (
        "🔄 <b>O'rganish yo'nalishini tanlang:</b>\n\n"
        "• <b>Inglizcha ➡️ O'zbekcha:</b> inglizcha so'z chiqadi, o'zbekchasini topasiz.\n"
        "• <b>O'zbekcha ➡️ Inglizcha:</b> o'zbekcha so'z chiqadi, inglizchasini topasiz.\n"
        "• <b>Aralash (Mix):</b> ikkala yo'nalish tasodifiy almashib keladi."
    )
    await call.message.edit_text(text, reply_markup=get_directions_keyboard(current_dir), parse_mode="HTML")
    await call.answer()

@router.callback_query(F.data.startswith("set_dir_"))
async def cb_set_dir(call: CallbackQuery):
    user_id = call.from_user.id
    direction = call.data.replace("set_dir_", "")
    update_user_setting(user_id, "direction", direction)

    dir_names = {
        "en_uz": "Inglizcha ➡️ O'zbekcha",
        "uz_en": "O'zbekcha ➡️ Inglizcha",
        "mix": "Aralash (Mix)"
    }
    await call.answer(f"✅ {dir_names.get(direction)} tanlandi!", show_alert=False)

    # Menuga qaytish
    settings = get_user_settings(user_id)
    word_list = get_words_for_page(settings.get("page", 1))
    struggling = get_struggling_words(user_id, word_list)
    from handlers.start import get_welcome_text
    await call.message.edit_text(
        get_welcome_text(user_id),
        reply_markup=get_main_menu_keyboard(settings, has_mistakes=bool(struggling)),
        parse_mode="HTML"
    )

# ==================== REJIM TANLASH ====================
@router.callback_query(F.data == "menu_modes")
async def cb_menu_modes(call: CallbackQuery):
    user_id = call.from_user.id
    settings = get_user_settings(user_id)
    current_mode = settings.get("mode", "quiz")

    text = (
        "🎮 <b>O'rganish rejimini tanlang:</b>\n\n"
        "1. 🎯 <b>Test (4 ta variant):</b> Variantlar orasidan to'g'ri javobni tanlash.\n"
        "2. 🎴 <b>Flashcard (Karta):</b> So'z chiqadi, tarjimani eslab ko'rasiz va 'Javobni ko'rish'ni bosasiz.\n"
        "3. ✍️ <b>Yozma test:</b> So'z chiqadi, tarjimasini chatga o'zingiz yozasiz."
    )
    await call.message.edit_text(text, reply_markup=get_modes_keyboard(current_mode), parse_mode="HTML")
    await call.answer()

@router.callback_query(F.data.startswith("set_mode_"))
async def cb_set_mode(call: CallbackQuery):
    user_id = call.from_user.id
    mode = call.data.replace("set_mode_", "")
    update_user_setting(user_id, "mode", mode)

    mode_names = {
        "quiz": "Test rejimi",
        "flashcard": "Flashcard rejimi",
        "written": "Yozma rejim"
    }
    await call.answer(f"✅ {mode_names.get(mode)} tanlandi!", show_alert=False)

    # Menuga qaytish
    settings = get_user_settings(user_id)
    word_list = get_words_for_page(settings.get("page", 1))
    struggling = get_struggling_words(user_id, word_list)
    from handlers.start import get_welcome_text
    await call.message.edit_text(
        get_welcome_text(user_id),
        reply_markup=get_main_menu_keyboard(settings, has_mistakes=bool(struggling)),
        parse_mode="HTML"
    )
