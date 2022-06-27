from abc import ABC, abstractmethod
from typing import Any

from smart_meter import SM

class DC(ABC):
    
    # Constructor

    def __init__(self, n_min: int, sm: list[SM], init_msg_time: int, final_msg_time: int):
        self._n_min = n_min
        self._sm = sm
        self._init_msg_time = init_msg_time
        self._final_msg_time = final_msg_time

    # Getters

    @property
    def n_min(self) -> int:
        return self._n_min

    @property
    def sm(self) -> list[SM]:
        return list(self._sm)

    @property
    def init_msg_time(self) -> int:
        return self._init_msg_time

    @property
    def final_msg_time(self) -> int:
        return self._final_msg_time

    # Abstract Methods

    @abstractmethod
    def collect_initial_msgs(self) -> tuple[list[int], list[int]]:
        pass

    @abstractmethod
    def activate_first_sm(self, l_rem) -> Any:
        pass

    @abstractmethod
    def collect_final_msg(self) -> tuple[list[int], list[int]]:
        pass

    @abstractmethod
    def calculate_aggregate(self, init_data, final_data, l_act) -> float:
        pass

    # Protocol Implementation

    def execute_round(self) -> None:
        init_data, l_rem = self.collect_initial_msgs()

        # terminate the round if the number of
        # participating smart meters is insufficient
        if len(l_rem) < self.n_min:
            return

        self.activate_first_sm(l_rem)
        final_data, l_act = self.collect_final_msg()
        self.calculate_aggregate(init_data, final_data, l_act)
