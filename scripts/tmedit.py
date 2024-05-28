from pge.core import Core
from pge.types import Singleton
from pge.utils import Easings, clamp, load_spritesheet, scale
from pge.containers import SpriteList

from scripts import SCREEN_DIMENSIONS, SCREEN_COLOR, IMAGE_PATH
from scripts import Alert, Tile
from scripts import Sidebar, Navbar
from scripts import TOOLS

from tkinter import filedialog

import dataclasses
import pygame
import pygame.gfxdraw
import json
import os

@dataclasses.dataclass
class Tilemap:
    data: dict
    images: dict

    surface: pygame.Surface
    bounds: pygame.Vector2

    chunks: dict

@Singleton
class Tmedit:
    def __init__(self):
        assert Core.instanced

        self.core = Core()
        self.easings = Easings()

        self.sidebar = Sidebar(self)
        self.navbar = Navbar(self)

        self.tilemap = None
        self.path = None

        self.viewport = pygame.Rect(0, 0, SCREEN_DIMENSIONS[0] - self.sidebar.rect.width, SCREEN_DIMENSIONS[1] - self.navbar.rect.height)
        self.fill = pygame.Rect(0, 0, SCREEN_DIMENSIONS[0] - self.sidebar.rect.width, SCREEN_DIMENSIONS[1] - self.navbar.rect.height)

        self.prev_viewport = pygame.Vector2((-1, -1))

        self.offset_anchor = None
        self.offset = pygame.Vector2()

        self.mouse_position = pygame.Vector2()
        self.global_mouse_position = pygame.Vector2()

        self.mouse_down = False
        self.mouse_focus = True

        self.renderable_chunks = []

        self.alerts = SpriteList()
        self.alert_y = 0

        self.actions = []

        self.tools = { k.lower(): v(self) for k, v in TOOLS.items() }
        self.tool = ('move', self.tools['move'])

        self.settings = {
            'strata': 0,
            'orientation': 0,
            'flipped': False
        }

        self.modes = {
            'strata filtering': True,
            'snapping': True
        }

        self.core.input_service.connect(None, pygame.KEYDOWN, self.on_input)
        self.core.input_service.connect([v.keybind for v in self.tools.values()], pygame.KEYDOWN, self.on_tool)

    def on_mouse_down(self, event):
        if not self.tilemap or not self.mouse_focus:
            return

        self.tool[1].on_mouse_down(event)

    def on_mouse_up(self, event):
        if not self.tilemap:
            return
        
        self.tool[1].on_mouse_up(event)
           
    def on_tool(self, key):
        if pygame.key.get_mods() & pygame.KMOD_ALT:
            return
        
        event = pygame.event.Event(pygame.MOUSEBUTTONUP, button=1)
        self.on_mouse_up(event)

        for name, tool in self.tools.items():
            if key != tool.keybind:
                continue

            self.tool = (name, tool)

    def on_input(self, key):
        if not self.tilemap:
            return
        
        if pygame.key.get_mods() & pygame.KMOD_ALT and not pygame.key.get_mods() & pygame.KMOD_CTRL:
            if key == pygame.K_z:
                self.modes['snapping'] = not self.modes['snapping']

            if key == pygame.K_x:
                self.modes['strata filtering'] = not self.modes['strata filtering']

        elif pygame.key.get_mods() & pygame.KMOD_CTRL and not pygame.key.get_mods() & pygame.KMOD_ALT:
            if key == pygame.K_z:
                self.undo()

        elif not pygame.key.get_mods() & pygame.KMOD_CTRL and not pygame.key.get_mods() & pygame.KMOD_ALT:
            try:
                self.settings['strata'] = clamp(int(pygame.key.name(key)), 0, 9)
            except ValueError:
                ...

            if key == pygame.K_r:
                self.settings['orientation'] = (self.settings['orientation'] + 90) % 360

            if key == pygame.K_t:
                self.settings['flipped'] = not self.settings['flipped']
    
    def undo(self):
        if not self.actions:
            return
        
        action = self.actions[-1]
        self.tools[action[0]].undo(action)

        self.alert(f'Undo: {action[0]}')
        self.actions.pop()

    def alert(self, message, duration=180):
        position = (self.sidebar.rect.right + self.viewport.width // 2, self.navbar.rect.bottom + 6 + (25 * self.alert_y))
        alert = Alert(position, message, duration)

        self.alerts.append(alert)
        self.alert_y += 1

    def save(self, alert=False):
        if not self.tilemap:
            return
        
        tiles = [t for s in [c[1] for c in self.tilemap.chunks.values()] for t in s]
        
        tile_data = []
        for tile in tiles:
            data = {
                'dimensions': tile._dimensions,
                'flipped': tile.flipped,
                'index': tile.image_index,
                'orientation': tile.orientation,
                'position': [round(tile.position.x), round(tile.position.y)],
                'strata': tile.strata,
                'tile': tile.tile,
                'tileset': tile.tileset
            }

            tile_data.append(data)

        self.tilemap.data['tiles'] = tile_data

        try:
            if not os.path.exists(self.path):
                raise FileNotFoundError

            with open(os.path.join(self.path, 'tilemap.json'), 'w') as t:
                json.dump(self.tilemap.data, t, indent=2, sort_keys=True)

        except (FileNotFoundError) as e: 
            print(e)
        
        if alert:
            self.alert(f'Tilemap Saved: {self.tilemap.data["config"]["name"]}')

    def load(self):
        if self.tilemap:
            self.save(False)

        self.path = filedialog.askdirectory()

        try:
            with open(os.path.join(self.path, 'tilemap.json')) as t:
                data = json.load(t)
    
        except (json.JSONDecodeError, FileNotFoundError) as e:
            print(f'[Tmedit::load] {e}')
            return

        images = {}
        for image in data['config']['images']:
            spritesheet_path = os.path.join(self.path, data['config']['images'][image]['path'])
            images[image] = load_spritesheet(spritesheet_path, scale=4)

        surface = pygame.Surface((data['config']['tile']['dimensions'][0] * data['config']['tilemap']['dimensions'][0], 
                                  data['config']['tile']['dimensions'][1] * data['config']['tilemap']['dimensions'][1])).convert_alpha()

        bounds = pygame.Vector2(surface.get_width() - self.viewport.width, surface.get_height() - self.viewport.height)

        chunks = {}

        x, y = 0, 0
        while y < surface.get_height():
            while x < surface.get_width():
                rect = pygame.Rect(x, y, data['config']['tile']['dimensions'][0] * 15, data['config']['tile']['dimensions'][1] * 15)
                chunks[(x, y)] = [rect, SpriteList()]

                x += rect.width

            y += rect.height
            x = 0

        for tile in data['tiles']:
            image = images[tile['tileset']][tile['index']]

            image = pygame.transform.rotate(image, -tile['orientation'])
            image = pygame.transform.flip(image, tile['flipped'], False)
        
            t = Tile(image, **tile)

            for position in chunks:
                if chunks[position][0].collidepoint(tile['position']):
                    chunks[position][1].append(t)

        self.tilemap = Tilemap(data, images, surface, bounds, chunks)

        self.sidebar.load(data)
        self.navbar.load(data)

        pygame.display.set_caption(f'{self.core.title} - {data["config"]["name"]}')
        self.alert(f'Tilemap Loaded: {self.tilemap.data["config"]["name"]}')
        
        event = pygame.event.Event(pygame.MOUSEBUTTONUP, button=1)
        self.on_mouse_up(event)

    def update(self):     
        self.easings.update(self.core.delta_time)
        self.sidebar.update()
        self.navbar.update()

        if self.tilemap == None:
            return

        self.global_mouse_position.x = clamp(pygame.mouse.get_pos()[0], self.sidebar.rect.width, SCREEN_DIMENSIONS[0])
        self.global_mouse_position.y = clamp(pygame.mouse.get_pos()[1], self.navbar.rect.height, SCREEN_DIMENSIONS[1])
       
        for event in self.core.events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                self.on_mouse_down(event)

            elif event.type == pygame.MOUSEBUTTONUP:
                self.on_mouse_up(event)

        for i, pressed in enumerate(pygame.mouse.get_pressed()):
            if not pressed:
                continue
            
            event = pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=i + 1)
            self.on_mouse_down(event)

        self.tool[1].update()

        self.viewport.x = clamp(self.viewport.x, -self.tilemap.bounds.x, 0)
        self.viewport.y = clamp(self.viewport.y, -self.tilemap.bounds.y, 0)

        self.fill.x, self.fill.y = -self.viewport.x, -self.viewport.y

        if self.viewport.x != self.prev_viewport.x or self.viewport.y != self.prev_viewport.y:
            self.renderable_chunks = []
            for position in self.tilemap.chunks:
                if self.tilemap.chunks[position][0].colliderect(self.fill):
                    self.renderable_chunks.append(position)

            self.prev_viewport.x = self.viewport.x
            self.prev_viewport.y = self.viewport.y

        self.mouse_focus = False
        if list(self.global_mouse_position.xy) == list(pygame.mouse.get_pos()):
            self.mouse_focus = True
            self.mouse_position.x = clamp(0, -self.viewport.x + pygame.mouse.get_pos()[0] - self.sidebar.rect.width, self.tilemap.bounds.x)
            self.mouse_position.y = clamp(0, -self.viewport.y + pygame.mouse.get_pos()[1] - self.navbar.rect.height, self.tilemap.bounds.y)

        self.alerts.update_all()

        del_alerts = []
        for alert in self.alerts:
            if alert.duration <= 0:
                del_alerts.append(alert)

        for del_alert in del_alerts:
            self.alerts.remove(del_alert)

        if len(self.alerts) == 0:
            self.alert_y = 0

    def render_grid(self):
        config = self.tilemap.data['config']
        color = (4, 4, 4)
        
        step_x = config['tile']['dimensions'][0]
        max_x = self.tilemap.surface.get_width()

        step_y = config['tile']['dimensions'][1]
        max_y = self.tilemap.surface.get_height()

        x = step_x
        while x <= max_x:
            pygame.gfxdraw.line(self.tilemap.surface, x, 0, x, max_y, color)
            x += step_x

        y = step_y
        while y <= max_y:
            pygame.gfxdraw.line(self.tilemap.surface, 0, y, max_x, y, color)
            y += step_y

    def render_tilemap(self):
        strata = self.settings['strata'] if self.modes['strata filtering'] else None
        for position in self.renderable_chunks:
            self.tilemap.chunks[position][1].render_all(self.tilemap.surface, strata)

        self.tool[1].render_pre()
        
    def render(self):
        self.core.screen.fill(SCREEN_COLOR)

        self.sidebar.render()
        self.navbar.render()

        if self.tilemap == None:
            self.tool[1].render_post()
            return

        self.tilemap.surface.fill((0, 0, 0), self.fill)

        self.render_grid()
        self.render_tilemap()

        surface = pygame.Surface((self.viewport.width, self.viewport.height))
        surface.blit(self.tilemap.surface, self.viewport)

        self.core.screen.blit(surface, (self.sidebar.rect.width, self.navbar.rect.height))
        
        y = 4
        for setting in self.settings:
            text = self.core.font_service.create('m3x6', f'{setting}: {self.settings[setting]}')    
            self.core.screen.blit(text, text.get_rect(topleft=(self.sidebar.rect.right + 6, self.navbar.rect.bottom + y)))

            y += text.get_height() + 4

        y = 4
        for mode in [s for s in self.modes.keys() if self.modes[s]]:
            text = self.core.font_service.create('m3x6', mode)
            self.core.screen.blit(text, text.get_rect(bottomleft=(self.sidebar.rect.right + 6, SCREEN_DIMENSIONS[1] - y)))

            y += text.get_height() + 4

        text = self.core.font_service.create('m3x6', f'{round(self.mouse_position.x), round(self.mouse_position.y)}')
        self.core.screen.blit(text, text.get_rect(bottomright=(SCREEN_DIMENSIONS[0] - 6, SCREEN_DIMENSIONS[1] - 4)))

        self.alerts.render_all()
        self.tool[1].render_post()
