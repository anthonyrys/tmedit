from pge.types import Singleton
from pge.utils import Bezier, BezierInfo

import dataclasses
import typing

T = typing.TypeVar('T')
@Singleton
class Easings:
    '''
    Helper class for managing bezier easings for objects
    '''

    @dataclasses.dataclass
    class EasingData:
        '''
        Data class for Easing data
        '''

        obj: T
        attribute: str
        from_to: tuple[float, float]

        to_time: list[int]
        to_bezier: BezierInfo

        count: typing.Optional[int] = 0

    def __init__(self) -> None:
        self._tasks: list[self.EasingData] = []

    def create(self, data: EasingData) -> None:
        '''
        Create a easing task using EasingData `data`
        '''

        del_tasks = []
        for t in self._tasks:
            if (t.obj, t.attribute) == (data.obj, data.attribute):
                del_tasks.append(t)

        for t in del_tasks:
            self._tasks.remove(t)

        self._tasks.append(data)

    def update(self, delta_time: float) -> None:
        '''
        Updates all of the current tasks, uses `delta_time`.
        '''

        del_tasks: list[self.EasingData] = []
        for task in self._tasks:
            if task.count > 0:
                task.count -= 1 * delta_time
                continue

            abs_prog: float = task.to_time[0] / task.to_time[1]

            d: float = task.from_to[1] - task.from_to[0]
            v: float = task.from_to[0] + d * Bezier().get_bezier_point(abs_prog, task.to_bezier)
            setattr(task.obj, task.attribute, v)

            task.to_time[0] += 1 * delta_time

            if task.to_time[0] > task.to_time[1]:
                task.to_time[0] = task.to_time[1]

                setattr(task.obj, task.attribute, task.from_to[1])
                del_tasks.append(task)

        for task in del_tasks:
            self._tasks.remove(task)
