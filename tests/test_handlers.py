import pytest
from bot.handlers import escape_markdown, determine_level_from_session


class TestEscapeMarkdown:
    def test_underscore(self):
        assert escape_markdown("She ___ a student.") == "She \\_\\_\\_ a student."

    def test_asterisk(self):
        assert escape_markdown("2*2=4") == "2\\*2=4"

    def test_backtick(self):
        assert escape_markdown("`code`") == "\\`code\\`"

    def test_square_bracket(self):
        assert escape_markdown("[link]") == "\\[link]"

    def test_no_special_chars(self):
        assert escape_markdown("Hello world") == "Hello world"

    def test_empty_string(self):
        assert escape_markdown("") == ""

    def test_multiple_specials(self):
        result = escape_markdown("_*`[")
        assert result == "\\_\\*\\`\\["


class TestDetermineLevel:
    def _make_session(self, score, total, level_results):
        return {
            "score": score,
            "asked_questions": list(range(total)),
            "level_results": level_results,
        }

    def test_empty_session_returns_a1(self):
        session = self._make_session(0, 0, {})
        assert determine_level_from_session(session) == "A1"

    def test_very_low_percentage_is_a1(self):
        """10% → A1."""
        session = self._make_session(3, 30, {
            "A1": {"correct": 3, "total": 5},
        })
        assert determine_level_from_session(session) == "A1"

    def test_40_percent_is_a2(self):
        session = self._make_session(12, 30, {
            "A1": {"correct": 4, "total": 5},
            "A2": {"correct": 3, "total": 5},
        })
        assert determine_level_from_session(session) == "A2"

    def test_57_percent_is_b1(self):
        """Реальный кейс юзера: 17/30 = 57% → B1."""
        session = self._make_session(17, 30, {
            "A1": {"correct": 1, "total": 5},
            "A2": {"correct": 4, "total": 5},
            "B1": {"correct": 2, "total": 5},
            "B2": {"correct": 2, "total": 5},
            "C1": {"correct": 5, "total": 5},
            "C2": {"correct": 3, "total": 5},
        })
        assert determine_level_from_session(session) == "B1"

    def test_70_percent_is_b2(self):
        session = self._make_session(21, 30, {
            "B2": {"correct": 3, "total": 5},
        })
        assert determine_level_from_session(session) == "B2"

    def test_80_percent_is_c1(self):
        session = self._make_session(24, 30, {
            "C1": {"correct": 4, "total": 5},
        })
        assert determine_level_from_session(session) == "C1"

    def test_95_percent_is_c2(self):
        session = self._make_session(29, 30, {
            "C2": {"correct": 5, "total": 5},
        })
        assert determine_level_from_session(session) == "C2"

    def test_downgrade_when_base_level_fails(self):
        """60% общий → B2, но B2 = 1/5 (20%) → должно упасть до B1."""
        session = self._make_session(18, 30, {
            "B2": {"correct": 1, "total": 5},
        })
        assert determine_level_from_session(session) == "B1"

    def test_no_downgrade_when_base_level_ok(self):
        """60% общий → B2, B2 = 2/5 (40%) — не падаем (порог 40%)."""
        session = self._make_session(18, 30, {
            "B2": {"correct": 2, "total": 5},
        })
        assert determine_level_from_session(session) == "B2"

    def test_a1_cannot_go_below(self):
        """A1 — минимальный уровень."""
        session = self._make_session(0, 30, {
            "A1": {"correct": 0, "total": 5},
        })
        assert determine_level_from_session(session) == "A1"
