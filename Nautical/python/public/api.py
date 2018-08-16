#!dep/bin/python

import os, sys, subprocess, shutil, json, flask
from flask import Flask, render_template, request
from flask_socketio import SocketIO
import pika, thread, gevent
import rethinkdb as r

app = Flask(__name__, static_folder = "static")
socketio = SocketIO(app)

"""
@app.route('/')
def main():
	return render_template('home.html')
"""


conn = r.connect(db='skipperTracker').repl()
r.table('skipper').run(conn)

#CONNECTION EVENTS
@socketio.on('connect')
def ws_connect():
	sid = str(request.sid)
	return
@socketio.on('add')
def ws_add(input):
	sid = str(request.sid)
	userData = json.loads(input)
	r.table("skipper").insert({
    	"skipperID": userData['userID'],
    	"sessionID": sid,
    	"GPS": userData['gps'],
    	"Room": "home"
	}).run(conn)
	print "NEW USER: ", request.sid
	c = render_template('home.html')
	socketio.emit('msg', {'content': c})
	return
	
@socketio.on('disconnect')
def ws_disconnect():
	sid = str(request.sid)
	return
@socketio.on('remove')
def ws_remove(input):
	sid = str(request.sid)
	r.table("skipper").filter({"sessionID": sid}).delete().run(conn)
	print "REMOVING USER remove: ", request.sid
	return
	



"""
@socketio.on('user')
def ws_user(input):
	#dump json, make db query
	#userID = json['d']
	#print('received userID: ' + userID)
	c = render_template('home.html')
	socketio.emit('msg', {'content': c})
	return
"""



#MICRO-APP EVENTS
@socketio.on('home')
def ws_home(input):
	sid = request.sid
	userData = json.loads(input)
	data = {"microapp":"home", "payload":input}
	c = render_template('home.html')
	socketio.emit('msg', {'content': c})
	r.table("skipper").filter({"skipperID": userData['userID']}).update({
    	"GPS": userData['gps'],
    	"Room": "home"
	}).run(conn)
	return
	
@socketio.on('menu')
def ws_menu(input):
	sid = request.sid
	userData = json.loads(input)
	data = {"microapp":"menu", "sid":sid, "payload":input}
	print userData['userPayload']
	digest = json.dumps(data)
	inpoint(digest)
	r.table("skipper").filter({"skipperID": userData['userID']}).update({
    	"GPS": userData['gps'],
    	"Room": userData['userPayload']
	}).run(conn)
	return	
	
@socketio.on('jukebox')
def ws_jukebox(input):
	sid = request.sid
	userData = json.loads(input)
	data = {"microapp":"jukebox", "sid":sid, "payload":input}
	digest = json.dumps(data)
	inpoint(digest)
	r.table("skipper").filter({"skipperID": userData['userID']}).update({
    	"GPS": userData['gps'],
    	"Room": "jukebox"
	}).run(conn)
	return

@socketio.on('games')
def ws_games(input):
	sid = request.sid
	userData = json.loads(input)
	data = {"microapp":"games", "sid":sid, "payload":input}
	digest = json.dumps(data)
	inpoint(digest)
	r.table("skipper").filter({"skipperID": userData['userID']}).update({
    	"GPS": userData['gps'],
    	"Room": "games"
	}).run(conn)
	return
	
@socketio.on('payments')
def ws_payments(input):
	sid = request.sid
	userData = json.loads(input)
	data = {"microapp":"payments", "sid": sid, "payload":input}
	digest = json.dumps(data)
	inpoint(digest)
	r.table("skipper").filter({"skipperID": userData['userID']}).update({
    	"GPS": userData['gps'],
    	"Room": "payments"
	}).run(conn)
	return
	
@socketio.on('loyalty')
def ws_payments(input):
	sid = request.sid
	userData = json.loads(input)
	data = {"microapp":"loyalty", "sid": sid, "payload":input}
	digest = json.dumps(data)
	inpoint(digest)
	r.table("skipper").filter({"skipperID": userData['userID']}).update({
    	"GPS": userData['gps'],
    	"Room": "loyalty"
	}).run(conn)
	return
	
@socketio.on('foodscan')
def ws_foodscan(input):
	sid = request.sid
	userData = json.loads(input)
	data = {"microapp":"foodscan", "sid": sid, "payload":input}
	digest = json.dumps(data)
	inpoint(digest)
	r.table("skipper").filter({"skipperID": userData['userID']}).update({
    	"GPS": userData['gps'],
    	"Room": "foodscan"
	}).run(conn)
	return

def inpoint(digest):
	data = json.loads(digest)
	microapp = data['microapp']
	connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
	channel = connection.channel()
	channel.exchange_declare(exchange='microapiTree', type='direct')

	channel.basic_publish(exchange='microapiTree', routing_key=microapp, body=digest)
	print("[X] INPOINT %r:%r" % (microapp, digest))
	connection.close()
	return

#NEW THREAD ?? PROBLEMS WITH TEMPLATE_RENDER ON DOUBLE TOUCH ONLY
def outpoint():
	print "THREAD outpoint!"
	connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
	channel = connection.channel()
	channel.queue_declare(queue='outboundQueue')
	with app.app_context():
		def callback(ch, method, properties, body):
			print("[x] OUTPOINT %r" % body)
			data = json.loads(body)
			t = data['microapp']+".html"
			v = data['return']['data']
			c = render_template(t, x=v)
			socketio.emit('msg', {'content': c}, room=data['sid'])
			print "RENDERED: "

			
		channel.basic_consume(callback, queue='outboundQueue', no_ack=True)
		channel.start_consuming()
	return
	
if __name__ == '__main__':
	address = subprocess.check_output("ifconfig en0 | awk '{ print $2}' | grep -E -o '([0-9]{1,3}[\.]){3}[0-9]{1,3}'", shell=True).strip()
	thread.start_new_thread(outpoint, ())
	socketio.run(app, host=address, port=7777, debug=True)
