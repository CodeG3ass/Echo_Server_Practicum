import json
import pickle
import socket
import re
from datetime import datetime
from dataclasses import dataclass, field
from threading import Thread
import hashlib, uuid
import validation

@dataclass
class Server:
    server_port: int
    status: str
    clients: list = field(default_factory=list)
    all_Users: dict = field(init=False)
    file_users: str = field(init=False)
    log_file: str = field(init=False, default="server_log.txt")
    socket: socket = field(init=False, default=9090)
    user_name: str =field(init=False)


    def __post_init__(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.file_users = 'users.json'
        self.server_start()

    def registr_user(self, conn, addr):
        conn.send(pickle.dumps(
            ["auth", ""]))
        name = pickle.loads(conn.recv(1024))[1]
        conn.send(pickle.dumps(["passwd", "Введите свой пароль: "]))
        passwd = pickle.loads(conn.recv(1024))[1]
        conn.send(pickle.dumps(["success", f"Приветствую, {name}"]))
        self.writeJSON({addr[0]:{'name': name, 'password': passwd}})
        conn.send('Успешно!'.encode())

    def get_hashed_password(self, plain_text_password):
        salt = uuid.uuid4().hex
        hashed_password = hashlib.sha512(plain_text_password + salt).hexdigest()
        return hashed_password

    def check_password(self, plain_text_password, hashed_password):
        if self.get_hashed_password(plain_text_password) == self.get_hashed_password(hashed_password):
            return True
        else:
            return False

    def broadcast(self, msg, conn, address, username):
        username += "_" + str(address[1])
        for sock in self.clients:
            if sock != conn:
                data = pickle.dumps(["message", msg, username])
                sock.send(data)
                self.write_log(f"Отправка данных клиенту {sock.getsockname()}: {msg}")

    def autheristaion_user(self, conn, addr ):
        try:
            self.all_Users = self.readJSON()
        except json.decoder.JSONDecodeError:
            self.registr_user(conn, addr)
        user_flag = False
        for x, k in self.all_Users.items():
            if addr[0] in x:
                    if x == addr[0]:
                        print('True 2')
                        self.user_name = k['name']
                        password = k['password']
                        conn.send(pickle.dumps(["passwd", "Введите свой пароль: "]))
                        input_passwd = pickle.loads(conn.recv(1024))[1]
                        conn.send(pickle.dumps(["success", f"Здравствуйте, {self.user_name}"]))
                        conn.send(f"Здравствуйте, {self.user_name}".encode())
                        if password == input_passwd:
                            user_flag = True
                        else:
                            self.autheristaion_user(conn, addr)
        if not user_flag:
            self.registr_user(conn, addr)

    def write_log(self, log):
        with open(self.log_file, "a") as file:
            file.write(f"{datetime.now()}:\n{log}\n\n")

    def listen_user(self, conn, addr):
        self.autheristaion_user(conn, addr)
        while True:
            try:
                data = conn.recv(1024)
            except ConnectionResetError:
                conn.close()
                self.clients.remove(conn)
                self.write_log(f"Отключение клиента {addr}")
                break

            if data:
                status, data, username = pickle.loads(data)
                self.write_log(f"Прием данных от клиента '{self.user_name}_{addr[0]}")
                if status == "message":
                    self.broadcast(data, conn, addr, username)
            else:
                conn.close()
                self.clients.remove(conn)
                self.write_log(f"Отключение клиента {addr}")
                break

    def readJSON(self):
        with open(self.file_users, 'r') as f:
            users = json.load(f)
        print(type(users))
        return users

    def writeJSON(self, msg):
        with open(self.file_users, 'a', encoding='utf-8') as f:
            json.dump(msg, f, ensure_ascii=False, indent=4)


    def server_start(self):
        sock = socket.socket()
        sock.bind(('', self.server_port))
        sock.listen(5)
        self.sock = sock
        self.write_log(f"Сервер стартанул, слушаем порт {self.server_port}")
        while True:
            conn, addr = self.sock.accept()
            Thread(target=self.listen_user, args=(conn, addr)).start()
            self.write_log(f"Подключение клиента {addr}")
            self.clients.append(conn)

def main():
    server_port = 9090
    if not validation.port_validation(9090, True):
        if not validation.is_free_port(9090):
            print(f"Порт по умолчанию {9090} занят")
            free_port = False
            while not free_port:
                server_port += 1
                free_port = validation.is_free_port(server_port)
    try:
        Server(server_port, None)
    except KeyboardInterrupt:
        print(f"Остановка сервера")

main()
