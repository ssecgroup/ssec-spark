from http.server import BaseHTTPRequestHandler
import json

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        
        response = {
            'status': 'working',
            'path': self.path,
            'donation': '0x8242f0f25c5445F7822e80d3C9615e57586c6639'
        }
        
        self.wfile.write(json.dumps(response).encode())
        return