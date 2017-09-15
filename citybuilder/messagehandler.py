import re
import json

handlers = {
    "build": lambda player, message: {'result': 0}
}

def handle_message(connection, player, message):
    handler = handlers[message['type']]
    if handler:
        connection.send_json(handler(player, message))
    else:
         connection.send_json({'result': 1})
