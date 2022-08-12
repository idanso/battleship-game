import sys
import socket
import selectors
import types
import server_service

#### Globals ####
BOARDWIDTH = 10 #Number of grids horizontally
BOARDHEIGHT = 10 #Number of grids vertically

DEFAULT_SHIP_NAME = None
DEFAULT_BOOL_SHOT = False

HOST = "127.0.0.1"  # The server's hostname or IP address
PORT = 1233  # The port used by the server

#################
def accept_wrapper(sock):
    conn, addr = sock.accept()  # Should be ready to read
    print(f"Accepted connection from {addr}")
    conn.setblocking(False)
    sock.settimeout(5)
    data = types.SimpleNamespace(addr=addr, inb=b"", outb=b"")
    events = selectors.EVENT_READ | selectors.EVENT_WRITE
    sel.register(conn, events, data=data)


def service_connection(key, mask):
    sock = key.fileobj
    data = key.data
    if mask & selectors.EVENT_READ:
        try:
            recv_data = sock.recv(1024)  # Should be ready to read

            if recv_data:
                data.outb += recv_data
                print("data recived from : " + bytes(recv_data).decode() + ", from: " + str(data.addr))
            else:
                print(f"Closing connection to {data.addr}")
                sel.unregister(sock)
                sock.close()

        except Exception as e:
            print(e)
    if mask & selectors.EVENT_WRITE:
        if data.outb:
            print(f"Echoing {data.outb!r} to {data.addr}")
            sent = sock.send(f"Echoing {data.outb!r} to {data.addr}".encode())  # Should be ready to write
            data.outb = data.outb[sent:]


sel = selectors.DefaultSelector()


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

