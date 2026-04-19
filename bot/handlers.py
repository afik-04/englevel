import logging
import time
from telegram import Update
from telegram.ext import ContextTypes
from bot.keyboards import get_main_keyboard, get_question_keyboard
from bot.database import save_result, get_user_results, get_user_best
from bot.rate_limiter import rate_limit
from questions import QUESTIONS, LEVEL_ORDER, get_questions_by_level

logger = logging.getLogger(__name__)

user_sessions = {}


def escape_markdown(text):
    """Экранирует спецсимволы Markdown в тексте вопросов."""
    for char in ['_', '*', '`', '[']:
        text = text.replace(char, '\\' + char)
    return text


def determine_level_from_session(session):
    """Определяет уровень по общему проценту + проверка провалов на промежуточных уровнях."""
    level_results = session.get("level_results", {})
    score = session["score"]
    total = len(session["asked_questions"])

    if total == 0:
        return "A1"

    percentage = (score / total) * 100

    # Базовый уровень по общему проценту
    if percentage < 30:
        base_level = "A1"
    elif percentage < 45:
        base_level = "A2"
    elif percentage < 60:
        base_level = "B1"
    elif percentage < 75:
        base_level = "B2"
    elif percentage < 90:
        base_level = "C1"
    else:
        base_level = "C2"

    # Корректировка: понижаем на 1 только если на базовом уровне реальный провал (<40%)
    base_idx = LEVEL_ORDER.index(base_level)
    if base_level in level_results:
        lr = level_results[base_level]
        if lr["total"] > 0:
            pct = (lr["correct"] / lr["total"]) * 100
            if pct < 40:
                base_idx = max(0, base_idx - 1)

    return LEVEL_ORDER[base_idx]


# --- Таймер ---
TEST_TIME_LIMIT = 1200  # 20 минут в секундах


@rate_limit
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🌟 *Welcome to English Level Test Bot!* 🌟\n\n"
        "Я помогу определить твой уровень английского.\n\n"
        "📝 /test — начать тест\n"
        "📊 /result — посмотреть результаты\n"
        "❓ /help — помощь",
        reply_markup=get_main_keyboard(),
        parse_mode="Markdown"
    )


@rate_limit
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "❓ *Как работает бот:*\n\n"
        "1. Нажми /test чтобы начать тест\n"
        "2. Тест состоит из *30 вопросов*\n"
        "3. Вопросы идут по порядку: A1 → A2 → B1 → B2 → C1 → C2\n"
        "4. На тест даётся *20 минут*\n"
        "5. После теста получишь подробный разбор по категориям\n\n"
        "*Уровни:*\n"
        "🟢 A1 — Beginner (Начинающий)\n"
        "🟡 A2 — Elementary (Элементарный)\n"
        "🔵 B1 — Intermediate (Средний)\n"
        "🟣 B2 — Upper Intermediate (Выше среднего)\n"
        "🟠 C1 — Advanced (Продвинутый)\n"
        "🔴 C2 — Proficiency (Владение в совершенстве)\n\n"
        "*Категории вопросов:*\n"
        "📗 Grammar — грамматика\n"
        "📘 Vocabulary — словарный запас\n"
        "📙 Reading — понимание текста",
        parse_mode="Markdown"
    )


@rate_limit
async def result_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    results = get_user_results(user_id, limit=5)

    if not results:
        await update.message.reply_text(
            "📊 У тебя пока нет результатов.\nНажми /test чтобы пройти тест!",
            parse_mode="Markdown"
        )
        return

    best = get_user_best(user_id)

    text = "📊 *Твои последние результаты:*\n\n"
    for i, r in enumerate(results, 1):
        date = r["created_at"][:10]
        duration = r["duration_seconds"]
        mins = duration // 60 if duration else 0
        secs = duration % 60 if duration else 0
        text += (
            f"*{i}.* {date} — *{r['score']}/{r['total']}* "
            f"({r['percentage']:.0f}%) — *{r['level']}*"
            f" — {mins}м {secs}с\n"
        )

    text += (
        f"\n🏆 *Лучший результат:* {best['score']}/{best['total']} "
        f"({best['percentage']:.0f}%) — *{best['level']}*"
    )

    await update.message.reply_text(text, parse_mode="Markdown")


