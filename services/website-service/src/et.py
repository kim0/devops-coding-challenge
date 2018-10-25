#!/usr/bin/env python3
from flask import Flask
import datetime
app = Flask(__name__)

@app.route("/healthz")
def healthz():
    return "OK!"

@app.route("/now")
def now():
    return datetime.datetime.utcnow().isoformat(timespec="seconds")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
