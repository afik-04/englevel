import time
import logging
from collections import defaultdict, deque
from functools import wraps

logger = logging.getLogger(__name__)

# Максимум N запросов за WINDOW секунд от одного пользователя
MAX_REQUESTS = 20
WINDOW = 60  # секунд

_user_requests = defaultdict(deque)


def rate_limit(func):
    """Декоратор для ограничения частоты запросов на пользователя."""
    @wraps(func)
    async def wrapper(update, context, *args, **kwargs):
        user = update.effective_user
        if not user:
            return await func(update, context, *args, **kwargs)

        user_id = user.id
        now = time.time()

        # Удаляем старые запросы
        requests = _user_requests[user_id]
        while requests and requests[0] < now - WINDOW:
            requests.popleft()

        if len(requests) >= MAX_REQUESTS:
            logger.warning(f"Rate limit exceeded for user {user_id}")
            if update.callback_query:
                await update.callback_query.answer(
                    "⏳ Слишком много запросов. Подожди немного.",
                    show_alert=True
                )
            elif update.message:
                await update.message.reply_text(
                    "⏳ Слишком много запросов. Подожди немного."
                )
            return

        requests.append(now)
        return await func(update, context, *args, **kwargs)

    return wrapper
