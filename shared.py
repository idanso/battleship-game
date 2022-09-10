import json
import traceback


def send_message(sock, data_dic, logger):
    """
    Function for sending data from the socket in json form.

    sock (socket) -> the socket object to send data from

    data (dictionary) -> the data that should be sent

    """
    try:
        data_json = json.dumps(data_dic)
        sock.send(data_json.encode())
        logger.info("Message sent: " + str(data_dic))
    except Exception:
        logger.error(traceback.format_exc())


def receive_message(sock, logger):
    """

    Function for receiving data from the socket in json form.

    sock (socket) -> the socket object to receive data from

    :return: dictionary containing the data

    """
    recv_data = sock.recv(5120)
    if recv_data:
        json_data = bytes(recv_data).decode()
        logger.info("Message received: " + str(json_data))
        return json.loads(json_data)
    else:
        logger.info("No data to receive")
        return None