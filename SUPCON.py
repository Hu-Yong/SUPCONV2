# -*- coding:utf-8 -*-
from time import sleep
import OpenOPC
import socket


def get_data(leafname):
    value = opc.read(leafname)
    return value


def getleafname(node):
    if len(opc.list(node)) == 0:
        return
    if len(opc.list(node)) == 1 and opc.list(node)[0].encode('gb2312') == node:
        taglist.append(node)
        value = get_data(node)
        f.write(str(node))
        f.write('\n')
        return

    opc_list = opc.list(node)

    for i in opc_list:
        getleafname(i)


def tag_list():
    with open('taglist.txt', 'a+') as f:
        flag = f.readline()
        if flag == "true\n":
            return True
        else:
            f.seek(0, 2)  # 指定从当前文件中的数据的末尾开始写
            f.write("true\n")
            return False


if __name__ == '__main__':
    taglist = []
    opc = OpenOPC.client()
    opcservers = opc.servers()
    for opcserver in opcservers:
        print(opcserver.encode('gb2312'))
    opc.connect(opcservers[0].encode('gb2312'))

    server = socket.socket(
        socket.AF_INET, socket.SOCK_STREAM)         # 创建 socket 对象
    host = socket.gethostname()  # 获取本地主机名
    # host = '172.20.0.130'
    print(host)
    port = 15681                # 设置端口
    server.bind((host, port))   # 绑定端口
    server.listen(5)

    if tag_list():
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
            getleafname(None)
    while True:
        conn, addr = server.accept()     # 建立客户端连接
        print(conn, addr)
        while True:
            try:
                datas = opc.read(taglist)
                for data in datas:
                    conn.send(str(data)+"\n")
                sleep(10)
            except:
                print("client is disconnect")
                break
        conn.close()
    server.close()
    opc.close()
