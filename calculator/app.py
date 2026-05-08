from flask import Flask, request, jsonify

app = Flask(__name__)


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
