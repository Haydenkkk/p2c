from flask import jsonify
import flask
from flask import request  # 获取参数
from flask_cors import CORS
from newgen import ProgramStructNode, Output
from Pparser import pParser

# 创建一个flask对象
app = flask.Flask(__name__)
CORS(app)

app.config['CORS_HEADERS'] = 'Content-Type'

@app.route('/p2c', methods=['post'])
def p2c():
    data = request.json
    Parser = pParser()
    middle = Parser.parse(data['PascalCode'])
    tree = middle['ast']
    if tree is None:
        return jsonify({
            'cCodes': 'Something wrong with this code.',
            'error': middle['error'],
            'warning': middle['warning']
        })
    else:
        program = ProgramStructNode(tree)
        program.Parse()
        cCodes = Output.FormatOutput()
        return jsonify({
            'cCodes': cCodes,
            'error': middle['error'],
            'warning': middle['warning']
        })


app.run(host = '0.0.0.0', port=5000,debug=True)  # 启动服务端
