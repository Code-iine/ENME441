import socket

# Generate HTML for the web page (with corrected HTML structure):
def web_page():
    # Note: I've fixed your HTML form structure here as well.
    # The nested <form> and misplaced </body></html> tags were invalid.
    html = """<html>

<head>
    <title>GPIO Pins</title>
</head>

<body>
    <h1>Pin States</h1>
    
    <form action="/cgi-bin/some-script.py" method="POST">
        <h4>Brightness Level:</h4>
        <input type="range" name="slider1" min="0" max="1000" value="500" /><br>
        
        <p>Select LED:</p>
        <input type="radio" name="LED" value="1" checked> LED 1 <br>
        <input type="radio" name="LED" value="2"> LED 2 <br>
        <input type="radio" name="LED" value="3"> LED 3 <br>
        
        <button name="Change Brightness" value="b1"> Change Brightness </button>
    </form>
        
</body>
</html>
        """
    print(html) # This prints to your *server's terminal*, not the webpage
    return (bytes(html,'utf-8'))   # convert html string to UTF-8 bytes object
     
# Serve the web page to a client on connection:
def serve_web_page():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # TCP-IP socket
    
    # This prevents the "Address already in use" error on restart
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    s.bind(('', 80)) # Remember this needs sudo
    s.listen(3)  # up to 3 queued connections
    
    while True:
        print('Waiting for connection...')
        conn, (client_ip, client_port) = s.accept()     # blocking call
        print(f'Connection from {client_ip}')
        
        # === THE FIX IS HERE ===
        # All header lines MUST end with \r\n
        conn.send(b'HTTP/1.0 200 OK\r\n')         # status line 
        conn.send(b'Content-type: text/html\r\n') # header (content type)
        conn.send(b'Connection: close\r\n\r\n') # header (extra \r\n to end headers)
        
        conn.sendall(web_page())                # body
        conn.close()

serve_web_page()