import errno
import imp
from header_utils import LENGTH_HEADER_SIZE, USER_HEADER_SIZE, format_message
import socket
import sys
from threading import Thread

IP = '127.0.0.1'
PORT = 5555
username = ''

while not username:
    username = input('Please enter a username (max. 16 characters)')

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((IP, PORT))
client_socket.setblocking(False)


def send():
    message = input(f'{username} > ')
    if message == '[exit]':
        message = format_message(username, 'Signing out')
        client_socket.send(message.encode('utf-8'))
        print('Signed out')
        client_socket.close()
        sys.exit()
    elif message:
        message = format_message(username, message).encode('utf-8')
        client_socket.send(message)


def receive():
    try:
        message_size = client_socket.recv(LENGTH_HEADER_SIZE)
        if message_size:
            message_size = int(message_size.decode('utf-8').strip())
            sender = client_socket.recv(
                USER_HEADER_SIZE).decode('utf-8').strip()
            message = client_socket.recv(message_size).decode('utf-8')
            print(f'\n{sender} > {message}\n{username} > ')

    except IOError as e:
        if e.errno != errno.EAGAIN and e.errno != errno.EWOULDBLOCK:
            print('Encountered error while readeing', e)
            client_socket.close()
            sys.exit()
    except Exception as e:
        client_socket.close()
        sys.exit()


def loop_receive():
    while True:
        receive()


receive_thread = Thread(target=loop_receive)
receive_thread.start()
while True:
    send()