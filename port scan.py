import threading
from optparse import OptionParser
import socket
import re
import queue

RED = '\033[1;31m'  #红色
GRE = '\033[1;32m'  #绿色
YEL = '\033[1;33m'  #黄色
que=queue.Queue()    #初始化
USAGE='''
Usage:python port.py 8.8.8.8
      python port.py 8.8.8.8 -p 21,80,8080
      python port.py 8.8.8.8 -p 21,80,8080 -n 50
'''

class Scanner(object):
    def __init__(self,target,port,threadnum = 100):
        if re.match(r"^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$",target):
            self.target = target
        else:
            print(RED+"[*]  IP Invalid !!!")
            exit()

        self.port=port
        self.threadnum=threadnum


    def start(self):
        if self.port == 65535:
            for i in range(0,65536):
                que.put(i)
        else:
            for i in self.port:
                if int(i) < 0 or int(i) > 65535:
                    print(RED + '\n[-] 端口错误！请指定0~65535之间的垛口范围！')
                    exit()
                que.put(i)

        try:
            print(YEL +"[*] 正在扫描%s"%self.target)
            thread_pool =[]
            for i in range(0,int(self.threadnum)):
                th = threading.Thread(target=self.run,args=())
                thread_pool.append(th)
            for th in thread_pool:
                th.setDaemon(True)
                th.start()
            que.join()
            print(YEL+"[*]扫描完成！！")  

        except Exception as e:
            print(e)
        except KeyboardInterrupt:
            print(YEL+"[*]用户自行退出扫描！！")   

    def run(self):
        while not que.empty():
            port = int(que.get())
            if self.portScan(port):
                banner = self.getSocketBanner(port)
                if banner:
                    print(GRE+"[*]%d------------open\t%s"%(port,banner))
                else:
                    print(GRE+"[*]%d------------open\t"%(port))
            que.task_done()            

    def portScan(self,prot):
        try:
            sk = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
            sk.settimeout(0.5)
            if sk.connect_ex((self.target,prot))==0:
                return True
            else:
                return False
        except KeyboardInterrupt:
            print(RED+"[*] 用户自行退出扫描!!")
            exit()
        except Exception as e:
            print("portscan:",e)
            pass

        finally:
            sk.close()

    def getSocketBanner(self,port):
        try:
            sk = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
            sk.settimeout(0.5)
            sk.connect_ex((self.target,port))
            sk.send("Hello\r\n".encode("utf-8"))
            return sk.recv(2048).decode("utf-8")
        except Exception as e:
            pass
        finally:
            sk.close()
                


    

parser = OptionParser()
parser.add_option('-p','--prot',action='store',type="str",dest="port",help="ALL ports to be scanned default ALL port")
parser.add_option('-n','--num',action='store',type="int",dest="threadnum",help="Thread num default 100")
(option , args) = parser.parse_args()
if option.port == None and option.threadnum ==None and len(args) == 1:
    scanner = Scanner(args[0],65535)
    scanner.start()
elif option.port != None and option.threadnum ==None and len(args) == 1:
     port = option.port.split(',')
     scanner = Scanner(args[0],port)
     scanner.start()
elif option.port == None and option.threadnum !=None and len(args) == 1:
     port = option.port.split(',')
     scanner = Scanner(args[0],65535,option.threadnum)
     scanner.start()
elif option.port != None and option.threadnum !=None and len(args) == 1:
     port = option.port.split(',')
     scanner = Scanner(args[0],port,option.threadnum)
     scanner.start()
else:
    print(GRE+USAGE+GRE)
    parser.print_help()

