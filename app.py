# starter code from tutorial on FB chat bots by Hartley Brody.
# https://blog.hartleybrody.com/fb-messenger-bot/

import os
import sys
import json
import psycopg2
import urlparse

import requests
from flask import Flask, request
from pydal import DAL, Field
from fbmq import Attachment, Template, QuickReply, Page

page = Page(EAAFcHZCdCaGwBAIP6pJPLww9ZA2rQDomnqA8mnWo6QdL7umCOzKtRdiUT0u4uYHhRrDwVZAgbt9b5ps5GdVMRnmvLsQJRy9dZBZCFPmFI2DiWWQj48kHFzKJtoZBQJ2mqEiT9O9Swfwo5ueh6oTeeBXGA6iq0Y0rqzx7AMVt5JXgZDZD);


urlparse.uses_netloc.append("postgres")
url = urlparse.urlparse(os.environ["DATABASE_URL"])

conn = psycopg2.connect(
    database="d1a2od5rrpp3su",
    user="gjgpjsukugfdfa",
    password="9013121b453bb37b38e6518bd32c615c5d6b6fcf162d6a3113ab0088ac91cfba",
    host="ec2-107-22-236-252.compute-1.amazonaws.com",
    port=5432
)

#db = DAL('postgres://gjgpjsukugfdfa:9013121b453bb37b38e6518bd32c615c5d6b6fcf162d6a3113ab0088ac91cfba@ec2-107-22-236-252.compute-1.amazonaws.com:5432/d1a2od5rrpp3su')

app = Flask(__name__)


@app.route('/', methods=['GET'])
def verify():
    # when the endpoint is registered as a webhook, it must echo back
    # the 'hub.challenge' value it receives in the query arguments
    if request.args.get("hub.mode") == "subscribe" and request.args.get("hub.challenge"):
        if not request.args.get("hub.verify_token") == os.environ["VERIFY_TOKEN"]:
            return "Verification token mismatch", 403
        return request.args["hub.challenge"], 200

    return "Hello world", 200


@app.route('/', methods=['POST'])
def webhook():

    # endpoint for processing incoming messaging events

    data = request.get_json()
    log(data)  # you may not want to log every incoming message in production, but it's good for testing

    if data["object"] == "page":

        for entry in data["entry"]:
            for messaging_event in entry["messaging"]:

                if messaging_event.get("message"):  # someone sent us a message



                    sender_id = messaging_event["sender"]["id"]        # the facebook ID of the person sending you the message
                    recipient_id = messaging_event["recipient"]["id"]  # the recipient's ID, which should be your page's facebook ID
                    message_text = messaging_event["message"]["text"]  # the message's text
                    if keyword(message_text):

                        #send_message(sender_id, "did it get here?")
                        conn.rollback()
                        cur = conn.cursor()
                        cur.execute("INSERT INTO ratings (student_id, class_id, rating) VALUES (2, 4, 3.5)")
                        conn.commit()
                        cur.close()
                        #db["classes"].insert(student_id = sender_id, class_id = 2, class_rating = 4.5)
                        send_generic_message(sender_id)
                    else:
                        send_message(sender_id, "new again!")
                        page.send(recipient_id, "hello world!")

                if messaging_event.get("delivery"):  # delivery confirmation
                    pass

                if messaging_event.get("optin"):  # optin confirmation
                    pass

                if messaging_event.get("postback"):  # user clicked/tapped "postback" button in earlier message
                    pass
    return "ok", 200



def is_class(text):
    text = text.replace(" ", "")
    text = text.lower()
    curr = conn.cursor();
    cur.execute("SELECT id FROM classes WHERE name = ?", )


def keyword(message):
    if (message == "home"):
        return True
    else:
        return False

def send_message(recipient_id, message_text):

    log("sending message to {recipient}: {text}".format(recipient=recipient_id, text=message_text))

    params = {
        "access_token": os.environ["PAGE_ACCESS_TOKEN"]
    }
    headers = {
        "Content-Type": "application/json"
    }
    data = json.dumps({
        "recipient": {
            "id": recipient_id
        },
        "message": {
            "text": message_text
        }
    })
    r = requests.post("https://graph.facebook.com/v2.6/me/messages", params=params, headers=headers, data=data)
    if r.status_code != 200:
        log(r.status_code)
        log(r.text)

def send_generic_message(recipientId):
    params = {
        "access_token": os.environ["PAGE_ACCESS_TOKEN"]
    }
    headers = {
        "Content-Type": "application/json"
    }
    messageData = json.dumps({
    "recipient": {
      "id": recipientId
    },
    "message": {
      "attachment": {
        "type": "template",
        "payload": {
          "template_type": "generic",
          "elements": [{
            "title": "rift",
            "subtitle": "Next-generation virtual reality",
            "item_url": "https://www.oculus.com/en-us/rift/",
            "image_url": "http://messengerdemo.parseapp.com/img/rift.png",
            "buttons": [{
              "type": "web_url",
              "url": "https://www.oculus.com/en-us/rift/",
              "title": "Open Web URL"
            }, {
              "type": "postback",
              "title": "Call Postback",
              "payload": "Payload for first bubble",
            }],
          }, {
            "title": "touch",
            "subtitle": "Your Hands, Now in VR",
            "item_url": "https://www.oculus.com/en-us/touch/",
            "image_url": "http://messengerdemo.parseapp.com/img/touch.png",
            "buttons": [{
              "type": "web_url",
              "url": "https://www.oculus.com/en-us/touch/",
              "title": "Open Web URL"
            }, {
              "type": "postback",
              "title": "Call Postback",
              "payload": "Payload for second bubble",
            }]
          }]
        }
      }
    }
    })
    r = requests.post("https://graph.facebook.com/v2.6/me/messages", params=params, headers=headers, data=messageData)
    if r.status_code != 200:
        log(r.status_code)
        log(r.text)



def log(message):  # simple wrapper for logging to stdout on heroku
    print str(message)
    sys.stdout.flush()


if __name__ == '__main__':
    app.run(debug=True)
