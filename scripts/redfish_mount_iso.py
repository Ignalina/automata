import _socket
import this

import redfish
import sys
import json
import http.server
import socketserver
import os
import socket
import threading
import time
import os
import ssl
from http.server import SimpleHTTPRequestHandler, HTTPServer
from urllib.parse import unquote

class SingleFileHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):

    def __init__(self, *args, **kwargs):
        self.file_to_serve = kwargs.pop('file_to_serve', None)  # Get the file from kwargs
        super().__init__(*args, **kwargs)


    def do_GET(self):
        # Serve the specific file when the root is requested
        print(self.path)
        return super().do_GET()


    def do_HEAD(self):
        # Serve the specific file when the root is requested
        self.path = unquote(self.path)

        # Check if the requested file exists
        filepath = self.translate_path(self.path)
        if os.path.exists(filepath):
            print(self.guess_type(self.path))
            # Send a successful response with content length header
            file_size = os.path.getsize(filepath)
            self.send_response(200)
            self.send_header('Content-type', self.guess_type(self.path))
            self.send_header('Content-Length', str(file_size))
            self.end_headers()
            super().do_HEAD()
        else:
            # Send 404 Not Found if file doesn't exist
            self.send_error(404, "File not found")
# Defining main function
def start_httpd_server(host_ip, port, file_to_serve):
    handler = lambda *args, **kwargs: SingleFileHTTPRequestHandler(*args, file_to_serve=file_to_serve, **kwargs)

    # Create and start the server on the host's local IP address
    with socketserver.TCPServer((host_ip, port), handler) as httpd:
        print(f"Serving {file_to_serve} on {host_ip}:{port}...")
        httpd.serve_forever()

def start_server_in_thread(host_ip, port, file_to_serve):
    server_thread = threading.Thread(target=start_httpd_server, args=(host_ip, port, file_to_serve,))
    server_thread.daemon = True  # Daemonize the thread to make it terminate with the main program
    server_thread.start()
    return server_thread

def main():


    # Configuration
    bmc_ip = sys.argv[1]
    login_account = sys.argv[2]
    login_password = sys.argv[3]
    file_to_serve = sys.argv[4]  # The file you want to expose

    if len(sys.argv)==5 :
        hostname = socket.gethostname()
        port=8000
    else:
        hostname, port = sys.argv[5].split(":")

    host_ip = socket.gethostbyname(hostname)
    start_server_in_thread(host_ip,port,file_to_serve)

    iso_url = f"http://{ host_ip }:{port}/{file_to_serve}"  # Replace this with the actual ISO URL
    manager_id = "1"
    system_id = "1"

    redfish_client = redfish.redfish_client(base_url=bmc_ip, username=login_account,password=login_password, default_prefix='/redfish/v1/')
    redfish_client.login(auth="session")

    # Test authentication
    auth_response = redfish_client.get('/redfish/v1')
    if auth_response.status == 200:
        print("Authentication successful.")
    else:
        print("Authentication failed:", auth_response.status_code, auth_response.text)
        exit(1)

# Step 2: Fill in the InsertMediaActionInfo for VirtualMedia1
# This will provide the information about the ISO image
#    insert_media_info_url = "/redfish/v1/Managers/1/VirtualMedia/VirtualMedia1/InsertMediaActionInfo"

    insert_media_info_url = "/redfish/v1/Managers/1/VirtualMedia/VirtualMedia1/Actions/VirtualMedia.InsertMedia"

    # Create the payload for the InsertMediaActionInfo resource
    insert_media_payload = {
    "Image": iso_url,  # URL of the ISO image
#    "MediaTypes": ["DVD"],  # The media type is DVD
    "Inserted": True,  # Indicates that the media should be inserted (mounted)
    "WriteProtected": True , # Specify whether the media should be write-protected
#    "TransferProtocol": "HTTPS",  # The protocol to use for transfer
    "TransferMethod": "Stream",  # Type of transfer: URL
#    "TransferProtocolType": "Https"  # Type of transfer: URL
}

# Send POST request to fill in the InsertMediaActionInfo resource
    response = redfish_client.post(insert_media_info_url, body=insert_media_payload)
    if response.status == 202:
        print("InsertMediaActionInfo populated successfully.")
    else:
        print("Failed to populate InsertMediaActionInfo:", response.status, response.text)
        exit(1)

# Step 3: Perform the InsertMedia action to mount the ISO
# URL for the InsertMedia action
    insert_media_action_url = "/redfish/v1/Managers/1/VirtualMedia/VirtualMedia1/Actions/VirtualMedia.InsertMedia"

# Send POST request to trigger the InsertMedia action
    response = redfish_client.post(insert_media_action_url)
    if response.status == 200:
        print("Virtual media (DVD ISO) mounted successfully.")
    else:
        print("Failed to mount virtual media:", response.status, response.text)
#        exit(1)
    # Step 3: Set Boot Order to Virtual Media
    boot_url = f"/redfish/v1/Systems/{system_id}"
    boot_payload = {
        "Boot": {
            "BootSourceOverrideEnabled": "Once",
            # Use "Once" to boot once, or "Continuous" for persistent boot from virtual media
            "BootSourceOverrideTarget": "Cd"  # "Cd" corresponds to booting from virtual media (ISO)
        }
    }

    # Send PATCH request to set the boot source
    response = redfish_client.patch(boot_url, body=boot_payload)
    if response.status == 200:
        print("Boot source set to Virtual Media.")
    else:
        print("Failed to set boot source:", response.status, response.text)
#        exit(1)

    # Step 4: Reboot the System to Boot from Virtual Media
    reset_url = f"/redfish/v1/Systems/{system_id}/Actions/ComputerSystem.Reset"
    reset_payload = {
        "ResetType": "ForceRestart"
    }

    # Send POST request to reboot the system
    response = redfish_client.post(reset_url, body=reset_payload)
    if response.status == 200:
        print("System rebooted successfully.")

    redfish_client.logout()

    print("Done")

    while True:
        time.sleep(3600)

# Using the special variable 
# __name__
if __name__=="__main__":
    main()



