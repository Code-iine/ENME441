#
# ***************************************************
# ******** FINAL REVISED SERVER FUNCTION ********
# ***************************************************
#
# Serve the web page to a client on connection:
def serve_web_page():
    # Define s = None outside the try block
    # so 'finally' can always access it
    s = None 
    try:
        # --- GPIO & PWM Setup ---
        pwm1.start(0) 
        pwm2.start(0) 
        pwm3.start(0) 
        
        ledBright1 = 0
        ledBright2 = 0
        ledBright3 = 0

        # --- Socket Setup ---
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        print("Attempting to bind to port 80...")
        # This is the line that probably fails without sudo
        s.bind(('', 80)) 
        
        s.listen(3)
        print("Server started successfully on port 80. Waiting for connections...")
        
        # --- Main Server Loop ---
        while True:
            conn = None # Initialize conn for this loop's error handling
            try:
                conn, (client_ip, client_port) = s.accept()     # blocking call
                print(f'\nConnection from {client_ip}:{client_port}')
                
                raw_data = conn.recv(1024)
                if not raw_data:
                    print("No data received. Closing connection.")
                    conn.close()
                    continue

                decoded_data = raw_data.decode('utf-8') 
                
                if decoded_data.startswith('POST'):
                    print("Received POST request.")
                    data = parsePOSTdata(decoded_data)
                    print(f"Parsed POST data: {data}")
                    
                    if 'led1' in data:
                        bright = int(data['led1'])
                        pwm1.ChangeDutyCycle(bright)
                        ledBright1 = bright
                        print(f"Set LED 1 to {bright}%")
                    
                    elif 'led2' in data:
                        bright = int(data['led2'])
                        pwm2.ChangeDutyCycle(bright)
                        ledBright2 = bright
                        print(f"Set LED 2 to {bright}%")
                    
                    elif 'led3' in data:
                        bright = int(data['led3'])
                        pwm3.ChangeDutyCycle(bright)
                        ledBright3 = bright
                        print(f"Set LED 3 to {bright}%")
                
                elif decoded_data.startswith('GET'):
                    print("Received GET request.")
                
                # --- Send Response (for both GET and POST) ---
                conn.send(b'HTTP/1.0 200 OK\n')
                conn.send(b'Content-type: text/html\n')
                conn.send(b'Connection: close\r\n\r\n')
                conn.sendall(web_page(ledBright1, ledBright2, ledBright3))
                
                conn.close()
                print(f"Connection from {client_ip} closed successfully.")

            except KeyboardInterrupt:
                print("\nServer shutting down (Ctrl+C).")
                break # Break the 'while True' loop to exit
            
            except Exception as e:
                # This catches errors during a single connection
                print(f"\n--- A CONNECTION ERROR OCCURRED ---")
                import traceback
                traceback.print_exc()
                if conn:
                    conn.close()
                    print("Connection closed due to error.")

    except Exception as e:
        # This outer 'except' catches SETUP errors (e.g., port 80 permission)
        print("\n--- A FATAL SETUP ERROR OCCURRED ---")
        import traceback
        traceback.print_exc()
        print("This is often a 'Permission denied' error. Try running with 'sudo'.")
        
    finally:
        # This 'finally' block runs NO MATTER WHAT
        print("\nCleaning up resources...")
        pwm1.stop()
        pwm2.stop()
        pwm3.stop()
        GPIO.cleanup()
        if s: # If the socket 's' was successfully created
            s.close()
            print("Socket closed.")
        print("Shutdown complete.")

# --- End of function ---