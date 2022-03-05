# import ezyapi.game_manager as manager
# from ezyapi.mysql_connection import DatabaseConnexionError
# from ezyapi.sessions import UserNotFoundException
# from ezyapi.UUID import UUID
# from threading import Thread
# from time import sleep
# from tkinter import *
# from random import randint, choice, shuffle
#
# GAME_UUID = UUID.parseUUID("ceb98c87-4800-49d0-3333-3b1aa79ba293")
# GAME_VERSION = manager.GameVersion("v1.0")
#
# class Error(Tk):
#     def __init__(self, name: str, desc: str):
#         super().__init__("err")
#         self.app_bg = 'black'
#         self.app_fg = 'white'
#         self.app_circle_color = 'blue'
#         self.app_cross_color = 'red'
#
#         self.title("Erreur")
#         # self.resizable(False, False)
#         self.geometry("300x300")
#         self.configure(background=self.app_bg)
#         try:
#             self.iconbitmap("tic_tac_toe.ico")
#         except Exception:
#             pass
#
#         self.name, self.desc = name, desc
#
#         self.name_label = Label(self, bg=self.app_bg, fg=self.app_fg, font=("", 16, "bold"), wraplengt=300, text=name)
#         self.name_label.pack(side=TOP, pady=10)
#
#         self.desc_label = Label(self, bg=self.app_bg, fg=self.app_fg, wraplengt=300, text=desc)
#         self.desc_label.pack(side=TOP, pady=10)
#
#         self.opt_frame = Frame(self, bg=self.app_bg)
#         self.cont_frame = Frame(self.opt_frame, bg=self.app_circle_color)
#         self.cont_btn = Button(self.cont_frame, activebackground=self.app_bg, bg=self.app_bg, bd=0, relief=SOLID,
#                                width=12, activeforeground=self.app_circle_color, fg=self.app_circle_color,
#                                highlightcolor=self.app_circle_color, font=("", 12, "bold"), text="Continuer !",
#                                command=self.cont_cmd)
#         self.cont_btn.pack(padx=1, pady=1)
#         self.cont_frame.pack(side=LEFT, padx=5)
#         self.quit_frame = Frame(self.opt_frame, bg=self.app_cross_color)
#         self.quit_btn = Button(self.quit_frame, activebackground=self.app_bg, bg=self.app_bg, bd=0, relief=SOLID,
#                                width=12, activeforeground=self.app_cross_color, fg=self.app_cross_color,
#                                highlightcolor=self.app_cross_color, font=("", 12, "bold"), text="Quitter.",
#                                command=self.quit_cmd)
#         self.quit_btn.pack(padx=1, pady=1)
#         self.quit_frame.pack(side=RIGHT, padx=5)
#         self.opt_frame.pack(side=BOTTOM, pady=5)
#
#         self.protocol("WM_DELETE_WINDOW", self.quit_cmd)
#         self.bind("<Configure>", self.event_handler)
#         self.bind("<Return>", self.on_return)
#         self.quit_btn.focus_set()
#
#         self.mainloop()
#
#     def on_return(self, event=None):
#         if self.focus_get() == self.cont_btn:
#             self.cont_cmd()
#         elif self.focus_get() == self.quit_btn:
#             self.quit_cmd()
#
#     def cont_cmd(self, event=None):
#         self.destroy()
#
#     def quit_cmd(self, event=None):
#         try:
#             sys.exit(1)
#         except NameError:
#             quit(1)
#
#     def event_handler(self, event=None):
#         new_wrap = int(self.winfo_geometry().split("x")[0]) - 5
#         self.name_label.config(wraplengt=new_wrap)
#         self.desc_label.config(wraplengt=new_wrap)
#
#
# class Update(Thread):
#     def __init__(self, from_version: manager.GameVersion = manager.GameVersion(),
#                  to_version: manager.GameVersion = manager.GameVersion()):
#         super().__init__()
#         self.running = True
#
#         self.from_version, self.to_version = from_version, to_version
#         self.tk: Tk = None
#
#     def stop(self):
#         self.running = False
#         if self.tk:
#             self.tk.destroy()
#         raise Exception("Thread Ending.")
#
#     def run(self):
#         self.tk = Tk("update")
#         self.app_bg = 'black'
#         self.app_fg = 'white'
#
#         self.tk.title("Mise-à-Jour")
#         self.tk.geometry("375x320")
#         self.tk.configure(background=self.app_bg)
#         try:
#             self.tk.iconbitmap("tic_tac_toe.ico")
#         except Exception:
#             pass
#
#         self.magic_frame = Frame(self.tk)
#         self.internal_frame = Frame(self.magic_frame, bg=self.app_bg)
#
#         self.magic_frame.pack_propagate(0)
#         self.internal_frame.pack_propagate(0)
#
#         self.title_frame = Frame(self.internal_frame, bg=self.app_bg)
#         self.name_label = Label(self.title_frame, bg=self.app_bg, fg=self.app_fg, font=("", 16, "bold"), text="Mise-à-Jour")
#         self.name_label.pack(side=TOP)
#
#         self.version_label = Label(self.title_frame, bg=self.app_bg, fg=self.app_fg, font=("", 12, "bold"), text=f"{self.from_version}  →  {self.to_version}")
#         self.version_label.pack(side=TOP)
#         self.title_frame.pack(side=TOP, fill=X, expand=True, pady=20, padx=20)
#
#         self.desc_label = Label(self.internal_frame, bg=self.app_bg, fg=self.app_fg, text="Nous remettons à jour votre jeu pour vous assurer une experience sans égale. Actuellement, nous transferont et compilons les nouveaux fichiers depuis la base de donnée. Si le jeu est important ou que votre connexion est mauvaise, l'action peut durer plusieurs minutes... Revenez un peu plus tard. (Temps éstimé: 5sec)")
#         self.desc_label.pack(side=BOTTOM, pady=20, padx=20)
#
#         self.internal_frame.pack(fill=BOTH, expand=True, padx=7, pady=7)
#         self.magic_frame.pack(fill=BOTH, expand=True, padx=30, pady=30)
#
#         self.tk.protocol("WM_DELETE_WINDOW", self.quit)
#         self.tk.bind("<Configure>", self.on_configure)
#
#         self.forced_exit_count = 0
#
#         while self.running:
#             self.loop()
#             self.tk.mainloop()
#         else:
#             self.quit()
#
#     def quit(self):
#         self.forced_exit_count += 1
#         if not self.running or self.forced_exit_count >= 20:
#             self.stop()
#
#     def on_configure(self, e=None):
#         wrap = int(self.tk.winfo_geometry().split("x")[0]) - 114  # 114 -> padx: 2*30 + 2*7 + 2*20
#         self.name_label.config(wraplengt=wrap)
#         self.desc_label.config(wraplengt=wrap)
#
#     def loop(self, infinite=True, random=True):
#         path = ["000", "100", "110", "010", "011", "001", "101", "111"]
#         color = [0, 0, 0]
#         while self.running:
#             temp_path = path[:]
#             if random:
#                 shuffle(temp_path)
#             for p in temp_path:
#                 run = True
#                 while run and self.running:
#                     run = False
#                     for i in range(len(color)):
#                         if p[i] == "0" and color[i] != 0:
#                             color[i] -= 2 if color[i] - 2 > 0 else 1
#                             run = True
#                         elif p[i] == "1" and color[i] != 255:
#                             color[i] += 2 if color[i] + 2 < 256 else 1
#                             run = True
#                     str_color = "#{color[0]:0>2X}{color[1]:0>2X}{color[2]:0>2X}".format(color=color)
#                     self.magic_frame.configure(bg=str_color)
#                     self.tk.update()
#                     sleep(0.0001)
#             if not infinite:
#                 break


# CONTINUE = "\n\nIf you Continue, you will not be able to get rewards and update the ranking."
# try:
#     try:
#         manager.setup(GAME_UUID, GAME_VERSION, __update=False)
#     except manager.UserParameterExpected as e:
#         Error("UserParameterExpected",
#               str(e) + "\nYou must run the game from the Launcher to avoid this error." + CONTINUE)
#     except UserNotFoundException as e:
#         Error("UserNotFoundException", str(e) + "\nThe user information given does not match with any user." + CONTINUE)
#
#     if not manager.updated():
#         u = Update(manager.__current_version, manager.__game_info.version)
#         u.start()
#         manager.update()
#         try:
#             u.stop()
#         except Exception:
#             pass
# except DatabaseConnexionError as e:
#     Error("DatabaseConnexionError",
#           str(e) + "\nThe SQL Serveur is potentially down for maintenance...\nWait and Retry Later." + CONTINUE)

# TicTacToe().start()

import wordle

wordle.Wordle().start()