@rate_limit
async def start_test(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    # Все 30 вопросов по порядку: A1 → A2 → B1 → B2 → C1 → C2
    all_questions = []
    for level in LEVEL_ORDER:
        all_questions.extend(get_questions_by_level(level))

    user_sessions[user_id] = {
        "current_question": 0,
        "score": 0,
        "answers": [],
        "asked_questions": [],
        "question_queue": all_questions,
        "level_results": {},
        "category_results": {"grammar": {"correct": 0, "total": 0},
                             "vocabulary": {"correct": 0, "total": 0},
                             "reading": {"correct": 0, "total": 0}},
        "start_time": time.time(),
    }

    await send_question(update, context, user_id)


async def send_question(update: Update, context: ContextTypes.DEFAULT_TYPE, user_id):
    session = user_sessions[user_id]

    # Проверка таймера
    elapsed = time.time() - session["start_time"]
    if elapsed >= TEST_TIME_LIMIT:
        await finish_test(update, context, user_id, timeout=True)
        return

    # Если вопросы закончились — завершаем тест
    if not session["question_queue"]:
        await finish_test(update, context, user_id)
        return

    question = session["question_queue"][0]
    q_num = len(session["asked_questions"]) + 1
    total_questions = q_num + len(session["question_queue"]) - 1

    # Оставшееся время
    remaining = int(TEST_TIME_LIMIT - elapsed)
    mins = remaining // 60
    secs = remaining % 60

    q_text = escape_markdown(question['text'])
    text = (
        f"📝 *Вопрос {q_num}/{total_questions}* "
        f"(уровень {question['level']}, {question['category']})\n"
        f"⏱ Осталось: {mins}:{secs:02d}\n\n"
        f"{q_text}"
    )
    keyboard = get_question_keyboard(question['options'])

    if update.callback_query:
        await update.callback_query.edit_message_text(
            text, reply_markup=keyboard, parse_mode="Markdown"
        )
    else:
        await update.message.reply_text(
            text, reply_markup=keyboard, parse_mode="Markdown"
        )


@rate_limit
async def handle_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = update.effective_user.id
    answer_index = int(query.data)

    if user_id not in user_sessions:
        await query.edit_message_text("Тест не активен. Нажми /test чтобы начать.")
        return

    session = user_sessions[user_id]

    # Проверка таймера
    elapsed = time.time() - session["start_time"]
    if elapsed >= TEST_TIME_LIMIT:
        await finish_test(update, context, user_id, timeout=True)
        return

    question = session["question_queue"].pop(0)
    is_correct = answer_index == question["correct"]

    if is_correct:
        session["score"] += 1

    # Сохраняем детали ответа
    session["answers"].append({
        "question": question,
        "user_answer": answer_index,
        "correct": is_correct
    })
    session["asked_questions"].append(question)

    # Обновляем статистику по уровню
    level = question["level"]
    if level not in session["level_results"]:
        session["level_results"][level] = {"correct": 0, "total": 0}
    session["level_results"][level]["total"] += 1
    if is_correct:
        session["level_results"][level]["correct"] += 1

    # Обновляем статистику по категории
    cat = question["category"]
    session["category_results"][cat]["total"] += 1
    if is_correct:
        session["category_results"][cat]["correct"] += 1

    await send_question(update, context, user_id)


async def finish_test(update: Update, context: ContextTypes.DEFAULT_TYPE,
                      user_id, timeout=False):
    session = user_sessions[user_id]
    score = session["score"]
    total = len(session["asked_questions"])

    if total == 0:
        del user_sessions[user_id]
        text = "❌ Тест завершён без ответов. Нажми /test чтобы попробовать снова."
        if update.callback_query:
            await update.callback_query.edit_message_text(text)
        else:
            await update.message.reply_text(text)
        return

    percentage = (score / total) * 100
    level = determine_level_from_session(session)

    duration = int(time.time() - session["start_time"])
    mins = duration // 60
    secs = duration % 60

    # Статистика по категориям
    cat_results = session["category_results"]
    cat_text = ""
    cat_icons = {"grammar": "📗", "vocabulary": "📘", "reading": "📙"}
    cat_names = {"grammar": "Грамматика", "vocabulary": "Словарный запас",
                 "reading": "Чтение"}
    for cat in ["grammar", "vocabulary", "reading"]:
        cr = cat_results[cat]
        if cr["total"] > 0:
            pct = (cr["correct"] / cr["total"]) * 100
            cat_text += (
                f"{cat_icons[cat]} {cat_names[cat]}: "
                f"*{cr['correct']}/{cr['total']}* ({pct:.0f}%)\n"
            )

    # Статистика по уровням
    level_text = ""
    level_results = session["level_results"]
    for lv in LEVEL_ORDER:
        if lv in level_results:
            lr = level_results[lv]
            pct = (lr["correct"] / lr["total"]) * 100
            emoji = "✅" if pct >= 50 else "❌"
            level_text += f"{emoji} {lv}: *{lr['correct']}/{lr['total']}*\n"

    # Разбор ошибок
    mistakes_text = ""
    mistakes = [a for a in session["answers"] if not a["correct"]]
    if mistakes:
        mistakes_text = "\n📕 *Разбор ошибок:*\n\n"
        for m in mistakes:
            q = m["question"]
            user_ans = escape_markdown(q["options"][m["user_answer"]])
            correct_ans = escape_markdown(q["options"][q["correct"]])
            q_escaped = escape_markdown(q['text'])
            mistakes_text += (
                f"❓ {q_escaped}\n"
                f"  Твой ответ: {user_ans}\n"
                f"  Правильно: *{correct_ans}*\n\n"
            )

    timeout_text = "\n⏰ *Время вышло!*\n" if timeout else ""

    result_text = (
        f"✅ *Тест завершён!*{timeout_text}\n\n"
        f"🎯 Результат: *{score}/{total}* ({percentage:.0f}%)\n"
        f"📊 Твой уровень: *{level}*\n"
        f"⏱ Время: {mins}м {secs}с\n\n"
        f"*По категориям:*\n{cat_text}\n"
        f"*По уровням:*\n{level_text}"
        f"{mistakes_text}"
        f"Нажми /test чтобы пройти снова."
    )

    # Сохраняем в БД
    username = update.effective_user.username or ""
    save_result(
        user_id=user_id,
        username=username,
        score=score,
        total=total,
        percentage=percentage,
        level=level,
        grammar_score=cat_results["grammar"]["correct"],
        vocabulary_score=cat_results["vocabulary"]["correct"],
        reading_score=cat_results["reading"]["correct"],
        grammar_total=cat_results["grammar"]["total"],
        vocabulary_total=cat_results["vocabulary"]["total"],
        reading_total=cat_results["reading"]["total"],
        duration_seconds=duration
    )

    del user_sessions[user_id]

    if update.callback_query:
        # Сообщение может быть слишком длинным для edit — отправляем новое
        await update.callback_query.message.reply_text(
            result_text, parse_mode="Markdown"
        )
    else:
        await update.message.reply_text(result_text, parse_mode="Markdown")
