import pytest
from unittest.mock import AsyncMock, MagicMock
from bot import rate_limiter
from bot.rate_limiter import rate_limit


@pytest.fixture(autouse=True)
def clear_requests():
    """Очищаем счётчики между тестами."""
    rate_limiter._user_requests.clear()
    yield
    rate_limiter._user_requests.clear()


def make_update(user_id=1, has_callback=False, has_message=True):
    """Создаёт мок Update."""
    update = MagicMock()
    update.effective_user.id = user_id

    if has_callback:
        update.callback_query = MagicMock()
        update.callback_query.answer = AsyncMock()
        update.message = None
    else:
        update.callback_query = None
        if has_message:
            update.message = MagicMock()
            update.message.reply_text = AsyncMock()
        else:
            update.message = None

    return update


class TestRateLimit:
    async def test_first_request_passes(self):
        called = False

        @rate_limit
        async def handler(update, context):
            nonlocal called
            called = True

        await handler(make_update(), None)
        assert called is True

    async def test_under_limit_passes(self):
        count = 0

        @rate_limit
        async def handler(update, context):
            nonlocal count
            count += 1

        update = make_update()
        for _ in range(rate_limiter.MAX_REQUESTS):
            await handler(update, None)

        assert count == rate_limiter.MAX_REQUESTS

    async def test_over_limit_blocked(self):
        count = 0

        @rate_limit
        async def handler(update, context):
            nonlocal count
            count += 1

        update = make_update()
        for _ in range(rate_limiter.MAX_REQUESTS + 5):
            await handler(update, None)

        assert count == rate_limiter.MAX_REQUESTS

    async def test_different_users_independent(self):
        """Лимит считается отдельно для каждого пользователя."""
        count = 0

        @rate_limit
        async def handler(update, context):
            nonlocal count
            count += 1

        # User 1 исчерпывает лимит
        update1 = make_update(user_id=1)
        for _ in range(rate_limiter.MAX_REQUESTS + 10):
            await handler(update1, None)

        # User 2 всё ещё может
        update2 = make_update(user_id=2)
        before = count
        await handler(update2, None)
        assert count == before + 1

    async def test_callback_query_notification(self):
        @rate_limit
        async def handler(update, context):
            pass

        update = make_update(has_callback=True)
        # Заполняем лимит
        for _ in range(rate_limiter.MAX_REQUESTS):
            await handler(update, None)

        # Следующий должен получить уведомление
        await handler(update, None)
        update.callback_query.answer.assert_called()

    async def test_message_notification(self):
        @rate_limit
        async def handler(update, context):
            pass

        update = make_update()
        for _ in range(rate_limiter.MAX_REQUESTS):
            await handler(update, None)

        await handler(update, None)
        update.message.reply_text.assert_called()
