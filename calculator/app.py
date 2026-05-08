from flask import Flask, request, jsonify
from werkzeug.exceptions import HTTPException
import logging

app = Flask(__name__)

# Disable Flask's default logging
log = logging.getLogger('werkzeug')
log.setLevel(logging.CRITICAL)

# Only log actual errors (exceptions)
logger = logging.getLogger(__name__)
logger.setLevel(logging.ERROR)


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


@app.errorhandler(Exception)
def handle_error(e):
    # Don't log HTTP errors (4XX, 5XX from Flask)
    if isinstance(e, HTTPException):
        return jsonify({'error': str(e)}), e.code
    
    # Log actual code errors
    logger.error(f"Error: {str(e)}")
    return jsonify({'error': 'Internal server error'}), 500
