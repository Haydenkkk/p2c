import json
from flask import jsonify
import flask
from flask import request  # 获取参数
from flask_cors import CORS
from gen import ProgramStructNode, Output
from Pparser import pParser

# server = flask.Flask(__name__)  # 创建一个flask对象
app = flask.Flask(__name__)
CORS(app)

app.config['CORS_HEADERS'] = 'Content-Type'

@app.route('/p2c', methods=['post'])
def p2c():
    data = request.json
    Parser = pParser()
    middle = Parser.parse(data['body'])
    tree = middle['ast']
    program = ProgramStructNode(tree)
    program.Parse()
    cCodes = Output.FormatOutput()
    res = {
        'cCodes': cCodes,
        'error': middle['error'],
        'warning': middle['warning']
    }
    return jsonify(res)


app.run(host = '0.0.0.0', port=5000,debug=True)  # 启动服务端
