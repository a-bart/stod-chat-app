#!/usr/bin/env python3
"""Script for Tkinter GUI chat client."""
from socket import AF_INET, socket, SOCK_STREAM
from threading import Thread
import json
import tkinter

def login(event=None):
    """Handles login in chat."""
    data = {}
    data['operation'] = "login"
    data['username'] = username.get()
    jsonData = json.dumps(data)
    username.set("")  # Clears input field.
    client_socket.send(bytes(jsonData, "utf8"))

    # hide/show GUI components
    username_entry_field.pack_forget()
    login_button.pack_forget()
    checkIsSendDirect.pack()
    msg_label.pack()
    msg_entry_field.pack()
    send_button.pack()
    get_users_button.pack()

def receive():
    """Handles receiving of messages."""
    while True:
        try:
            jsonData = client_socket.recv(BUFSIZ).decode("utf8")
            data = json.loads(jsonData)
            print("handle receive data: %s" % data)

            if data and 'users' in data:
                msg_list.insert(tkinter.END, "Список онлайн пользователей:")
                if len(data['users']) == 0:
                    msg_list.insert(tkinter.END, "На данный момент вы одни в чате")
                else:
                    for user in data['users']:
                        msg_list.insert(tkinter.END, "Имя: {}, Адрес: {}".format(user['username'], user['address']))

            if data and 'msg' in data:
                msg = data['msg']
                msg_list.insert(tkinter.END, msg)
        except OSError:  # Possibly client has left the chat.
            break


def send(event=None):  # event is passed by binders.
    """Handles sending of messages."""
    msg = my_msg.get()
    data = {}
    data['msg'] = msg

    if isSendDirect.get():
        data['operation'] = "send_direct"
        data['search_by'] = direct_user.get()
    else:
        data['operation'] = "send_to_all"

    jsonData = json.dumps(data)
    my_msg.set("")  # Clears input field.
    direct_user.set("") # Clears input field.
    client_socket.send(bytes(jsonData, "utf8"))
    if msg == "{quit}":
        client_socket.close()
        top.quit()

def getOnlineUsers(event=None):
    data = {}
    data['operation'] = "get_online_users"
    jsonData = json.dumps(data)
    client_socket.send(bytes(jsonData, "utf8"))

def on_closing(event=None):
    """This function is to be called when the window is closed."""
    my_msg.set("{quit}")
    send()

def handleDirectChange():
    print("in handleDirectChange: %s" % isSendDirect.get())

    if isSendDirect.get():
        msg_label.pack_forget()
        msg_entry_field.pack_forget()
        send_button.pack_forget()
        get_users_button.pack_forget()
        direct_user_label.pack()
        direct_user_field.pack()
        msg_label.pack()
        msg_entry_field.pack()
        send_button.pack()
        get_users_button.pack()
    else:
        direct_user_label.pack_forget()
        direct_user_field.pack_forget()

top = tkinter.Tk()
top.title("Чат")

messages_frame = tkinter.Frame(top)
scrollbar = tkinter.Scrollbar(messages_frame)  # To navigate through past messages.
# Following will contain the messages.
msg_list = tkinter.Listbox(messages_frame, height=15, width=50, yscrollcommand=scrollbar.set)
scrollbar.pack(side=tkinter.RIGHT, fill=tkinter.Y)
msg_list.pack(side=tkinter.LEFT, fill=tkinter.BOTH)
msg_list.pack()
messages_frame.pack()

# login part
username = tkinter.StringVar()  # For username.
username_entry_field = tkinter.Entry(top, textvariable=username)
username_entry_field.bind("<Return>", login)
username_entry_field.pack()
login_button = tkinter.Button(top, text="Войти", command=login)
login_button.pack()

# send messages part
isSendDirect = tkinter.IntVar()
checkIsSendDirect = tkinter.Checkbutton(top, text="Отправить лично", command=handleDirectChange, variable=isSendDirect, onvalue=1, offvalue=0)
checkIsSendDirect.pack()
checkIsSendDirect.pack_forget()
direct_user_label = tkinter.Label(top, text="Адрес или имя:")
direct_user_label.pack()
direct_user_label.pack_forget()
direct_user = tkinter.StringVar()  # For the address/username to send a message.
direct_user_field = tkinter.Entry(top, textvariable=direct_user)
direct_user_field.bind("<Return>", send)
direct_user_field.pack()
direct_user_field.pack_forget()
msg_label = tkinter.Label(top, text="Сообщение:")
msg_label.pack()
msg_label.pack_forget()
my_msg = tkinter.StringVar()  # For the messages to be sent.
msg_entry_field = tkinter.Entry(top, textvariable=my_msg)
msg_entry_field.bind("<Return>", send)
msg_entry_field.pack()
msg_entry_field.pack_forget()
send_button = tkinter.Button(top, text="Отправить", command=send)
send_button.pack()
send_button.pack_forget()
get_users_button = tkinter.Button(top, text="Список онлайн пользователей", command=getOnlineUsers)
get_users_button.pack()
get_users_button.pack_forget()

top.protocol("WM_DELETE_WINDOW", on_closing)

#----Now comes the sockets part----
HOST = '127.0.0.1'
PORT = 33000

BUFSIZ = 1024
ADDR = (HOST, PORT)

client_socket = socket(AF_INET, SOCK_STREAM)
client_socket.connect(ADDR)

receive_thread = Thread(target=receive)
receive_thread.start()
tkinter.mainloop()  # Starts GUI execution.
