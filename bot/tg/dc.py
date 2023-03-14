from dataclasses import dataclass, field
from typing import List, Optional

import marshmallow
import marshmallow_dataclass

# {"ok":true,
#  "result":
#      [{
#          "update_id":650945696,
#          "message":{"message_id":1,
#                     "from":{"id":327134280,"is_bot":false,"first_name":"Yuliya","username":"yuliya_b7","language_code":"ru"},
#                     "chat":{"id":327134280,"first_name":"Yuliya","username":"yuliya_b7","type":"private"},
#                     "date":1678274704,
#                     "text":"/start",
#                     "entities":[{"offset":0,"length":6,"type":"bot_command"}]
#                     }
#      }]
#  }
#
# {"ok":true,
#  "result":
#      {"message_id":3,
#       "from":{"id":6248252954,"is_bot":true,"first_name":"Todolist","username":"goals_tracking_bot"},
#       "chat":{"id":327134280,"first_name":"Yuliya","username":"yuliya_b7","type":"private"},
#       "date":1678274955,
#       "text":"hello"}
#  }


@dataclass
class Chat:
    id: int
    first_name: str
    last_name: Optional[str]
    username: str
    type: Optional[str]
    title: Optional[str]


@dataclass
class MessageFrom:
    id: int
    is_bot: bool
    first_name: str
    last_name: Optional[str]
    username: str


@dataclass
class Message:
    message_id: int
    from_: MessageFrom
    chat: Chat
    text: Optional[str]


@dataclass
class Update:
    update_id: int
    message: Message


UpdateObj = marshmallow_dataclass.class_schema(Update)
MessageObj = marshmallow_dataclass.class_schema(Message)


@dataclass
class GetUpdatesResponse:
    ok: bool
    result: List[UpdateObj] = field(default_factory=list)

    class Meta:
        unknown = marshmallow.EXCLUDE


@dataclass
class SendMessageResponse:
    ok: bool
    result: MessageObj

    class Meta:
        unknown = marshmallow.EXCLUDE
