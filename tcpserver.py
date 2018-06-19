#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import socket
import time, threading

def tcplink(sock, addr):
    print('Accept new connection from %s:%s...' % addr)
#    sock.send(b'Welcome!')
    while True:
        data = sock.recv(1024)
        time.sleep(1)
        print("data reveiced=",data,len(data))
        if not data or data.decode('utf-8') == 'exit':
            break
#        sock.send(('I got, %s!' % data.decode('utf-8')).encode('utf-8'))
        print(('I got, %s!' % data))
        sock.send(data)
    sock.close()
    print('Connection from %s:%s closed.' % addr)
    

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# 绑定端口:
s.bind(('127.0.0.1', 9094))
s.listen(5)
print('Bind UDP on 9999...')

while True:
    # 接受一个新连接:
    sock, addr = s.accept()
    # 创建新线程来处理TCP连接:
    t = threading.Thread(target=tcplink, args=(sock, addr))
    t.start()