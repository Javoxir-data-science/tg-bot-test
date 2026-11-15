# -*- coding: utf-8 -*-
from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from services.training import prepare_question, check_written_answer
from database.db import (
    get_user_settings,
    get_current_session,
    record_answer,
    mark_session_answered,
    get_struggling_words
)
from data.words import get_words_for_page
from keyboards.inline import (
    get_quiz_options_keyboard,
    get_quiz_next_keyboard,
    get_flashcard_question_keyboard,
    get_flashcard_answer_keyboard,
    get_written_keyboard,
    get_main_menu_keyboard
)

router = Router()

async def send_next_question(call_or_msg, user_id: int, only_mistakes: bool = False, edit: bool = False):
    """Yangi savol yoki kartani foydalanuvchiga yuboradi"""
    settings = get_user_settings(user_id)
    page = settings.get("page", 1)
    word_list = get_words_for_page(page)

    if only_mistakes:
        struggling = get_struggling_words(user_id, word_list)
        if not struggling:
            text = (
                "🎉 <b>Ajoyib natija!</b>\n\n"
                "Ushbu sahifada xato qilingan so'zlar qolmadi! Barchasini muvaffaqiyatli o'zlashtirdingiz."
            )
            keyboard = get_main_menu_keyboard(settings, has_mistakes=False)
            if isinstance(call_or_msg, CallbackQuery):
                await call_or_msg.message.edit_text(text, reply_markup=keyboard, parse_mode="HTML")
            else:
                await call_or_msg.answer(text, reply_markup=keyboard, parse_mode="HTML")
            return

    q = prepare_question(user_id, only_mistakes=only_mistakes)
    mode = q["mode"]
    direction = q["direction"]
    page_num = q["page"]
    page_text = f"{page_num}-sahifa" if page_num != 0 else "Barcha sahifalar"
    dir_label = "🇬🇧 ➡️ 🇺🇿" if direction == "en_uz" else "🇺🇿 ➡️ 🇬🇧"
    word_display = q["prompt_word"].upper()

    divider = "───────────────────────"

    if mode == "quiz":
        text = (
            f"🎯 <b>[{page_text}] • Test ({dir_label})</b>\n"
            f"{divider}\n\n"
            "📝 <b>Tarjima qilinadigan so'z:</b>\n\n"
            f"<b>{word_display}</b>\n\n"
            "<i>To'g'ri tarjimani tanlang:</i>"
        )
        keyboard = get_quiz_options_keyboard(q["options"])
    elif mode == "flashcard":
        text = (
            f"🎴 <b>[{page_text}] • Flashcard ({dir_label})</b>\n"
            f"{divider}\n\n"
            "📝 <b>Tarjima qilinadigan so'z:</b>\n\n"
            f"<b>{word_display}</b>\n\n"
            "<i>Tarjimani eslang va javobni oching:</i>"
        )
        keyboard = get_flashcard_question_keyboard()
    else:  # written
        text = (
            f"✍️ <b>[{page_text}] • Yozma test ({dir_label})</b>\n"
            f"{divider}\n\n"
            "📝 <b>Tarjima qilinadigan so'z:</b>\n\n"
            f"<b>{word_display}</b>\n\n"
            "<i>To'g'ri tarjimani yozib yuboring:</i>"
        )
        keyboard = get_written_keyboard()

    if isinstance(call_or_msg, CallbackQuery):
        if edit:
            try:
                await call_or_msg.message.edit_text(text, reply_markup=keyboard, parse_mode="HTML")
            except Exception:
                await call_or_msg.message.answer(text, reply_markup=keyboard, parse_mode="HTML")
        else:
            await call_or_msg.message.answer(text, reply_markup=keyboard, parse_mode="HTML")
    else:
        await call_or_msg.answer(text, reply_markup=keyboard, parse_mode="HTML")

# ==================== MASHQNI BOSHLASH ====================
@router.callback_query(F.data == "start_training")
async def cb_start_training(call: CallbackQuery):
    await send_next_question(call, call.from_user.id, only_mistakes=False, edit=True)
    await call.answer()

@router.callback_query(F.data == "next_question")
async def cb_next_question(call: CallbackQuery):
    await send_next_question(call, call.from_user.id, only_mistakes=False, edit=True)
    await call.answer()

@router.callback_query(F.data == "practice_mistakes")
async def cb_practice_mistakes(call: CallbackQuery):
    await send_next_question(call, call.from_user.id, only_mistakes=True, edit=True)
    await call.answer()

