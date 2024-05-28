from pge.utils import Bezier, BezierInfo
from pge.core import Sprite, Core
from pge.containers import SpriteList

import dataclasses
import typing

import pygame
import pygame.gfxdraw

ParticlePoints = typing.NewType('ParticlePoints', typing.Sequence[tuple[int, int]])

class Particle(Sprite):
    '''
    Custom particle sprite object.
    '''

    @dataclasses.dataclass
    class ParticleInfo:
        '''
        Data class for holding particle information.
        '''

        duration: float

        position: pygame.Vector2
        to_position: pygame.Vector2

        points: ParticlePoints 
        to_points: ParticlePoints

        size: int
    
        position_bezier: BezierInfo
        point_bezier: BezierInfo

        color: typing.Optional[tuple[int, int, int]] = (255, 255, 255)
        gravity: typing.Optional[float] = 0

        rotation: typing.Optional[float] = 0

    def __init__(self, info: ParticleInfo, index: typing.Optional[int] = 0) -> None:
        '''
        Create the particle sprite, with the given particle 
        `info`, and an optional render `index`.
        '''

        super().__init__(pygame.Surface((1, 1)), index)

        if not isinstance(info.position, pygame.Vector2):
            info.position = pygame.Vector2(info.position)

        if not isinstance(info.to_position, pygame.Vector2):
            info.to_position = pygame.Vector2(info.to_position)

        if abs(info.size) != 1:
            for i in range(len(info.points)):
                info.points[i][0] = info.points[i][0] * info.size
                info.points[i][1] = info.points[i][1] * info.size

            for i in range(len(info.to_points)):
                info.to_points[i][0] = info.to_points[i][0] * info.size
                info.to_points[i][1] = info.to_points[i][1] * info.size

        self.info: self.ParticleInfo = info

        self.time: float = 0

        self.current_position: pygame.Vector2 = self.info.position.copy()
        self.current_points: ParticlePoints = [[p[0], p[1]] for p in self.info.points]
        self.current_gravity: float = 0
        self.current_rotation: float = 0

        self.core = Core()

    def update(self) -> typing.Union[None, str]:
        '''
        Update the particle sprite.
        
        Returns `SpriteList.SPRITELIST_DELETE` when the 
        particle's `duration` has expired.
        '''

        self.time += 1 * self.core.delta_time
        self.current_gravity += self.info.gravity * self.core.delta_time 
        self.current_rotation += self.info.rotation * self.core.delta_time

        if self.time >= self.info.duration:
            return SpriteList.SPRITELIST_DELETE

        t: float = self.time / self.info.duration

        if self.info.position != self.info.to_position:
            self.current_position.x = self.info.position.x + (
                (self.info.to_position.x - self.info.position.x) * Bezier().get_bezier_point(t, self.info.position_bezier)
            )

            self.current_position.y = self.info.position.y + (
                (self.info.to_position.y - self.info.position.y) * Bezier().get_bezier_point(t, self.info.position_bezier)
            )

        self.current_position.y += self.current_gravity

        if self.info.points != self.info.to_points:
            for i in range(len(self.current_points)):
                self.current_points[i][0] = self.info.points[i][0] + (
                    (self.info.to_points[i][0] - self.info.points[i][0]) * Bezier().get_bezier_point(t, self.info.point_bezier)
                )

                self.current_points[i][1] = self.info.points[i][1] + (
                    (self.info.to_points[i][1] - self.info.points[i][1]) * Bezier().get_bezier_point(t, self.info.point_bezier)
                )

        self.rect.topleft = self.current_position

    def render(self, surface=None) -> None:
        '''
        Render the particle sprite.
        '''

        if not surface:
            surface = self.core.screen

        if self.current_rotation != 0:
            points = []
            for p in self.current_points:
                point = pygame.Vector2(p).rotate(self.current_rotation)
                points.append((self.current_position[0] + point[0], self.current_position[1] + point[1]))
        else:
            points = [[self.current_position.x + p[0], self.current_position.y + p[1]] for p in self.current_points]

        pygame.gfxdraw.filled_polygon(surface, points, self.info.color)
