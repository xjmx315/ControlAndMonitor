from http.server import BaseHTTPRequestHandler
from urllib import parse
import json

class GetHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed_path = parse.urlparse(self.path)
        message_parts = [
            'CLIENT VALUES:', 'client_address={} ({})'.format(self.client_address, self.address_string),
            'command={}'.format(self.command), 
            'path={}'.format(self.path), 
            'real path={}'.format(parsed_path.path), 
            'query={}'.format(parsed_path.query), 
            'request_version={}'.format(self.request_version), 
            '', 
            'SERVER VALUES: ', 
            'server_version={}'.format(self.server_version), 
            'sys_version={}'.format(self.sys_version), 
            'protocol_version'.format(self.protocol_version), 
            '', 
            'HEADERS RECEIVED: ', ]
        for name, value in sorted(self.headers.items()):
            message_parts.append('{}={}'.format(name, value.rstrip()))
        message_parts.append('')
        message = '\n'.join(message_parts)
        self.send_response(200)
        self.send_header('Content-Type', 'text/plain; charset=utf-8')
        self.end_headers()
        #self.wfile.write(message.encode('utf-8'))
        targetData = {"server_name": "Crawling3", "crawl_state": "working", "total_substances": 160, "processed_substances": 57, "percentage": "34.97", "start_time": "240809-160903", "end_time": "00:00"}
        data = json.dumps(targetData)
        self.wfile.write(data.encode())
        
        print(message)
        
def start_server():
    from http.server import HTTPServer
    server = HTTPServer(('localhost', 8080), GetHandler)
    print('Starting server, <Ctrl+C> to stop')
    server.serve_forever()
        
if __name__ == '__main__':
    start_server()