from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional


import marshmallow
import marshmallow_dataclass

# ☐ В коде описаны датаклассы для данных: Message, Update, Chat, MessageFrom.
# ☐ Не используются dict для описания данных.

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
    is_bot: bool    # must be mandatory?
    first_name: str
    last_name: Optional[str]
    username: str
    # language_code: Optional[str]  # may be absent


@dataclass
class Message:
    message_id: int
    from_: MessageFrom
    chat: Chat
    # date: Optional[str]   # must be mandatory? datetime.date
    # date: Optional[datetime.date]
    text: Optional[str]
    # entities: Optional[List[dict]]   # may be without entities


@dataclass
class Update:
    update_id: int
    message: Message

# PersonSchema = marshmallow_dataclass.class_schema(Person)
# PersonSchema().load({"name": "alex", "age": "100", "ds": 123})
# # Person(name='alex', age=100)
# if error ==  marshmallow.exceptions.ValidationError
# см детали по field(metadata={"data_key": "firstName"}), если формат ключей передан неожиданный


UpdateObj = marshmallow_dataclass.class_schema(Update)
MessageObj = marshmallow_dataclass.class_schema(Message)


@dataclass
class GetUpdatesResponse:
    ok: bool
    # result: List[UpdateObj]
    # result: list[UpdateObj] = field(default_factory=list)
    result: List[UpdateObj] = field(default_factory=list)
    # result: List[UpdateObj]

    class Meta:
        # unknown = EXCLUDE
        unknown = marshmallow.EXCLUDE   # непредвиденные поля просто исключаем/игнорируем???


@dataclass
class SendMessageResponse:
    ok: bool
    # result: Message
    result: MessageObj

    class Meta:
        # unknown = EXCLUDE
        unknown = marshmallow.EXCLUDE
