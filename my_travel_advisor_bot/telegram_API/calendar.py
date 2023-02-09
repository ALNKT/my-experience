import calendar
from datetime import datetime, timedelta

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.callback_data import CallbackData
from aiogram.types import CallbackQuery


# setting callback_data prefix and parts
calendar_callback = CallbackData('simple_calendar', 'act', 'year', 'month', 'day')


class SimpleCalendar:

    @staticmethod
    async def start_calendar(year: int = datetime.now().year, month: int = datetime.now().month) -> InlineKeyboardMarkup:
        """
        Создает встроенную клавиатуру с предоставленными годом и месяцем
        :param int year: Год для использования в календаре, если его нет, используется текущий год.
        :param int month: Месяц для использования в календаре, если нет, используется текущий месяц.
        :return: Возвращает объект разметки клавиатуры в строке с календарем.
        """
        inline_kb = InlineKeyboardMarkup(row_width=7)
        ignore_callback = calendar_callback.new("IGNORE", year, month, 0)  # игнорируем кнопки без ответов
        # первая строка год
        inline_kb.row()
        inline_kb.insert(InlineKeyboardButton("<", callback_data=calendar_callback.new("PREV-YEAR", year, month, 1)))
        inline_kb.insert(InlineKeyboardButton(f"{str(year)}", callback_data=ignore_callback))
        inline_kb.insert(InlineKeyboardButton(">", callback_data=calendar_callback.new("NEXT-YEAR", year, month, 1)))
        ru_month = ['Январь', 'Февраль', 'Март', 'Апрель', 'Май', 'Июнь', 'Июль',
                    'Август', 'Сентябрь', 'Октябрь', 'Ноябрь', 'Декабрь']
        # вторая строка месяц
        inline_kb.row()
        inline_kb.insert(InlineKeyboardButton("<<", callback_data=calendar_callback.new("PREV-MONTH", year, month, 1)))
        inline_kb.insert(InlineKeyboardButton(f'{ru_month[month - 1]}', callback_data=ignore_callback))
        inline_kb.insert(InlineKeyboardButton(">>", callback_data=calendar_callback.new("NEXT-MONTH", year, month, 1)))
        # третья строка дни недели
        inline_kb.row()
        for day in ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]:
            inline_kb.insert(InlineKeyboardButton(day, callback_data=ignore_callback))

        # дни календаря (числа)
        month_calendar = calendar.monthcalendar(year, month)
        for week in month_calendar:
            inline_kb.row()
            for day in week:
                if day == 0:
                    inline_kb.insert(InlineKeyboardButton(" ", callback_data=ignore_callback))
                    continue
                # сравниваем выбранную дату с текущей
                elif datetime.strptime(f'{year}-{month}-{day}', '%Y-%m-%d') < \
                        datetime.strptime(datetime.now().strftime('%d-%m-%Y'), '%d-%m-%Y'):
                    inline_kb.insert(InlineKeyboardButton(" ", callback_data=ignore_callback))
                    continue
                inline_kb.insert(InlineKeyboardButton(
                    str(day), callback_data=calendar_callback.new("DAY", year, month, day)))

        return inline_kb

    async def process_selection(self, query: CallbackQuery, data: CallbackData) -> tuple:
        """
        Обработайте обратный вызов_query. Этот метод генерирует новый календарь, если пересылать или
        нажата кнопка назад. Этот метод должен вызываться внутри обработчика запроса обратного вызова
        :param query: предусмотрено обработчиком запроса обратного вызова
        :param data: callback_data, словарь, заданный calendar_callback
        :return: возвращает кортеж (логическое значение,datetime), указывающий, выбрана ли дата
        и возвращает дату, если это так.
        """
        return_data = (False, None)
        temp_date = datetime(int(data['year']), int(data['month']), 1)
        # для пустых кнопок действий нет
        if data['act'] == "IGNORE":
            await query.answer(cache_time=60)
        # user picked a day button, return date
        if data['act'] == "DAY":
            # await query.message.delete_reply_markup()   # removing inline keyboard
            await query.answer()
            return_data = True, datetime(int(data['year']), int(data['month']), int(data['day']))
        # user navigates to previous year, editing message with new calendar
        if data['act'] == "PREV-YEAR":
            prev_date = datetime(int(data['year']) - 1, int(data['month']), 1)
            await query.message.edit_reply_markup(await self.start_calendar(int(prev_date.year), int(prev_date.month)))
        # user navigates to next year, editing message with new calendar
        if data['act'] == "NEXT-YEAR":
            next_date = datetime(int(data['year']) + 1, int(data['month']), 1)
            await query.message.edit_reply_markup(await self.start_calendar(int(next_date.year), int(next_date.month)))
        # user navigates to previous month, editing message with new calendar
        if data['act'] == "PREV-MONTH":
            prev_date = temp_date - timedelta(days=1)
            await query.message.edit_reply_markup(await self.start_calendar(int(prev_date.year), int(prev_date.month)))
        # user navigates to next month, editing message with new calendar
        if data['act'] == "NEXT-MONTH":
            next_date = temp_date + timedelta(days=31)
            await query.message.edit_reply_markup(await self.start_calendar(int(next_date.year), int(next_date.month)))
        # at some point user clicks DAY button, returning date
        return return_data
