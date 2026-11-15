# -*- coding: utf-8 -*-
from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery
from database.db import (
    get_user_settings,
    get_user_stats,
    get_struggling_words,
    reset_user_page_progress
)
from data.words import get_words_for_page, get_total_words
from keyboards.inline import get_main_menu_keyboard, get_stats_keyboard

router = Router()

def get_welcome_text(user_id: int) -> str:
    settings = get_user_settings(user_id)
    page = settings.get("page", 1)
    direction = settings.get("direction", "en_uz")
    mode = settings.get("mode", "quiz")

    page_words = get_words_for_page(page)
    page_text = f"{page}-sahifa" if page != 0 else "Barcha sahifalar"

    dir_map = {
        "en_uz": "🇬🇧 Inglizcha ➡️ 🇺🇿 O'zbekcha",
        "uz_en": "🇺🇿 O'zbekcha ➡️ 🇬🇧 Inglizcha",
        "mix": "🔀 Aralash (Mix)"
    }
    mode_map = {
        "quiz": "🎯 Test (4 ta variant)",
        "flashcard": "🎴 Flashcard (Karta usuli)",
        "written": "✍️ Yozma (So'zni yozib kiritish)"
    }

    stats = get_user_stats(user_id, page_words)
    total = stats["total"]
    mastered = stats["mastered"]
    struggling = stats["struggling"]

    text = (
        "👋 <b>Assalomu alaykum!</b>\n\n"
        "Ingliz tili so'zlarini <b>mukammal yodlash botiga</b> xush kelibsiz!\n"
        f"📚 Bazada jami: <b>{get_total_words()} ta so'z</b> (6 ta sahifaga ajratilgan).\n\n"
        "⚙️ <b>Sizning sozlamalaringiz:</b>\n"
        f"• 📄 Sahifa: <b>{page_text}</b> ({total} ta so'z)\n"
        f"• 🔄 Yo'nalish: <b>{dir_map.get(direction)}</b>\n"
        f"• 🎮 Rejim: <b>{mode_map.get(mode)}</b>\n\n"
        f"📊 <b>Ushbu sahifadagi natijangiz:</b>\n"
        f"✅ Yodlangan: <b>{mastered}</b> ta | ❌ Qiyin so'zlar: <b>{struggling}</b> ta\n\n"
        "<i>Kerakli sahifa yoki rejimni tanlang va mashqni boshlang!</i>"
    )
    return text

@router.message(CommandStart())
async def cmd_start(message: Message):
    user_id = message.from_user.id
    settings = get_user_settings(user_id)
    page = settings.get("page", 1)
    word_list = get_words_for_page(page)
    struggling = get_struggling_words(user_id, word_list)

    text = get_welcome_text(user_id)
    keyboard = get_main_menu_keyboard(settings, has_mistakes=bool(struggling))
    await message.answer(text, reply_markup=keyboard, parse_mode="HTML")

@router.message(Command("help"))
async def cmd_help(message: Message):
    text = (
        "📖 <b>Botdan foydalanish bo'yicha qo'llanma:</b>\n\n"
        "1. <b>Sahifa tanlash:</b> Ro'yxatdagi 6 ta sahifadan birini yoki barcha 532 ta so'zni tanlashingiz mumkin.\n"
        "2. <b>Yo'nalishlar:</b>\n"
        "   • <i>Inglizcha ➡️ O'zbekcha</i> — inglizcha so'z beriladi, tarjimani topasiz.\n"
        "   • <i>O'zbekcha ➡️ Inglizcha</i> — o'zbekcha so'z beriladi, inglizcha variantini topasiz.\n"
        "   • <i>Aralash (Mix)</i> — har gal tasodifiy yo'nalish tushadi.\n"
        "3. <b>O'rganish rejimlari:</b>\n"
        "   • 🎯 <b>Test:</b> 4 ta variantdan to'g'risini tanlash.\n"
        "   • 🎴 <b>Flashcard:</b> Karta ko'rinishida o'zingizni tekshirish.\n"
        "   • ✍️ <b>Yozma test:</b> Klaviaturada so'zni o'zingiz yozib yuborish.\n"
        "4. <b>Spaced Repetition:</b> Siz xato qilgan so'zlarni bot avtomatik eslab qoladi va ularni ko'proq takrorlatadi.\n\n"
        "Buyruqlar:\n"
        "/start — Asosiy menyu\n"
        "/stats — Natijalar va statistika\n"
        "/help — Qo'llanma"
    )
    await message.answer(text, parse_mode="HTML")

