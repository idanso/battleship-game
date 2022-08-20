import json


def send_message(sock, data_dic):
    """
    Function for sending data from the socket in json form.

    sock (socket) -> the socket object to send data from

    data (dictionary) -> the data that should be sent

    """
    try:
        data_json = json.dumps(data_dic)
        sock.send(data_json.encode())
    except Exception as e:
        print(e)


def receive_message(sock):
    """

    Function for receiving data from the socket in json form.

    sock (socket) -> the socket object to receive data from

    :return: dictionary containing the data

    """
    try:
        recv_data = sock.recv(5120)
        if recv_data:
            json_data = bytes(recv_data).decode()
            return json.loads(json_data)
        else:
            return None

    except Exception as e:
        print(e)
        return None
