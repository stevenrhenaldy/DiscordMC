from flask import Flask, send_from_directory
from threading import Thread
import random


app = Flask('')

@app.route('/')
def home():
	return 'Im in!'

@app.route('/pic/<path:path>')
def send_js(path):
    return send_from_directory('pic', path)

def run():
  app.run(
		host='0.0.0.0',
		port=80
	)

def keep_alive():
	'''
	Creates and starts new thread that runs the function run.
	'''
	t = Thread(target=run)
	t.start()