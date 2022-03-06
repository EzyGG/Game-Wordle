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
    def __init__(self, master, letter: str = "", theme: Theme = Theme.LIGHT(), state: str = State.NONE, locked=False):
        super().__init__(master)
        self.config(bd=0, highlightthickness=0, height=100, width=100)

        self.theme = theme
        self.radius = 25
        self.locked = locked
        self.state = state
        self.letter = letter

        self.bg_rect = self.round_rectangle(5, 5, 95, 95, radius=self.radius)
        self.border_rect = self.round_rectangle(5, 5, 95, 95, radius=self.radius)
        self.rect = self.round_rectangle(6, 6, 94, 94, tags="#", radius=self.radius - 1)
        self.text = self.create_text(50, 50, tags="#", text=letter, anchor="center")
        self.update_colors()

        self.tag_bind("#", "<ButtonPress>", lambda x: self.null(lock=False))
        self.tag_bind("#", "<ButtonRelease>", lambda x: self.hover())
        self.tag_bind("#", "<Enter>", lambda x: self.hover())
        self.tag_bind("#", "<Leave>", lambda x: self.reset())

    def __str__(self):
        return str(self.get_data())

    def __repr__(self):
        return str(self.get_data())

    def get_data(self):
        return {"letter": self.letter, "state": self.state, "locked": self.locked}

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


DEFAULT_PRESET = [[{'letter': 's', 'state': 'null', 'locked': True}, {'letter': 'a', 'state': 'null', 'locked': True},
                   {'letter': 'l', 'state': 'null', 'locked': True},
                   {'letter': 'u', 'state': 'misplaced', 'locked': True},
                   {'letter': 't', 'state': 'misplaced', 'locked': True}],
                  [{'letter': 'a', 'state': 'null', 'locked': True}, {'letter': 'n', 'state': 'null', 'locked': True},
                   {'letter': 't', 'state': 'misplaced', 'locked': True},
                   {'letter': 'r', 'state': 'null', 'locked': True}, {'letter': 'e', 'state': 'good', 'locked': True}],
                  [{'letter': 'm', 'state': 'null', 'locked': True},
                   {'letter': 'u', 'state': 'misplaced', 'locked': True},
                   {'letter': 'c', 'state': 'null', 'locked': True}, {'letter': 'h', 'state': 'null', 'locked': True},
                   {'letter': 'e', 'state': 'good', 'locked': True}],
                  [{'letter': 'e', 'state': 'good', 'locked': True}, {'letter': 't', 'state': 'good', 'locked': True},
                   {'letter': 'u', 'state': 'good', 'locked': True}, {'letter': 'd', 'state': 'good', 'locked': True},
                   {'letter': 'e', 'state': 'good', 'locked': True}],
                  [{'letter': '', 'state': 'none', 'locked': True},
                   {'letter': '', 'state': 'none', 'locked': True},
                   {'letter': '', 'state': 'none', 'locked': True},
                   {'letter': '', 'state': 'none', 'locked': True},
                   {'letter': '', 'state': 'none', 'locked': True}],
                  [{'letter': '', 'state': 'none', 'locked': True},
                   {'letter': '', 'state': 'none', 'locked': True},
                   {'letter': '', 'state': 'none', 'locked': True},
                   {'letter': '', 'state': 'none', 'locked': True},
                   {'letter': '', 'state': 'none', 'locked': True}]]


class Wordle(tk.Tk):
    def __init__(self, title: str = "Wordle", label: str = "Wordle", theme: Theme = Theme.DARK(),
                 word: str = "etude", preset: list[list[dict]] = DEFAULT_PRESET):
        self.theme = theme
        self.label = label

        self.DB = []
        try:
            with open("DB 5 7980.txt", "r") as file:
                self.DB = [unidecode.unidecode(w) for w in file.read().lower().replace("\n", " ").replace("  ", " ")
                           .split(" ") if w and w.isalpha() and w not in self.DB]
        except:
            from db_5_7980 import DB
            self.DB = [unidecode.unidecode(w) for w in str(DB).lower().replace("\n", " ").replace("  ", " ")
                       .split(" ") if w and w.isalpha() and w not in self.DB]

        super().__init__(title)
        self.title(title)
        self.geometry("550x680")

        self.title_lbl = tk.Label(self)
        self.lines = [tk.Frame(self) for _ in range(6 if preset is None else len(preset))]
        self.buttons = [[RoundedButton(l) if preset is None else RoundedButton(l, **preset[i][j])
                         for j in range(5 if preset is None else len(preset[i]))] for i, l in enumerate(self.lines)]

        self.playable = True
        self.cursor = [0, 0]
        self.word = choice(self.DB) if word is None else word
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

        self.title_lbl.config(bg=self.theme.bg, fg=self.theme.fg, font=self.theme.title_font, text=self.label)
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
        print(self.buttons)
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

        if not sum([0 if a == State.GOOD else 1 for a in answers]) or self.cursor == len(self.buttons) - 1:
            self.score()
            return

        self.cursor[0] += 1
        self.cursor[1] = 0
        self.playable = True

    def score(self):
        Scores(theme=self.theme, preset=[[self.buttons[i][j].get_data() for j in range(len(self.buttons[i]))] for i in range(len(self.buttons))]).start()

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


