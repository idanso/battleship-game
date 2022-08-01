import sys
import socket
import selectors
import types
from time import sleep


sel = selectors.DefaultSelector()
messages = [b"Message 1 from client.", b"Message 2 from client."]


def start_connections(host, port):
    server_addr = (host, port)
    while True:
        try:
            print(f"Starting connection to {server_addr}")
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.setblocking(False)
            sock.settimeout(5)
            sock.connect_ex(server_addr)
            events = selectors.EVENT_READ | selectors.EVENT_WRITE
            data = types.SimpleNamespace(
                msg_total=sum(len(m) for m in messages),
                recv_total=0,
                messages=messages.copy(),
                outb=b"",
            )
            sel.register(sock, events, data=data)
            usr_input = input("enter name: ")
            sock.send(usr_input.encode())
            recv_data = sock.recv(1024)  # Should be ready to read
            print("data recived from server: " + bytes(recv_data).decode())
            sleep(100)
        finally:
            print("socket closed")
            sock.close()


start_connections('127.0.0.1', 65432)