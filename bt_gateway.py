#!/usr/bin/env python3
import os, sys, requests, bluetooth
from PyOBEX import headers, responses, server

# Monkey-patch sendall so PyOBEX can use it
bluetooth.BluetoothSocket.sendall = bluetooth.BluetoothSocket.send

HTTP_ENDPOINT = "http://127.0.0.1:5000/upload"
TMP_DIR       = "tmp"
os.makedirs(TMP_DIR, exist_ok=True)

class GatewayPushServer(server.PushServer):
    def __init__(self, address):
        super().__init__(address)

    def put(self, sock, request):
        name = ""
        body = bytearray()

        # read headers+body until final
        while True:
            for hdr in request.header_data:
                if isinstance(hdr, headers.Name):
                    name = hdr.decode().strip("\x00")
                    print(f"[Gateway] Receiving {name}")
                # for both Body and End_Of_Body, read only .data (the payload)
                elif isinstance(hdr, headers.Body) or isinstance(hdr, headers.End_Of_Body):
                    chunk = hdr.data
                    if isinstance(chunk, (bytes, bytearray)):
                        body.extend(chunk)

            if request.is_final():
                break

            # ask for next chunk
            self.send_response(sock, responses.Continue())
            request = self.request_handler.decode(sock)

        # send final OK
        self.send_response(sock, responses.Success())

        # save raw payload
        filename = os.path.basename(name) or "file"
        tmp_path = os.path.join(TMP_DIR, filename)
        with open(tmp_path, "wb") as f:
            f.write(body)
        print(f"[Gateway] Saved to {tmp_path}  ({len(body)} bytes)")

        # forward to HTTP
        with open(tmp_path, "rb") as f:
            r = requests.post(HTTP_ENDPOINT, files={"file": f})
        print(f"[Gateway] HTTP status: {r.status_code}")

        os.remove(tmp_path)


def run_gateway():
    local_addr = bluetooth.read_local_bdaddr()[0]
    port       = bluetooth.PORT_ANY

    while True:
        srv     = None
        bt_sock = None
        try:
            srv     = GatewayPushServer(local_addr)
            bt_sock = srv.start_service(port)
            channel = bt_sock.getsockname()[1]
            print(f"[Gateway] Listening OBEX Push on {local_addr}, channel {channel}")

            # block until session done
            srv.serve(bt_sock)
            srv.stop_service(bt_sock)

        except KeyboardInterrupt:
            print("\n[Gateway] Interrupted, shutting down…")
            if srv and bt_sock:
                srv.stop_service(bt_sock)
            break

        except Exception as e:
            print(f"[Gateway] ERROR: {e}\n[Gateway] Restarting…")
            if srv and bt_sock:
                try: srv.stop_service(bt_sock)
                except: pass

if __name__ == "__main__":
    run_gateway()
