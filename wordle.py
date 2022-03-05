import tkinter as tk
import time
import unidecode
from random import choice


class Theme:
    def __init__(self, bg, fg, good, misplaced, null, hover, border, error, title_font, letter_font, text_font):
        self.bg = bg
        self.fg = fg
        self.good = good
        self.misplaced = misplaced
        self.null = null
        self.hover = hover
        self.border = border
        self.error = error
        self.title_font = title_font
        self.letter_font = letter_font
        self.text_font = text_font

    @staticmethod
    def LIGHT():
        return Theme("white", "black", "green3", "orange", "gray67", "light gray", "black", "red",
                     ("Monaco", 40, "bold"), ("Lucida Console", 50, "bold"), ("Courier New",))

    @staticmethod
    def DARK():
        return Theme("black", "white", "green", "orange", "gray", "gray13", "white", "red",
                     ("Monaco", 40, "bold"), ("Lucida Console", 50, "bold"), ("Courier New",))


class State:
    NONE = "none"
    ERROR = "error"
    HOVER = "hover"
    NULL = "null"
    MISPLACED = "misplaced"
    GOOD = "good"


class RoundedButton(tk.Canvas):
    def __init__(self, master, letter: str = "", theme: Theme = Theme.LIGHT(), radius=25, locked=False):
        super().__init__(master)
        self.config(bd=0, highlightthickness=0, height=100, width=100)

        self.theme = theme
        self.radius = radius
        self.locked = locked
        self.state = State.NONE
        self.letter = letter

        self.bg_rect = self.round_rectangle(5, 5, 95, 95, radius=radius)
        self.border_rect = self.round_rectangle(5, 5, 95, 95, radius=radius)
        self.rect = self.round_rectangle(6, 6, 94, 94, tags="#", radius=radius - 1)
        self.text = self.create_text(50, 50, tags="#", text=letter, anchor="center")
        self.update_colors()

        self.tag_bind("#", "<ButtonPress>", lambda x: self.null(lock=False))
        self.tag_bind("#", "<ButtonRelease>", lambda x: self.hover())
        self.tag_bind("#", "<Enter>", lambda x: self.hover())
        self.tag_bind("#", "<Leave>", lambda x: self.reset())

    def change_theme(self, theme: Theme):
        self.theme = theme
        self.update_colors()

    def change_letter(self, letter: str = "", lock=False):
        if not self.locked:
            self.letter = letter
            self.itemconfig(self.text, text=letter)
            if lock:
                self.locked = True

    def change_state(self, state, lock=False):
        if not self.locked:
            self.state = state
            self.update_colors()
            if lock:
                self.lock()

    def update_colors(self):
        self.config(bg=self.theme.bg)
        self.itemconfig(self.bg_rect, fill=self.theme.bg)
        self.itemconfig(self.border_rect, fill=self.theme.border)
        self.itemconfig(self.text, fill=self.theme.fg, font=self.theme.letter_font)
        self.itemconfig(self.rect, fill=self.theme.good if self.state == State.GOOD else self.theme.misplaced
                        if self.state == State.MISPLACED else self.theme.null if self.state == State.NULL
                        else self.theme.hover if self.state == State.HOVER else self.theme.bg
                        if self.state == State.NONE else self.theme.error)

    def reset(self, lock=False): self.change_state(State.NONE, lock)
    def hover(self, lock=False): self.change_state(State.HOVER, lock)
    def click(self, lock=False): self.change_state(State.NULL, lock)
    def good(self, lock=True): self.change_state(State.GOOD, lock)
    def misplaced(self, lock=True): self.change_state(State.MISPLACED, lock)
    def null(self, lock=True): self.change_state(State.NULL, lock)
    def error(self, lock=True): self.change_state(State.ERROR, lock)

    def lock(self): self.locked = True
    def unlock(self): self.locked = False

    def round_rectangle(self, x1, y1, x2, y2, radius=25, master_to_update=None, **kwargs):
        # if update is False a new rounded rectangle's id will be returned else updates existing rounded rect.
        # source: https://stackoverflow.com/a/44100075/15993687
        points = [x1 + radius, y1, x1 + radius, y1, x2 - radius, y1, x2 - radius, y1, x2, y1, x2, y1 + radius,
                  x2, y1 + radius, x2, y2 - radius, x2, y2 - radius, x2, y2, x2 - radius, y2, x2 - radius, y2,
                  x1 + radius, y2, x1 + radius, y2, x1, y2, x1, y2 - radius, x1, y2 - radius, x1, y1 + radius,
                  x1, y1 + radius, x1, y1]
        if not master_to_update:
            return self.create_polygon(points, **kwargs, smooth=True)
        else:
            self.coords(master_to_update, points)

    def reveal_animation(self, reveal_func=None):
        sleep = 0.001
        for i in range(0, 40, 2):
            self.round_rectangle(5, 5 + i, 95, 95 - i, radius=self.radius, master_to_update=self.border_rect)
            self.round_rectangle(6, 6 + i, 94, 94 - i, tags="#", radius=self.radius - 1, master_to_update=self.rect)
            self.update()
            time.sleep(sleep)

        reveal_func()

        for i in range(0, 40, 2):
            self.round_rectangle(5, 45 - i, 95, 55 + i, radius=self.radius, master_to_update=self.border_rect)
            self.round_rectangle(6, 46 - i, 94, 54 + i, tags="#", radius=self.radius - 1, master_to_update=self.rect)
            self.update()
            time.sleep(sleep)


