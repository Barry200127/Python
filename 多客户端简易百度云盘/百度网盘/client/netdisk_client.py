# author: Barry
# 2023年03月08日16时50分00秒
# email:2990670974@qq.com

from socket import *
import struct


class client:
    def __init__(self, ip, port):
        self.ip = ip
        self.port = port
        self.client_socket = None
        # self.new_socket = None

    def tcp_connect(self):
        tcp_client_socket = socket(AF_INET, SOCK_STREAM)
        tcp_client_socket.connect((self.ip, self.port))
        self.client_socket = tcp_client_socket


    def send_train(self, data, flag_bytes=False):
        if flag_bytes:
            data_len = len(data)
            # 发火车头，4个字节，包含的是文件名的长度
            self.client_socket.send(b'1'+struct.pack('I', data_len))
            # 车厢是文件名
            self.client_socket.send(data)
        else:
            data_bytes = data.encode("utf8")
            # 发火车头，4个字节，包含的是文件名的长度
            self.client_socket.send(struct.pack('I', len(data_bytes)))
            # 车厢是文件名
            self.client_socket.send(data_bytes)

    def recv_trian(self):
        # 拿到火车头
        train_len = self.client_socket.recv(4)
        train_content_len = struct.unpack('I', train_len)[0]
        train_content: bytes = self.client_socket.recv(train_content_len)
        return train_content.decode("utf8")

    def do_gets(self, command):
        """
        向服务器获取文件
        :return:
        """
        file_name = command.split()[1]
        # 先获取验证码，如果是1就正常运行
        no_file_flag = self.client_socket.recv(1)
        print(no_file_flag)
        if no_file_flag == b'2':
            print("No such file in server")
        else:
            # 接文件名
            # file_name = self.recv_trian()
            # 根据文件名创建文件
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

    def do_puts(self, command):
        """
        往服务端发送文件
        :return:
        """
        # 发文件名
        file_name = command.split()[1]  # 认为文件名一定存在
        try:
            # self.send_train(file_name)
            # 发文件内容
            file = open(file_name, 'rb')
            file_content = file.read()
            self.send_train(file_content, True)
            file.close()
        except FileNotFoundError:
            self.client_socket.send(b'2')
            print('No such file')

    def do_cd(self):
        ls_or_not_dir = self.client_socket.recv(1)
        if ls_or_not_dir == b'1':
            data = self.recv_trian()
            print(data, end="")
        else:
            print('No such dir in server')

    def do_ls(self):
        str_ls_dict = self.recv_trian()
        ls_dict = eval(str_ls_dict)
        for key in ls_dict:
            print('{:>5}{:>25}{:>20}'.format(ls_dict[key][1], key, ls_dict[key][0]))

    def do_rm(self):
        have_or_not_dir = self.client_socket.recv(1)
        if have_or_not_dir == b'1':
            data = self.recv_trian()
            print(data, end="")
        else:
            print('No such dir in server')

    def do_pwd(self):
        data = self.recv_trian()
        print(data, end="")


    def user_operation(self):
        client_name = input('请输入用户名:')
        while True:
            command = input(client_name + ':')
            self.send_train(command, False)
            if command[:4] == 'gets':
                self.do_gets(command)
            elif command[:4] == 'puts':
                self.do_puts(command)
            elif command[:2] == 'cd':
                self.do_cd()
            elif command[:2] == 'ls':
                self.do_ls()
            elif command[:2] == 'rm':
                self.do_rm()
            elif command[:3] == 'pwd':
                self.do_pwd()
            # else:
            #     data = self.recv_trian()
            #     print(data, end="")
            #     pass
        self.client_socket.close()

if __name__ == '__main__':
    c = client("192.168.3.25", 2000)
    c.tcp_connect()
    c.user_operation()
