from flask import Flask
import os

app = Flask(__name__)

@app.route("/")
def home():
    token = os.environ.get("UPSTOX_TOKEN", "NO TOKEN")
    if token == "NO TOKEN":
        return "<h1>Token not found</h1>"
    return "<h1>Nifty Dashboard Cloud Running</h1><p>Token loaded: YES</p>"
