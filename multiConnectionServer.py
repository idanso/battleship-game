import socket
import selectors
import types
import server_service
from shared import *

HOST = "127.0.0.1"  # The server's hostname or IP address
PORT = 1233  # The port used by the server


#################

def accept_wrapper(sock):
    conn, addr = sock.accept()  # Should be ready to read
    print(f"Accepted connection from {addr}")
    conn.setblocking(False)
    sock.settimeout(200)
    data = types.SimpleNamespace(addr=addr)
    events = selectors.EVENT_READ | selectors.EVENT_WRITE
    sel.register(conn, events, data=data)


def service_connection(key, mask):
    sock = key.fileobj
    data = key.data

    if mask & selectors.EVENT_READ:
        try:
            print("service_connection data address: " + str(data.addr))
            recv_data = receive_message(sock)  # Should be ready to read
            if recv_data:
                operation_mapper(sock, data.addr, recv_data)
        except Exception as e:
            print(e)


# TODO: consider replacing actions string to enums
def operation_mapper(sock, address, received_data):
    if received_data["Action"] == "start_game":
        if received_data["Quit"] == 0 or received_data["Quit"] == 1:
            game = game_handler.get_game_by_address(address)
            game.status = server_service.GameStatus.ENDED
            if received_data["Quit"] == 0:
                game.players[1]["win"] += 1
                game.players[0]["lose"] += 1
            elif received_data["Quit"] == 1:
                game.players[0]["win"] += 1
                game.players[1]["lose"] += 1

        game_handler.start_game(address,
                                received_data["Player_name"],
                                [received_data["Board_1"], received_data["Board_2"]])

        data_dict = dict({"Action": "start_game"})
        send_message(sock, data_dict)
    else:
        game = game_handler.get_game_by_address(address)
        if not game:
            print("couldn't find game from address: %s", received_data["Address"])
            # TODO: consider throwing error
            return
        if received_data["Action"] == "attack":
            board = game.boards[received_data["Hitted_player"]]
            hit_res = server_service.check_revealed_tile(
                board,
                received_data["Location"])
            if hit_res:
                board[received_data["Location"][0]][received_data["Location"][1]][1] = True
            win_res = server_service.check_for_win(board)
            if win_res:
                if received_data["Hitted_player"] == 1:
                    game.players[0]["win"] += 1
                    game.players[1]["lose"] += 1
                    game.status = server_service.GameStatus.ENDED
            data_dict = dict({"Action": "hit", "Success": hit_res, "Finished": win_res})
            send_message(sock, data_dict)
        # TODO: check if needed cause the score displayed in server side
        # elif received_data["Action"] == "scores":
        #     scores = game.score
        #     data_dict = dict({"Action": "hit", "Scores": scores})
        #     send_message(sock, data_dict)

        elif received_data["Action"] == "close_connection":
            print(f"Closing connection to {address}")
            game = game_handler.get_game_by_address(address)
            game.status = server_service.GameStatus.ENDED
            sel.unregister(sock)
            sock.close()
        else:
            print("unknown Action: %s", received_data["Action"])
            # TODO: consider throwing error


sel = selectors.DefaultSelector()

game_handler = server_service.ServerGamesHandler()

host, port = HOST, PORT  # sys.argv[1], int(sys.argv[2])
lsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
lsock.bind((host, port))
lsock.listen()
print(f"Listening on {(host, port)}")
lsock.setblocking(False)
sel.register(lsock, selectors.EVENT_READ, data=None)


try:
    while True:
        events = sel.select(timeout=None)
        for key, mask in events:
            if key.data is None:
                accept_wrapper(key.fileobj)
            else:
                service_connection(key, mask)
except KeyboardInterrupt:
    print("Caught keyboard interrupt, exiting")
finally:
    sel.close()

