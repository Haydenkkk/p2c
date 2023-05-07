import json
from flask import jsonify
import flask
from flask import request  # 获取参数
from flask_cors import CORS
from Pparser import pParser

# server = flask.Flask(__name__)  # 创建一个flask对象
app = flask.Flask(__name__)
CORS(app)

app.config['CORS_HEADERS'] = 'Content-Type'

@app.route('/p2c', methods=['post'])
def p2c():
    data = request.json
    Parser = pParser()
    res = Parser.parse(data)
    # temp_data = json.dumps(res)
    print(data)
    return jsonify(res)