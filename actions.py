from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

from rasa_sdk import Action
from rasa_sdk.events import SlotSet
import zomatopy
import json
import smtplib
from email.message import EmailMessage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

class ActionSearchRestaurants(Action):
	def name(self):
		return 'action_search_restaurants'
		
	def run(self, dispatcher, tracker, domain):
		config={ "user_key":"f4924dc9ad672ee8c4f8c84743301af5"}
		zomato = zomatopy.initialize_app(config)
		loc = tracker.get_slot('location')
		cuisine = tracker.get_slot('cuisine')
		location_detail=zomato.get_location(loc, 1)
		d1 = json.loads(location_detail)
		lat=d1["location_suggestions"][0]["latitude"]
		lon=d1["location_suggestions"][0]["longitude"]
		cuisines_dict={'bakery':5,'chinese':25,'cafe':30,'italian':55,'biryani':7,'north indian':50,'south indian':85}
		results=zomato.restaurant_search("", lat, lon, str(cuisines_dict.get(cuisine)), 5, "&sort=rating&order=desc")
		d = json.loads(results)
		response=""
		if d['results_found'] == 0:
			response= "no results"
		else:
			for restaurant in d['restaurants']:
				response=response+ "Found "+ restaurant['restaurant']['name']+ " in "+ restaurant['restaurant']['location']['address'] + " has been rated "+ restaurant['restaurant']['user_rating']['aggregate_rating']+"\n"
		
		dispatcher.utter_message("-----"+response)
		return [SlotSet('location',loc)]
	
class ActionSendEmail(Action):
	def name(self):
		return 'action_send_email'
	
	def run(self, dispatcher, tracker, domain):
		config={ "user_key":"f4924dc9ad672ee8c4f8c84743301af5"}
		zomato = zomatopy.initialize_app(config)
		loc = tracker.get_slot('location')
		cuisine = tracker.get_slot('cuisine')
		location_detail=zomato.get_location(loc, 1)
		d1 = json.loads(location_detail)
		lat=d1["location_suggestions"][0]["latitude"]
		lon=d1["location_suggestions"][0]["longitude"]
		cuisines_dict={'bakery':5,'chinese':25,'cafe':30,'italian':55,'biryani':7,'north indian':50,'south indian':85}
		results=zomato.restaurant_search("", lat, lon, str(cuisines_dict.get(cuisine)), 10, "&sort=rating&order=desc")
		d = json.loads(results)
		response=""
		if d['results_found'] == 0:
			response= "no results"
		else:
			for restaurant in d['restaurants']:
				response=response+ "<ul><li> Restaurant name: "+ restaurant['restaurant']['name']+ "</li><li>Restaurant locality address: "+ restaurant['restaurant']['location']['address'] + "</li><li>Zomato user rating: "+ restaurant['restaurant']['user_rating']['aggregate_rating'] + "</li></ul>"
		user_email = tracker.get_slot('email')
		msg = MIMEMultipart('alternative')
		msg['Subject'] = "Restaurants tailored for you"
		msg['From'] = "birjushah.dml17@iiitb.net"
		msg['To'] = user_email
		msg.attach(MIMEText(response, 'html'))
		# Send the message via our own SMTP server.
		server = smtplib.SMTP_SSL('smtp.gmail.com',465)
		server.ehlo()
		server.login('birjushah.dml17@iiitb.net','Certanity@123')
		server.sendmail('birjushah.dml17@iiitb.net',user_email,msg.as_string())
		server.close()
		dispatcher.utter_message('Mail sent')


