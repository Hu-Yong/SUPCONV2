# -*- coding:utf-8 -*-
import threading
import time
from typing import Any
import OpenOPC

#from client import HTTPConnection, HTTPResponse


def opc_init():
    opc = OpenOPC.client()
    opcservers = opc.servers()
    for opcserver in opcservers:
        print(opcserver.encode('gb2312'))
    opc.connect(opcservers[0].encode('gb2312'))
    return opc


class OPCConnectionPool:

    def __init__(self, host, max_size=5, idle_timeout=20):
        """
        :param host: pass
        :param max_size: 同时存在的最大连接数, 默认None->连接数无限,没了就创建
        :param idle_timeout: 单个连接单次最长空闲时间,超时自动关闭,默认None->不限时
        """
        self.host = host
        self.max_size = max_size
        self.idle_timeout = idle_timeout
        self._lock = threading.Condition()
        self._pool = []
        # 这里的conn_num指的是总连接数,包括其它线程拿出去正在使用的连接
        self.conn_num = 0
        self.is_closed = False
        self._clearer = None
        self.start_clear_conn()

    def acquire(self, blocking=True, timeout=None):
        if self.is_closed:
            raise ConnectionPoolClosed
        with self._lock:
            if self.max_size is None or not self.is_full():
                # 在还能创建新连接的情况下,如果没有空闲连接,直接创建一个就行了
                if self.is_pool_empty():
                    self._put_connection(self._create_connection())
            else:
                # 不能创建新连接的情况下,如果设置了blocking=False,没连接就报错
                # 否则,就基于timeout进行阻塞,直到超时或者有可用连接为止
                if not blocking:
                    if self.is_pool_empty():
                        raise EmptyPoolError
                elif timeout is None:
                    while self.is_pool_empty():
                        self._lock.wait()
                elif timeout < 0:
                    raise ValueError("'timeout' must be a non-negative number")
                else:
                    end_time = time.time() + timeout
                    while self.is_pool_empty():
                        remaining = end_time - time.time()
                        if remaining <= 0:
                            raise EmptyPoolError
                        self._lock.wait(remaining)
            # 走到这一步了,池子里一定有空闲连接
            return self._get_connection()

    def release(self, conn):
        if self.is_closed:
            # 如果这个连接是在连接池关闭后才释放的,那就不用回连接池了,直接放生
            conn.close()
            return
        # 实际上,python列表的append操作是线程安全的,可以不加锁
        # 这里调用锁是为了通过notify方法通知其它正在wait的线程:现在有连接可用了
        with self._lock:
            if not conn.is_available:
                # 如果这个连接不可用了,就应该创建一个新连接放进去,因为可能还有其它线程在等着连接用
                conn.close()
                self.conn_num -= 1
                conn = self._create_connection()
            self._put_connection(conn)
            self._lock.notify()

    def _get_connection(self):
        # 这个方法会把连接从_idle_conn移动到_used_conn列表中,并返回这个连接
        try:
            return self._pool.pop()
        except IndexError:
            raise EmptyPoolError

    def _put_connection(self, conn):
        conn.last_time = time.time()
        self._pool.append(conn)

    def _create_connection(self):
        self.conn_num += 1
        return opc_init()

    def is_pool_empty(self):
        # 这里指的是,空闲可用的连接是否为空
        return len(self._pool) == 0

    def is_full(self):
        if self.max_size is None:
            return False
        return self.conn_num >= self.max_size

    def close(self):
        if self.is_closed:
            return
        self.is_closed = True
        self.stop_clear_conn()
        pool, self._pool = self._pool, None
        for conn in pool:
            conn.close()

    def clear_idle_conn(self):
        if self.is_closed:
            raise ConnectionPoolClosed
        # 这里开一个新线程来清理空闲连接,避免了阻塞主线程导致的定时精度出错
        threading.Thread(target=self._clear_idle_conn).start()

    def _clear_idle_conn(self):
        if not self._lock.acquire(timeout=self.idle_timeout):
            # 因为是每隔self.idle_timeout秒检查一次
            # 如果过了self.idle_timeout秒还没申请到锁,下一次都开始了,本次也就不用继续了
            return
        current_time = time.time()
        if self.is_pool_empty():
            pass
        elif current_time - self._pool[-1].last_time >= self.idle_timeout:
            # 这里处理下面的二分法没法处理的边界情况,即所有连接都闲置超时的情况
            self.conn_num -= len(self._pool)
            self._pool.clear()
        else:
            # 通过二分法找出从左往右第一个不超时的连接的指针
            left, right = 0, len(self._pool) - 1
            while left < right:
                mid = (left + right) // 2
                if current_time - self._pool[mid].last_time >= self.idle_timeout:
                    left = mid + 1
                else:
                    right = mid
            self._pool = self._pool[left:]
            self.conn_num -= left
        self._lock.release()

    def start_clear_conn(self):
        if self.idle_timeout is None:
            # 如果空闲连接的超时时间为无限,那么就不应该清理连接
            return
        self.clear_idle_conn()
        self._clearer = threading.Timer(
            self.idle_timeout, self.start_clear_conn)
        self._clearer.start()

    def stop_clear_conn(self):
        if self._clearer is not None:
            self._clearer.cancel()

    def __enter__(self):
        return self

    def __exit__(self, *exit_info):
        self.close()


class EmptyPoolError(Exception):
    pass


class ConnectionPoolClosed(Exception):
    pass
