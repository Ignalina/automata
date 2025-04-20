import os
from http import HTTPStatus
from time import sleep

import redfish
import sys
from http.server import HTTPServer, SimpleHTTPRequestHandler
import socket
import threading
import time
from RangeHTTPServer import RangeRequestHandler, parse_byte_range
from pathlib import Path

import os
import re



def copy_byte_range(infile, outfile, start=None, stop=None, bufsize=16*1024):
    """Like shutil.copyfileobj, but only copy a range of the streams.

    Both start and stop are inclusive.
    """
    if start is not None: infile.seek(start)
    while 1:
        to_read = min(bufsize, stop + 1 - infile.tell() if stop else bufsize)
        buf = infile.read(to_read)
        if not buf:
            break
        outfile.write(buf)


BYTE_RANGE_RE = re.compile(r'bytes=(\d+)-(\d+)?$')
def parse_byte_range(byte_range):
    """Returns the two numbers in 'bytes=123-456' or throws ValueError.

    The last number or both numbers may be None.
    """
    if byte_range.strip() == '':
        return None, None

    m = BYTE_RANGE_RE.match(byte_range)
    if not m:
        raise ValueError('Invalid byte range %s' % byte_range)

    first, last = [x and int(x) for x in m.groups()]
    if last and last < first:
        raise ValueError('Invalid byte range %s' % byte_range)
    return first, last
class ImprovedRangeRequestHandler(RangeRequestHandler):
    def send_head_normal(self):
        path = self.translate_path(self.path)
        f = None
        ctype = 'application/octet-stream'
        try:
            f = open(path, 'rb')
        except OSError:
            self.send_error(HTTPStatus.NOT_FOUND, "File not found")
            return None

        try:
            fs = os.fstat(f.fileno())
            # Use browser cache if possible
            if ("If-Modified-Since" in self.headers
                    and "If-None-Match" not in self.headers):
                # compare If-Modified-Since and time of last file modification
                try:
                    ims = email.utils.parsedate_to_datetime(
                        self.headers["If-Modified-Since"])
                except (TypeError, IndexError, OverflowError, ValueError):
                    # ignore ill-formed values
                    pass
                else:
                    if ims.tzinfo is None:
                        # obsolete format with no timezone, cf.
                        # https://tools.ietf.org/html/rfc7231#section-7.1.1.1
                        ims = ims.replace(tzinfo=datetime.timezone.utc)
                    if ims.tzinfo is datetime.timezone.utc:
                        # compare to UTC datetime of last modification
                        last_modif = datetime.datetime.fromtimestamp(
                            fs.st_mtime, datetime.timezone.utc)
                        # remove microseconds, like in If-Modified-Since
                        last_modif = last_modif.replace(microsecond=0)

                        if last_modif <= ims:
                            self.send_response(HTTPStatus.NOT_MODIFIED)
                            self.end_headers()
                            f.close()
                            return None

            self.send_response(HTTPStatus.OK)
            self.send_header("Content-type", ctype)
            self.send_header("Content-Length", str(fs[6]))
            self.send_header("Last-Modified",
                self.date_time_string(fs.st_mtime))
            self.end_headers()
            return f
        except:
            f.close()
            raise

    def send_head(self):
        print("in new send_head")
        if 'Range' not in self.headers:
            self.range = None
            return self.send_head_normal()
        try:
            print("in range mode {self.headers}")

            self.range = parse_byte_range(self.headers['Range'])
        except ValueError as e:
            self.send_error(400, 'Invalid byte range')
            return None
        first, last = self.range

        # Mirroring SimpleHTTPServer.py here
        path = self.translate_path(self.path)
        f = None
        ctype = 'application/octet-stream'
        try:
            f = open(path, 'rb')
        except IOError:
            self.send_error(404, 'File not found')
            return None

        fs = os.fstat(f.fileno())
        file_len = fs[6]
        if first >= file_len:
            self.send_error(416, 'Requested Range Not Satisfiable')
            return None

        self.send_response(206)
        self.send_header('Content-type', ctype)

        if last is None or last >= file_len:
            last = file_len - 1
        response_length = last - first + 1

        self.send_header('Content-Range',
                         'bytes %s-%s/%s' % (first, last, file_len))
        self.send_header('Content-Length', str(response_length))
        self.send_header('Last-Modified', self.date_time_string(fs.st_mtime))
        self.end_headers()
        return f

    def end_headers(self):
        self.send_header('Accept-Ranges', 'bytes')
        return SimpleHTTPRequestHandler.end_headers(self)

    def copyfile(self, source, outputfile):
        if not self.range:
            return SimpleHTTPRequestHandler.copyfile(self, source, outputfile)

        # SimpleHTTPRequestHandler uses shutil.copyfileobj, which doesn't let
        # you stop the copying before the end of the file.
        start, stop = self.range  # set in send_head()
        copy_byte_range(source, outputfile, start, stop)


def start_server_in_thread(host_ip, port, file_to_serve):

    def start_server():
        global httpd
        ImprovedRangeRequestHandler.protocol_version = 'HTTP/1.1'
        p = Path(file_to_serve)
        ImprovedRangeRequestHandler.directory=Path(file_to_serve).parent.resolve()
        httpd = HTTPServer((f'{host_ip}', port), ImprovedRangeRequestHandler)
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
    elif response.status == 200:
        print("InsertMediaActionInfo was already populated.")
    else:
        print("Failed to populate InsertMediaActionInfo:", response.status, response.text)


    sleep(1)


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

    # Step 4: Power on  the System to Boot from Virtual Media
    reset_url = f"/redfish/v1/Systems/{system_id}/Actions/ComputerSystem.Reset"
    reset_payload = {
        "ResetType": "On"
    }

    # Send POST request to reboot the system
    response = redfish_client.post(reset_url, body=reset_payload)
    if response.status == 200:
        print("System rebooted successfully.")


    sleep(60*60*1000)

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



