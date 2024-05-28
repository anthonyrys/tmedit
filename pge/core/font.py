from pge.types import Singleton
from pge.utils import load_spritesheet

import pygame
import typing
import os

@Singleton
class Font:
    '''
    Singleton class for handling fonts.
    '''

    _FONT_PATH: typing.Final[str] = os.path.join('pge', '_data', 'fonts')
    _FONT_KEYS: typing.Final[tuple[str]] = tuple(map(str, 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890!?,.;:\'\"/|\_()[]{}<>@#$%+-*=^&')) 

    def __init__(self) -> None:
        self._fonts: dict[str, typing.Union[int, dict[chr, pygame.Surface]]] = {
            'm3x6': {
                'spacing': 2,
                'letters': {}
            } 
        }

        for file in os.listdir(self._FONT_PATH):
            name: str = file.split('.')[0]
            images: list[pygame.Surface] = load_spritesheet(os.path.join(self._FONT_PATH, file))

            for index, key in enumerate(self._FONT_KEYS):
                self._fonts[name]['letters'][key] = images[index]

    def create(self, font: str, text: str, size: typing.Optional[int] = 1, 
               color: typing.Optional[tuple[int, int, int]] = (255, 255, 255)) -> pygame.Surface:
        '''
        Returns a new font image based on the given `font` and `text`.
        Can optionally specify a `size` and a `color`.
        '''

        surface_size: list[int] = [0, 0]
        images: list[pygame.Surface] = []

        for letter in str(text):
            image: pygame.Surface = None

            if letter == ' ':
                image = pygame.Surface((self._fonts[font]['spacing'] * 2, self._fonts[font]['letters']['a'].get_height())).convert_alpha()
                image.set_colorkey((0, 0, 0))
            else:
                image = self._fonts[font]['letters'][letter].copy()

            surface_size[0] += (image.get_width() + self._fonts[font]['spacing'])
            if image.get_height() > surface_size[1]:
                surface_size[1] += image.get_height()

            image = pygame.transform.scale(image, (image.get_width() * size, image.get_height() * size)).convert_alpha()
            image = pygame.mask.from_surface(image).to_surface(setcolor=color, unsetcolor=(0, 0, 0)).convert_alpha()

            images.append(image)

        surface: pygame.Surface = pygame.Surface((surface_size[0] * size, surface_size[1] * size)).convert_alpha()
        surface.set_colorkey((0, 0, 0))

        x: int = 0
        for image, letter in zip(images, str(text)):
            surface.blit(image, (x, 0))
            x += image.get_width() + (self._fonts[font]['spacing'] * size)

        return surface
