from flask import Flask, request
from threading import Thread
import requests
from requests.structures import CaseInsensitiveDict
import os

app = Flask('')

@app.route('/')
def home():
    return "Hello. I am alive!"

@app.route('/delete', methods = ["POST"])
def deletemessage():
  data = request.get_json()
  url = "https://discord.com/api/channels/"+str(data["channelid"]).split('.')[0]+"/messages/"+data["messageid"]
  print(url)
  headers = CaseInsensitiveDict()
  headers["Authorization"] = "Bot "+os.environ['Bot_secret']
  print(headers)
  resp = requests.delete(url, headers=headers)
  print(resp.text)
  if resp.ok:
    return "Deleted"
  return "Error"


def run():
  app.run(host='0.0.0.0',port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()