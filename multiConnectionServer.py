import socket
import selectors
import traceback
import types
import server_service
from shared import *
from os.path import exists
import logging
from datetime import datetime

HOST = "127.0.0.1"  # The server's hostname or IP address
PORT = 1233  # The port used by the server

#################


def accept_wrapper(sock):
    conn, addr = sock.accept()  # Should be ready to read
    logging.info(f"Accepted connection from {addr}")
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
            logging.info("received message data from address: " + str(data.addr))
            recv_data = receive_message(sock, logging)  # Should be ready to read
            if recv_data:
                operation_mapper(sock, data.addr, recv_data)
            else:
                raise Exception("Error in receiving socket data")
        except Exception as e:
            traceback.print_exc()  # TODO: delete when finish
            logging.error(traceback.format_exc())


# TODO: consider replacing actions string to enums
def operation_mapper(sock, address, received_data):
    if received_data["Action"] == "start_game":
        restart = False
        if received_data["Quit"] in (0,1):
            game = game_handler.get_game_by_address(address)
            game.status = server_service.GameStatus.ENDED
            restart = True
            if received_data["Quit"] == 0:
                (server_service.User)(game.players[1]).score["win"] += 1
                (server_service.User)(game.players[0]).score["lose"] += 1
            elif received_data["Quit"] == 1:
                (server_service.User)(game.players[0]).score["win"] += 1
                (server_service.User)(game.players[1]).score["lose"] += 1
            game_handler.readyPlayers = [(server_service.User)(game.players[0]).name, (server_service.User)(game.players[1]).name]


        game_handler.start_game(address,game_handler.readyPlayers, [received_data["Board_1"], received_data["Board_2"]])
        game_handler.readyPlayers = [None, None]
        # data_dict = dict({"Action": "start_game", "Restart": restart})
        # send_message(sock, data_dict)

    if received_data["Action"] == "start_server":
        game_handler.readyPlayers = ['idan', 'shiran'] # TODO: only for testing need to delete
        for player in game_handler.readyPlayers: # TODO: only for testing need to delete
            if player not in game_handler.users:
                game_handler.add_user(server_service.User(player))
        data_dict = dict({"Action": "start_game", "Players": game_handler.readyPlayers, "Restart": False})
        send_message(sock, data_dict, logging)
    else:
        game = game_handler.get_game_by_address(address)
        if not game:
            logging.error("couldn't find game from address: %s", address)
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
            send_message(sock, data_dict, logging)

        elif received_data["Action"] == "close_connection":
            logging.info(f"Closing connection to {address}")
            game = game_handler.get_game_by_address(address)
            game.status = server_service.GameStatus.ENDED
            sel.unregister(sock)
            sock.close()
        else:
            logging.error("unknown Action: %s", received_data["Action"])
            # TODO: consider throwing error


# set logger
format_data = "%d_%m_%y_%H_%M"
date_time = datetime.now().strftime(format_data)
logging.basicConfig(filename='Log/Server_log_' + date_time + '.log', filemode='w',
                    level=logging.DEBUG,
                    format='%(asctime)s : %(message)s')

sel = selectors.DefaultSelector()

if exists(server_service.FILE_NAME):
    game_handler = server_service.load_data_from_file()
else:
    game_handler = server_service.ServerGamesHandler()

host, port = HOST, PORT  # sys.argv[1], int(sys.argv[2])
lsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
lsock.bind((host, port))
lsock.listen()
logging.info(f"Listening on {(host, port)}")
lsock.setblocking(False)
sel.register(lsock, selectors.EVENT_READ, data=None)

test_start_client = 0 # TODO: for testing to delete
try:
    while True:
#        server_service.start_client(game_handler)
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
    logging.info("socket closed")
    game_handler.finish_all_games()
    server_service.save_data_to_file(game_handler)