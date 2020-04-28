from parser import *

FONT = sf.Font.from_file("DejaVuSansMono.ttf")


class GUI:
    def __init__(self):
        self.header = sf.Text("Find easiest problems for you", FONT, 18)
        self.name = sf.Text("", FONT, 16)
        self.name.position = sf.Vector2(30, 30)
        # self.header.color = sf.Color.WHITE

    def draw(self, window):
        window.draw(self.header)
        window.draw(self.name)

    def text_entered(self, c):
        print(ord(c))
        if ord(c) == 8:
            if len(self.name.string):
                self.name.string = self.name.string[:-1]
        if 177 > ord(c) >= 40:
            self.name.string += c


parser = Parser()
gui = GUI()
window = sf.RenderWindow(sf.VideoMode(800, 600), "Parse Informatics Conduit")
running = True
while running:
    event = window.poll_event()
    while event:
        if event.type == sf.Event.CLOSED:
            running = False
        if event.type == sf.Event.TEXT_ENTERED:
            if ord(event.get("unicode")) < 128:
                gui.text_entered(event.get('unicode'))
        event = window.poll_event()
    window.clear(sf.Color.BLACK)
    gui.draw(window)
    window.display()
