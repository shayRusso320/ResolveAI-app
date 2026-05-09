from flask import Flask, request, jsonify
from werkzeug.exceptions import HTTPException
import logging
import sys
from pythonjsonlogger import jsonlogger

app = Flask(__name__)


# Set up structured JSON logging for our app only
logger = logging.getLogger(__name__)
handler = logging.StreamHandler()
formatter = jsonlogger.JsonFormatter('%(asctime)s %(levelname)s %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)
logger.propagate = False

# Handle uncaught exceptions through JSON logger
def handle_uncaught(exc_type, exc_value, exc_traceback):
    logger.error("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))

sys.excepthook = handle_uncaught


def add(a, b):
    return a + b


def subtract(a, b):
    return a - b


def multiply(a, b):
    return a * b


def divide(a, b):
    return a / b


@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'healthy'})


@app.route('/add', methods=['POST'])
def add_route():
    data = request.json
    return jsonify({'result': add(data['a'], data['b'])})


@app.route('/subtract', methods=['POST'])
def subtract_route():
    data = request.json
    return jsonify({'result': subtract(data['a'], data['b'])})


@app.route('/multiply', methods=['POST'])
def multiply_route():
    data = request.json
    return jsonify({'result': multiply(data['a'], data['b'])})


@app.route('/divide', methods=['POST'])
def divide_route():
    data = request.json
    return jsonify({'result': divide(data['a'], data['b'])})

