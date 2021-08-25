
from flask import *
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO,send, join_room,leave_room, emit
import requests
import json
import isodate
from datetime import datetime
from youtube_search import YoutubeSearch

app = Flask(__name__)
app.config["SECRET_KEY"]="secret!"
socket= SocketIO(app,cors_allowed_origins="*")


@app.route("/")
def main():
		return render_template("index.html")

	

users_ar = []


current_vid={}

@socket.on("create")
def on_join(data):
	global current_vid
	global users_ar
	username=data["username"]
	#new room joining
	room=data["room"][len(data["room"])-1]
	old_room=data["room"][0]
	data["room"]=room
	sid=request.sid
	join_room(room)
	data["sid"]=request.sid
	name_ar = list(map(lambda x: x["username"],users_ar))
	if current_vid.get(room):
		emit("requested_video_id",current_vid.get(room),room=sid)
	print(current_vid,"curent vid")
	if data not in users_ar and username not in name_ar:
		users_ar.append(data)
		same_room = list(filter(lambda y: filt_room(y,room) ,users_ar))
		emit("entered",same_room,room=room)
		send(username+" has entered the room",to=room)
	elif data not in users_ar and username in name_ar:
		users_ar.remove(list(filter(lambda a: filt(a,username) , users_ar))[0])
		users_ar.append(data)
		same_room = list(filter(lambda y: filt_room(y,room) ,users_ar))
		emit("entered",same_room,room=room)
		send(username+" has entered the room",to=room)
	if old_room != room:
	   leave_room(old_room)
	   send(username + ' has left the room.', to=old_room)
	   same_room = list(filter(lambda y: filt_room(y,old_room) ,users_ar))
	   emit("entered",same_room,room=old_room)
	   print(old_room)
	print(users_ar)


"""@socket.on('leave')
def on_leave(data):
    
    print(users_ar,"leave")
    username = data['username']
    room = data['room']
    leave_room(room)
    send(username + ' has left the room.', to=room)
    same_room = list(filter(lambda y: filt_room(y,room) ,users_ar))
    emit("entered",same_room,room=room)
    print(same_room,users_ar,room," same_room")
    """
    

def filt_room(b,room):
	if b["room"]==room:
		return True 
	else:
		return False

def filt(a,username):
	if a["username"]==username:
		return True
	else :
		return False 
	


@socket.on("room_msg")
def rooms(msg):
	print(msg["msg"])
	sid_ar= list(map(lambda x: x["sid"],users_ar))
	room=msg["room"]
	sender=request.sid
	send (msg["msg"],room=room)
	if room in sid_ar:
		send(msg["msg"])



@socket.on("requested_video")
def requested_video(obj):
	global current_vid
	id=obj["id"]
	if obj["room"]:
		room=obj["room"]
	else:
		room=request.sid
	current_vid[room]=id
	emit("requested_video_id",id,room=room)
	
@socket.on("c_time")
def c_time(obj):
	name=obj.get("name")
	c_time=obj.get("c_time")
	room=obj["room"]
	same_room = list(filter(lambda y: filt_room(y,room) ,users_ar))
	for i in same_room:
		if i["username"]==name:
			i["c_time"]=c_time
	highest= max(list(map(lambda x: x["c_time"],same_room)))
	if int(c_time) < int(highest):
		emit("getTo",highest,room=request.sid)

@socket.on("seeked")
def seeked(obj):
	 room=obj["room"]
	 c_time=obj["time"]
	 same_room = list(filter(lambda y: filt_room(y,room) ,users_ar))
	 for i in same_room:
	 	i["c_time"]=c_time
	 emit("seekto",obj,room=room)

@socket.on("paused")
def paused(obj):
	room=obj["room"]
	emit("stop",{},room=room)
@socket.on("played")
def played(obj):
	room=obj["room"]
	emit("start",{},room=room)
@app.route("/yt_search/<string:q>")
def yt_search(q):
	g= YoutubeSearch(q, max_results=50).to_dict()
	videos_ar= []
	
	for j in g:
		thumbnail= "https://i.ytimg.com/vi/"+j["id"]+"/mqdefault.jpg"
		
		videos_ar.append({"id":j["id"],"publishedAt":j["publish_time"],"title":j["title"],"thumbnail":j["thumbnails"][0],"channelTitle":j["channel"],"duration":j["duration"] })
		
	print(videos_ar[0])
	return json.dumps(videos_ar)

entry_names={}
@socket.on("uname")
def uname(name):
	name=name["name"]
	sid=request.sid
	if name not in entry_names.values():
		entry_names[sid]=name
		socket.emit("unique_name",1,room=sid)
		print("unik name")
	else:
		socket.emit("unique_name",0,room=sid)
		print("unik name")
	print(entry_names)
		
@socket.on("disconnect")
def disconnect():
	sid=request.sid
	for i in users_ar:
		if i["sid"]==sid:
			users_ar.remove(i)
	print(users_ar,"users")
	if sid in entry_names.keys():
		entry_names.pop(sid)
	print(entry_names,"entry")
	print(users_ar,"users")
	


if __name__=="__main__":
	app.run()
