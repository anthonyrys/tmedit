from pge.core import Core, Sprite
from pge.utils import Bezier, Easings

import pygame
import pygame.gfxdraw

class Button(Sprite):
    def __init__(self, image, position):
        assert Core.instanced
        self.core = Core()
        self.easings = Easings()
        self.bezier = Bezier()

        super().__init__(image, position=position)

        self.on_click_func = None
        self.hovering = False
        self.alpha = 100

    def on_click(self, func, *args):
        self.on_click_func = (func, args)

    def update(self):
        position = pygame.mouse.get_pos()

        data = None
        if self.rect.collidepoint(*position) and not self.hovering:
            self.hovering = True
            data = self.easings.EasingData(self, 'alpha', (self.alpha, 255), [0, 30], self.bezier.BezierPresets.EASE_OUT)

        elif not self.rect.collidepoint(*position) and self.hovering:
            self.hovering = False
            data = self.easings.EasingData(self, 'alpha', (self.alpha, 100), [0, 20], self.bezier.BezierPresets.EASE_OUT)

        self.image.set_alpha(self.alpha)
        if data:
            self.easings.create(data)

        if not self.hovering:
            return

        if self.on_click_func:
            if [e for e in self.core.events if e.type == pygame.MOUSEBUTTONDOWN]:
                self.on_click_func[0](*self.on_click_func[1])
    
    def render(self):
        self.core.screen.blit(self.image, self.rect)

class Alert(Sprite):
    def __init__(self, position, message, duration):
        assert Core.instanced
        self.core = Core()
        self.easings = Easings()
        self.bezier = Bezier()

        self.message = message
        self.duration = duration

        self.alpha = 255

        image = self.core.font_service.create('m3x6', message)
        super().__init__(image, position=position)

        data = self.easings.EasingData(self, 'alpha', (255, 0), [0, self.duration], self.bezier.BezierPresets.EASE_IN)
        self.easings.create(data)

    def update(self):
        self.duration -= 1 * self.core.delta_time
        self.image.set_alpha(self.alpha)
        
    def render(self):
        self.core.screen.blit(self.image, self.image.get_rect(midtop=self.position))

class Tile(Sprite):
    def __init__(self, image, dimensions, flipped, index, orientation, position, strata, tile, tileset):
        super().__init__(image, strata, position)
        self._dimensions = dimensions

        self.flipped = flipped
        self.orientation = orientation
        self.strata = strata

        self.tile = tile
        self.tileset = tileset
        self.image_index = index

    def render(self, surface, strata=None):
        if strata != None:
            if strata == self.strata and self.image.get_alpha() != 255:
                self.image.set_alpha(255)
            
            if strata != self.strata and self.image.get_alpha() != 55:
                self.image.set_alpha(55)

        else:
            if self.image.get_alpha() != 255:
                self.image.set_alpha(255)

        surface.blit(self.image, self.rect)
