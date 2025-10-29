# webserver.py
#
# Web server via sockets.
#
# When contacted by a client (web browser), send a web page
# displaying the states of selected GPIO pins.
#
# Must run as sudo to access port 80

#Q1 of Lab 7 - REVISED

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
    # Find the start of the POST data (after the double newline)
    idx = data.find('\r\n\r\n')
    if idx == -1:
        return {} # No POST data found
        
    data = data[idx+4:] # Get only the body of the request
    
    # Check if data is not empty
    if not data:
        return {}
        
    data_pairs = data.split('&')
    for pair in data_pairs:
        key_val = pair.split('=')
        if len(key_val) == 2:
            # URL-decode common characters like %20 (space), etc.
            # This is a simple version; a full one is more complex
            key = key_val[0]
            value = key_val[1]
            data_dict[key] = value
    return data_dict

#
# ***************************************************
# ************* REVISED WEB PAGE FUNCTION ***********
# ***************************************************
#
# Generate HTML for the web page:
def web_page(ledin1, ledin2, ledin3):
    """
    Generates the HTML and JavaScript for the LED control page.
    This code is sent to the client's web browser.
    """
    html = f"""
<html>
<head>
    <title>RPi LED Control</title>
    <style>
        body {{ 
            font-family: Arial, sans-serif; 
            margin: 30px; 
            background-color: #f4f4f4;
        }}
        h1 {{ 
            color: #333; 
        }}
        .slider-container {{
            margin-bottom: 20px;
            display: flex;
            align-items: center;
            width: 500px;
        }}
        label {{
            font-size: 1.1em;
            width: 100px; /* Aligns labels */
        }}
        input[type="range"] {{
            width: 300px;
            margin-right: 15px;
            cursor: pointer;
        }}
        span {{
            font-weight: bold;
            font-size: 1.1em;
            color: #007BFF;
            min-width: 30px; /* Stops layout from jumping */
            text-align: right;
        }}
    </style>
</head>
<body>
    <h1>RPi LED Control (No Reload)</h1>

    <div class="slider-container">
        <label for="slider1">LED 1:</label>
        <input type="range" id="slider1" name="led1" min="0" max="100"
               value="{ledin1}" oninput="sendData(this)">
        <span id="value1">{ledin1}</span>%
    </div>

    <div class="slider-container">
        <label for="slider2">LED 2:</label>
        <input type="range" id="slider2" name="led2" min="0" max="100"
               value="{ledin2}" oninput="sendData(this)">
        <span id="value2">{ledin2}</span>%
    </div>

    <div class="slider-container">
        <label for="slider3">LED 3:</label>
        <input type="range" id="slider3" name="led3" min="0" max="100"
               value="{ledin3}" oninput="sendData(this)">
        <span id="value3">{ledin3}</span>%
    </div>

    <script>
    function sendData(slider) {{
        const name = slider.name;  // e.g., "led1"
        const value = slider.value; // e.g., "75"
        
        // 1. Update the brightness value display next to the slider
        // We find the <span> by its ID, e.g., 'value1' from 'led1'
        const displayId = 'value' + name.substring(3); 
        document.getElementById(displayId).textContent = value;

        // 2. Prepare the data to send (e.g., "led1=75")
        const bodyData = `${name}=${value}`;

        // 3. Send the POST request asynchronously using fetch()
        // This sends the data to the server without reloading the page.
        fetch('/', {{
            method: 'POST',
            headers: {{
                // This header tells the server it's form data
                'Content-Type': 'application/x-www-form-urlencoded',
            }},
            body: bodyData
        }})
        .then(response => {{
            // The server sends back the whole page, but we
            // don't need to do anything with it. The 'fetch'
            // call happens in the background.
            console.log('Request sent:', bodyData);
        }})
        .catch(error => {{
            // Log any errors to the browser console
            console.error('Error sending data:', error);
        }});
    }}
    </script>

</body>
</html>
"""
    return (bytes(html,'utf-8'))   # convert html string to UTF-8 bytes object


#
# ***************************************************
# ************* REVISED SERVER FUNCTION *************
# ***************************************************
#
# Serve the web page to a client on connection:
def serve_web_page():
    pwm1.start(0) 
    pwm2.start(0) 
    pwm3.start(0) 
    
    # These variables hold the last-known brightness levels
    ledBright1 = 0
    ledBright2 = 0
    ledBright3 = 0

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # TCP-IP socket
    s.bind(('', 80))
    s.listen(3)  # up to 3 queued connections
    
    print("Server started on port 80. Waiting for connections...")
    
    while True:
        try:
            conn, (client_ip, client_port) = s.accept()     # blocking call
            print(f'Connection from {client_ip}:{client_port}')
            
            raw_data = conn.recv(1024)              
            decoded_data = raw_data.decode('utf-8') 
            
            # Check if this is a POST request (i.e., from our slider)
            if decoded_data.startswith('POST'):
                data = parsePOSTdata(decoded_data)
                
                # --- NEW LOGIC to handle individual slider data ---
                # The 'data' dict will be {'led1': '50'} or {'led2': '30'}, etc.
                
                if 'led1' in data:
                    bright = int(data['led1'])
                    pwm1.ChangeDutyCycle(bright)
                    ledBright1 = bright  # Update server-side state
                    print(f"Set LED 1 to {bright}%")
                
                elif 'led2' in data:
                    bright = int(data['led2'])
                    pwm2.ChangeDutyCycle(bright)
                    ledBright2 = bright # Update server-side state
                    print(f"Set LED 2 to {bright}%")
                
                elif 'led3' in data:
                    bright = int(data['led3'])
                    pwm3.ChangeDutyCycle(bright)
                    ledBright3 = bright # Update server-side state
                    print(f"Set LED 3 to {bright}%")
            
            # --- This part runs for ALL requests (GET and POST) ---
            
            # Send the HTTP response headers
            conn.send(b'HTTP/1.0 200 OK\n')         # status line 
            conn.send(b'Content-type: text/html\n') # header (content type)
            conn.send(b'Connection: close\r\n\r\n') # header (tell client to close at end)
            
            # Send the actual web page, using the most recent brightness values
            # For a GET, this sends the current state.
            # For a POST, this is also sent, but the client's JS ignores it.
            conn.sendall(web_page(ledBright1, ledBright2, ledBright3))
            
            conn.close()
            print(f"Connection from {client_ip} closed.")

        except KeyboardInterrupt:
            print("\nServer shutting down.")
            break
        except Exception as e:
            print(f"An error occurred: {e}")
            if conn:
                conn.close()

    # Cleanup
    pwm1.stop()
    pwm2.stop()
    pwm3.stop()
    GPIO.cleanup()
    s.close()

# Start the server
serve_web_page()