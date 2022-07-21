from abc import ABC, abstractmethod
from typing import TypeVar, Generic
import asyncio

T = TypeVar("T")

class TimeoutableCoroutine(ABC, Generic[T]):
    async def run(self, timeout: float, *args, **kwargs) -> T:
        try:
            return await asyncio.wait_for(self._coroutine(*args, **kwargs), timeout)
        except asyncio.TimeoutError:
            return self._on_timeout()

    @abstractmethod
    async def _coroutine(self, *args, **kwargs) -> T:
        pass

    @abstractmethod
    def _on_timeout(self) -> T:
        pass
