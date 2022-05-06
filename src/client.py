import jsonpickle
import requests
import multiprocessing
from things import Thing


if __name__ == '__main__':
    print('Thing is working...')
    print('"enroll" - to enroll')
    print("Trying to connect to server...")
    response = requests.get('http://127.0.0.1:5000')
    print(response.json())

    thing = Thing()
    while True:
        print(thing)
        inp = input("")
        match inp:
            case "enroll":
                print(thing.enroll())
            case "post":
                msg = input("Input message to post on blockchain.\n")
                print(thing.post(msg))
            case "pls":
                response = requests.get('http://127.0.0.1:5005/getpls')
                res = jsonpickle.decode(response.json()['message'])
                thing.receive(res[0])
                thing.receive(res[1])
                thing.receive(res[2])
            case "get":
                block_number = input("Input block number.\n")
                user_id = input("Input user id.\n")
                thing.get_contrib(block_number, user_id)
            case _:
                print("Incorrect input! Try again.\n")
