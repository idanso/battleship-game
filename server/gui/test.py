import tkinter as tk



def main():
    window = tk.Tk()
    window.wm_title("Server")

    frame = tk.Frame(master=window, width=500, height=500)
    frame.pack()

    title_headline = tk.Label(
        master=frame,
        text="Battleship Server",
        width=20,
        height=3
    )
    title_headline.place(x=250, y=0, anchor="n")
    title_player_1 = tk.Label(
        master=frame,
        text="Player 1",
        width=20,
    )
    title_player_1.place(x=100, y=80, anchor="n")
    plyr_1_ent = tk.Entry(
        master=frame,
        width=20
    )
    plyr_1_ent.place(x=100, y=120, anchor="n")
    title_player_2 = tk.Label(
        master=frame,
        text="Player 2",
        width=20,
    )
    title_player_2.place(x=400, y=80, anchor="n")

    plyr_2_ent = tk.Entry(
        master=frame,
        width=20
    )
    plyr_2_ent.place(x=400, y=120, anchor="n")

    #title_showlog = tk.Label(
     #   master=frame,
      #  text="Show Log",
       # width=20,
    #)
    #title_showlog.place(x=60, y=80, anchor="n")

    def new_game_command():
        plyr_1 = plyr_1_ent.get()
        plyr_2 = plyr_2_ent.get()

        # TODO actually start a game
        print(plyr_1, plyr_2)

    new_game_btn = tk.Button(
        master=frame,
        text="New Game",
        command=new_game_command,
        width=20,
        height=3
    )
    new_game_btn.place(x=250, y=200, anchor="n")

    show_log_btn = tk.Button(
        master=frame,
        text="Show log",
        command=new_game_command,
        width=20,
        height=3
    )
    show_log_btn.place(x=250, y=280, anchor="n")

    window.mainloop()


if __name__ == '__main__':
    main()
