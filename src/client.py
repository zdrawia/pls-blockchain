import requests
import socket
import multiprocessing
from things import Thing

def listen_pls():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    sock.bind(('', 5005))
    while True:
        data, addr = sock.recvfrom(1024)
        print(data)


if __name__ == '__main__':
    print('Thing is working...')
    print('"enroll" - to enroll')
    print("Trying to connect to server...")
    response = requests.get('http://127.0.0.1:5000')
    print(response.json())

    thread = multiprocessing.Process(target=listen_pls, )
    # thread.start()

    listen_pls()

    thing = Thing()
    while True:
        inp = input("")
        match inp:
            case "enroll":
                print(thing.enroll())
            case "post":
                msg = input("Input message to post on blockchain.\n")
                print(thing.post(msg))
            case "get":
                block_number = input("Input block number.\n")
                user_id = input("Input user id.\n")
                thing.get_contrib(block_number, user_id)
            case _:
                print("Incorrect input! Try again.\n")