@router.message(Command("stats"))
async def cmd_stats(message: Message):
    user_id = message.from_user.id
    settings = get_user_settings(user_id)
    page = settings.get("page", 1)
    word_list = get_words_for_page(page)
    stats = get_user_stats(user_id, word_list)

    page_text = f"{page}-sahifa" if page != 0 else "Barcha sahifalar"
    text = (
        f"📊 <b>{page_text} bo'yicha statistika:</b>\n\n"
        f"📝 Jami so'zlar: <b>{stats['total']} ta</b>\n"
        f"✅ Yodlangan so'zlar: <b>{stats['mastered']} ta</b>\n"
        f"❌ Qiyin / xato qilingan so'zlar: <b>{stats['struggling']} ta</b>\n"
        f"⏳ Hali o'rganilmagan: <b>{stats['not_started']} ta</b>\n"
    )
    keyboard = get_stats_keyboard(page)
    await message.answer(text, reply_markup=keyboard, parse_mode="HTML")

@router.callback_query(F.data == "back_to_menu")
async def cb_back_to_menu(call: CallbackQuery):
    user_id = call.from_user.id
    settings = get_user_settings(user_id)
    page = settings.get("page", 1)
    word_list = get_words_for_page(page)
    struggling = get_struggling_words(user_id, word_list)

    text = get_welcome_text(user_id)
    keyboard = get_main_menu_keyboard(settings, has_mistakes=bool(struggling))
    
    try:
        await call.message.edit_text(text, reply_markup=keyboard, parse_mode="HTML")
    except Exception:
        await call.message.answer(text, reply_markup=keyboard, parse_mode="HTML")
    await call.answer()

@router.callback_query(F.data == "show_stats")
async def cb_show_stats(call: CallbackQuery):
    user_id = call.from_user.id
    settings = get_user_settings(user_id)
    page = settings.get("page", 1)
    word_list = get_words_for_page(page)
    stats = get_user_stats(user_id, word_list)

    page_text = f"{page}-sahifa" if page != 0 else "Barcha sahifalar"
    text = (
        f"📊 <b>{page_text} bo'yicha statistika:</b>\n\n"
        f"📝 Jami so'zlar: <b>{stats['total']} ta</b>\n"
        f"✅ Yodlangan so'zlar: <b>{stats['mastered']} ta</b>\n"
        f"❌ Qiyin / xato qilingan so'zlar: <b>{stats['struggling']} ta</b>\n"
        f"⏳ Hali boshlanmagan: <b>{stats['not_started']} ta</b>\n"
    )
    keyboard = get_stats_keyboard(page)
    await call.message.edit_text(text, reply_markup=keyboard, parse_mode="HTML")
    await call.answer()

@router.callback_query(F.data.startswith("reset_stats_"))
async def cb_reset_stats(call: CallbackQuery):
    user_id = call.from_user.id
    page = int(call.data.replace("reset_stats_", ""))
    word_list = get_words_for_page(page)
    reset_user_page_progress(user_id, word_list)

    page_text = f"{page}-sahifa" if page != 0 else "Barcha sahifalar"
    await call.answer(f"{page_text} statistikasi nollashtirildi!", show_alert=True)

    # Menuga qaytish
    settings = get_user_settings(user_id)
    text = get_welcome_text(user_id)
    keyboard = get_main_menu_keyboard(settings, has_mistakes=False)
    await call.message.edit_text(text, reply_markup=keyboard, parse_mode="HTML")
