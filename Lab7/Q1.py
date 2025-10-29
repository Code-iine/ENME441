# webserver.py
#
# Web server via sockets.
#
# When contacted by a client (web browser), send a web page
# displaying the states of selected GPIO pins.
#
# Must run as sudo to access port 80

#Q1 of Lab 7

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
def web_page(ledin1, ledin2, ledin3):
    html = f"""
                <html>
        <head>
            <title>GPIO Pins</title>
        </head>
        <body>
            <h1>Pin States</h1>
            <form action="/cgi-bin/range.py" method="POST">
            <h4>Brightness Level:</h4>
                <input type="range" name="slider1" min="0" max="100" value="0" /><br>
                    <p>Select LED:</p>
                    <input type="radio" name="LED" value="1">LED 1 ({ledin1}%)<br>
                    <input type="radio" name="LED" value="2">LED 2 ({ledin2}%)<br>
                    <input type="radio" name="LED" value="3">LED 3 ({ledin3}%)<br>
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
    
    ledBright1 = 0
    ledBright2 = 0
    ledBright3 = 0

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # TCP-IP socket
    s.bind(('', 80))
    s.listen(3)  # up to 3 queued connections
    while True:
        print('Waiting for connection...')
        conn, (client_ip, client_port) = s.accept()     # blocking call
        print(f'Connection from {client_ip}')
        
        raw_data = conn.recv(1024)              
        decoded_data = raw_data.decode('utf-8') 
        data = parsePOSTdata(decoded_data)
        
        #data = parsePOSTdata(conn.recv(1024))
        
        
        if decoded_data.startswith('POST'): #post checker
                data = parsePOSTdata(decoded_data)
                led_select = data.get('LED')
                submit = data.get('submit')
                changeBright = data.get('slider1')
                bright = int(changeBright)
        
                if submit == "b1":
                    print("submitted")
                    if led_select == "1":
                        pwm1.ChangeDutyCycle(bright)
                        ledBright1 = bright
                        print("led1")
                    elif led_select == "2":
                        pwm2.ChangeDutyCycle(bright)
                        ledBright2 = bright
                    elif led_select == "3":
                        pwm3.ChangeDutyCycle(bright)
                        ledBright3 = bright
        
        conn.send(b'HTTP/1.0 200 OK\n')         # status line 
        conn.send(b'Content-type: text/html\n') # header (content type)
        conn.send(b'Connection: close\r\n\r\n') # header (tell client to close at end)
        conn.sendall(web_page(ledBright1,ledBright2,ledBright3))                # body
        conn.close()

serve_web_page()
