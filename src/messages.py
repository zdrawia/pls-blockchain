from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from things import Thing

from enum import Enum


class MessageType(Enum):
    PROOF_PLS = 1
    LINK_PLS = 2
    SIGNATURE_PLS = 3
    ENROLMENT = 4
    ACK = 5
    FAIL = 6
    SIGNATURE_SLVP = 7
    LINKVERIFY_SLVP = 8
    PROOF_SLVP = 9


class Message:
    def __init__(self, content, message_type: MessageType, thing: Thing = None):
        self.content = content
        self.message_type = message_type
        self.message_origin = thing
