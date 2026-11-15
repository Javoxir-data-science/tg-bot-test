# -*- coding: utf-8 -*-
import sqlite3
import json
import os
from datetime import datetime
from typing import Optional, Dict, Any, List

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "bot_data.db")

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    
    # Foydalanuvchi sozlamalari
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS user_settings (
        user_id INTEGER PRIMARY KEY,
        page INTEGER DEFAULT 1,
        direction TEXT DEFAULT 'en_uz',
        mode TEXT DEFAULT 'quiz'
    )
    """)
    
    # Har bir so'z bo'yicha yodlash statistikasi
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS user_progress (
        user_id INTEGER,
        word_en TEXT,
        correct_count INTEGER DEFAULT 0,
        incorrect_count INTEGER DEFAULT 0,
        last_reviewed TEXT,
        PRIMARY KEY (user_id, word_en)
    )
    """)
    
    # Joriy savol holati
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS user_current_session (
        user_id INTEGER PRIMARY KEY,
        current_en TEXT,
        current_uz TEXT,
        current_direction TEXT,
        options_json TEXT,
        correct_index INTEGER,
        is_answered INTEGER DEFAULT 0
    )
    """)
    
    conn.commit()
    conn.close()

def get_user_settings(user_id: int) -> Dict[str, Any]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM user_settings WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()
    if not row:
        cursor.execute(
            "INSERT INTO user_settings (user_id, page, direction, mode) VALUES (?, 1, 'en_uz', 'quiz')",
            (user_id,)
        )
        conn.commit()
        cursor.execute("SELECT * FROM user_settings WHERE user_id = ?", (user_id,))
        row = cursor.fetchone()
    
    settings = dict(row)
    conn.close()
    return settings

def update_user_setting(user_id: int, key: str, value: Any):
    allowed_keys = {"page", "direction", "mode"}
    if key not in allowed_keys:
        return
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT user_id FROM user_settings WHERE user_id = ?", (user_id,))
    if cursor.fetchone():
        cursor.execute(f"UPDATE user_settings SET {key} = ? WHERE user_id = ?", (value, user_id))
    else:
        defaults = {"page": 1, "direction": "en_uz", "mode": "quiz"}
        defaults[key] = value
        cursor.execute(
            "INSERT INTO user_settings (user_id, page, direction, mode) VALUES (?, ?, ?, ?)",
            (user_id, defaults["page"], defaults["direction"], defaults["mode"])
        )
    conn.commit()
    conn.close()

def record_answer(user_id: int, word_en: str, is_correct: bool):
    conn = get_connection()
    cursor = conn.cursor()
    now_str = datetime.now().isoformat()
    cursor.execute("SELECT correct_count, incorrect_count FROM user_progress WHERE user_id = ? AND word_en = ?", (user_id, word_en))
    row = cursor.fetchone()
    if row:
        c = row["correct_count"] + (1 if is_correct else 0)
        i = row["incorrect_count"] + (0 if is_correct else 1)
        cursor.execute(
            "UPDATE user_progress SET correct_count = ?, incorrect_count = ?, last_reviewed = ? WHERE user_id = ? AND word_en = ?",
            (c, i, now_str, user_id, word_en)
        )
    else:
        c = 1 if is_correct else 0
        i = 0 if is_correct else 1
        cursor.execute(
            "INSERT INTO user_progress (user_id, word_en, correct_count, incorrect_count, last_reviewed) VALUES (?, ?, ?, ?, ?)",
            (user_id, word_en, c, i, now_str)
        )
    conn.commit()
    conn.close()

def get_user_stats(user_id: int, word_list: List[Dict[str, str]]) -> Dict[str, int]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT word_en, correct_count, incorrect_count FROM user_progress WHERE user_id = ?", (user_id,))
    rows = cursor.fetchall()
    conn.close()
    
    prog_dict = {r["word_en"]: r for r in rows}
    total = len(word_list)
    mastered = 0
    struggling = 0
    not_started = 0
    
    for w in word_list:
        en = w["en"]
        if en in prog_dict:
            c = prog_dict[en]["correct_count"]
            i = prog_dict[en]["incorrect_count"]
            if c >= 2 and i == 0:
                mastered += 1
            elif i > 0:
                struggling += 1
            elif c > 0:
                mastered += 1
            else:
                not_started += 1
        else:
            not_started += 1
            
    return {
        "total": total,
        "mastered": mastered,
        "struggling": struggling,
        "not_started": not_started
    }

def get_struggling_words(user_id: int, word_list: List[Dict[str, str]]) -> List[Dict[str, str]]:
    """Foydalanuvchi xato qilgan yoki qiynalayotgan so'zlar ro'yxati"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT word_en FROM user_progress WHERE user_id = ? AND incorrect_count > 0", (user_id,))
    rows = cursor.fetchall()
    conn.close()
    
    struggling_set = {r["word_en"] for r in rows}
    return [w for w in word_list if w["en"] in struggling_set]

def reset_user_page_progress(user_id: int, word_list: List[Dict[str, str]]):
    conn = get_connection()
    cursor = conn.cursor()
    for w in word_list:
        cursor.execute("DELETE FROM user_progress WHERE user_id = ? AND word_en = ?", (user_id, w["en"]))
    conn.commit()
    conn.close()

def save_current_session(user_id: int, current_en: str, current_uz: str, current_dir: str, options: List[str] = None, correct_idx: int = -1):
    conn = get_connection()
    cursor = conn.cursor()
    options_json = json.dumps(options or [], ensure_ascii=False)
    cursor.execute("""
    INSERT INTO user_current_session (user_id, current_en, current_uz, current_direction, options_json, correct_index, is_answered)
    VALUES (?, ?, ?, ?, ?, ?, 0)
    ON CONFLICT(user_id) DO UPDATE SET
        current_en = excluded.current_en,
        current_uz = excluded.current_uz,
        current_direction = excluded.current_direction,
        options_json = excluded.options_json,
        correct_index = excluded.correct_index,
        is_answered = 0
    """, (user_id, current_en, current_uz, current_dir, options_json, correct_idx))
    conn.commit()
    conn.close()

def get_current_session(user_id: int) -> Optional[Dict[str, Any]]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM user_current_session WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()
    conn.close()
    if not row:
        return None
    res = dict(row)
    res["options"] = json.loads(res["options_json"]) if res["options_json"] else []
    return res

def mark_session_answered(user_id: int):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE user_current_session SET is_answered = 1 WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()
