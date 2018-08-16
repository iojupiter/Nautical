#!dep/bin/python

import pika, sys, json, os



def subscriber():

	connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
	channel = connection.channel()
	
	channel.exchange_declare(exchange='microapiTree', type='direct')
	channel.queue_declare(queue='foodscan')
	channel.queue_bind(exchange='microapiTree', queue='foodscan', routing_key='foodscan')

	def callback(ch, method, properties, body):
		if(body != ''):	
			print "...doing work..."
			data = json.loads(body)
			userPayload = json.loads(data['payload'])
			snippet = userPayload['userPayload']
			data = {"sid":data['sid'], "microapp":"foodscan", "return":{"data":snippet}
			data = json.dumps(data)
			connection.close()
			publisher(data)
			"""
			b = json.loads(body)
			if 'payload' in b:
				c = b['payload']
				print c
				if 'userPayload' in c:
					barcode = int(c['userPayload'])
					print barcode
					query = "http://world.openfoodfacts.org/api/v0/product/%d.json" % (barcode)
					OFFquery = "curl "+ query
					OFFresponse = os.popen(OFFquery).read()
					print(OFFresponse)
					data = json.loads(OFFresponse)
					if (data['status_verbose'] == 'product not found'):
						#return product not found
						response = {"status":"product not found"}
						#readyResponse = json.dumps(response)
						#connection.close()
						#publishResponseToFront(readyResponse)
					elif (data['status_verbose'] == 'product found'):
						product = data['product']
						if 'image_small_url' not in product:
							prodImg = "unknown"
						else:
							prodImg = data['product']['image_small_url']
						if 'generic_name' not in product:
							prodName = "unknown"
						else:
							prodName = data['product']['generic_name']
						if 'nutrient_levels' not in product:
							nutrientLevels = "unknown"
						else:
							nutrientLevels = data['product']['nutrient_levels']
						if 'ingredients_text' not in product:
							ingredients = "unknown"
						else:
							ingredients = data['product']['ingredients_text']
						if 'allergens_tags' not in product:
							allergens = "unknown"
						else:
							allergens = data ['product']['allergens_tags']
						allergenArray = []
						for a in allergens:
							y = a[3:]
							s = y.encode("utf-8")
							allergenArray.append(s)
						response = {
							"status": "product found",
							"prodImg": prodImg,
							"prodName": prodName,
							"nutrientLevels": nutrientLevels,
							"ingredients": ingredients,
							"allergens": allergenArray
							}
						readyResponse = json.dumps(response)
						print readyResponse
						
				else:
					print "userID log bro!"
			"""
					
			
	channel.basic_consume(callback, queue='foodscan', no_ack=True)

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