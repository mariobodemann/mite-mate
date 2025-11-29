import subprocess as sub

from base64 import b64encode

import json

import requests

from flask import request
from flask import Flask
app = Flask('MiteMate.Server')

@app.get('/')
def root():
    return '"OK"'

@app.get('/battery')
def battery():
    proc = sub.run(["termux-battery-status"], capture_output=True)
    return proc.stdout

@app.get('/notes')
def notes():
    proc = sub.run(["termux-notification-list"], capture_output=True)
    cleaned = filter(lambda l: l['title'], json.loads(proc.stdout))
    return [{'from':x['packageName'],'title':x['title'], 'content':x['content']} for x in cleaned]

@app.get('/pokemon')
def mon():
    mon_id = request.args.get("id", 42)

    try:
        mon = requests.get(f"https://pokeapi.co/api/v2/pokemon/{mon_id}")
        if mon.ok:
            monj = mon.json()

            sprite = requests.get(
                monj["sprites"]["front_default"]
            )

            spriteb64 = b64encode(sprite.content).decode() if sprite.ok else None
            return {
                "id":monj["id"],
                "name":monj["name"],
                "image":spriteb64,
            }
        else:
            return (f'{{"{mon.status}": "{mon.content}"}}',mon.status)
    except Exception as e:
        print(e)
        return (f'{{"400": "{e}"}}',400)


@app.get('/fetch')
def fetch():
    method = request.args.get("method", "GET")
    url = request.args.get("url", None)
    if not url:
        return 404

    else:
        if method == "GET":
            return requests.get(url)
        else:
            return f"Method {method} not found."


app.run()
