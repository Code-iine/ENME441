# webserver.py
#
# Web server via sockets.
#
# When contacted by a client (web browser), send a web page
# displaying the states of selected GPIO pins.
#
# Must run as sudo to access port 80

#Q2 of Lab 7

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
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>LED Brightness Control</title>
    <style>
        /* Basic styles for a clean, modern look */
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            display: grid;
            place-items: center;
            min-height: 90vh;
            background-color: #f4f7f6;
            color: #333;
            margin: 0;
            padding: 1rem;
        }}
        .container {{
            background: #ffffff;
            padding: 2rem 2.5rem;
            border-radius: 12px;
            box-shadow: 0 8px 24px rgba(0, 0, 0, 0.05);
            width: 100%;
            max-width: 400px;
            box-sizing: border-box;
        }}
        h1 {{
            text-align: center;
            color: #222;
            margin-top: 0;
            margin-bottom: 2rem;
            font-size: 1.75rem;
        }}
        .slider-group {{
            margin-bottom: 1.5rem;
        }}
        .slider-group:last-child {{
            margin-bottom: 0.5rem;
        }}
        .slider-group label {{
            display: block;
            margin-bottom: 0.75rem;
            font-weight: 600;
            font-size: 1rem;
            color: #444;
        }}
        /* Style for the current value display */
        .value-display {{
            font-weight: 700;
            color: #007bff;
            background-color: #e6f2ff;
            padding: 0.15rem 0.5rem;
            border-radius: 6px;
            font-size: 0.95rem;
            display: inline-block;
            min-width: 2.5em; /* Ensures space for 3 digits */
            text-align: center;
        }}
        /* Styling the range slider */
        input[type="range"] {{
            width: 100%;
            cursor: pointer;
            margin-top: 0.25rem;
            -webkit-appearance: none;
            appearance: none;
            height: 8px;
            background: #dee2e6;
            border-radius: 5px;
            outline: none;
        }}
        input[type="range"]::-webkit-slider-thumb {{
            -webkit-appearance: none;
            appearance: none;
            width: 20px;
            height: 20px;
            background: #007bff;
            border-radius: 50%;
            border: 2px solid #fff;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            transition: background 0.2s ease;
        }}
        input[type="range"]::-moz-range-thumb {{
            width: 18px;
            height: 18px;
            background: #007bff;
            border-radius: 50%;
            border: 2px solid #fff;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            transition: background 0.2s ease;
        }}
        input[type="range"]:active::-webkit-slider-thumb {{
             background: #0056b3;
        }}
        input[type="range"]:active::-moz-range-thumb {{
             background: #0056b3;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>LED Brightness Control</h1>
        
        <!-- LED 1 Slider -->
        <div class="slider-group">
            <label for="led1">LED 1: <span id="led1-value" class="value-display">{ledin1}</span>%</label>
            <!-- 
              - We use the server-injected value for the initial 'value'
              - 'data-led' attribute stores the LED number for our JS
            -->
            <input type="range" id="led1" name="led1" min="0" max="100" value="{ledin1}" data-led="1">
        </div>
        
        <!-- LED 2 Slider -->
        <div class="slider-group">
            <label for="led2">LED 2: <span id="led2-value" class="value-display">{ledin2}</span>%</label>
            <input type="range" id="led2" name="led2" min="0" max="100" value="{ledin2}" data-led="2">
        </div>
        
        <!-- LED 3 Slider -->
        <div class="slider-group">
            <label for="led3">LED 3: <span id="led3-value" class="value-display">{ledin3}</span>%</label>
            <input type="range" id="led3" name="led3" min="0" max="100" value="{ledin3}" data-led="3">
        </div>
    </div>

    <script>
        // Wait for the HTML document to be fully loaded
        document.addEventListener('DOMContentLoaded', () => {{
            // Get all elements with the 'input[type="range"]' selector
            const sliders = document.querySelectorAll('input[type="range"]');
            
            // Add an 'input' event listener to each slider.
            // This fires every time the slider's value changes (i.e., as it's being dragged)
            sliders.forEach(slider => {{
                slider.addEventListener('input', handleSliderInput);
            }});
        }});

        function handleSliderInput(event) {{
            // 'event.target' is the specific slider element that was moved
            const slider = event.target;
            const newValue = slider.value;
            // Get the LED number we stored in the 'data-led' attribute
            const ledNumber = slider.dataset.led; 
            
            // Find the corresponding 'span' element to display the value
            const valueSpan = document.getElementById(`led${{ledNumber}}-value`);
            if (valueSpan) {{
                // Update its text to show the new value
                valueSpan.textContent = newValue;
            }}
            
            // Send this new data to the server in the background
            sendBrightnessUpdate(ledNumber, newValue);
        }}

        /**
         * Sends the brightness update to the server using the Fetch API.
         * This happens asynchronously and does not reload the page.
         */
        async function sendBrightnessUpdate(ledNumber, brightnessValue) {{
            // Format the data as 'application/x-www-form-urlencoded'
            // This matches what a standard HTML form sends, and what
            // your parsePOSTdata function expects.
            const bodyData = `LED=${{encodeURIComponent(ledNumber)}}&slider1=${{encodeURIComponent(brightnessValue)}}`;

            try {{
                // Send the POST request back to the same server URL that served this page
                const response = await fetch('', {{
                    method: 'POST',
                    body: bodyData,
                    headers: {{
                        'Content-Type': 'application/x-www-form-urlencoded'
                    }}
                }});
                
                // Optional: Check if the server responded successfully
                if (!response.ok) {{
                    console.error('Server responded with an error:', response.status);
                }}
                
                // You could also process a response from the server if it sends one, e.g.:
                // const result = await response.text();
                // console.log('Server response:', result);

            }} catch (error) {{
                // Log any errors that occur during the fetch operation
                console.error('Error sending update to server:', error);
            }}
        }}
    </script>
</body>
</html>
"""
    return (bytes(html,'utf-8'))   # convert html string to UTF-8 bytes object



# Serve the web page to a client on connection:
def serve_web_page():
    pwm1.start(0) 
    pwm2.start(0) 
    pwm3.start(0) 
    
    ledBright1 = 0
    ledBright2 = 0
    ledBright3 = 0
    
    conn = None # Initialize conn to None
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # TCP-IP socket
    s.bind(('', 80))
    s.listen(3)  # up to 3 queued connections
    
    while True:
        try:
            print('Waiting for connection...')
            conn, (client_ip, client_port) = s.accept()     # blocking call
            print(f'Connection from {client_ip}')
            
            raw_data = conn.recv(1024)              
            decoded_data = raw_data.decode('utf-8') 
            
            # Check if it's a POST request and handle data
            if decoded_data.startswith('POST'):
                    data = parsePOSTdata(decoded_data)
                    led_select = data.get('LED')
                    changeBright = data.get('slider1')
                    
                    # --- FIX ---
                    # We must check if BOTH keys were found and are not None.
                    # The error 'int() argument... not 'NoneType'' happens when
                    # 'changeBright' is None, meaning 'slider1' was missing
                    # from the POST request. This 'if' statement prevents
                    # the code from running if *either* value is missing.
                    if led_select and changeBright is not None:
                        try:
                            bright = int(changeBright)
                            if bright < 0: bright = 0
                            if bright > 100: bright = 100
                            
                            print(f"POST received: LED={led_select}, Brightness={bright}")

                            if led_select == "1":
                                pwm1.ChangeDutyCycle(bright)
                                ledBright1 = bright # Update the persistent value
                                print("Updated LED 1")
                            elif led_select == "2":
                                pwm2.ChangeDutyCycle(bright)
                                ledBright2 = bright # Update the persistent value
                                print("Updated LED 2")
                            elif led_select == "3":
                                pwm3.ChangeDutyCycle(bright)
                                ledBright3 = bright # Update the persistent value
                                print("Updated LED 3")
                        
                        except ValueError:
                            # Added quotes around 'changeBright' for clearer logging
                            print(f"Invalid brightness value received: '{changeBright}'")
                        except Exception as e:
                            print(f"Error processing POST data: {e}")
            
            # For ALL requests (GET or POST), send the web page
            conn.send(b'HTTP/1.0 200 OK\n')         # status line 
            conn.send(b'Content-type: text/html\n') # header (content type)
            conn.send(b'Connection: close\r\n\r\n') # header (tell client to close at end)
            conn.sendall(web_page(ledBright1,ledBright2,ledBright3))                # body
            conn.close()
            conn = None # Reset conn after closing

        except KeyboardInterrupt:
            print("\nShutting down server...")
            break # Exit the while loop
        except Exception as e:
            print(f"An error occurred: {e}")
            if conn:
                conn.close()
                conn = None # Reset conn after closing

    # Cleanup code runs after loop exits
    print("Stopping PWM and cleaning up GPIO...")
    pwm1.stop()
    pwm2.stop()
    pwm3.stop()
    GPIO.cleanup()
    s.close()
    print("Server shut down. GPIO cleaned up.")


serve_web_page()

