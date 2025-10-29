# webserver.py
#
# Web server via sockets.
#
# When contacted by a client (web browser), send a web page
# displaying the states of selected GPIO pins.
#
# Must run as sudo to access port 80

import socket
import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)

led1 = 16
led2 = 20
led3 = 21
GPIO.setup(led1, GPIO.OUT)
GPIO.setup(led2, GPIO.OUT)
GPIO.setup(led3, GPIO.OUT)
pwm1 = GPIO.PWM(led1, 100)   
pwm2 = GPIO.PWM(led2, 100)   
pwm3 = GPIO.PWM(led3, 100)   


def parsePOSTdata(data):
    data_dict = {}
    idx = data.find('\r\n\r\n')+4
    data = data[idx:]
    data_pairs = data.split('&')
    for pair in data_pairs:
        key_val = pair.split('=')
        if len(key_val) == 2:
            data_dict[key_val[0]] = key_val[1]
    return data_dict

# Generate HTML for the web page:
def web_page():
    html = """
                <html>
        <head>
            <title>GPIO Pins</title>
        </head>
        <body>
            <h1>Pin States</h1>
            <h4>Brightness Level:</h4>
            <form action="/cgi-bin/range.py" method="POST">
                <input type="range" name="slider1" min="0" max="100" value="0" /><br>
                <form action="/cgi-bin/radio.py" method="POST">
                    <p>Select LED:</p>
                    <input type="radio" name="LED" value="1">LED 1<br>
                    <input type="radio" name="LED" value="2">LED 2<br>
                    <input type="radio" name="LED" value="3">LED 3<br>
                    <button name="submit" value="b1"> Change Brightness </button>
                </form>
        </body>
        </html>
        """
    print(html)
    return (bytes(html,'utf-8'))   # convert html string to UTF-8 bytes object



# Serve the web page to a client on connection:
def serve_web_page():
    pwm1.start(0) 
    pwm2.start(0) 
    pwm3.start(0) 
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # TCP-IP socket
    s.bind(('', 80))
    s.listen(3)  # up to 3 queued connections
    while True:
        print('Waiting for connection...')
        conn, (client_ip, client_port) = s.accept()     # blocking call
        print(f'Connection from {client_ip}')
        
        raw_data = conn.recv(1024)              # This is a 'bytes' object
        decoded_data = raw_data.decode('utf-8') # Now it's a 'str'
        data = parsePOSTdata(decoded_data)
        
        #data = parsePOSTdata(conn.recv(1024))
        led_select = data['LED']
        submit = data['submit']
        changeBright = data['slider1']
        
        if submit == "b1":
            if led_select == 1:
                pwm1.ChangeDutyCycle(changeBright)
            elif led_select == 2:
                pwm2.ChangeDutyCycle(changeBright)
            elif led_select == 3:
                pwm3.ChangeDutyCycle(changeBright)
        
        conn.send(b'HTTP/1.0 200 OK\n')         # status line 
        conn.send(b'Content-type: text/html\n') # header (content type)
        conn.send(b'Connection: close\r\n\r\n') # header (tell client to close at end)
        conn.sendall(web_page())                # body
        conn.close()

serve_web_page()
