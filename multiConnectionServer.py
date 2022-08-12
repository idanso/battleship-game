import sys
import socket
import selectors
import types
import server_service
import json

HOST = "127.0.0.1"  # The server's hostname or IP address
PORT = 1233  # The port used by the server

#################


def accept_wrapper(sock, ready_players):
    conn, addr = sock.accept()  # Should be ready to read
    print(f"Accepted connection from {addr}")
    conn.setblocking(False)
    sock.settimeout(5)
    data = types.SimpleNamespace(addr=addr)  # TODO: check if needed
    events = selectors.EVENT_READ | selectors.EVENT_WRITE
    sel.register(conn, events, data=data)
    if ready_players[0] is None:  # check if there is player ready for a game
        ready_players[0] = server_service.Player(addr)
    else:
        ready_players[1] = server_service.Player(addr)
    print(ready_players)
    return ready_players


def service_connection(key, mask):
    sock = key.fileobj
    data = key.data

    if mask & selectors.EVENT_READ:
        try:
            print("service_connection data address: " + str(data.addr))
            player_data = game_handler.get_active_player_and_game_by_port(data.addr)

            if player_data is None:
                # TODO: handle error of player not found
                pass
            else:
                print("player Id: " + player_data.id + ", player address: " + player_data.address)
            recv_data = sock.recv(1024)  # Should be ready to read
            if recv_data:
                operation_mapper(json.loads(bytes(recv_data).decode()))
                if mask & selectors.EVENT_WRITE:
                    send_data = json.dumps({"action": "hellow world"})
                    sock.send(send_data.encode())
            else:
                print(f"Closing connection to {data.addr}")
                sel.unregister(sock)
                sock.close()

        except Exception as e:
            print(e)
    # if mask & selectors.EVENT_WRITE:
    #     if data.outb:
    #         print(f"Echoing {data.outb!r} to {data.addr}")
    #         sent = sock.send(f"Echoing {data.outb!r} to {data.addr}".encode())  # Should be ready to write
    #         data.outb = data.outb[sent:]


def operation_mapper(received_data):
    print(received_data)


sel = selectors.DefaultSelector()

game_handler = server_service.GamesHandler()
ready_players = [None, None]

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
                ready_players = accept_wrapper(key.fileobj, ready_players)
                if ready_players[1] is not None:  # check if there is two players ready to start game
                    new_game_id = game_handler.start_game(ready_players[0], ready_players[1])  # create new game
                    ready_players = [None, None]

                    # TODO: send to clients their boards
            else:
                service_connection(key, mask)
except KeyboardInterrupt:
    print("Caught keyboard interrupt, exiting")
finally:
    sel.close()

