from flask import Flask, request, session, render_template
from flask_socketio import join_room, leave_room, send, SocketIO # type: ignore
import random
from string import ascii_uppercase

chat_app = Flask(__name__)
chat_app.config["SECRET_KEY"] = "asdfjkl;"
socketio = SocketIO(chat_app, cors_allowed_origins="*", async_mode='eventlet')

rooms = {}

def ack():
    print('message received!')

def generate_unique_code(length=4):
    while True:
        code = ''
        for _ in range(length):
            code += random.choice(ascii_uppercase)

        if code not in rooms:
            break

    return code

@socketio.on('create_room')
def handle_create_room():
    room_code = generate_unique_code()
    rooms[room_code] = { 'members': set(), "messages": []}
    print(f'room created: {room_code}')
    socketio.emit('room_created', {"room": room_code})

@socketio.on("join_room")
def handle_join_room(data):
    name = data.get('name')
    room = data.get('room')

    if not name or not room:
        return
    
    if room not in rooms:
        rooms[room] = {'members': set(), "messages": []}

    # Add the user to the room
    rooms[room]['members'].add(name)
    join_room(room)
    

    print(f"✅ {name} joined room {room}")

@socketio.on('send_message')
def handle_send_message(data):
    print(data)
    name = data.get('name')
    room = data.get('room')
    message = data.get('message')

    if room not in rooms:
        print('this shit is fucked lmao')
        return

    # Store the message in the room's message list
    rooms[room]["messages"].append({"name": name, "message": message})
    
    # Broadcast the message to all users in the room
    socketio.emit("display_message", {
            "name": name,
            "message": message,
            "room": room
        }, room=room)
    
    print(f'Message sent to room {room}', name, message)

@socketio.on('leave_room')
def handle_leave_room(data):
    name = data.get("name")
    room = data.get("room")

    leave_room(room)

    if room in rooms and name in rooms[room]["members"]:
        rooms[room]["members"].remove(name)
        socketio.emit("receive_message", {
            "name": "System",
            "message": f"{name} has left the chat.",
            "room": room
        }, room=room)

if __name__ == "__main__":
    socketio.run(chat_app, port='1222', host='0.0.0.0')