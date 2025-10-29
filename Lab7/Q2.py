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
    
    # This option allows reusing the address, helpful for quick restarts
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    s.bind(('', 80))
    s.listen(3)  # up to 3 queued connections
    
    print("Server started on port 80. Waiting for connections...")
    
    while True:
        conn = None # Initialize conn to None to prevent UnboundLocalError
        try:
            conn, (client_ip, client_port) = s.accept()     # blocking call
            print(f'\nConnection from {client_ip}:{client_port}')
            
            raw_data = conn.recv(1024)
            if not raw_data:
                # This can happen if the browser just probes the connection
                print("No data received. Connection closed.")
                conn.close()
                continue

            decoded_data = raw_data.decode('utf-8') 
            
            # Check if this is a POST request (i.e., from our slider)
            if decoded_data.startswith('POST'):
                print("Received POST request.")
                data = parsePOSTdata(decoded_data)
                print(f"Parsed POST data: {data}")
                
                # --- Logic to handle individual slider data ---
                
                if 'led1' in data:
                    try:
                        bright = int(data['led1'])
                        pwm1.ChangeDutyCycle(bright)
                        ledBright1 = bright  # Update server-side state
                        print(f"Set LED 1 to {bright}%")
                    except ValueError:
                        print(f"Invalid data received for led1: {data['led1']}")
                
                elif 'led2' in data:
                    try:
                        bright = int(data['led2'])
                        pwm2.ChangeDutyCycle(bright)
                        ledBright2 = bright # Update server-side state
                        print(f"Set LED 2 to {bright}%")
                    except ValueError:
                        print(f"Invalid data received for led2: {data['led2']}")

                elif 'led3' in data:
                    try:
                        bright = int(data['led3'])
                        pwm3.ChangeDutyCycle(bright)
                        ledBright3 = bright # Update server-side state
                        print(f"Set LED 3 to {bright}%")
                    except ValueError:
                        print(f"Invalid data received for led3: {data['led3']}")
            
            elif decoded_data.startswith('GET'):
                print("Received GET request.")
            
            # --- This part runs for ALL requests (GET and POST) ---
            
            # Send the HTTP response headers
            conn.send(b'HTTP/1.0 200 OK\n')         # status line 
            conn.send(b'Content-type: text/html\n') # header (content type)
            conn.send(b'Connection: close\r\n\r\n') # header (tell client to close at end)
            
            # Send the actual web page, using the most recent brightness values
            conn.sendall(web_page(ledBright1, ledBright2, ledBright3))
            
            conn.close()
            print(f"Connection from {client_ip} closed successfully.")

        except KeyboardInterrupt:
            print("\nServer shutting down.")
            break
        except Exception as e:
            print(f"\n--- AN ERROR OCCURRED ---")
            # This import is here to print the full error stack
            import traceback
            traceback.print_exc() 
            print(f"Error details: {e}")
            print(f"---------------------------\n")
            if conn:
                conn.close()
                print("Connection closed due to error.")

    # Cleanup
    print("Stopping PWM and cleaning up GPIO...")
    pwm1.stop()
    pwm2.stop()
    pwm3.stop()
    GPIO.cleanup()
    s.close()
    print("Server shutdown complete.")