class TestDatabase:
    def test_save_and_retrieve(self, temp_db):
        temp_db.save_result(
            user_id=123, username="test_user",
            score=20, total=30, percentage=66.7, level="B2",
            grammar_score=8, vocabulary_score=7, reading_score=5,
            grammar_total=12, vocabulary_total=12, reading_total=6,
            duration_seconds=600
        )

        results = temp_db.get_user_results(123)
        assert len(results) == 1
        assert results[0]["score"] == 20
        assert results[0]["level"] == "B2"
        assert results[0]["username"] == "test_user"

    def test_multiple_results_ordered_by_date(self, temp_db):
        for i in range(3):
            temp_db.save_result(
                user_id=1, username="u",
                score=i * 5, total=30, percentage=i * 16.7, level="A1",
                grammar_score=0, vocabulary_score=0, reading_score=0,
                grammar_total=0, vocabulary_total=0, reading_total=0,
                duration_seconds=60
            )

        results = temp_db.get_user_results(1, limit=10)
        assert len(results) == 3

    def test_limit(self, temp_db):
        for i in range(5):
            temp_db.save_result(
                user_id=1, username="u",
                score=i, total=30, percentage=i * 3.3, level="A1",
                grammar_score=0, vocabulary_score=0, reading_score=0,
                grammar_total=0, vocabulary_total=0, reading_total=0,
                duration_seconds=60
            )

        assert len(temp_db.get_user_results(1, limit=3)) == 3

    def test_get_best_returns_highest_percentage(self, temp_db):
        temp_db.save_result(
            user_id=1, username="u", score=10, total=30, percentage=33.3,
            level="A1", grammar_score=0, vocabulary_score=0, reading_score=0,
            grammar_total=0, vocabulary_total=0, reading_total=0,
            duration_seconds=60
        )
        temp_db.save_result(
            user_id=1, username="u", score=25, total=30, percentage=83.3,
            level="C1", grammar_score=0, vocabulary_score=0, reading_score=0,
            grammar_total=0, vocabulary_total=0, reading_total=0,
            duration_seconds=60
        )

        best = temp_db.get_user_best(1)
        assert best["score"] == 25
        assert best["level"] == "C1"

    def test_no_results_for_new_user(self, temp_db):
        assert temp_db.get_user_results(99999) == []
        assert temp_db.get_user_best(99999) is None

    def test_users_isolated(self, temp_db):
        """Результаты пользователей не пересекаются."""
        temp_db.save_result(
            user_id=1, username="a", score=10, total=30, percentage=33,
            level="A1", grammar_score=0, vocabulary_score=0, reading_score=0,
            grammar_total=0, vocabulary_total=0, reading_total=0,
            duration_seconds=60
        )
        temp_db.save_result(
            user_id=2, username="b", score=25, total=30, percentage=83,
            level="C1", grammar_score=0, vocabulary_score=0, reading_score=0,
            grammar_total=0, vocabulary_total=0, reading_total=0,
            duration_seconds=60
        )

        assert len(temp_db.get_user_results(1)) == 1
        assert len(temp_db.get_user_results(2)) == 1
        assert temp_db.get_user_results(1)[0]["score"] == 10
        assert temp_db.get_user_results(2)[0]["score"] == 25
