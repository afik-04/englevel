from questions import (
    QUESTIONS, LEVEL_ORDER,
    get_questions_by_level, get_questions_by_category
)


class TestQuestionsData:
    def test_total_count(self):
        """Всего должно быть 30 вопросов."""
        assert len(QUESTIONS) == 30

    def test_all_levels_present(self):
        """По 5 вопросов на каждый уровень."""
        for level in LEVEL_ORDER:
            assert len(get_questions_by_level(level)) == 5

    def test_level_order(self):
        """Правильный порядок уровней."""
        assert LEVEL_ORDER == ["A1", "A2", "B1", "B2", "C1", "C2"]

    def test_all_categories_present(self):
        """Все 3 категории должны быть представлены."""
        for category in ["grammar", "vocabulary", "reading"]:
            assert len(get_questions_by_category(category)) > 0


class TestQuestionStructure:
    def test_required_fields(self):
        """Каждый вопрос должен иметь все обязательные поля."""
        required = {"text", "options", "correct", "level", "category"}
        for q in QUESTIONS:
            assert required.issubset(q.keys()), \
                f"Вопрос без нужных полей: {q}"

    def test_options_count(self):
        """4 варианта ответа в каждом вопросе."""
        for q in QUESTIONS:
            assert len(q["options"]) == 4, \
                f"Неверное количество вариантов: {q['text']}"

    def test_correct_index_valid(self):
        """Индекс правильного ответа в диапазоне 0-3."""
        for q in QUESTIONS:
            assert 0 <= q["correct"] <= 3, \
                f"Неверный индекс у: {q['text']}"

    def test_level_valid(self):
        """Уровень — один из допустимых."""
        for q in QUESTIONS:
            assert q["level"] in LEVEL_ORDER

    def test_category_valid(self):
        """Категория — одна из допустимых."""
        valid = {"grammar", "vocabulary", "reading"}
        for q in QUESTIONS:
            assert q["category"] in valid

    def test_no_duplicate_questions(self):
        """Нет одинаковых вопросов."""
        texts = [q["text"] for q in QUESTIONS]
        assert len(texts) == len(set(texts))

    def test_options_unique_within_question(self):
        """Варианты ответов внутри вопроса уникальны."""
        for q in QUESTIONS:
            assert len(q["options"]) == len(set(q["options"])), \
                f"Дубли в вариантах: {q['text']}"


class TestFilters:
    def test_get_by_level_returns_only_that_level(self):
        for level in LEVEL_ORDER:
            questions = get_questions_by_level(level)
            assert all(q["level"] == level for q in questions)

    def test_get_by_category_returns_only_that_category(self):
        for cat in ["grammar", "vocabulary", "reading"]:
            questions = get_questions_by_category(cat)
            assert all(q["category"] == cat for q in questions)

    def test_get_by_unknown_level(self):
        assert get_questions_by_level("Z9") == []

    def test_get_by_unknown_category(self):
        assert get_questions_by_category("music") == []
