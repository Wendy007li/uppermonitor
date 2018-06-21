#!/usr/bin/env python3
# -*- coding: utf-8 -*-
__author__ = 'Li qiaoxia'

from twisted.words.protocols.irc import lowDequote
from builtins import str
from _ast import Str
import logging; logging.basicConfig(level=logging.INFO)
from chardet.chardistribution import Big5DistributionAnalysis
from aiohttp.web_urldispatcher import get
from _socket import IPPORT_RESERVED
from socket import *
import traceback
    

import logging; logging.basicConfig(level=logging.INFO)
from switch import switch

import asyncio, os, json, time
from datetime import datetime
from multiprocessing import Pool
import os, time, random
from config import configs
import mysql.connector
import socket


'''
async tcp application.
'''



PlCstationtype=    {
    'typename':'A',
    'register':'a',
    'instruction':'aRSC',
    }
    
#    {'typename':'B',
#     'register':'b',
#     'instruction':'bRSC'
#          },
   
    

def sendmes(stationnum,ipaddr,port,stationtype,data):
    #waiting for content to be filled in
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # 建立连接:
    s.connect((ipaddr, port))
    # 接收欢迎消息:
    #print(s.recv(1024).decode('utf-8'))
    # 将读到的信息发出去
    for data in [b'Michael', b'Tracy', b'Sarah']:
        # 发送数据:
        s.send(data)
        print(s.recv(1024).decode('utf-8'))
    s.send(b'exit')
    s.close() 
    pass



def plccmd(stationnum,instr,data=''):
  
    instruction='%'
    instruction+=stationnum

       #stationnum本来就是字符串，需转换成ascii
    
    instruction+='#'   #命令指令
  
    instruction+= instr+data
    #BCC
    bcc=0
    insascii=instruction.encode('ascii')
    print("first ascii",insascii)
    for i in range(len(insascii)) :
#        print (insascii[i])
        bcc^=insascii[i]
#        print('bcc=',bcc)
    
    highbcc= hex(int(bcc/16))
    lowbcc= hex(int(bcc%16))

    print('high=%s,low=%s' % (highbcc.encode("ascii"),lowbcc.encode("ascii")))
    
    insascii+=highbcc.strip("0x").encode("ascii")
    insascii+=lowbcc.strip("0x").encode("ascii")

#    insascii+=hex(10).encode("ascii") #0x0a的值转为ascii码，终于对了。
    insascii+=b'\x0d'


#    insascii+=chr(int('0a', 16)).encode("ascii")
   
    print(insascii)
    return insascii
    
def rcvplcmsg(msgdatacome,instr):
    
 #   msgdata= msgdatacome.decode("utf-8")
    datafromplc={
        'getdata':"",
        'res':False
         }
    msgdata= msgdatacome
    print("msgdata=",msgdata)
    datafromplc['res']=False
    l= len(msgdata)
    
    
    
    if msgdata[l-1:l]==  b'\x0d' :
        print('get cr =',msgdata[l-1:l])
    
    if msgdata[0:1] != b'%' :
        logging.info("first character should be %%,not %s " % msgdata[0])
    
    stationnum=msgdata[1:2]
    
    if msgdata[3:4] == b'$' :  #正常应答
        if msgdata[4:6]==instr.encode("ascii"):
            #bcc 校验

            mlen=len(msgdatacome)
            print("mlen=",mlen)
            bcc=0
           
            for i in range(mlen-3) :
#                print (msgdata[i])
                bcc^=msgdata[i]
#                print('bcc=',bcc)
#            getbcc=int(msgdatacome[mlen-3:mlen-3],16)*16+int(msgdatacome[mlen-2:mlen-2])
            
            getbcc = int(str(msgdata[mlen-3:mlen-1],encoding="utf-8"),16)
            
#            print('getbcc=',msgdata[mlen-3:mlen-1],getbcc)
            if getbcc == bcc :
 #               print("ca=",msgdatacome[4:6])
                ca=msgdatacome[4:6].decode()
                print("ca=",ca)
                for case in switch(ca):
                    if case('RD'):  #读取数据寄存器
                        #从第8个字符到len-3 之间的数据，每4个字符一组，16进制，高位在后，低位在前
                        data=msgdata[6:mlen-3]
                        i=0
                        data0 =""
                        if len(data) <4 :
                            break
                        while (i<len(data)):
                            data0+=str(data[i+2:i+4],encoding="utf-8")+str(data[i+0:i+2],encoding="utf-8")
