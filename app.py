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
#from fbmq import Attachment, Template, QuickReply, Page

#page = Page(PAGE_ACCESS_TOKEN)
messages = {}

#urlparse.uses_netloc.append("postgres")
#url = urlparse.urlparse(os.environ["DATABASE_URL"])

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
                    log("message")
                    if "is_echo" in messaging_event["message"]:
                        return ("ok", 200)
                    sender_id = messaging_event["sender"]["id"]        # the facebook ID of the person sending you the message
                    recipient_id = messaging_event["recipient"]["id"]  # the recipient's ID, which should be your page's facebook ID
                    message_text = messaging_event["message"]["text"]  # the message's text
                    if sender_id in messages:
                        # if we've gotton a class already, this must be the rating.
                        if message_text == "done":
                            send_message(sender_id, "Thank you for your ratings! Please wait a moment while we load your recommendations.")
                            messages[sender_id] = (False, "")
                            return "ok", 200
                        if messages[sender_id][0]:
                            rating = message_text.replace(" ","")
                            if rating.isdigit() and int(rating) > 0 and int(rating) <=5:
                                messages[sender_id] = (False, "")
                                conn.rollback()
                                cur = conn.cursor()
                                stud_id = int(sender_id)
                                class_id = messages[sender_id][1]
                                num_rating = int(rating)
                                cur.execute("INSERT INTO ratings (student_id, class_id, rating) VALUES (%s, %s, %s)", (stud_id, class_id, num_rating))
                                conn.commit()
                                cur.close()
                                send_message(sender_id, "Thanks for the rating. What's another class you are taking?")
                                #print("got the rating")
                                return "ok", 200
                            else:
                                send_message(sender_id, "Your rating must be a number between 1 and 5. Please try again")
                                return "ok", 200
                        else:
                            class_num = which_class(message_text)
                            if class_num > -1:
                                messages[sender_id] = (True, class_num)
                                #print("got the class")
                                send_message(sender_id, "Please rank your enjoyment of the class on a scale of 1 - 5")
                                return "ok", 200
                            else:
                                send_message(sender_id, "I'm sorry, we didn't recognize that class. Please enter another class, or try a shorter abbreviation (ie cs50, sls20, etc")
                                return "ok", 200
                    else:
                        messages[sender_id] = (False, "")
                        #print("added to the dict")
                        send_message(sender_id, "Welcome to ClassRate! We will ask your enjoyment of classes you've taken so far, then give you reccomendations for other classes. The more classes you rate, the better the reccomendations!")
                        send_message(sender_id, "What's a class you are taking or have taken?")
                        return "ok", 200

                    # if keyword(message_text):

                    #     #send_message(sender_id, "did it get here?")
                    #     conn.rollback()
                    #     cur = conn.cursor()
                    #     cur.execute("INSERT INTO ratings (student_id, class_id, rating) VALUES (2, 4, 3.5)")
                    #     conn.commit()
                    #     cur.close()
                    #     #db["classes"].insert(student_id = sender_id, class_id = 2, class_rating = 4.5)
                    #     send_generic_message(sender_id)
                    # else:
                    #     send_message(sender_id, "new again!")
                    #     page.send(recipient_id, "hello world!")

                if messaging_event.get("delivery"):  # delivery confirmation
                    pass

                if messaging_event.get("optin"):  # optin confirmation
                    pass

                if messaging_event.get("postback"):  # user clicked/tapped "postback" button in earlier message
                    pass
    return "ok", 200



def which_class(text):
    text = text.replace(" ", "")
    text = text.lower()
    cur = conn.cursor()
    #conn.rollback()
    row = cur.execute("SELECT id FROM classes WHERE name1 = (%s)", (text,))
    conn.commit()
    cur.close()
    return 2
    if len(row) < 1:
        return -1
    else:
        return row[0]


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
            "title": "ClassRate",
            "subtitle": "Q guide for the lazy",
            "buttons": [{
              "type": "postback",
              "url": "https://www.oculus.com/en-us/rift/",
              "title": "Enter classes"
            }, {
              "type": "postback",
              "title": "Recommend me",
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
