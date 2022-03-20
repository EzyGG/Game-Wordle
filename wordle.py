import tkinter as tk
import time
import unidecode
import ezyapi.contants as consts
import ezyapi.game_manager as manager
from random import choice

import db_5_7980


GAME_VERSION = manager.__current_version


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
    def __init__(self, master, letter: str = "", theme: Theme = Theme.LIGHT(), state: str = State.NONE, locked=False,
                 width_without_pad=90, height_without_pad=90, padx=5, pady=5, radius=25, text_size=50):
        super().__init__(master)

        self.theme = theme
        self.height_without_pad, self.width_without_pad = height_without_pad, width_without_pad
        self.padx, self.pady = padx, pady
        self.text_size = text_size
        self.radius = radius
        self.locked = locked
        self.state = state
        self.letter = letter

        self.config(bd=0, highlightthickness=0, height=self.height_without_pad + self.pady * 2, width=self.width_without_pad + self.padx * 2)
        self.bg_rect = self.round_rectangle(self.padx, self.pady, self.width_without_pad + self.padx, self.height_without_pad + self.pady, radius=self.radius)
        self.border_rect = self.round_rectangle(self.padx, self.pady, self.width_without_pad + self.padx, self.height_without_pad + self.pady, radius=self.radius)
        self.rect = self.round_rectangle(self.padx + 1, self.pady + 1, self.width_without_pad + self.padx - 1, self.height_without_pad + self.pady - 1, tags="#", radius=self.radius - 1)
        self.text = self.create_text(int((self.width_without_pad + self.padx * 2) / 2), int((self.height_without_pad + self.pady * 2) / 2), tags="#", text=self.letter, anchor="center")
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
        font = (self.theme.letter_font[0] if len(self.theme.letter_font) else "",
                self.text_size,
                self.theme.letter_font[2] if len(self.theme.letter_font) >= 3 else "")
        self.config(bg=self.theme.bg)
        self.itemconfig(self.bg_rect, fill=self.theme.bg)
        self.itemconfig(self.border_rect, fill=self.theme.border)
        self.itemconfig(self.text, fill=self.theme.fg, font=font)
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

    def round_rectangle(self, x1, y1, x2, y2, radius=None, master_to_update=None, **kwargs):
        rad = self.radius if radius is None else radius
        # if update is False a new rounded rectangle's id will be returned else updates existing rounded rect.
        # source: https://stackoverflow.com/a/44100075/15993687
        points = [x1 + rad, y1, x1 + rad, y1, x2 - rad, y1, x2 - rad, y1, x2, y1, x2, y1 + rad,
                  x2, y1 + rad, x2, y2 - rad, x2, y2 - rad, x2, y2, x2 - rad, y2, x2 - rad, y2,
                  x1 + rad, y2, x1 + rad, y2, x1, y2, x1, y2 - rad, x1, y2 - rad, x1, y1 + rad,
                  x1, y1 + rad, x1, y1]
        if not master_to_update:
            return self.create_polygon(points, **kwargs, smooth=True)
        else:
            self.coords(master_to_update, points)

    def reveal_animation(self, reveal_func=None):
        sleep, step = 0.01, 4
        break_height = int(4 / 9 * self.height_without_pad)

        for i in range(0, break_height, step):
            self.round_rectangle(self.padx, self.pady + i, self.width_without_pad + self.padx, self.height_without_pad + self.pady - i, radius=self.radius, master_to_update=self.border_rect)
            self.round_rectangle(self.padx + 1, self.pady + 1 + i, self.width_without_pad + self.padx - 1, self.height_without_pad + self.pady - 1 - i, tags="#", radius=self.radius - 1, master_to_update=self.rect)
            self.update()
            time.sleep(sleep)

        reveal_func()

        for i in range(0, break_height, step):
            self.round_rectangle(self.padx, self.pady + break_height - i, self.width_without_pad + self.padx, self.height_without_pad + self.pady - break_height + i, radius=self.radius, master_to_update=self.border_rect)
            self.round_rectangle(self.padx + 1, self.pady + 1 + break_height - i, self.width_without_pad + self.padx - 1, self.height_without_pad + self.pady - 1 - break_height + i, tags="#", radius=self.radius - 1, master_to_update=self.rect)
            self.update()
            time.sleep(sleep)


        self.round_rectangle(self.padx, self.pady, self.width_without_pad + self.padx, self.height_without_pad + self.pady, radius=self.radius, master_to_update=self.border_rect)
        self.round_rectangle(self.padx + 1, self.pady + 1, self.width_without_pad + self.padx - 1, self.height_without_pad + self.pady - 1, tags="#", radius=self.radius - 1, master_to_update=self.rect)


