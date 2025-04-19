
from time import sleep

import redfish
import sys
from http.server import HTTPServer
import socket
import threading
import time
from RangeHTTPServer import RangeRequestHandler
from pathlib import Path

def start_server_in_thread(host_ip, port, file_to_serve):
    def start_server():
        global httpd
        RangeRequestHandler.protocol_version = 'HTTP/1.1'
        p = Path(file_to_serve)
        RangeRequestHandler.directory=Path(file_to_serve).parent.resolve()
        httpd = HTTPServer((f'{host_ip}', port), RangeRequestHandler)
        httpd.serve_forever()

    server_thread = threading.Thread(target=start_server)
    server_thread.start()
    time.sleep(1.0)
    return httpd,server_thread

def start_server(file_to_serve,port):
     global httpd
     RangeRequestHandler.protocol_version = 'HTTP/1.1'
     p = Path(file_to_serve)
     RangeRequestHandler.directory=file_to_serve
     httpd = HTTPServer(('', port), RangeRequestHandler)
     httpd.serve_forever()


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
    httpd,server_thread=start_server_in_thread(host_ip,port,file_to_serve)


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
#    "Image": "http://10.1.1.13:8081/Rocky-9.5-x86_64-minimal.iso",  # URL of the ISO image
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


    sleep(1000)


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


    httpd.shutdown()
    server_thread.join()

    redfish_client.logout()

    print("Done")

    while True:
        time.sleep(3600)

# Using the special variable 
# __name__
if __name__=="__main__":
    main()



