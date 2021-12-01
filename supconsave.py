# -*- coding:utf-8 -*-
from time import sleep
import OpenOPC


def opc_init():
    opc = OpenOPC.client()
    opcservers = opc.servers()
    for opcserver in opcservers:
        print(opcserver.encode('gb2312'))
    opc.connect(opcservers[0].encode('gb2312'))
    return opc


if __name__ == '__main__':
    taglist = []
    if len(taglist) == 0:
        with open('taglist.txt', 'r') as f:
            for line in f.readlines():
                line = line.strip('\n')
                taglist.append(line)
            taglist = taglist[1:]
    opc = opc_init()
    x = 0
    dic = {}
    with open('data.txt', 'w+') as f:
        for name, value, quality, time in opc.iread(taglist):
            dic[name] = value
        dic_str = str(dic)
        f.write(dic_str)
    while True:
        with open('data.txt', 'w+') as f:
            for name, value, quality, time in opc.iread(taglist):
                if(quality == "Good"):
                    dic[name] = value
            dic_str = str(dic)
            f.write(dic_str)
        sleep(3)
        x = x + 1
        print(x)
    opc.close()