class Wordle(tk.Tk):
    DB = list(set(w.title() if w.isupper() else w for w in str(db_5_7980.DB).replace("\n", " ")
                  .replace("  ", " ").split(" ") if w and w.isalpha()))
    REGULARS = list(set(w.title() if w.isupper() else w for w in str(db_5_7980.REGULAR).replace("\n", " ")
                        .replace("  ", " ").split(" ") if w and w.isalpha()))

    def __init__(self, title: str = "Wordle (%VERSION%)", label: str = "Wordle", theme: Theme = Theme.DARK(),
                 word: str | None = None, preset: list[list[dict]] | None = None, width_without_pad=90,
                 height_without_pad=90, padx=5, pady=5, text_size=50, radius: int | None = None,
                 commit: bool = True):
        self.theme = theme
        self.label = label
        self.commit = commit

        super().__init__(title)

        self.title(title.replace("%VERSION%", GAME_VERSION.get_version()))
        try:
            self.iconbitmap("Wordle Icon.ico")
        except Exception:
            pass

        self.width_without_pad, self.height_without_pad = width_without_pad, height_without_pad
        self.padx, self.pady = padx, pady
        self.text_size = text_size
        self.radius = radius

        self.title_lbl = tk.Label(self, text=label)
        self.lines = [tk.Frame(self) for _ in range(6 if preset is None else len(preset))]
        self.buttons = [[RoundedButton(l, width_without_pad=self.width_without_pad, padx=self.padx, height_without_pad=self.height_without_pad, pady=self.pady, text_size=self.text_size)
                         if preset is None else RoundedButton(l, **preset[i][j] | {"width_without_pad": self.width_without_pad, "padx": self.padx, "height_without_pad": self.height_without_pad, "pady": self.pady, "text_size": self.text_size, "radius": int((self.width_without_pad + self.padx * 2 + self.height_without_pad + self.pady * 2) / 2 / 4) if self.radius is None else self.radius})
                         for j in range(5 if preset is None else len(preset[i]))] for i, l in enumerate(self.lines)]

        self.playable = True
        self.cursor = [0, 0]
        self.word = choice(self.REGULARS) if word is None else word

        self.update_all()

        self.reset_geometry()

        self.bind("<Key>", self.on_keypress)
        self.bind("<BackSpace>", self.on_backspace)
        self.bind("<Return>", self.on_return)

    def clear(self):
        for widgets in self.winfo_children():
            widgets.forget()

    def update_all(self):
        self.clear()

        self.config(bg=self.theme.bg)

        self.title_lbl.config(bg=self.theme.bg, fg=self.theme.fg, font=self.theme.title_font)
        self.title_lbl.place(y=0, relx=0.5, anchor="n")

        for i, l in enumerate(self.lines):
            l.config(bg=self.theme.bg)
            # y -> i * <box_size>
            # + <font_size> * 1.5(=> natural pady)
            # + half_of_<box_size>(=> because of anchor="center")
            # + 5(=> title pady)
            l.place(y=i * (self.height_without_pad + self.pady * 2) + self.theme.title_font[1] * 1.5 + (self.height_without_pad + self.pady * 2) / 2 + 5, relx=0.5, anchor="center")

        for l in self.buttons:
            for b in l:
                b.change_theme(self.theme)
                b.pack(side="left")

        self.update()

    def get_geometry(self) -> tuple[int, int]:
        box_w, box_h = self.width_without_pad + self.padx * 2, self.height_without_pad + self.pady * 2
        box_pad = 20
        row, col = len(self.lines), len(self.buttons[0] if self.buttons else 0)
        title_w, title_h = self.title_lbl.winfo_width(), self.title_lbl.winfo_height()
        return int(max(box_w * col + box_pad * 2, title_w)), int(box_h * row + box_pad + title_h)

    def reset_geometry(self):
        self.geometry(f"{self.get_geometry()[0]}x{self.get_geometry()[1]}")

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

        word, objective = unidecode.unidecode(word.lower()), str(unidecode.unidecode(self.word).lower())

        if word not in [unidecode.unidecode(d.lower()) for d in self.DB]:
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
                objective = objective.replace(c, "#", 1)

        self.playable = False
        for b, a in zip(self.buttons[self.cursor[0]], answers):
            b.reveal_animation(b.good if a == State.GOOD else b.misplaced if a == State.MISPLACED else b.null)

        if not sum([0 if a == State.GOOD else 1 for a in answers]) or self.cursor[0] == len(self.buttons) - 1:
            self.score()
            return

        self.cursor[0] += 1
        self.cursor[1] = 0
        self.playable = True

    def score(self):
        for bts in self.buttons:
            for b in bts:
                if b.state == State.HOVER:
                    b.unlock()
                    b.change_state(State.NONE)
                    b.lock()
        Scores(theme=self.theme, word=self.word, commit=self.commit,
               preset=[[self.buttons[i][j].get_data() for j in range(len(self.buttons[i]))] for i in range(len(self.buttons))]).start()

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

    def __init__(self, preset: list[list[dict]], word: str = None, title: str = "Wordle - Scores (%VERSION%)", label: str = "Score", theme: Theme = Theme.DARK(), commit: bool = True):
        super().__init__(title=title, label=label, theme=theme, preset=preset, height_without_pad=20, pady=2, width_without_pad=20, padx=2, text_size=10)
        if word:
            self.word = word
        self.playable = False

        self.commit = commit
        self.score = 0

        self.count_null, self.count_misplaced, self.count_good, self.count_none = 0, 0, 0, 0

        self.won = not min(sum(1 for b in bts if b.state != State.GOOD) for bts in self.buttons)

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

        if not self.won:
            self.score = int(self.score / 2)

        self.title_lbl.config(text=label + ": " + str(self.score))

        self.frame = tk.Frame(self)
        self.line_frame1 = tk.Frame(self.frame, height=3)
        self.line_frame2 = tk.Frame(self.frame, height=3)
        self.buttons_config = {"height_without_pad": 30, "pady": 3, "width_without_pad": 30, "padx": 3, "text_size": 15, "radius": 7}
        self.button_null = RoundedButton(self.frame, state=State.NULL, locked=True, **self.buttons_config)
        self.button_misplaced = RoundedButton(self.frame, state=State.MISPLACED, locked=True, **self.buttons_config)
        self.button_good = RoundedButton(self.frame, state=State.GOOD, locked=True, **self.buttons_config)
        self.button_none = RoundedButton(self.frame, state=State.NONE, locked=True, **self.buttons_config)
        self.labels_config = {"bg": self.theme.bg, "fg": consts.COLOR_GRAY, "font": self.theme.text_font}
        self.word_reveal = tk.Label(self.frame, text=f"Mot: {self.word}", **self.labels_config)
        self.times_null_x = tk.Label(self.frame, text="x", **self.labels_config)
        self.times_null_n = tk.Label(self.frame, text=f"{self.count_null}", **self.labels_config)
        self.times_misplaced_x = tk.Label(self.frame, text="x", **self.labels_config)
        self.times_misplaced_n = tk.Label(self.frame, text=f"{self.count_misplaced}", **self.labels_config)
        self.times_good_x = tk.Label(self.frame, text="x", **self.labels_config)
        self.times_good_n = tk.Label(self.frame, text=f"{self.count_good}", **self.labels_config)
        self.times_none_x = tk.Label(self.frame, text="x", **self.labels_config)
        self.times_none_n = tk.Label(self.frame, text=f"{self.count_none}", **self.labels_config)
        self.score_label = tk.Label(self.frame, text="Score", **self.labels_config)
        self.score_null = tk.Label(self.frame, text=f"{self.count_null * self.NULL_SCORE}", **self.labels_config)
        self.score_misplaced = tk.Label(self.frame, text=f"{self.count_misplaced * self.MISPLACED_SCORE}", **self.labels_config)
        self.score_good = tk.Label(self.frame, text=f"{self.count_good * self.GOOD_SCORE}", **self.labels_config)
        self.score_none = tk.Label(self.frame, text=f"{self.count_none * self.NONE_SCORE}", **self.labels_config)
        self.score_total = tk.Label(self.frame, text="{:}".format(int((self.count_null * self.NULL_SCORE + self.count_misplaced * self.MISPLACED_SCORE + self.count_good * self.GOOD_SCORE + self.count_none * self.NONE_SCORE) / (1 if self.won else 2))), **self.labels_config | {"fg": self.theme.fg})
        self.exp_label = tk.Label(self.frame, text="EXP", **self.labels_config)
        self.exp_null = tk.Label(self.frame, text=f"{self.count_null * self.NULL_EXP}", **self.labels_config)
        self.exp_misplaced = tk.Label(self.frame, text=f"{self.count_misplaced * self.MISPLACED_EXP}", **self.labels_config)
        self.exp_good = tk.Label(self.frame, text=f"{self.count_good * self.GOOD_EXP}", **self.labels_config)
        self.exp_none = tk.Label(self.frame, text=f"{self.count_none * self.NONE_EXP}", **self.labels_config)
        self.exp_total = tk.Label(self.frame, text="{:+}".format(int((self.count_null * self.NULL_EXP + self.count_misplaced * self.MISPLACED_EXP + self.count_good * self.GOOD_EXP + self.count_none * self.NONE_EXP) / (1 if self.won else 2))), **self.labels_config | {"fg": consts.COLOR_EXP})
        self.gp_label = tk.Label(self.frame, text="GP", **self.labels_config)
        self.gp_null = tk.Label(self.frame, text=f"{self.count_null * self.NULL_GP}", **self.labels_config)
        self.gp_misplaced = tk.Label(self.frame, text=f"{self.count_misplaced * self.MISPLACED_GP}", **self.labels_config)
        self.gp_good = tk.Label(self.frame, text=f"{self.count_good * self.GOOD_GP}", **self.labels_config)
        self.gp_none = tk.Label(self.frame, text=f"{self.count_none * self.NONE_GP}", **self.labels_config)
        self.gp_total = tk.Label(self.frame, text="{:+}".format(int((self.count_null * self.NULL_GP + self.count_misplaced * self.MISPLACED_GP + self.count_good * self.GOOD_GP + self.count_none * self.NONE_GP) / (1 if self.won else 2))), **self.labels_config | {"fg": consts.COLOR_GP})
        self.total_label = tk.Label(self.frame, text="Total", **self.labels_config | {"fg": self.theme.fg})
        self.victory_label = tk.Label(self.frame, text="Victoire !", **self.labels_config | {"fg": consts.COLOR_GREEN})
        self.defeat_label = tk.Label(self.frame, text="Défaite... (/2)", **self.labels_config | {"fg": consts.COLOR_RED})

        self.frame.place(rely=1, relx=0.5, anchor="s")
        self.word_reveal.grid(sticky="news", row=0, column=0, columnspan=99, pady=5)
        self.line_frame1.grid(sticky="news", row=1, column=0, columnspan=99, pady=5)
        self.line_frame2.grid(sticky="news", row=8, column=0, columnspan=99, pady=5)
        if self.won:
            self.victory_label.grid(row=7, column=0, columnspan=6)
        else:
            self.defeat_label.grid(row=7, column=0, columnspan=6)

        self.button_null.grid(row=3, column=0)
        self.button_misplaced.grid(row=4, column=0)
        self.button_good.grid(row=5, column=0)
        self.button_none.grid(row=6, column=0)
        self.total_label.grid(row=9, column=0, columnspan=3, sticky="e", pady=12)

        self.times_null_x.grid(row=3, column=1)
        self.times_null_n.grid(row=3, column=2, sticky="e")
        self.times_misplaced_x.grid(row=4, column=1)
        self.times_misplaced_n.grid(row=4, column=2, sticky="e")
        self.times_good_x.grid(row=5, column=1)
        self.times_good_n.grid(row=5, column=2, sticky="e")
        self.times_none_x.grid(row=6, column=1)
        self.times_none_n.grid(row=6, column=2, sticky="e")

        self.score_label.grid(row=2, column=3, padx=7)
        self.score_null.grid(row=3, column=3)
        self.score_misplaced.grid(row=4, column=3)
        self.score_good.grid(row=5, column=3)
        self.score_none.grid(row=6, column=3)
        self.score_total.grid(row=9, column=3)

        self.exp_label.grid(row=2, column=4, padx=7)
        self.exp_null.grid(row=3, column=4)
        self.exp_misplaced.grid(row=4, column=4)
        self.exp_good.grid(row=5, column=4)
        self.exp_none.grid(row=6, column=4)
        self.exp_total.grid(row=9, column=4)

        self.gp_label.grid(row=2, column=5, padx=7)
        self.gp_null.grid(row=3, column=5)
        self.gp_misplaced.grid(row=4, column=5)
        self.gp_good.grid(row=5, column=5)
        self.gp_none.grid(row=6, column=5)
        self.gp_total.grid(row=9, column=5)

        self.unbind("<Configure>")
        self.bind("<Configure>", self.update_all_overridden)

        self.update()
        self.reset_geometry_overridden()

        if self.commit and manager.linked():
            manager.start_new_game()
            manager.commit_new_set(self.won,
                                   int((self.count_null * self.NULL_EXP + self.count_misplaced * self.MISPLACED_EXP + self.count_good * self.GOOD_EXP + self.count_none * self.NONE_EXP) / (1 if self.won else 2)),
                                   int((self.count_null * self.NULL_GP + self.count_misplaced * self.MISPLACED_GP + self.count_good * self.GOOD_GP + self.count_none * self.NONE_GP) / (1 if self.won else 2)),
                                   other=f"score={int((self.count_null * self.NULL_SCORE + self.count_misplaced * self.MISPLACED_SCORE + self.count_good * self.GOOD_SCORE + self.count_none * self.NONE_SCORE) / (1 if self.won else 2))}")

    def update_all_overridden(self, event=None):
        self.update_all()
        self.frame.config(bg=self.theme.bg)
        self.line_frame1.config(bg=self.theme.fg)
        self.line_frame2.config(bg=self.theme.fg)

        self.button_null.change_theme(self.theme)
        self.button_misplaced.change_theme(self.theme)
        self.button_good.change_theme(self.theme)
        self.button_none.change_theme(self.theme)

    def get_geometry_overridden(self) -> tuple[int, int]:
        box_w, box_h = self.width_without_pad + self.padx * 2, self.height_without_pad + self.pady * 2
        box_pad = 20
        row, col = len(self.lines), len(self.buttons[0] if self.buttons else 0)
        title_w, title_h = self.title_lbl.winfo_width(), self.title_lbl.winfo_height()
        frame_w, frame_h = self.frame.winfo_width(), self.frame.winfo_height()
        return int(max(box_w * col + box_pad * 2, title_w, frame_w)), int(box_h * row + box_pad + title_h + frame_h)

    def reset_geometry_overridden(self):
        self.geometry(f"{self.get_geometry_overridden()[0]}x{self.get_geometry_overridden()[1]}")

