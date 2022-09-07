import sys
import tkinter as tk
from server_service import start_client


class ServerScreen(tk.Frame):
    def __init__(self, window):

        # some screen settings
        window.attributes("-topmost", True)
        window.title('Battleship Server')
        window.resizable(True, True)

        tk.Frame.__init__(self, master=window, width=500, height=500)

        self.plyr_1_name = None
        self.plyr_2_name = None
        self.error = None

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
            command=self.new_game_command,
            width=20,
            height=3
        )
        self.show_log_btn.place(x=250, y=280, anchor="n")

        #title_showlog = tk.Label(
         #   master=frame,
          #  text="Show Log",
           # width=20,
        #)
        #title_showlog.place(x=60, y=80, anchor="n")

    def new_game_command(self):
        self.plyr_1_name = self.plyr_1_ent.get()
        self.plyr_2_name = self.plyr_2_ent.get()
        if self.plyr_1_name and self.plyr_2_name:
            self.plyr_1_ent.delete(0, 'end')
            self.plyr_2_ent.delete(0, 'end')
            # TODO actually start a game
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

        print(self.plyr_1_name, self.plyr_2_name)




def show_screen():
    root = tk.Tk()
    ServerScreen(root).pack(expand=True, fill='both')
    root.mainloop()

if __name__ == "__main__":
    show_screen()