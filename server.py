from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import urlparse
import os

class MyHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        print("Just received a GET request")
        self.send_response(200)
    	self.send_header('Content-Type', 'application/txt')
        self.end_headers()
	print self.path
	print urlparse.parse_qs(self.path)
        self.wfile.write('Hello world')

        return

    def log_request(self, code=None, size=None):
        print('Request')

    def log_message(self, format, *args):
        print('Message')

if __name__ == "__main__":
    try:
        server = HTTPServer(('', 8000), MyHandler)
        print('Started http server')
        server.serve_forever()
    except KeyboardInterrupt:
        print('^C received, shutting down server')
        server.socket.close()
