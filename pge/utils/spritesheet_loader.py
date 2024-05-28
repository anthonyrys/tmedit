import pygame
import typing

SPRITESHEET_STOP_COLOR: typing.Final[tuple[int, int, int, int]] = (255, 0, 0, 255)

def load_spritesheet(path: str, frames: typing.Optional[typing.Sequence[int]] = None, 
                     colorkey: typing.Optional[tuple[int, int, int]] = (0, 0, 0),
                     scale: typing.Optional[float] = 1.0) -> list[pygame.Surface]:
    '''
    Returns a list of sprites from a given image `path`. 
    
    Optionally, can specify a sequence of `frames` for animation,
    `colorkey` or `scale`.
    '''

    images: list[pygame.Surface] = []
    sheet: pygame.Surface = pygame.image.load(path).convert_alpha()

    width: int = sheet.get_width()
    height: int = sheet.get_height()

    image_count: int = 0
    start: int = 0
    stop: int = 0
    i: int = 0

    for i in range(width):
        if sheet.get_at((i, 0)) != SPRITESHEET_STOP_COLOR:
            continue
    
        stop = i
        image: pygame.Surface = pygame.Surface((stop - start, height)).convert_alpha()
        image.set_colorkey(colorkey)
        image.blit(sheet, (0, 0), (start, 0, stop - start, height))

        if scale != 1.0:
            image = pygame.transform.scale(image, (image.get_width() * scale, image.get_height() * scale)).convert_alpha()
            
        if frames:
            for _ in range(frames[image_count]):
                images.append(image)
        else:
            images.append(image)

        image_count += 1
        start = stop + 1

    return images
    
