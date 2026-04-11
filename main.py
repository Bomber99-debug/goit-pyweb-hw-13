import asyncio
import logging
from datetime import timedelta, datetime, date

import httpx
import names
import websockets
from websockets import WebSocketServerProtocol
from websockets.exceptions import ConnectionClosedOK

logging.basicConfig(level=logging.INFO)


class Server:
    def __init__(self) -> None:
        self.clients: set[WebSocketServerProtocol] = set()

    async def register(self, ws: WebSocketServerProtocol) -> None:
        ws.name = names.get_full_name()
        self.clients.add(ws)
        logging.info(f"{ws.remote_address} connects")

    async def unregister(self, ws: WebSocketServerProtocol) -> None:
        self.clients.remove(ws)
        logging.info(f"{ws.remote_address} disconnects")

    async def send_to_clients(self, message: str) -> None:
        if self.clients:
            [await client.send(message) for client in self.clients]

    async def ws_handler(self, ws: WebSocketServerProtocol) -> None:
        await self.register(ws)
        try:
            await self.distribute(ws)
        except ConnectionClosedOK:
            pass
        finally:
            await self.unregister(ws)

    async def request(self, url: str) -> str:
        async with httpx.AsyncClient() as client:
            response: httpx.Response = await client.get(url)
            if response.status_code == 200:
                result: dict[str, object] = response.json()
                return str(result)
            return "Не вдалося отримати курс валют. Спробуйте ще раз пізніше."

    def build_date_string(self, days_ago: int) -> str:
        """Повертає дату у форматі dd.mm.YYYY для API ПриватБанку."""
        current_date: date = datetime.now().date()
        delta: timedelta = timedelta(days=days_ago)
        return (current_date - delta).strftime("%d.%m.%Y")

    async def get_exchange(self, date_string: str) -> str:
        response: str = await self.request(
            f"https://api.privatbank.ua/p24api/exchange_rates?date={date_string}"
        )
        return response

    async def format_return_exchange(self, message: str) -> str:
        parts: list[str] = message.split(" ")
        days_count: int = 0

        if len(parts) > 1:
            raw_days: str = parts[1]
            if not raw_days.isdigit():
                return "Кількість днів повинна бути цілим невід’ємним числом."
            days_count = int(raw_days)
            if days_count < 0 or days_count > 10:
                return "Кількість днів повинна бути в межах від 0 до 10."

        date_string: str = self.build_date_string(days_count)
        exchange: str = await self.get_exchange(date_string)
        return exchange

    async def distribute(self, ws: WebSocketServerProtocol) -> None:
        async for message in ws:
            parts: list[str] = message.split(" ")
            if parts[0] == "exchange":
                exchange: str = await self.format_return_exchange(message)
                await self.send_to_clients(exchange)
            else:
                await self.send_to_clients(f"{ws.name}: {message}")


async def main() -> None:
    server: Server = Server()
    # Тримаємо сервер запущеним без завершення main().
    async with websockets.serve(server.ws_handler, "localhost", 8080):
        await asyncio.Future()


if __name__ == "__main__":
    asyncio.run(main())