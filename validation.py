import json
import socket
import re
from datetime import datetime
from dataclasses import dataclass, field

def is_free_port(port):
    try:
        sock = socket.socket()
        sock.bind(("", port))
        sock.close()
        return True
    except OSError:
        return False


def port_validation(port, isfree=False):
    try:
        if 1 <= int(port) <= 65535:
            if isfree:
                return is_free_port(port)
            return True
        return False
    except ValueError:
        return False

def ip_validation(ip):
    if ip == "":
        return False
    else:
        try:
            octets = ip.split(".", 4)
            if len(octets) == 4:
                for octet in octets:
                    octet = int(octet)
                    if 0 <= octet <= 255:
                        pass
                    else:
                        return False
            else:
                return False
        except ValueError:
            return False
        return True