class Scores(Wordle):
    NULL_SCORE = 0
    NULL_EXP = 0
    NULL_GP = - 0.5
    MISPLACED_SCORE = 1
    MISPLACED_EXP = 5
    MISPLACED_GP = 0.5
    GOOD_SCORE = 3
    GOOD_EXP = 10
    GOOD_GP = 1
    NONE_SCORE = 3
    NONE_EXP = 15
    NONE_GP = 1

    def __init__(self, preset: list[list[dict]], title: str = "Wordle - Scores", label: str = "Scores", theme: Theme = Theme.DARK()):
        super().__init__(title=title, label=label, theme=theme, preset=preset)
        self.geometry("550x705")
        self.playable = False

        self.score = 0

        self.count_null, self.count_misplaced, self.count_good, self.count_none = 0, 0, 0, 0

        for l in self.buttons:
            for b in l:
                s = self.NULL_SCORE if b.state == State.NULL else self.MISPLACED_SCORE if b.state == State.MISPLACED else self.GOOD_SCORE if b.state == State.GOOD else self.NONE_SCORE if b.state == State.NONE else 0
                self.score += s
                if b.state == State.NONE:
                    self.count_none += 1
                elif b.state == State.GOOD:
                    self.count_good += 1
                elif b.state == State.MISPLACED:
                    self.count_misplaced += 1
                elif b.state == State.NULL:
                    self.count_null += 1
                b.unlock()
                b.change_letter(f"{str(s) if s else ''}")
                b.lock()

        self.title_lbl.config(text=label + " : " + str(self.score))

        self.frame = tk.Frame(self)
        self.line_frame = tk.Frame(self.frame, height=3)
        self.button_null = RoundedButton(self.frame, state=State.NULL, locked=True)
        self.button_misplaced = RoundedButton(self.frame, state=State.MISPLACED, locked=True)
        self.button_good = RoundedButton(self.frame, state=State.GOOD, locked=True)
        self.button_none = RoundedButton(self.frame, state=State.NONE, locked=True)
        self.times_null_x = tk.Label(self.frame, text="x")
        self.times_null_n = tk.Label(self.frame, text=f"{self.count_null}")
        self.times_misplaced_null_x = tk.Label(self.frame, text="x")
        self.times_misplaced_null_n = tk.Label(self.frame, text=f"{self.count_misplaced}")
        self.times_good_null_x = tk.Label(self.frame, text="x")
        self.times_good_null_n = tk.Label(self.frame, text=f"{self.count_good}")
        self.times_none_null_x = tk.Label(self.frame, text="x")
        self.times_none_null_n = tk.Label(self.frame, text=f"{self.count_none}")
        self.score_label = tk.Label(self.frame)
        self.score_null = tk.Label(self.frame)
        self.score_misplaced = tk.Label(self.frame)
        self.score_good = tk.Label(self.frame)
        self.score_none = tk.Label(self.frame)
        self.exp_label = tk.Label(self.frame)
        self.exp_null = tk.Label(self.frame)
        self.exp_misplaced = tk.Label(self.frame)
        self.exp_good = tk.Label(self.frame)
        self.exp_none = tk.Label(self.frame)
        self.gp_label = tk.Label(self.frame)
        self.gp_null = tk.Label(self.frame)
        self.gp_misplaced = tk.Label(self.frame)
        self.gp_good = tk.Label(self.frame)
        self.gp_none = tk.Label(self.frame)

        self.unbind("<Configure>")
        self.bind("<Configure>", self.update_all_overridden)

    def update_all_overridden(self, event=None):
        self.update_all()
        # y -> i * <box_size>
        # + <font_size> * 1.5(=> natural pady)
        # + half_of_<box_size>(=> because of anchor="center")
        # + 5(=> title pady)
        self.frame.config(bg=self.theme.bg)
        self.frame.place(y=len(self.buttons) * 100 + self.theme.title_font[1] * 1.5, relx=0.5, anchor="n")
        self.line_frame.config(bg=self.theme.fg)
        self.line_frame.grid(sticky="nesw", row=0, column=0, rowspan=2, pady=5)
        self.frame.grid_propagate()

        self.times_null_x.config(bg=self.theme.bg, fg=self.theme.fg, font=self.theme.text_font)
        self.times_null_x.grid(sticky="nesw", row=1, column=0, pady=5, padx=5)
        self.times_null_n.config(bg=self.theme.bg, fg=self.theme.fg, font=self.theme.text_font)
        self.times_null_n.grid(sticky="nesw", row=1, column=1, pady=5, padx=5)
