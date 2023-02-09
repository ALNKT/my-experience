from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.files import JSONStorage

from telegram_API.handlers.common import register_handlers_common, register_callbacks_common, other_message
from telegram_API.handlers.hotels import register_callbacks_hotels, register_handlers_search_hotels
from telegram_API.handlers.places import register_callbacks_places, register_handlers_search_places
from telegram_API.handlers.restaurants import register_handlers_search_restaurants

from settings import BotSettings, logger

bot_token = BotSettings().bot_token.get_secret_value()

logger.info('STARTING BOT'.center(85, '='))

storage = JSONStorage('JSONStorage.json')
bot = Bot(token=bot_token)
dp = Dispatcher(bot, storage=storage)

# регистрируем все обработчики в нужном порядке
register_handlers_common(dp)
register_callbacks_common(dp)
register_handlers_search_hotels(dp)
register_callbacks_hotels(dp)
register_handlers_search_places(dp)
register_callbacks_places(dp)
register_handlers_search_restaurants(dp)
dp.register_message_handler(other_message, state='*')  # в последнюю очередь регистрируем обработчик обычных сообщений
