# author: Barry
# 2023年03月08日16时49分39秒
# email:2990670974@qq.com
import struct
from socket import *
import os
from multiprocessing import Pool


class server:
    def __init__(self, ip, port):
        self.ip = ip
        self.port = port
        self.path = os.getcwd()
        self.tcp_server_socket: socket = None
        self.client_socket: socket = None

    def tcp_init(self):
        tcp_server_socket = socket(AF_INET, SOCK_STREAM)
        # 重用对应地址和端口，不会造成占用地址
        tcp_server_socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        # 本地IP地址和端口
        tcp_server_socket.bind((self.ip, self.port))
        # 客户端监听
        tcp_server_socket.listen(128)

        self.tcp_server_socket = tcp_server_socket

    def send_train(self, data, flag_bytes=False):
        # flag_bytes用于区分gets、puts和其他操作
        # 因为发送和获取文件过程用的就是字节流
        if flag_bytes:
            data_len = len(data)
            # 发火车头，4个字节，包含的是文件名的长度
            self.client_socket.send(b'1' + struct.pack('I', data_len))
            # 车厢是文件内容
            self.client_socket.send(data)
        else:
            # 字符串
            data_bytes = data.encode("utf8")
            # 发火车头，4个字节，包含的是文件名的长度
            self.client_socket.send(struct.pack('I', len(data_bytes)))
            # 车厢是文件名
            self.client_socket.send(data_bytes)

    def recv_trian(self, new_socket):
        # 拿到火车头
        train_len = new_socket.recv(4)
        train_content_len = struct.unpack('I', train_len)[0]
        train_content: bytes = new_socket.recv(train_content_len)
        return train_content.decode("utf8")

    def do_ls(self):
        """
        当前路径下的信息传输给客户端
        :return:
        """
        ls_dict = {}
        for file in os.listdir(self.path):
            ls_size = os.stat(file).st_size
            ls_bool_type = os.path.isdir(file)
            if ls_bool_type:
                type = 'dir'
            else:
                type = 'file'
            ls_dict[file] = (ls_size,type)
            # data += '{:>5}{:>10}{:>20}'.format(str(type),file,str(os.stat(file).st_size))
        # print(ls_dict)
        self.send_train(str(ls_dict))

    def do_cd(self, command: str):
        """
        切换路径
        :return:
        """
        dir_name = command.split()[1]  # 拿到将要跳转到的目录
        for i in os.listdir(self.path):
            if i == dir_name and os.path.isdir(dir_name):
                self.client_socket.send(b'1')
                os.chdir(dir_name)
                self.path = os.getcwd()
                data = f'Now path is {self.path}'
                self.send_train(data + '\n')
                break
        else:
            self.client_socket.send(b'2')

    def do_pwd(self):
        """
        显示当前地址
        :return:
        """
        data = self.path + '\n'
        self.send_train(data)

    def do_rm(self, command: str):
        """
        删除空文件夹
        :return:
        """
        dir_name = command.split()[1]
        try:
            for i in os.listdir(self.path):
                if i == dir_name and os.path.isdir(dir_name):
                    self.client_socket.send(b'1')
                    os.rmdir(dir_name)
                    data = f'{dir_name}已删除' + '\n'
                    self.send_train(data)
                    break
            else:
                self.client_socket.send(b'2')
        except Exception as e:
            print(e)

    def do_gets(self, command: str):
        """
        往客户端发送文件
        :return:
        """
        # 发文件名
        file_name = command[5:]  # 认为文件名一定存在
        try:
            # 发文件内容
            file = open(file_name, 'rb')
            file_content = file.read()
            file.close()
            # self.send_train(file_name)
            self.send_train(file_content, True)
        except FileNotFoundError:
            self.client_socket.send(b'2')

    def do_puts(self, command: str):
        """
        接受客户端发来的文件
        :return:
        """
        # 认为文件名一定存在
        file_name = command[5:]  # 认为文件名一定存在
        # print(file_name)
        # 接文件名
        # file_name = self.recv_trian(self.client_socket)
        # 根据文件名创建文件
        no_file_flag = self.client_socket.recv(1)
        # print(no_file_flag)
        if no_file_flag == b'2':
            pass
        else:
            file = open(file_name, 'wb')
            train_len = self.client_socket.recv(4)
            # 接到了文件长度
            file_content_len = struct.unpack('I', train_len)[0]
            total = 0
            while total < file_content_len:
                file_content = self.client_socket.recv(file_content_len)
                total += len(file_content)
                file.write(file_content)
            file.close()

    def deal_command(self, client_socket):
        while True:
            command = self.recv_trian(client_socket)
            print(command)
            if command[:2] == 'ls':
                self.do_ls()
            elif command[:2] == 'cd':
                self.do_cd(command)
            elif command[:3] == 'pwd':
                self.do_pwd()
            elif command[:4] == 'gets':
                self.do_gets(command)
            elif command[:4] == 'puts':
                self.do_puts(command)
            elif command[:2] == 'rm':
                self.do_rm(command)
            else:
                print("wrong command")

    def loop_deal_command(self):
        po = Pool(3)
        while True:
            client_socket, client_addr = self.tcp_server_socket.accept()
            po.apply_async(self.deal_command, (client_socket,))
            self.client_socket = client_socket
            print(client_addr)
        po.close()
        po.join()
        # self.tcp_server_socket.close()


if __name__ == '__main__':
    s = server('192.168.3.25', 2000)
    s.tcp_init()
    s.loop_deal_command()
