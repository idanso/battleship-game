import sys
import threading
import tkinter as tk
from tkinter import messagebox
import Pmw
import multiConnectionServer


class ServerScreen(tk.Frame):
    """
        ServerScreen represents a server with it's screen and data
    """
    def __init__(self, window):
        # some screen settings
        window.attributes("-topmost", True)
        window.title('Battleship Server')
        window.resizable(True, True)

        tk.Frame.__init__(self, master=window, width=500, height=500)
        self.window = window
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
        """fuction for the show graph button that open a new window and displays the graph"""
        graph_Window = tk.Toplevel(self)
        graph_Window.attributes("-topmost", True)
        graph_Window.title('Players graph')
        graph_Window.resizable(True, True)
        #to show graph just do
        #plt.show()


    def new_game_command(self):
        """fuction for the start a new client upon press of new game button """
        self.plyr_1_name = self.plyr_1_ent.get()
        self.plyr_2_name = self.plyr_2_ent.get()
        if self.plyr_1_name and self.plyr_2_name:
            self.plyr_1_ent.delete(0, 'end')
            self.plyr_2_ent.delete(0, 'end')
            # TODO actually start a game
            multiConnectionServer.start_client((self.plyr_1_name, self.plyr_2_name))
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
            self.show_log_btn.configure(text="Hide log")
            self.frame = tk.Frame(self, padx=5, pady=10)
            self.frame.place(x=250, y=350, anchor="n")
            self.text = Pmw.ScrolledText(self.frame,
                             borderframe=5,
                             vscrollmode='dynamic',
                             hscrollmode='dynamic',
                             labelpos='n',
                             label_text='Server Log',
                             text_width=55,
                             text_height=4,
                             text_wrap='none',
                             )
            self.text.insert('end', open(self.filename, 'r').read())
            self.showing_log = True
            self.text.pack()
        else:
            self.show_log_btn.configure(text="Show log")
            self.showing_log = False
            self.frame.place_forget()


def show_screen():
    """function that start a new window to make sure before closing"""
    root = tk.Tk()
    root.protocol("WM_DELETE_WINDOW", lambda : root.destroy() if messagebox.askokcancel("Quit", "Do you want to quit?") else None)
    ServerScreen(root).pack(expand=True, fill='both')
    root.mainloop()


if __name__ == "__main__":

    server_main_thread = threading.Thread(target=multiConnectionServer.server_main)
    server_main_thread.start()
    show_screen()
    multiConnectionServer.end_server_thread()