#                            data0+=str(data[i+2:i+3],encoding="utf-8")+str(data[i+3:i+4],encoding="utf-8")+str(data[i+0:i+1],encoding="utf-8")+str(data[i+1:i+2],encoding="utf-8")    
                            i+=4
                        print("get data0 is ",data0)
                        getnum=int(data0,16)

                        print("get 16 base num = ",getnum)
                        datafromplc['res']=True
                        break
                    if case('WD'):  #写入数据寄存器
                        datafromplc['res']=True
                        break
                    if case('SD'):  #预置数据寄存器
                        datafromplc['res']=True
                        break
                    if case():
                        print("nothing in cases")
                        
                        break
                    
            else:
               logging.info("BCC校验出错,收到的bcc=%d, 计算的为%d" %(getbcc, bcc))      
                
            
        else:
           logging.info("非本指令的应答:%s, %s" % (instr[0:2],msgdata[4:6]))   
        
    elif msgdata[3:4] == b'!' :  #出错了
        logging.info("something wrong here,the number is: %s" % msgdata[4:6])  
    else :
        logging.info("not legal code: %s" % msgdata[3:4])     
    return datafromplc
        
def getplcontent(stationnum,ipaddr,stationtype,ipport=9094):   
    #testip='192.168.1.10'
    #testip='127.0.0.1'
    testip=ipaddr
    testport= int(ipport)
    #testsendmsg="D0110501107"  #随便造的测试数据
    rdsendmsg="D3250032501" #read data test
    wdsendmsg="D325003250112345678" #read data test
    wdinstr='WD'
    rdinstr='RD'
    
    print('ipaddr=%s' % ipaddr)

    #    for  data in [1]:
    #改用进程后，需要死循环来获取数据
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
       
    #100ms 超时时间    
    s.settimeout(1) 
    addr=(testip,testport)
    # 建立连接:
    err=s.connect_ex(addr)
    if err != 0 :
        print("cannot connect to %s:%d,errnum=%d " %(testip,testport,err))
        return()
    cc=0
    t1=time.time()
    while True :
        # 发送数据:
        
                
#        print("%d times send to sever",ss.decode(), len(ss) % cc)
        print("%d times send to sever" % cc)
        cc+=1
        '''
        ss=plccmd(stationnum,wdinstr,wdsendmsg)
        try :
            s.sendall(ss)
        except Exception as e:  #catch all exceptions        
            print("something unexpected happened!")
            print ('traceback.print_exc():',traceback.print_exc())
        else :
            print("send over")
        try:
            testrevmsg=s.recv(1024)
        except timeout:
            print("something unexpected happened!")
            print ('traceback.print_exc():',traceback.print_exc())
        else :        
            print("received:",testrevmsg)
        #    print(testrevmsg.decode('utf-8'))
            rcvplcmsg(testrevmsg,wdinstr)
        '''
    # 读测试    
        ss=plccmd(stationnum,rdinstr,rdsendmsg)
        print("send to sever",ss.decode(), len(ss))
    
        s.send(ss)
     #   s.send('\n'.encode('ascii'))
        print("send over")
        testrevmsg=s.recv(1024)
        print("received:",testrevmsg)
    #    print(testrevmsg.decode('utf-8'))
        try:
            rcvplcmsg(testrevmsg,rdinstr)
        except  Exception as e:
            print(" RD test: something unexpected happened!")
            print ('traceback.print_exc():',traceback.print_exc())
        else :        
            print(" RD received:",testrevmsg) 
        time.sleep(0.2)
    #    s.send(b'exit')
    s.close()
    t2=time.time()
    print("run seconds=%d" %(t2-t1))
    #plccmd('01','RD',testsendmsg)
    #testrevmsg=b"%01$RD630044330A0062\n"
    #print("testrevmsg=",testrevmsg)
    #rcvplcmsg(testrevmsg,"RD")


if __name__ == '__main__':  

    kw=configs.db  #get database config file
    # 注意把password设为你的root口令:
    conn = mysql.connector.connect(
            host=kw.get('host', 'localhost'),
            port=kw.get('port', 3306),
            user=kw['user'],
            password=kw['password'],
            db=kw['db'],
            charset=kw.get('charset', 'utf8'),
            autocommit=kw.get('autocommit', True)
        )
    # 运行查询:
    cursor = conn.cursor()
    cursor.execute('select * from PLCstation order by created_at desc')
    plcstations = cursor.fetchall()
    
    p = Pool(5)
    
    for plcsta in plcstations:
    #    print(plcsta)
        stationnum=plcsta[1];
        ipaddr=plcsta[2];
        stationtype=plcsta[3];
        ipport=plcsta[5];
        print("get station=%s,%s,%s,%s" % (stationnum,ipaddr,stationtype,ipport))
        #add processes to deal with every PLc
        p.apply_async(getplcontent, args=(stationnum,ipaddr,stationtype,ipport,))
    
#        sdata=getplcontent(stationnum,ipaddr,stationtype,ipport)
         #   sendmes(stationnum,ipaddr,stationtype,data)
    # 关闭Cursor和Connection: 
    cursor.close()
    conn.close()

    print ('Waiting for all subprocesses done...')
    p.close()
    p.join()
    print ('All subprocesses done.')

   







