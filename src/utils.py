from itertools import cycle
from operator import xor


def xor_two_str(a, b):
    short, long = sorted((a.encode('latin-1'), b.encode('latin-1')), key=len)
    xored = bytes(map(xor, long, cycle(short)))
    return xored.hex()


def sxor(s1: str, s2: str):
    return ''.join(chr(ord(a) ^ ord(b)) for a, b in zip(s1, s2))
