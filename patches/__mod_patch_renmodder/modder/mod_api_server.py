import socket
from threading import Thread
from struct import pack, unpack
from renpy.renmodder.config import VERBOSE_LOG
from renpy.renmodder.mod_api_proto import *


def log(text, end='\n'):
    print(f"[RENMODDER] API SERVER: {text}", end=end)

def vlog(text, end='\n'):
    if VERBOSE_LOG:
        log(text, end=end)

class APIServerHandler:
    mods = {}

    def __init__(self, conn, addr):
        self.conn = conn
        self.addr = addr
        self.handle()

    def handle(self):
        log("New request!")
        try:
            data = self.conn.recv(1024)
            req_type = unpack('B', data[:1])[0]

            if req_type == CONNECT_CHECK:
                self.conn.send(pack('B', CONNECT_CHECK))
            elif req_type == REGISTER:
                mod_name = data[1:].decode()
                mod_version = unpack('I', self.conn.recv(4))[0]
                mod_id = unpack('I', self.conn.recv(4))[0]
                
                self.register_mod(mod_name, mod_version, mod_id)
            elif req_type == GET_LOADED_MODS:
                self.send_loaded_mods()
            elif req_type == EVENT_SUBSCRIBE:
                self.handle_event_subscription()
            else:
                vlog(f"Unknown request type: {req_type}")
                self.conn.send(pack('B', ACTION_RESULT_FAIL))
        except Exception as e:
            vlog(f"Error in handler: {e}")
            self.conn.send(pack('B', ACTION_RESULT_FAIL))
        finally:
            self.conn.close()

    def register_mod(self, mod_name, mod_version, mod_id):
        token = f"{mod_name}-{mod_version}-{mod_id}"
        self.mods[token] = {
            "name": mod_name,
            "version": mod_version,
            "id": mod_id
        }
        vlog(f"Mod registered: {mod_name} (v{mod_version}), ID: {mod_id}")
        self.conn.send(token.encode())

    def send_loaded_mods(self):
        mod_list = list(self.mods.keys())
        self.conn.send(pack('I', len(mod_list)))
        for mod in mod_list:
            self.conn.send(mod.encode())

    def handle_event_subscription(self):
        token = self.conn.recv(1024).decode()
        event_type = unpack('B', self.conn.recv(1))[0]
        vlog(f"Subscribed to event type {event_type} for token {token}")
        self.conn.send(b"Subscription successful")

class APIServer:
    thread = None
    stop = False
    loaded = False

    def __init__(self, host='localhost', port=8000):
        self.host = host
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind((self.host, self.port))
        self.sock.listen(5)
        log("Server initialized!")

    def start(self):
        log("Server started!")
        self.thread = Thread(target=self._serve, daemon=True)
        self.thread.start()

    def _serve(self):
        self.loaded = True
        while not self.stop:
            try:
                conn, addr = self.sock.accept()
                log(f"Connection from {addr}")
                handler_thread = Thread(target=APIServerHandler, args=(conn, addr), daemon=True)
                handler_thread.start()
            except Exception as e:
                vlog(f"Error accepting connection: {e}")
        
    def stop_server(self):
        self.stop = True
        self.sock.close()
        log("Server stopped!")
    
    def shutdown(self):
        self.stop_server()
