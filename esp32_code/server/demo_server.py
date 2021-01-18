import machine
import math
import time
import re
import socket
import uasyncio
import network
import hashlib
import binascii
import uselect

from machine import Pin
red = Pin(23, Pin.OUT)
blue = Pin(5, Pin.OUT)
green = Pin(0, Pin.OUT)
fpga_halt = Pin(18, Pin.OUT)
fpga_halt.off()

#Custom:
import hdc1080

# TODO:
# Message Fragmentation
# Binary data 
# Disconnect event
# Error state recovery
# Multiple clients


def get_mime(ext):
    # Set mime type appropriately
    if(ext == 'html'):
        return 'text/html'
    elif(ext == 'acc'):
        return 'audio/acc'
    elif(ext == 'abw'):
        return 'application/x-abiword'
    elif(ext == 'arc'):
        return 'application/x-freearc'
    elif(ext == 'avi'):
        return 'video/x-msvideo'
    elif(ext == 'azw'):
        return 'application/vnd.amazon.ebook'
    elif(ext == 'bin'):
        return 'application/octet-stream'
    elif(ext == 'bmp'):
        return 'image/bmp'
    elif(ext == 'bz'):
        return 'application/x-bzip'
    elif(ext == 'bz2'):
        return 'application/x-bzip2'
    elif(ext == 'csh'):
        return 'application/x-csh'
    elif(ext == 'css'):
        return 'text/css'
    elif(ext == 'csv'):
        return 'text/csv'
    elif(ext == 'doc'):
        return 'application/msword'
    elif(ext == 'docx'):
        return 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
    elif(ext == 'eot'):
        return 'application/vnd.ms-fontobject'
    elif(ext == 'epub'):
        return 'application/epub+zip'
    elif(ext == 'gz'):
        return 'application/gzip'
    elif(ext == 'gif'):
        return 'image/gif'
    elif(ext == 'htm'):
        return 'text/html'
    elif(ext == 'ico'):
        return 'image/vnd.microsoft.icon'
    elif(ext == 'ics'):
        return 'text/calendar'
    elif(ext == 'jar'):
        return 'application/java-archive'
    elif(ext == 'jpeg'):
        return 'image/jpeg'
    elif(ext == 'jpg'):
        return 'image/jpeg'
    elif(ext == 'js'):
        return 'text/javascript'
    elif(ext == 'json'):
        return 'application/json'
    elif(ext == 'jsonld'):
        return 'application/ld+json'
    elif(ext == 'mid'):
        return 'audio/midi'
    elif(ext == 'midi'):
        return 'audio/midi'
    elif(ext == 'mjs'):
        return 'text/javascript'
    elif(ext == 'mp3'):
        return 'audio/mpeg'
    elif(ext == 'mpeg'):
        return 'video/mpeg'
    elif(ext == 'mpkg'):
        return 'application/vnd.apple.installer+xml'
    elif(ext == 'odp'):
        return 'application/vnd.oasis.opendocument.presentation'
    elif(ext == 'ods'):
        return 'application/vnd.oasis.opendocument.spreadsheet'
    elif(ext == 'odt'):
        return 'application/vnd.oasis.opendocument.text'
    elif(ext == 'oga'):
        return 'audio/ogg'
    elif(ext == 'ogv'):
        return 'video/ogg'
    elif(ext == 'ogx'):
        return 'application/ogg'
    elif(ext == 'opus'):
        return 'audio/opus'
    elif(ext == 'otf'):
        return 'font/otf'
    elif(ext == 'png'):
        return 'image/png'
    elif(ext == 'pdf'):
        return 'application/pdf'
    elif(ext == 'php'):
        return 'application/x-httpd-php'
    elif(ext == 'ppt'):
        return 'application/vnd.ms-powerpoint'
    elif(ext == 'pptx'):
        return 'application/vnd.openxmlformats-officedocument.presentationml.presentation'
    elif(ext == 'rar'):
        return 'application/vnd.rar'
    elif(ext == 'rtf'):
        return 'application/rtf'
    elif(ext == 'sh'):
        return 'application/x-sh'
    elif(ext == 'svg'):
        return 'image/svg+xml'
    elif(ext == 'swf'):
        return 'application/x-shockwave-flash'
    elif(ext == 'tar'):
        return 'application/x-tar'
    elif(ext == 'tif'):
        return 'image/tiff'
    elif(ext == 'tiff'):
        return 'image/tiff'
    elif(ext == 'ts'):
        return 'video/mp2t'
    elif(ext == 'ttf'):
        return 'font/ttf'
    elif(ext == 'txt'):
        return 'text/plain'
    elif(ext == 'vsd'):
        return 'application/vnd.visio'
    elif(ext == 'wav'):
        return 'audio/wav'
    elif(ext == 'weba'):
        return 'audio/webm'
    elif(ext == 'webm'):
        return 'audio/webm'
    elif(ext == 'webp'):
        return 'image/webp'
    elif(ext == 'woff'):
        return 'font/woff'
    elif(ext == 'woff2'):
        return 'font/woff2'
    elif(ext == 'xhtml'):
        return 'application/xhtml+xml'
    elif(ext == 'xls'):
        return 'application/vnd.ms-excel'
    elif(ext == 'xlsx'):
        return 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    elif(ext == 'xml'):
        return 'text/xml'
    elif(ext == 'xul'):
        return 'application/vnd.mozilla.xul+xml'
    elif(ext == 'zip'):
        return 'application/zip'
    elif(ext == '3gp'):
        return 'video/3gpp'
    elif(ext == '3g2'):
        return 'video/3gpp2'
    elif(ext == '7z'):
        return 'application/x-7z-compressed'
    else:
        return 'text'

