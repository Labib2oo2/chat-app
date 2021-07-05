
from flask import Flask , render_template

from flask_socketio import SocketIO,send, join_room,leave_room

app = Flask(__name__)
app.config["SECRET_KEY"]="secret!"

socket= SocketIO(app,cors_allowed_origins="*")

@app.route("/")
def main():
	return render_template("index.html")

@socket.on("create")
def on_join(data):
	username=data["username"]
	room=data["room"]
	join_room(room)
	send(username+" has entered the room",to=room)

@socket.on("room_msg")
def rooms(msg):
	room=msg["room"]
	send(msg["msg"],to=room)

@socket.on('message')
def handle_my_custom_event(msg):
    print('msg ' + str(msg))
    send(msg, broadcast=True)
   
    

if __name__=="__main__":
	socket.run(app)
	
