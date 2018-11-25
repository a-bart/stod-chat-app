#!/usr/bin/env python3
"""Server for multithreaded (asynchronous) chat application."""
import json, sys, time
from socket import AF_INET, socket, SOCK_STREAM
from threading import Thread

def accept_incoming_connections():
    """Sets up handling for incoming clients."""

    while True:
        client, client_address = SERVER.accept()
        print("%s:%s has connected." % client_address)
        greetings = "Добро пожаловать в чат! Введите Ваш никнейм чтобы общаться"
        greetings_msg = {}
        greetings_msg['msg'] = greetings
        client.send(bytes(json.dumps(greetings_msg), "utf8"))
        addresses[client] = client_address
        Thread(target=handle_client, args=(client,)).start()
        time.sleep(0.5)


def handle_client(client):  # Takes client socket as argument.
    """Handles a single client connection."""

    jsonData = client.recv(BUFSIZ).decode("utf8")
    data = json.loads(jsonData)
    print("handle_client data: %s" % data)
    name = data['username']
    welcome = 'Добро пожаловать, %s! Если захочешь выйти, введи {выход}' % name
    aware_msg = {}
    aware_msg['msg'] = welcome
    client.send(bytes(json.dumps(aware_msg), "utf8"))
    broadcast("%s присоединился к чату!" % name)
    clients[client] = name

    while True:
        jsonData = client.recv(BUFSIZ).decode("utf8")
        data = json.loads(jsonData)

        if data and 'operation' in data and data['operation'] == "get_online_users":
            users = []

            for key, value in clients.items():
                print("each user: %s" % value)
                if (clients[key] != clients[client]):
                    user = {}
                    user['username'] = clients[key]
                    user['address'] = "{}:{}".format(addresses[key][0], addresses[key][1])
                    users.append(user.copy())

            list_msg = {}
            list_msg['users'] = users
            client.send(bytes(json.dumps(list_msg), "utf8"))

        if data and 'msg' in data:
            msg = data['msg']
            if msg == '{quit}':
                client.send(bytes("{quit}", "utf8"))
                client.close()
                del clients[client]
                broadcast("%s has left the chat." % name)
                break

            if 'operation' in data and data['operation'] == "send_to_all":
                broadcast(msg, name+": ")

            if 'operation' in data and data['operation'] == "send_direct":
                search_by = data['search_by']
                is_user_found = False
                # try to find user by provided search
                for sample_client, username in clients.items():
                    if username == search_by:
                        is_user_found = True
                        client_to_send = sample_client
                        break

                if is_user_found == False:
                    for sample_client, address in addresses.items():
                        if "{}:{}".format(addresses[sample_client][0], addresses[sample_client][1]) == search_by:
                            is_user_found = True
                            client_to_send = sample_client
                            break

                if is_user_found:
                    msg_with_name = "{}: {}".format(name, msg)
                    data = {}
                    data['msg'] = msg_with_name
                    client.send(bytes(json.dumps(data), "utf8"))
                    client_to_send.send(bytes(json.dumps(data), "utf8"))
                else:
                    aware_msg['msg'] = 'Невозможно найти пользователя по заданному параметру: "{}"'.format(search_by)
                    client.send(bytes(json.dumps(aware_msg), "utf8"))

def broadcast(msg, prefix=""):  # prefix is for name identification.
    """Broadcasts a message to all the clients."""

    for sock in clients:
        data = {}
        data['msg'] = prefix + msg
        jsonData = json.dumps(data)
        sock.send(bytes(jsonData, "utf8"))


clients = {}
addresses = {}

HOST = '127.0.0.1'
PORT = 33000
BUFSIZ = 1024
ADDR = (HOST, PORT)

SERVER = socket(AF_INET, SOCK_STREAM)
SERVER.bind(ADDR)

def main():
    SERVER.listen(5)
    print("Waiting for connection...")

    ACCEPT_THREAD = Thread(target=accept_incoming_connections)
    ACCEPT_THREAD.start()
    ACCEPT_THREAD.join()
    SERVER.close()

if __name__ == '__main__':
    main()
