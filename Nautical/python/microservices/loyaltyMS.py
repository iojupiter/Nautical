#!dep/bin/python

import pika, sys, json



def subscriber():

	connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
	channel = connection.channel()
	
	channel.exchange_declare(exchange='microapiTree', type='direct')
	channel.queue_declare(queue='loyalty')
	channel.queue_bind(exchange='microapiTree', queue='loyalty', routing_key='loyalty')

	def callback(ch, method, properties, body):
		if(body != ''):	
			print "...doing work..."
			data = json.loads(body)
			userPayload = json.loads(data['payload'])
			snippet = userPayload['userPayload']
			data = {"sid":data['sid'], "microapp":"loyalty", "return":{"data":snippet}}
			data = json.dumps(data)
			connection.close()
			publisher(data)
			
	channel.basic_consume(callback, queue='loyalty', no_ack=True)

	print(' [*] Waiting for messages. To exit press CTRL+C')
	channel.start_consuming()
	
	return
	
def publisher(data):	
	connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
	channel = connection.channel()

	channel.queue_declare(queue='outboundQueue')

	channel.basic_publish(exchange='', routing_key='outboundQueue', body=data)

	connection.close()
	subscriber()
	
if __name__ == '__main__':
	subscriber()