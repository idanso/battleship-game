import tkinter as tk

window = tk.Tk()
window.wm_title("Server")

frame = tk.Frame(master=window, width=500, height=500)
frame.pack()

title = tk.Label(
    master=frame,
    text="Battleship Server",
    width=20,
    height=3
)
title.place(x=250, y=0, anchor="n")
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

new_game_btn = tk.Button(
    master=frame,
    text="New Game",
    width=20,
    height=3
)
new_game_btn.place(x=250, y=200, anchor="n")


def main():
    window.mainloop()


if __name__ == '__main__':
    main()