class Wordle(tk.Tk):

    def __init__(self):
        self.app_name = "Wordle"
        self.theme = Theme.LIGHT()

        self.DB = []
        try:
            with open("DB 5 7980.txt", "r") as file:
                self.DB = [unidecode.unidecode(w) for w in file.read().lower().replace("\n", "").replace("  ", " ")
                           .split(" ") if w and len(w) == 5 and w.isalpha() and w not in self.DB]
        except:
            from db_5_7980 import DB
            self.DB = [unidecode.unidecode(w) for w in str(DB).lower().replace("\n", "").replace("  ", " ")
                       .split(" ") if w and len(w) == 5 and w.isalpha() and w not in self.DB]

        super().__init__(self.app_name)
        self.title(self.app_name)
        self.geometry("550x680")

        self.title_lbl = tk.Label(self)
        self.lines = [tk.Frame(self) for _ in range(6)]
        self.buttons = [[RoundedButton(l) for _ in range(5)] for l in self.lines]

        self.playable = True
        self.cursor = [0, 0]
        self.word = choice(self.DB)
        print(self.word)

        self.update_all()

        self.bind("<Key>", self.on_keypress)
        self.bind("<BackSpace>", self.on_backspace)
        self.bind("<Return>", self.on_return)

    def clear(self):
        for widgets in self.winfo_children():
            widgets.forget()

    def update_all(self):
        self.clear()

        self.config(bg=self.theme.bg)

        self.title_lbl.config(bg=self.theme.bg, fg=self.theme.fg, font=self.theme.title_font, text=self.app_name)
        self.title_lbl.place(y=0, relx=0.5, anchor="n")

        for i, l in enumerate(self.lines):
            l.config(bg=self.theme.bg)
            # y -> i * <box_size>
            # + <font_size> * 1.5(=> natural pady)
            # + half_of_<box_size>(=> because of anchor="center")
            # + 5(=> title pady)
            l.place(y=i * 100 + self.theme.title_font[1] * 1.5 + 55, relx=0.5, anchor="center")

        for l in self.buttons:
            for b in l:
                b.change_theme(self.theme)
                b.pack(side="left")

    def on_keypress(self, event_or_char):
        if not self.playable:
            return
        c = event_or_char if isinstance(event_or_char, str) else str(event_or_char.char)
        if c.isalpha() and self.cursor[1] < len(self.buttons[self.cursor[0]]):
            self.buttons[self.cursor[0]][self.cursor[1]].change_letter(c)
            self.cursor[1] += 1

    def on_backspace(self, event=None):
        if not self.playable:
            return
        self.cursor[1] -= 1
        if self.cursor[1] < 0:
            self.cursor[1] = 0
        self.buttons[self.cursor[0]][self.cursor[1]].change_letter()

    def on_return(self, event=None):
        if not self.playable:
            return
        answers = [State.NULL for _ in range(len(self.buttons[self.cursor[0]]))]
        word = ""
        for b in self.buttons[self.cursor[0]]:
            if not b.letter:
                self.error_animation(self.cursor[0])
                return
            else:
                word += b.letter

        word, objective = unidecode.unidecode(word.lower()), str(self.word.lower())

        if word not in self.DB:
            self.error_animation(self.cursor[0])
            return

        for i, (c, w) in enumerate(zip(word, objective)):
            if c != "#" and c == w:
                answers[i] = State.GOOD
                word, objective = list(word), list(objective)
                word[i], objective[i] = "##"
                word, objective = "".join(word), "".join(objective)
        for i, (c, w) in enumerate(zip(word, objective)):
            if c != "#" and c in objective:
                answers[i] = State.MISPLACED
                word = list(word)
                word[i] = "#"
                word = "".join(word)
                objective.replace(c, "#", 1)

        self.playable = False
        for b, a in zip(self.buttons[self.cursor[0]], answers):
            b.reveal_animation(b.good if a == State.GOOD else b.misplaced if a == State.MISPLACED else b.null)

        self.cursor[0] += 1
        self.cursor[1] = 0
        self.playable = True

    def error_animation(self, line: int):
        was_playable = not not self.playable
        self.playable = False

        for b in self.buttons[line]:
            b.error()

        self.update()

        sleep = 0.0001
        for _ in range(2):
            for _ in range(3):
                time.sleep(sleep)
                self.lines[line].place_configure(x=int(self.lines[line].place_info()["x"]) - 3)
                self.update()
            for _ in range(6):
                time.sleep(sleep)
                self.lines[line].place_configure(x=int(self.lines[line].place_info()["x"]) + 3)
                self.update()
            for _ in range(3):
                time.sleep(sleep)
                self.lines[line].place_configure(x=int(self.lines[line].place_info()["x"]) - 3)
                self.update()
        for _ in range(12):
            time.sleep(sleep)

        for b in self.buttons[line]:
            b.unlock()
            b.reset()

        self.playable = was_playable

    def start(self):
        self.mainloop()
