from sequencer import Sequencer

seq = Sequencer()

while True:
    inp = input("")
    match inp:
        case "cast":
            print(seq.broadcast())
        case _:
            print("Incorrect input! Try again.\n")