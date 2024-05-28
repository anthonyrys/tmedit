def main():
    tmedit.update()
    tmedit.render()

if __name__ == '__main__':
    from pge.core import Core

    from scripts import TITLE, SCREEN_DIMENSIONS, FRAME_RATE
    from scripts import Tmedit

    import tkinter

    tkinter.Tk().withdraw()

    core = Core(TITLE, SCREEN_DIMENSIONS, FRAME_RATE, mouse=False)
    tmedit = Tmedit()

    core.run(main)
    tmedit.save()
