# -*- coding:utf-8 -*-
import opcpool

pool = opcpool.OPCConnectionPool('127.0.0.1', 5, 10)
while 1:
    conn = pool.acquire()
    print(conn.info())
