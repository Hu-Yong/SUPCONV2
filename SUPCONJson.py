# -*- coding:utf-8 -*-
from time import sleep
import OpenOPC
from flask import Flask, request, render_template, jsonify


app = Flask(__name__)


def get_data(leafname):
    value = opc.read(leafname)
    return value


def get_datas(opc):
    dic = {}
    for name, value, quality, time in opc.iread(taglist[0:20]):
        dic[name] = value
    return jsonify('metal', dic)


def getleafname(opc, node):
    if len(opc.list(node)) == 0:
        return
    if len(opc.list(node)) == 1 and opc.list(node)[0].encode('gb2312') == node:
        taglist.append(node)
        f.write(str(node))
        f.write('\n')
        return

    opc_list = opc.list(node)

    for i in opc_list:
        getleafname(opc, i)


def is_there():
    with open('taglist.txt', 'a+') as f:
        flag = f.readline()
        if flag == "true\n":
            return True
        else:
            f.seek(0, 2)  # 指定从当前文件中的数据的末尾开始写
            f.write("true\n")
            return False


def opc_init():
    opc = OpenOPC.client()
    opcservers = opc.servers()
    for opcserver in opcservers:
        print(opcserver.encode('gb2312'))
    opc.connect(opcservers[0].encode('gb2312'))
    return opc


@app.route("/getdata")
def getdata():
    datas = get_datas(opc)
    return datas


@app.route('/setdata', methods=['POST'])
def setdata():
    name = request.args.get('leafItemId')
    data = request.args.get('pointValue')

    tagname = str(name)
    tagdata = float(str(data))
    print(tagname, tagdata)
    return "success"


if __name__ == '__main__':
    datas = ""
    taglist = []
    all_value = []

    if is_there():
        if len(taglist) == 0:
            with open('taglist.txt', 'r') as f:
                for line in f.readlines():
                    line = line.strip('\n')
                    taglist.append(line)
                taglist = taglist[1:]
        else:
            pass
    else:
        # 往文本里面记录相应的值
        with open('taglist.txt', 'a') as f:
            opc = opc_init()
            getleafname(opc, None)
            opc.close()
    #pool = opcpool.OPCConnectionPool('127.0.0.1')

    opc = opc_init()

    app.run(host='localhost', port=8890, debug=True)
