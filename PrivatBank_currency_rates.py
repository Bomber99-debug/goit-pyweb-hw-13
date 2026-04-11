import platform
import asyncio
import aiohttp
from datetime import timedelta, datetime, date
from sys import argv
import json


async def fetch_exchange_rates(
    session: aiohttp.ClientSession, url: str
) -> dict[str, object] | None:
    """Повертає JSON-відповідь API або None, якщо сервер повернув не 200."""
    async with session.get(url) as response:
        if response.status == 200:
            return await response.json()
        return None


def build_date_string(days_ago: int) -> str:
    """Повертає дату у форматі dd.mm.YYYY на вказану кількість днів назад."""
    current_date: date = datetime.now().date()
    delta: timedelta = timedelta(days=days_ago)
    return (current_date - delta).strftime("%d.%m.%Y")


def parse_days_argument() -> int:
    """Зчитує кількість днів з командного рядка та перевіряє допустимий діапазон."""
    try:
        raw_days: str = argv[1]
    except IndexError:
        return 0

    if not raw_days.isdigit():
        raise ValueError("Кількість днів повинна бути цілим невід’ємним числом.")

    days_count: int = int(raw_days)
    if days_count < 0 or days_count > 10:
        raise ValueError("Кількість днів повинна бути в межах від 0 до 10.")

    return days_count


async def main(date_string: str) -> dict[str, object] | None:
    """Формує URL запиту та отримує курс валют за вказану дату."""
    url: str = (
        f"https://api.privatbank.ua/p24api/exchange_rates?date={date_string}"
    )
    async with aiohttp.ClientSession() as session:
        return await fetch_exchange_rates(session, url)


if __name__ == "__main__":
    # Для Windows встановлюємо сумісну policy для asyncio.
    if platform.system() == "Windows":
        asyncio.set_event_loop_policy(
            asyncio.WindowsProactorEventLoopPolicy()
        )

    days_count: int = parse_days_argument()
    date_string: str = build_date_string(days_count)
    result: dict[str, object] | None = asyncio.run(main(date_string))
    print(json.dumps(result, indent=4, ensure_ascii=False))