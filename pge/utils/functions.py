import inspect
import typing
import pygame
import math
import sys

T = typing.TypeVar('T')
def generate_import_dict(*excludes: typing.Sequence[T]) -> dict[str, T]:
    '''
    Generates a dictionary of objects for imports.
    Optionally, can specify a list `excludes`.
    '''

    if not excludes:
        excludes = ()

    name: str = sys.modules[inspect.getmodule(inspect.stack()[1][0]).__name__]

    return {
        k: v for k, v in (c for c in inspect.getmembers(name, inspect.isclass) if c[0] not in excludes)
    }


def scale(image, sx: float, sy: typing.Optional[float] = None) -> pygame.Surface:
    '''
    Simplified pygame scale function.

    Returns the image scaled by `sx` on both axes.
    
    Optionally, `sx` on the x-axis, and `sy` on the y-axis.
    '''
        
    if not sy: sy = sx
    return pygame.transform.scale(image, (image.get_width() * sx, image.get_height() * sy)).convert_alpha()


def clamp(v: float, mi: float, mx: float) -> float:
    '''
    Returns value `v` clamped between `mi` and `mx`.
    '''

    return max(mi, min(v, mx))

def get_distance(p1: tuple[float, float], p2: tuple[float, float]) -> float:
    '''
    Returns the distance between point `p1` and point `p2`.
    '''

    rx: float = abs(p1[0] - p2[0])
    ry: float = abs(p1[1] - p2[1])

    return math.sqrt(((rx **2) + (ry **2)))
