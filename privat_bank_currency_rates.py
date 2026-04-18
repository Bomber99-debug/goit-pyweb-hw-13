import platform
import asyncio
from typing import Any

import aiohttp
from aiohttp import ClientError, ClientConnectorError
import argparse
from argparse import Namespace
from datetime import timedelta, datetime, date
import json

DEFAULT_CURRENCIES: list[str] = ["EUR", "USD"]


async def fetch_exchange_rates(
        session: aiohttp.ClientSession, url: str
) -> dict[str, str] | Any:
    """Повертає JSON-відповідь API або словник з повідомленням про помилку."""
    async with session.get(url) as response:
        try:
            if response.status == 200:
                return await response.json()
        except ClientConnectorError as e:
            return {f"Помилка підключення до {url}: {e}"}
        except asyncio.TimeoutError:
            return {f"Тайм-аут запиту до {url}"}
        except ClientError as e:
            return {f"Помилка aiohttp: {e}"}
        except Exception as e:
            return {f"Непередбачена помилка: {e}"}
        return {"error": "Не вдалося отримати курс валют. Спробуйте пізніше."}


def build_date_string(days_ago: int) -> str:
    """Формує дату у форматі dd.mm.YYYY на вказану кількість днів назад."""
    current_date: date = datetime.now().date()
    delta: timedelta = timedelta(days=days_ago)
    return (current_date - delta).strftime("%d.%m.%Y")


def generate_urls(days_count: int):
    """Генерує URL-адреси для запиту курсів валют за потрібну кількість днів."""
    for day_offset in range(days_count + 1):
        date_string: str = build_date_string(day_offset)
        yield f"https://api.privatbank.ua/p24api/exchange_rates?date={date_string}"


def format_result(
        response_data: dict[str, object],
) -> dict[str, dict[str, float | int | str]] | dict[str, str]:
    """Форматує відповідь API у зручний для виводу вигляд."""
    formatted_rates: dict[str, dict[str, float | int | str]] = {}

    if "date" not in response_data:
        return response_data
    if not isinstance(response_data["date"], str):
        return response_data

    response_date: str = response_data["date"]

    # Якщо курсів немає або структура відповіді некоректна,
    # повертаємо дату з порожнім значенням.
    if "exchangeRate" not in response_data:
        return {response_date: ""}
    if not isinstance(response_data["exchangeRate"], list):
        return {response_date: ""}
    if not response_data["exchangeRate"]:
        return {response_date: ""}

    for rate_data in response_data["exchangeRate"]:
        sale_rate: float | int | str = ""
        purchase_rate: float | int | str = ""

        if not isinstance(rate_data, dict):
            continue

        if "currency" in rate_data:
            if rate_data["currency"] in DEFAULT_CURRENCIES:
                if "saleRateNB" in rate_data:
                    if isinstance(rate_data["saleRateNB"], float) or isinstance(
                            rate_data["saleRateNB"], int
                    ):
                        sale_rate = rate_data["saleRateNB"]

                if "purchaseRateNB" in rate_data:
                    if isinstance(rate_data["purchaseRateNB"], float) or isinstance(
                            rate_data["purchaseRateNB"], int
                    ):
                        purchase_rate = rate_data["purchaseRateNB"]

                formatted_rates[rate_data["currency"]] = {
                    "sale": sale_rate,
                    "purchase": purchase_rate,
                }

    return {response_date: formatted_rates}


def add_valid_currency(currency: str) -> None:
    """Додає валюту до списку для відображення."""
    if currency.isdigit():
        raise ValueError(f'"{currency}" не є коректним кодом валюти.')

    DEFAULT_CURRENCIES.append(currency.upper())


def parse_args() -> Namespace:
    """Зчитує аргументи командного рядка."""
    parser = argparse.ArgumentParser(
        prog="exchange_rates",
        description="Отримує курс валют із PrivatBank."
    )

    parser.add_argument(
        "days_count",
        type=int,
        nargs="?",
        choices=(0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10),
        default=0,
        help="Кількість днів, за які потрібно отримати курс валют."
    )

    parser.add_argument(
        "-c",
        "--currencies",
        type=add_valid_currency,
        nargs="*",
        help=(
            "Коди валют, які потрібно додати для відображення.\n"
            "Доступні приклади:\n"
            "USD - долар США (за замовчуванням);\n"
            "EUR - євро (за замовчуванням);\n"
            "CHF - швейцарський франк;\n"
            "GBP - британський фунт;\n"
            "PLN - польський злотий;\n"
            "SEK - шведська крона;\n"
            "XAU - золото;\n"
            "CAD - канадський долар."
        ),
    )

    return parser.parse_args()


async def main(days_count: int) -> list[dict[str, object]]:
    """Отримує й форматує курси валют за вказану кількість днів."""
    urls = generate_urls(days_count)

    async with aiohttp.ClientSession() as session:
        request_coroutines = [
            fetch_exchange_rates(session, url) for url in urls
        ]
        responses = await asyncio.gather(*request_coroutines)

    results: list[dict[str, object]] = [
        format_result(response) for response in responses
    ]
    return results


if __name__ == "__main__":
    # Для Windows встановлюємо сумісну policy для asyncio.
    if platform.system() == "Windows":
        asyncio.set_event_loop_policy(
            asyncio.WindowsProactorEventLoopPolicy()
        )

    days_count: int = parse_args().days_count
    result: list[dict[str, object]] = asyncio.run(main(days_count))
    print(json.dumps(result, indent=4, ensure_ascii=False))
