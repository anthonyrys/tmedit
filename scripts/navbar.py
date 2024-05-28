from pge.core import Core
from pge.types import Singleton
from pge.containers import SpriteList
from pge.utils import scale

from scripts import SCREEN_DIMENSIONS, IMAGE_PATH
from scripts import Button

import pygame
import pygame.gfxdraw
import os

@Singleton
class Navbar:
    def __init__(self, tmedit):
        assert Core.instanced

        self.core = Core()
        self.tmedit = tmedit
            
        self.surface = pygame.Surface((SCREEN_DIMENSIONS[0], 76)).convert_alpha()
        self.surface.fill((21, 21, 21))

        self.rect = self.surface.get_rect()

        load = scale(pygame.image.load(os.path.join(IMAGE_PATH, 'buttons', 'load.png')), 3)
        save = scale(pygame.image.load(os.path.join(IMAGE_PATH, 'buttons', 'save.png')), 3)

        self.load_button = Button(load, (10, 10))
        self.save_button = Button(save, (70, 10))

        self.load_button.on_click(self.tmedit.load)
        self.save_button.on_click(self.tmedit.save, True)

        self.buttons = SpriteList([v for k, v in self.__dict__.items() if 'button' in k])

    def load(self, data):
        ...

    def update(self):
        self.buttons.update_all()

    def render(self):
        self.core.screen.blit(self.surface, self.rect)
        self.buttons.render_all()