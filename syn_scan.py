import os
import fcntl
import socket
import struct
import argparse
from scapy.all import *
from time import sleep
from threading import Thread
from queue import Queue

parser=argparse.ArgumentParser(description="单端口多IP无状态SYN扫描器\t——By Moofeng")
parser.add_argument('-t', '--threads', dest='threads', default=os.cpu_count()*5, type=int, help='发包线程数')
parser.add_argument('-f', '--file_name', dest='file_name', default='ip.txt', type=str, help='待扫描ip列表')
parser.add_argument('-p', '--port', dest='port', required=True, type=int, help='指定扫描端口')
parser.add_argument('-i', '--interface', dest='interface', required=True, type=str, help='指定网卡')
args=parser.parse_args()


INTERFACE = args.interface
PORT = args.port
THREAD_NUM = args.threads
ip_queue = Queue()
ip_list = list()
def load_ips():
    with open(args.file_name) as f:
        for line in f:
            ip = line.strip()
            ip_list.append(ip)
            ip_queue.put(ip)

# 获取指定网卡下本机ip
def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    return socket.inet_ntoa(fcntl.ioctl(
        s.fileno(),
        0x8915,  # SIOCGIFADDR
        struct.pack('256s', bytes(INTERFACE[:15].encode('utf-8')))
        )[20:24])

USER_IP = get_ip()

def send_syn():
    while not ip_queue.empty():
        ip = ip_queue.get()
        print(ip)
        send(IP(dst=ip)/TCP(dport=PORT, sport=RandShort(), flags=2), verbose=False)

# 回调函数
def prn(pkt):
    flag = pkt.getlayer(TCP).flags
    src_ip = pkt.getlayer(IP).src
    if src_ip not in ip_list:
        return
    if flag == "SA":
        print(pkt.sprintf("%IP.src%:%IP.sport%  is open!!!"))
    else:
        print(pkt.sprintf("%IP.src%:%IP.sport%  is closed.\tflag: {}".format(flag)))

# tcpdump语法过滤数据包
def sniffer():
    sniff(iface=INTERFACE, filter='tcp and dst {} and src port {}'.format(USER_IP, PORT), prn=prn)

if __name__ == "__main__":
    load_ips()
    sniffer_thread = Thread(target=sniffer)
    sniffer_thread.start()
    threads = [Thread(target=send_syn) for _ in range(THREAD_NUM)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    # 延时3S结束，防止遗漏
    sleep(3)
    os._exit(0)
    
