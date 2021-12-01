# -*- coding:utf-8 -*-
from flask import Flask, jsonify, request
import OpenOPC
app = Flask(__name__)


def opc_init():
    opc = OpenOPC.client()
    opc.connect('SUPCON.SCRTCore')
    return opc


def read_data():
    with open('data.txt', 'r') as f:
        tmp = f.read()
        return tmp


@app.route('/setdata', methods=['POST'])
def setdata():
    if request.method == 'POST':
        name = request.form['leafItemId']
        data = request.form['pointValue']

        tagname = str(name)
        tagdata = str(data)
        print(tagname, tagdata)
        opc = opc_init()
        flag = opc.write([tagname, tagdata])
        opc.close()
        return flag
    else:
        return "please send a post request"


@app.route("/getdata")
def getdata():
    datas = read_data()
    return datas


if __name__ == '__main__':
    app.run(host='172.20.0.130', port=8888, debug=True)
