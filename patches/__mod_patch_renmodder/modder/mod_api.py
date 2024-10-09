import sys
from socket import socket
from time import sleep
from struct import pack, unpack
from renpy.renmodder.mod_api_proto import *
from renpy.renmodder.config import *

def modapi_log(text, end='\n'):
    """Log function for Mod API"""
    print(f"[RENMODDER] Mod API: {text}", end=end)

def parse(*args, **kwargs):
    raise NotImplementedError("Renmodder Error: Mod API not loaded, but used function that uses other modules")

mod_api_loaded = False

def load_mod_api():
    global mod_api_loaded

    if mod_api_loaded:
        return

    mod_api_loaded = True
    modapi_log("Mod API loaded successfully.")

def run_renpy_code(code, linenumber):
    """Run Ren'Py code"""
    parse(code, linenumber=linenumber)

def register(mod_name, version, ID):
    """Register a new mod in RenModder Mod API system"""
    client = socket()

    try:
        modapi_log(f"Registering mod: {mod_name}, version: {version}, ID: {ID}")
        
        # Connect to server
        client.connect((BIND_TO, BIND_PORT))
        
        # CONNECT_CHECK
        client.send(pack('B', CONNECT_CHECK))
        response = unpack('B', client.recv(1))[0]
        if response != CONNECT_CHECK:
            modapi_log(f"Failed CONNECT_CHECK: {response}")
            return False
        
        # Registration process
        client.send(pack('B', REGISTER))
        client.send(mod_name.encode())
        client.send(pack('I', version))
        client.send(pack('I', ID))
        
        # Receive token
        token = client.recv(1024).decode()
        modapi_log(f"Received token: {token}")
        
        return client, token

    except Exception as e:
        modapi_log(f"Failed to register mod: {e}")
        return False

def subscribe(client, token, event_type):
    """Subscribe to a specific event type"""
    try:
        modapi_log(f"Subscribing to event type {event_type} with token {token}")
        
        # CONNECT_CHECK before action
        client.send(pack('B', CONNECT_CHECK))
        response = unpack('B', client.recv(1))[0]
        if response != CONNECT_CHECK:
            modapi_log(f"Failed CONNECT_CHECK before event subscription: {response}")
            return False
        
        # Send event subscription request
        client.send(pack('B', EVENT_SUBSCRIBE))
        client.send(token.encode())
        client.send(pack('B', event_type))
        
        # Receive confirmation
        result = client.recv(1024)
        modapi_log(f"Subscription result: {result}")
        
        return True

    except Exception as e:
        modapi_log(f"Failed to subscribe to event: {e}")
        return False

def get_loaded_mods(client, token):
    """Get the list of currently loaded mods"""
    try:
        
        # CONNECT_CHECK before action
        client.send(pack('B', CONNECT_CHECK))
        response = unpack('B', client.recv(1))[0]
        if response != CONNECT_CHECK:
            modapi_log(f"Failed CONNECT_CHECK before requesting loaded mods: {response}")
            return False
        
        # Send GET_LOADED_MODS request
        client.send(pack('B', GET_LOADED_MODS))
        client.send(token.encode())
        
        # Receive mod list
        mod_count = unpack('I', client.recv(4))[0]
        modapi_log(f"Number of loaded mods: {mod_count}")
        
        mods = []
        for _ in range(mod_count):
            mod_name = client.recv(1024).decode()
            mods.append(mod_name)
        
        return mods

    except Exception as e:
        modapi_log(f"Failed to get loaded mods: {e}")
        return []

def wait_for_mod(client, token, mod_name):
    """Wait for a specific mod to load by checking GET_LOADED_MODS in a loop"""
    while True:
        mods = get_loaded_mods(client, token)
        if mod_name in mods:
            return True
        
        sleep(0.3)

def send_action(client, token, action_type, data=None):
    """Send actions to RenModder Mod API server"""
    try:
        
        # CONNECT_CHECK before action
        client.send(pack('B', CONNECT_CHECK))
        response = unpack('B', client.recv(1))[0]
        if response != CONNECT_CHECK:
            modapi_log(f"Failed CONNECT_CHECK before action: {response}")
            return False
        
        # Send action with token
        client.send(pack('B', action_type))
        client.send(token.encode())
        
        if data:
            client.send(data)
        
        # Receive response
        result = client.recv(1024)
        
        return result

    except Exception as e:
        modapi_log(f"Failed to send action: {e}")
        return False
