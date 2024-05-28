from pge.core import Core
from pge.types import Singleton

from scripts import SCREEN_DIMENSIONS
from scripts import Button

import pygame
import pygame.gfxdraw

@Singleton
class Sidebar:
    def __init__(self, tmedit):
        assert Core.instanced

        self.core = Core()
        self.tmedit = tmedit

        self.surface = pygame.Surface((316, SCREEN_DIMENSIONS[1] - 76)).convert_alpha()
        self.surface.fill((14, 14, 14))

        self.rect = self.surface.get_rect()
        self.rect.top = 76

        self.buttons = {}
        self.button_keys = ()

        self.page = 12
        self.page_text = None

        self.selected = None

        self.core.input_service.connect(pygame.K_d, pygame.KEYDOWN, self.increment)
        self.core.input_service.connect(pygame.K_a, pygame.KEYDOWN, self.decrement)

    def select(self, data):
        self.selected = data

    def load(self, data):
        tilesets = data['config']['images']
        for tileset in tilesets:
            self.buttons[tileset] = []

            tiles = data['config']['images'][tileset]['tiles']
            if not isinstance(tiles, list):
                tiles = [tiles for _ in range(len(self.tmedit.tilemap.images[tileset]))]

            padding = 12
            x, y = self.rect.left + padding, self.rect.top + 48 + padding
            for i, (tile, image) in enumerate(zip(tiles, self.tmedit.tilemap.images[tileset])):
                surface = pygame.Surface((64, 64)).convert_alpha()
                surface.blit(image, (0, 0))

                button = Button(surface, (x, y))
                button.on_click(self.select, {'tile': tile, 'tileset': tileset, 'index': i})

                self.buttons[tileset].append(button)

                x += 64 + padding
                if x >= self.rect.width:
                    y += 64 + padding
                    x = self.rect.left + padding

                self.selected = {'tile': tile, 'tileset': tileset, 'index': i}

        self.button_keys = tuple(self.buttons.keys())

    def increment(self):
        if not self.tmedit.tilemap:
            return

        if pygame.key.get_mods() & pygame.KMOD_ALT:
            return
            
        self.page = (self.page + 1) % len(self.button_keys)
        
    def decrement(self):
        if not self.tmedit.tilemap:
            return
        
        if pygame.key.get_mods() & pygame.KMOD_ALT:
            return
               
        self.page = (self.page - 1) % len(self.button_keys)
               
    def update(self):
        if not self.tmedit.tilemap:
            return
        
        self.page_text = self.core.font_service.create('m3x6', self.button_keys[self.page], 1)
        for button in self.buttons[self.button_keys[self.page]]:
            button.update()

    def render(self):
        self.core.screen.blit(self.surface, self.rect)

        if not self.tmedit.tilemap:
            return

        if self.page_text:
            self.core.screen.blit(self.page_text, (self.rect.left + 6, self.rect.top + 6))

        for button in self.buttons[self.button_keys[self.page]]:
            button.render()