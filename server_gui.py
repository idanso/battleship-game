import threading
import logging
import tkinter as tk
import traceback
from tkinter import messagebox
import Pmw
import multiConnectionServer
import client_gui
import pandas as pd
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg,
)
import server_service

graphWindow = None
game_handler_locker = server_service.Game_handler_locker()

class ServerScreen(tk.Tk):
    """
        ServerScreen represents a server with it's screen and data
    """
    def __init__(self):
        # some screen settings
        super().__init__()
        self.protocol("WM_DELETE_WINDOW",
                      lambda: self.destroy() if messagebox.askokcancel("Quit", "Do you want to quit?") else None)
        self.attributes("-topmost", True)
        self.title('Battleship Server')
        self.resizable(True, True)
        self.geometry("500x360")

        self.plyr_1_name = None
        self.plyr_2_name = None
        self.error = None
        self.log_win = None

        self.title_headline = tk.Label(
            master=self,
            text="Battleship Server",
            width=20,
            height=3
        )
        self.title_headline.place(x=250, y=0, anchor="n")
        self.title_player_1 = tk.Label(
            master=self,
            text="Player 1",
            width=20,
        )
        self.title_player_1.place(x=100, y=80, anchor="n")
        self.plyr_1_ent = tk.Entry(
            master=self,
            width=20
        )
        self.plyr_1_ent.place(x=100, y=120, anchor="n")
        self.title_player_2 = tk.Label(
            master=self,
            text="Player 2",
            width=20,
        )
        self.title_player_2.place(x=400, y=80, anchor="n")

        self.plyr_2_ent = tk.Entry(
            master=self,
            width=20
        )
        self.plyr_2_ent.place(x=400, y=120, anchor="n")

        self.new_game_btn = tk.Button(
            master=self,
            text="New Game",
            command=self.new_game_command,
            width=20,
            height=3
        )
        self.new_game_btn.place(x=250, y=200, anchor="n")

        self.show_log_btn = tk.Button(
            master=self,
            text="Show log",
            command=self.log_button,
            width=20,
            height=3
        )
        self.show_log_btn.place(x=150, y=280, anchor="n")

        self.show_graph_btn = tk.Button(
            master=self,
            text="Show graph",
            command=self.show_graph_command,
            width=20,
            height=3
        )
        self.show_graph_btn.place(x=350, y=280, anchor="n")

        self.filename = "Log\\Server_log.log"
        self.text = None
        self.showing_log = False

    def show_graph_command(self):
        """function for the show graph button that open a new window and displays the graph"""
        try:
            global graphWindow
            graph_Window = tk.Toplevel(self)
            graph_Window.attributes("-topmost", True)
            graph_Window.title('Result Summary')
            graph_Window.resizable(True, True)
            graph_Window.protocol("WM_DELETE_WINDOW", lambda: graph_Window.destroy())
            data = multiConnectionServer.get_results_data()
            if len(data["wins"]) > 5:
                data["plot"] = data["plot"][:5]
            if len(data["games"]) > 5:
                data["games"] = data["games"][:5]

            wins_lst = list(map(lambda user: user.score["win"], data["wins"][:5]))
            players_lst = list(map(lambda user: user.name, data["wins"][:5]))

            figure1 = Figure(figsize=(5, 4), dpi=100)
            ax1 = figure1.add_subplot(111)
            bar1 = FigureCanvasTkAgg(figure1, graph_Window)
            bar1.get_tk_widget().pack(side=tk.LEFT, fill=tk.BOTH)
            df1 = pd.DataFrame(wins_lst, index=players_lst, columns=["Wins"])
            df1.plot(kind='bar', ax=ax1)
            ax1.set_title('Top 5 Players most wins')

            games_lst = list(map(lambda user: user.score["win"] + user.score["lose"], data["games"][:5]))
            players_lst = list(map(lambda user: user.name, data["games"][:5]))

            figure2 = Figure(figsize=(5, 4), dpi=100)
            ax2 = figure2.add_subplot(111)
            line2 = FigureCanvasTkAgg(figure2, graph_Window)
            line2.get_tk_widget().pack(side=tk.LEFT, fill=tk.BOTH)
            df2 = pd.DataFrame(games_lst, index=players_lst, columns=["Games"])
            df2.plot(kind='bar', ax=ax2)
            ax2.set_title('Top 5 Players most games')

        except Exception as e:
            logging.error(traceback.format_exc())


    def new_game_command(self):
        """fuction for the start a new client upon press of new game button """
        self.plyr_1_name = self.plyr_1_ent.get()
        self.plyr_2_name = self.plyr_2_ent.get()
        if self.plyr_1_name and self.plyr_2_name:
            self.plyr_1_ent.delete(0, 'end')
            self.plyr_2_ent.delete(0, 'end')
            start_client((self.plyr_1_name, self.plyr_2_name))
            self.plyr_1_name = None
            self.plyr_2_name = None

            if self.error:
                self.error.destroy()
        else:
            self.error = tk.Label(
                master=self,
                text="Please enter both names",
                width=20,
                height=3,
                fg='#f00'
            )
            self.error.place(x=250, y=30, anchor="n")



    def log_button(self):
        """fuction for the reveal the log upon press of the show log button """
        if not self.showing_log:
            self.geometry("630x750")
            self.show_log_btn.configure(text="Hide log")
            self.frame = tk.Frame(self, padx=5, pady=5)
            self.frame.place(x=250, y=350, anchor="n")
            self.text = Pmw.ScrolledText(self.frame,
                             borderframe=5,
                             vscrollmode='dynamic',
                             hscrollmode='dynamic',
                             labelpos='n',
                             label_text='Server Log',
                             text_width=90,
                             text_height=23,
                             text_wrap='none',
                             )
            self.text.insert('end', open(self.filename, 'r').read())
            self.showing_log = True
            self.text.pack()
        else:
            self.geometry("500x360")
            self.show_log_btn.configure(text="Show log")
            self.showing_log = False
            self.frame.place_forget()


def show_screen():
    """function that start a new window to make sure before closing"""
    screen = ServerScreen()
    screen.mainloop()

def start_client(players=('idan', 'shiran')):
    """
    Function for starting new client and the client gui as a thread
    :Param players: new players names for the new game
    """
    global game_handler_locker
    for player in players:
        user = game_handler_locker.get_game_handler.get_user_by_name(player)
        if not user:
            game_handler_locker.get_game_handler.add_user(player)

    game_handler_locker.get_game_handler.readyPlayers = players
    client_gui_thread = threading.Thread(target=client_gui.start_client_gui)
    client_gui_thread.setDaemon(True)
    game_handler_locker.get_game_handler.ready_thread = client_gui_thread
    client_gui_thread.start()


if __name__ == "__main__":

    server_main_thread = threading.Thread(target=multiConnectionServer.server_main, args=(game_handler_locker,))
    server_main_thread.start()
    show_screen()
    multiConnectionServer.end_server_thread()