def decode_client_message(client_message, conn):
    client_message = conn.recv(1024)
    client_fin = (client_message[0] & b'\x80'[0]) >> 7
    client_op = client_message[0] & b'\x0F'[0]
    client_mask = (client_message[1] & b'\x80'[0]) >> 7
    client_len = client_message[1] & b'\x7F'[0]
    if(client_len > 125):
        if(client_len > 126):
            client_len = int.from_bytes(client_message[2:10], "big")
            client_mask_key = client_message[10:14]
            client_data = client_message[14:14+client_len]
        else:
            client_len = int.from_bytes(client_message[2:4], "big")
            client_mask_key = client_message[4:8]
            client_data = client_message[8:8+client_len]
    else:
        client_mask_key = client_message[2:6]
        client_data = client_message[6:6+client_len]

    client_data_decoded = []
    for i in range(client_len):
        client_data_decoded.append(client_data[i] ^ client_mask_key[i % 4])
    
    client_data_decoded = bytearray(client_data_decoded)
    try:
        client_data_decoded = client_data_decoded.decode('utf-8')
    except UnicodeError:
        return -1

    # print('Client message: %s' % client_message)
    # print('Client message length: %s' % len(client_message))
    # print('Client fin: %s' % client_fin)
    # print('Client opcode: %s' % client_op)
    # print('Client mask bit: %s' % client_mask)
    # print('Client data length: %s' % client_len)
    # print('Client mask key: %s' % client_mask_key)
    # print('Client data: %s\n' % client_data_decoded)

    return client_data_decoded

def encode_server_message(message):
    message = str(message)
    payload_len = len(message)

    if(payload_len > 125):
        raise OSError('Extended length (>125) not supported (yet)')

    encoded_message = []
    encoded_message.append(129)
    encoded_message.append(payload_len & 127)
    for b in bytes(message, 'utf-8'):
        encoded_message.append(b)
    return bytearray(encoded_message)

