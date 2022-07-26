from abc import ABC, abstractmethod
from typing import TypeVar, Generic
import asyncio

T = TypeVar("T")

class TimeoutableCoroutine(ABC, Generic[T]):
    async def run(self, timeout: float, **kwargs) -> T:
        try:
            return await asyncio.wait_for(self._coroutine(**kwargs), timeout)
        except asyncio.TimeoutError:
            return await self._on_timeout()

    @abstractmethod
    async def _coroutine(self, **kwargs) -> T:
        pass

    @abstractmethod
    async def _on_timeout(self) -> T:
        pass