# ==================== TEST (QUIZ) REJIMI ====================
@router.callback_query(F.data.startswith("quiz_ans_"))
async def cb_quiz_answer(call: CallbackQuery):
    user_id = call.from_user.id
    session = get_current_session(user_id)
    if not session or session["is_answered"]:
        await call.answer("Bu savolga allaqachon javob berilgan!", show_alert=False)
        return

    chosen_idx = int(call.data.replace("quiz_ans_", ""))
    correct_idx = session["correct_index"]
    options = session["options"]
    en_word = session["current_en"]
    uz_word = session["current_uz"]

    is_correct = (chosen_idx == correct_idx)
    record_answer(user_id, en_word, is_correct)
    mark_session_answered(user_id)

    divider = "───────────────────────"

    if is_correct:
        text = (
            "✅ <b>TO'G'RI JAVOB! BARAKALLA!</b>\n"
            f"{divider}\n\n"
            f"🇬🇧 <b>{en_word}</b>  ➔  🇺🇿 <b>{uz_word}</b>"
        )
    else:
        chosen_text = options[chosen_idx] if 0 <= chosen_idx < len(options) else ""
        text = (
            "❌ <b>NOTO'G'RI!</b>\n"
            f"{divider}\n\n"
            f"Siz tanladingiz: <s>{chosen_text}</s>\n\n"
            "To'g'ri javob:\n"
            f"✅ 🇬🇧 <b>{en_word}</b>  ➔  🇺🇿 <b>{uz_word}</b>\n\n"
            "<i>(Ushbu so'z mustahkamlash uchun yana takrorlanadi)</i>"
        )

    await call.message.edit_text(text, reply_markup=get_quiz_next_keyboard(), parse_mode="HTML")
    await call.answer()

# ==================== FLASHCARD REJIMI ====================
@router.callback_query(F.data == "flash_reveal")
async def cb_flash_reveal(call: CallbackQuery):
    user_id = call.from_user.id
    session = get_current_session(user_id)
    if not session:
        await cb_next_question(call)
        return

    en_word = session["current_en"]
    uz_word = session["current_uz"]
    divider = "───────────────────────"

    text = (
        "🎴 <b>FLASHCARD NATIJASI</b>\n"
        f"{divider}\n\n"
        f"🇬🇧 <b>{en_word}</b>\n"
        f"🇺🇿 <b>{uz_word}</b>\n\n"
        "<i>To'g'ri eslay oldingizmi?</i>"
    )
    await call.message.edit_text(text, reply_markup=get_flashcard_answer_keyboard(), parse_mode="HTML")
    await call.answer()

@router.callback_query(F.data == "flash_known")
async def cb_flash_known(call: CallbackQuery):
    user_id = call.from_user.id
    session = get_current_session(user_id)
    if session and not session["is_answered"]:
        record_answer(user_id, session["current_en"], is_correct=True)
        mark_session_answered(user_id)
    await send_next_question(call, user_id, only_mistakes=False, edit=True)
    await call.answer("✅ Yodda qoldi!")

@router.callback_query(F.data == "flash_unknown")
async def cb_flash_unknown(call: CallbackQuery):
    user_id = call.from_user.id
    session = get_current_session(user_id)
    if session and not session["is_answered"]:
        record_answer(user_id, session["current_en"], is_correct=False)
        mark_session_answered(user_id)
    await send_next_question(call, user_id, only_mistakes=False, edit=True)
    await call.answer("❌ Qaytadan takrorlanadi")

# ==================== YOZMA REJIM ====================
@router.callback_query(F.data == "written_reveal")
async def cb_written_reveal(call: CallbackQuery):
    user_id = call.from_user.id
    session = get_current_session(user_id)
    if not session:
        await cb_next_question(call)
        return

    en_word = session["current_en"]
    uz_word = session["current_uz"]
    record_answer(user_id, en_word, is_correct=False)
    mark_session_answered(user_id)
    divider = "───────────────────────"

    text = (
        "💡 <b>TO'G'RI JAVOB:</b>\n"
        f"{divider}\n\n"
        f"🇬🇧 <b>{en_word}</b>  ➔  🇺🇿 <b>{uz_word}</b>\n\n"
        "<i>(Ushbu so'z mustahkamlash uchun yana takrorlanadi)</i>"
    )
    await call.message.edit_text(text, reply_markup=get_quiz_next_keyboard(), parse_mode="HTML")
    await call.answer()

@router.message(F.text & ~F.text.startswith("/"))
async def handle_written_message(message: Message):
    user_id = message.from_user.id
    settings = get_user_settings(user_id)
    
    if settings.get("mode") != "written":
        return

    session = get_current_session(user_id)
    if not session or session["is_answered"]:
        return

    direction = session["current_direction"]
    en_word = session["current_en"]
    uz_word = session["current_uz"]

    target_word = uz_word if direction == "en_uz" else en_word
    user_input = message.text.strip()

    is_correct = check_written_answer(user_input, target_word)
    record_answer(user_id, en_word, is_correct)
    mark_session_answered(user_id)
    divider = "───────────────────────"

    if is_correct:
        text = (
            "✅ <b>BARAKALLA! TO'G'RI YOZDINGIZ!</b>\n"
            f"{divider}\n\n"
            f"🇬🇧 <b>{en_word}</b>  ➔  🇺🇿 <b>{uz_word}</b>"
        )
    else:
        text = (
            "❌ <b>XATO YOZILDI!</b>\n"
            f"{divider}\n\n"
            f"Siz yozdingiz: <s>{user_input}</s>\n\n"
            "To'g'ri javob:\n"
            f"✅ 🇬🇧 <b>{en_word}</b>  ➔  🇺🇿 <b>{uz_word}</b>"
        )

    await message.answer(text, reply_markup=get_quiz_next_keyboard(), parse_mode="HTML")
