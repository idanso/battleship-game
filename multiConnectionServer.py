import socket
import selectors
import sys
import threading
import types
import client_gui
import server_service
from shared import *
from os.path import exists
import logging as log
from datetime import datetime


HOST = "127.0.0.1"  # The server's hostname or IP address
PORT = 1233  # The port used by the server
sel = None
game_handler_locker = server_service.Game_handler_locker()
Logging = None

#################


def accept_wrapper(sock):
    """
    Function accepting new socket connection and register it
    :Param sock: socket to accept and register
    """
    try:
        conn, addr = sock.accept()  # Should be ready to read
        logging.info(f"Accepted connection from {addr}")
        conn.setblocking(False)
        sock.settimeout(200)
        data = types.SimpleNamespace(addr=addr)
        events = selectors.EVENT_READ | selectors.EVENT_WRITE
        sel.register(conn, events, data=data)
    except Exception:
        logging.error(traceback.format_exc())


def service_connection(key, mask):
    """
    Function for handle received messages from sockets and send it to operation_mapper

    :Param key: containing the socket and data attached to the socket
    """
    sock = key.fileobj
    data = key.data

    if  mask & selectors.EVENT_READ:
        try:
            logging.info("received message data from address: " + str(data.addr))
            recv_data = receive_message(sock, logging)  # Should be ready to read
            if recv_data:
                operation_mapper(sock, data.addr, recv_data)
            else:
                raise Exception("Error in receiving socket data")
        except Exception:
            logging.error(traceback.format_exc())

def operation_mapper(sock, address, received_data):
    """
    Function mapper for different operation based on received data message action
    :Param sock: socket of the sender client
    :Param address: tuple containing address and port of client
    :Param received_data: dict the data receive from client buffer
    """
    try:
        game_handler = game_handler_locker.get_game_handler
        if received_data["Action"] == "start_game":
            restart = False
            if received_data["Quit"] in (0,1):
                game = game_handler.get_game_by_address(address)
                game.status = server_service.GameStatus.ENDED
                restart = True
                if received_data["Quit"] == 0:
                    game.players[1].score["win"] += 1
                    game.players[0].score["lose"] += 1
                elif received_data["Quit"] == 1:
                    game.players[0].score["win"] += 1
                    game.players[1].score["lose"] += 1
                game_handler.readyPlayers = [game.players[0].name, game.players[1].name]

            if "Players" in received_data.keys() and received_data["Players"][0] is not None:
                game_handler.readyPlayers = received_data["Players"]
            game = game_handler.start_game(address=address,players=game_handler.readyPlayers, thread=game_handler.ready_thread)
            game_handler.readyPlayers = [None, None]
            game_handler.ready_thread = None
            data_dict = dict({"Action": "start_game", "Restart": restart, "Board_1": game.boards[0], "Board_2": game.boards[1],
                                "Players":  [game.players[0].name, game.players[1].name]})
            send_message(sock, data_dict, logging)

        if received_data["Action"] == "start_server":
            data_dict = dict({"Action": "start_game", "Players": game_handler.readyPlayers, "Restart": False})
            send_message(sock, data_dict, logging)
        else:
            game = game_handler.get_game_by_address(address)
            if not game:
                logging.error("couldn't find game from address: %s", address)
                return
            if received_data["Action"] == "attack":
                board = game.boards[received_data["Hitted_player"]]
                hit_res = server_service.check_revealed_tile(
                    board,
                    received_data["Location"])
                if hit_res:
                    board[received_data["Location"][0]][received_data["Location"][1]][1] = True
                win_res = server_service.check_for_win(board)
                winner = None
                if win_res:
                    if received_data["Hitted_player"] == 1:
                        game.players[0].score["win"] += 1
                        game.players[1].score["lose"] += 1
                        winner = 1
                    else:
                        game.players[0].score["lose"] += 1
                        game.players[1].score["win"] += 1
                        winner = 0
                    game.status = server_service.GameStatus.ENDED

                data_dict = dict({"Action": "hit", "Success": hit_res, "Finished": win_res})
                if winner is not None:
                    data_dict["Winner"] = winner
                send_message(sock, data_dict, logging)

            elif received_data["Action"] == "close_connection":
                logging.info(f"Closing connection to {address}")
                game = game_handler.get_game_by_address(address)
                game.status = server_service.GameStatus.ENDED
                sel.unregister(sock)
                sock.close()
            else:
                logging.error("unknown Action: %s", received_data["Action"])
    except Exception():
        logging.error(traceback.format_exc())

def server_thread():
    """
    Function main operation of the server to initiate socket and enter the main loop for managing the sockets
    """
    global sel, game_handler_locker
    host, port = HOST, PORT  # sys.argv[1], int(sys.argv[2])
    lsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    lsock.bind((host, port))
    lsock.listen()
    logging.info(f"Listening on {(host, port)}")
    lsock.setblocking(False)
    sel.register(lsock, selectors.EVENT_READ, data=None)
    try:
        while True:
            if game_handler_locker.get_game_handler.kill_server:
                break
            events = sel.select(timeout=0.5)
            for key, mask in events:
                if key.data is None:
                    accept_wrapper(key.fileobj)
                else:
                    service_connection(key, mask)
    except KeyboardInterrupt:
        logging.error("Caught keyboard interrupt, exiting")
        logging.error(traceback.format_exc())
    finally:
        sel.close()
        logging.info("socket closed")


def start_client(players=('idan', 'shiran')):
    """
    Function for starting new client and the client gui as a thread
    :Param players: new players names for the new game
    """
    global game_handler_locker
    game_handler = game_handler_locker.get_game_handler
    # TODO: consider adding sleep
    for player in players:
        user = game_handler.get_user_by_name(player)
        if not user:
            game_handler.add_user(server_service.User(player))

    game_handler.readyPlayers = players
    client_gui_thread = threading.Thread(target=client_gui.start_client_gui)
    client_gui_thread.setDaemon(True)
    game_handler.ready_thread = client_gui_thread
    client_gui_thread.start()


def server_main():
    """
    Function main function of the server to initiate Logger and game handler and call the server thread for main operation
    """
    try:
        global sel, game_handler_locker, logging
        # set logger
        format_data = "%d_%m_%y_%H_%M"
        date_time = datetime.now().strftime(format_data)
        #log_file_name = 'Log/Server_log_' + date_time + '.log'
        log_file_name = 'Log/Server_log.log'
        logging = log.getLogger()
        logging.setLevel(log.DEBUG)
        log.basicConfig(filename=log_file_name, filemode='a',
                            level=log.DEBUG,
                            format='%(asctime)s : %(message)s')

        sel = selectors.DefaultSelector()
        game_handler_locker = server_service.Game_handler_locker()
        if exists(server_service.FILE_NAME):
            game_handler_locker.set_game_handler(server_service.load_data_from_file())
            game_handler_locker.get_game_handler.reset_vars()
        else:
            game_handler_locker.create_game_handler()

        server_thread()

        game_handler_locker.get_game_handler.finish_all_games()
        server_service.save_data_to_file(game_handler_locker.get_game_handler)
    except Exception():
        logging.error(traceback.format_exc())

def end_server_thread():
    """
    Function set the game_handler to know exit application need to be done
    """
    global game_handler_locker
    game_handler_locker.get_game_handler.kill_server = True

def get_plot_data():
    """
    Function returning data for the result window
    """
    global game_handler_locker
    return game_handler_locker.get_game_handler.get_ordered_best_players()