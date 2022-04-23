import requests
from things import Thing

if __name__ == '__main__':
    print('Thing is working...')
    print('"enroll" - to enroll')
    print("Trying to connect with server...")
    response = requests.get('http://127.0.0.1:5000')
    print(response.json())
    thing = Thing()
    while True:
        inp = input("")
        match inp:
            case "enroll":
                print(thing.enroll())
            case "post":
                msg = input("Input message to post on blockchain.")
                print(thing.post(msg))
            case _:
                print("Incorrect input! Try again.")