import http.server
from custom_handler import custom_cgi_handler

PORT = 5555

Handler = custom_cgi_handler

server = http.server.ThreadingHTTPServer(("", PORT), Handler)

print("serving at port", PORT)
server.serve_forever()

