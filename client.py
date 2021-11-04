import socket
from datetime import datetime
from threading import Thread
import sys
import pickle
from validation import ip_validation, port_validation
from getpass import getpass
from time import sleep

IP_DEFAULT = "127.0.0.1"
PORT_DEFAULT = 9090
class Client:

    def __init__(self, server_ip, port, status = None):

        self.server_ip = server_ip
        self.port = port
        self.status = status
        self.server_connection()
        self.polling()
        self.log_file = 'client_log.txt'

    def server_connection(self):
        sock = socket.socket()
        sock.setblocking(1)
        try:
            sock.connect((self.server_ip, self.port))
        except ConnectionRefusedError:
            print(f"Не удалось присоединиться к серверу {self.server_ip, self.port}")
            sys.exit(0)
        self.sock = sock

    def polling(self):
        print("Используйте 'exit', чтобы разорвать соединение")
        while self.status != 'finish':
            if self.status:
                if self.status == "auth":
                    self.auth()
                elif self.status == "passwd":
                    self.sendPasswd()
                elif self.status == "success":
                    self.success()
                else:
                    msg = input(f"{self.username}> ")
                    if msg != "":
                        if msg == "exit":
                            self.status = "finish"

                            break
                        # Отправляем сообщение и имя клиента
                        sendM = pickle.dumps(["message", msg, self.username])
                        self.sock.send(sendM)

        self.sock.close()

    def sendPasswd(self):
        passwd = getpass(self.data)
        self.sock.send(pickle.dumps(["passwd", passwd]))
        # если убрать sleep ничего работать не будет!!!
        sleep(1.5)

    def auth(self):
        print("Введите имя:")
        self.username = input()
        self.sock.send(pickle.dumps(["auth", self.username]))
        # если убрать sleep ничего работать не будет!!!
        sleep(1.5)

    def write_log(self, log):
        with open(self.log_file, "a") as file:
            file.write(f"{datetime.now()}:\n{log}\n\n")

    def success(self):
        print(self.data)
        self.status = "ready"
        self.username = self.data.split(" ")[1]


    def recv(self):
        while True:
            try:
                self.data = self.sock.recv(1024)
                if not self.data:
                    sys.exit(0)
                status = pickle.loads(self.data)[0]
                self.status = status
                if self.status == "message":
                    print(f"\n{pickle.loads(self.data)[2]} -->", pickle.loads(self.data)[1])
                    # можно проверить с помощью двух присоединений к серверу

                else:
                    self.data = pickle.loads(self.data)[1]
            except OSError:
                break


def main():
    user_port = input("Введите порт (enter для значения по умолчанию):")
    if not port_validation(user_port):
        user_port = PORT_DEFAULT
        print(f"Установили порт {user_port} по умолчанию")

    user_ip = input("Введите ip сервера (enter для значения по умолчанию):")
    if not ip_validation(user_ip):
        user_ip = IP_DEFAULT
        print(f"Установили ip-адресс {user_ip} по умолчанию")

    Client(user_ip, int(user_port))


if __name__ == "__main__":
    main()