async def web_server():
    file_pat = re.compile('GET\\s+/(\\S*)\\s+')
    file_ext = re.compile('^\\w+.([a-zA-Z]+)$')
    conn_pat = re.compile('Connection:\\s+(\\S*)')
    websocket_key_pat = re.compile('Sec-WebSocket-Key:\\s+(\\S*)')
    origin_pat = re.compile('Origin:\\s+(\\S*)')
    ws_connected = False
    conn = None
    ws_message = bytearray(b'\x81\x01\x40')

    wlan = network.WLAN(network.STA_IF)
    ip_addr = wlan.ifconfig()[0]

    addr = socket.getaddrinfo(ip_addr, 80)[0][-1]

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    #s.setblocking(False)
    s.bind(addr)
    s.listen(5)

    print('listening on', addr)
    while True:
        if ws_connected == False:
            conn, addr = s.accept()
            print('client connected from', str(addr))
            request = conn.recv(1024)
            request = request.decode('utf-8')
            print('Content = \n%s' % request)
            conn_type = conn_pat.search(request).group(1)
            print('Connection Type: %s' % conn_type)

            if(conn_type == 'Upgrade'):
                websocket_key = websocket_key_pat.search(request).group(1)
                print('WebSocket Key: %s' % websocket_key)
                origin = origin_pat.search(request).group(1)
                print('Origin: %s' % origin)
                if(origin == 'http://' + ip_addr):
                    sec_websocket_acc = websocket_key + '258EAFA5-E914-47DA-95CA-C5AB0DC85B11'
                    sec_websocket_acc = hashlib.sha1(sec_websocket_acc).digest()
                    sec_websocket_acc = binascii.b2a_base64(sec_websocket_acc).decode('utf-8')
                    sec_websocket_acc = 'Sec-WebSocket-Accept: ' + sec_websocket_acc + '\n'
                    conn.send('HTTP/1.1 101 Switching Protocols\n')
                    conn.send('Upgrade: websocket\n')
                    conn.send('Connection: Upgrade\n')
                    conn.send(sec_websocket_acc)
                    ws_connected = True
            else:
                file_req = file_pat.search(request).group(1)
                if(file_req == ''):
                    print('Client requested root\n')
                    response = open('demo_server.html', 'rb').read()
                    ext = 'html'
                else:
                    print('client requested: %s' % file_req)
                    ext = file_ext.search(file_req).group(1)
                    try:
                        response = open(file_req, 'rb').read()
                    except OSError:
                        response = open('page_not_found.html', 'rb').read()
                        ext = 'html'


                conn.send('HTTP/1.1 200 OK\n')
                c_type = 'Content-Type: ' + get_mime(ext) + '\n'
                conn.send(c_type)
                conn.send('Connection: close\n\n')
                conn.sendall(response)
                conn.close()


        if ws_connected == True:
            # Check for data from client
            poller = uselect.poll()
            poller.register(conn, uselect.POLLIN)
            client_message = poller.poll(1)
            if client_message:
                client_message_decoded = decode_client_message(client_message, conn)
                if(client_message_decoded == -1):
                    # Close the connection
                    ws_connected = False
                    print('Error decoding client message, connection closed')
                print('Got "%s" from client.\n' % client_message_decoded)

                # Change LEDs
                if(client_message_decoded == "#RED"):
                    red.on()
                    green.off()
                    blue.off()
                if(client_message_decoded == "#GREEN"):
                    red.off()
                    green.on()
                    blue.off()
                if(client_message_decoded == "#BLUE"):
                    red.off()
                    green.off()
                    blue.on()
                if(client_message_decoded == "#FPGA_HALT"):
                    if(fpga_halt.value() == 1):
                        fpga_halt.value(0)
                    else:
                        fpga_halt.value(1)


            # Send data to client
            ws_message = encode_server_message('Temp: ' + str(hdc1080.read()[0]) + '\n Humidity: ' + str(hdc1080.read()[1]))
            try:
                conn.sendall(ws_message)
            except OSError:
                ws_connected = False
                print('Client disconnected: broken socket')


        await uasyncio.sleep_ms(10)



uasyncio.run(web_server())