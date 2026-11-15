# 📚 Vocabulary Mastery Bot (Aiogram 3)

Telegram orqali ingliz tili so'zlarini bosqichma-bosqich va mukammal yodlash uchun mo'ljallangan zamonaviy bot. 

Bot PDF hujjatidagi barcha **532 ta so'zni** o'z ichiga oladi va ularni **6 ta sahifaga** ajratgan holda yodlatadi.

---

## 🌟 Botning asosiy imkoniyatlari

1. **📄 Sahifalar bo'yicha mustaqil o'rganish:**
   - Har bir sahifa uchun alohida inline tugmalar mavjud:
     - `1-sahifa` (94 ta so'z)
     - `2-sahifa` (90 ta so'z)
     - `3-sahifa` (90 ta so'z)
     - `4-sahifa` (92 ta so'z)
     - `5-sahifa` (92 ta so'z)
     - `6-sahifa` (74 ta so'z)
     - `📚 Barcha sahifalar` (532 ta so'z jamlanmasi)
   - Siz qaysi sahifani tanlasangiz, mashg'ulotlar **faqat shu sahifa** bo'yicha ketadi.

2. **🔄 3 xil o'rganish yo'nalishi:**
   - 🇬🇧 **Inglizcha ➡️ O'zbekcha:** Inglizcha so'z beriladi, uning o'zbekcha ma'nosini topasiz.
   - 🇺🇿 **O'zbekcha ➡️ Inglizcha:** O'zbekcha ma'no beriladi, uning inglizcha variantini topasiz.
   - 🔀 **Aralash (Mix):** Ikkala yo'nalish navbatma-navbat tasodifiy tarzda almashib keladi.

3. **🎮 3 xil mashq rejimi (mukammal yodlash uchun):**
   - 🎯 **Test rejimi:** 4 ta variant beriladi, bitta to'g'ri variantni tanlaysiz.
   - 🎴 **Flashcard (Karta rejimi):** So'z chiqadi, tarjimasini xotirangizda eslaysiz, `👁 Tarjimani ko'rish` tugmasini bosib tekshirasiz va `✅ Yodda qoldi` yoki `❌ Bilmadim` tugmalari orqali baholaysiz.
   - ✍️ **Yozma test:** So'z chiqadi, uning tarjimasini chatga o'zingiz yozasiz. Bot sinonimlar va matn xususiyatlarini inobatga olgan holda tekshiradi.

4. **🧠 Spaced Repetition (Xatolar ustida ishlash):**
   - Bot har bir foydalanuvchining to'g'ri va noto'g'ri javoblarini SQLite bazasida saqlab boradi.
   - Xato qilingan so'zlar mashg'ulot davomida avtomatik ravishda qayta-qayta beriladi.
   - Istalgan vaqtda `🔁 Xatolar ustida ishlash` tugmasi orqali faqat qiynalgan so'zlarni alohida takrorlash mumkin.

---

## 📁 Loyiha tuzilishi

```text
tg-bot-test/
├── data/
│   └── words.py          # 6 ta sahifadagi barcha 532 ta so'z va tarjimalar
├── database/
│   └── db.py             # SQLite bazasi (sozlamalar va progress)
├── keyboards/
│   └── inline.py         # Sahifa, yo'nalish va rejim tugmalari
├── handlers/
│   ├── start.py          # /start, /help, /stats komandalari
│   ├── settings.py       # Sahifa va rejim o'zgartirish
│   └── training.py       # Test, Flashcard va Yozma mashg'ulotlar
├── services/
│   └── training.py       # Savol tayyorlash va javoblarni tekshirish
├── config.py             # Bot token va konfiguratsiya
├── main.py               # Botni ishga tushiruvchi asosiy fayl
├── requirements.txt      # Kutubxonalar ro'yxati
├── Dockerfile            # Docker orqali serverda ishga tushirish uchun
├── Procfile              # Lunafy / PaaS serverlar uchun
├── .env.example          # Token namunasi
└── README.md             # Qo'llanma
```

---

## 🚀 Kompyuterda ishga tushirish

1. Telegramda [@BotFather](https://t.me/BotFather) orqali yangi bot oching va **API Token** oling.
2. Loyiha papkasida `.env` faylini yarating va tokenni kiriting:
   ```bash
   cp .env.example .env
   ```
   `.env` fayli ichiga tokeningizni yozing:
   ```env
   BOT_TOKEN=123456789:AAFgEXAMPLE...
   ```
3. Virtual muhit (venv) yaratib, kerakli kutubxonalarni o'rnating:
   ```bash
   python3 -m venv venv
   source venv/bin/activate   # Windowsda: venv\Scripts\activate
   pip install -r requirements.txt
   ```
4. Botni ishga tushiring:
   ```bash
   python main.py
   ```

---

## 🌐 Lunafy serveriga yuklash (Deploy qilish)

Lunafy platformasida botni yuklash juda oson:

### 1-usul: GitHub orqali Lunafy ga yuklash (Tavsiya etiladi)
1. Ushbu loyihani o'zingizning **GitHub** hisobingizga yuklang (push qiling).
2. [Lunafy](https://lunafy.net) paneliga kiring va yangi loyiha (New App/Service) yarating.
3. GitHub reponi tanlang.
4. **Environment Variables** (Muhit o'zgaruvchilari) bo'limida:
   - Kalit: `BOT_TOKEN`
   - Qiymat: `@BotFather` dan olgan tokeningizni yozing.
5. Loyiha avtomatik ravishda `Dockerfile` yoki `requirements.txt` va `Procfile` orqali tanib olinadi va `python main.py` buyrug'i bilan 24/7 rejimda ishga tushadi.

### 2-usul: Lunafy / Docker orqali
Loyiha ichida `Dockerfile` tayyorlangan. Lunafy Docker build orqali bir tugma bilan konteynerni ishga tushiradi.
Faqatgina `BOT_TOKEN` o'zgaruvchisini sozlamalar bo'limida kiritib qo'ysangiz kifoya.
