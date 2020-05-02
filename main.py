from parser import *
from sfml import sf


FONT = sf.Font.from_file("DejaVuSansMono.ttf")
parser = Parser()


class GUI:
    def __init__(self):
        self.header = sf.Text("Find easiest problems for you", FONT, 18)
        self.name = sf.Text("", FONT, 16)
        self.name.color = sf.Color.GREEN
        self.name.position = sf.Vector2(30, 30)
        # self.header.color = sf.Color.WHITE
        self.autocompleter_list = []

    def update_autocompleter_list(self):
        cur_string = self.name.string
        self.autocompleter_list = []
        for el in parser.get_names():
            if len(cur_string) <= len(el):
                if el[:len(cur_string)] == cur_string:
                    self.autocompleter_list.append(el)

    def draw(self, window):
        self.update_autocompleter_list()
        window.draw(self.header)
        name_empty = False
        if len(self.name.string) == 0:
            name_empty = 1
            self.name.string = "Input your name here:"
        window.draw(self.name)
        cur_y = 60
        MENU_HEIGHT = 25
        for el in self.autocompleter_list:
            text = sf.Text(el, FONT, 18)
            text.position = sf.Vector2(30, cur_y)
            text.color = sf.Color.WHITE
            window.draw(text)
            cur_y += MENU_HEIGHT

        if len(self.autocompleter_list) == 1:
            cur_y += 20
            stat = parser.get_stat(self.autocompleter_list[0])
            cnt = min(20, len(stat))
            text = sf.Text("{:<15} {:<15} {:<15}".format("Contest_id", "Problem", "Score"), FONT, 18)
            text.position=sf.Vector2(30, cur_y)
            text.color = sf.Color.WHITE
            window.draw(text)
            cur_y += MENU_HEIGHT
            for i in range(cnt):
                text = sf.Text("{:<15} {:<15} {:<15}".format(stat[i].contest.id, stat[i].short_name, stat[i].score), FONT, 18)
                text.position=sf.Vector2(30, cur_y)
                text.color = sf.Color.WHITE
                window.draw(text)
                cur_y += MENU_HEIGHT

        if name_empty:
            self.name.string = ""


    def text_entered(self, c):
        print(c)
        if ord(c) == 8:
            if len(self.name.string):
                self.name.string = self.name.string[:-1]
        if ord(c) >= 32:
            self.name.string += c


gui = GUI()
window = sf.RenderWindow(sf.VideoMode(600, 700), "Problem Chooser v1.0")
running = True
while running:
    event = window.poll_event()
    while event:
        if event.type == sf.Event.CLOSED:
            running = False
        if event.type == sf.Event.TEXT_ENTERED:
            gui.text_entered(event.get('unicode'))
        event = window.poll_event()
    window.clear(sf.Color.BLACK)
    gui.draw(window)
    window.display()
