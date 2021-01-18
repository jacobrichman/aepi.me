import os

from http.server import BaseHTTPRequestHandler
import socketserver

import requests
from contextlib import closing
import csv

port = int(os.getenv('PORT', '5000'))
spreadsheet_url = os.getenv('SPREADSHEET_URL')

main = '''
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">

<!-- Global site tag (gtag.js) - Google Analytics -->
<script async src="https://www.googletagmanager.com/gtag/js?id=UA-58617131-14"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());

  gtag('config', 'UA-58617131-14');
</script>
'''

addiframe = '<iframe src="https://docs.google.com/forms/d/e/1FAIpQLSdi1ZPs-cvVq1Wiy1dfnCxoGT-8vTcDvP6jR9VQA6pdgmTNYg/viewform?embedded=true" style="position:fixed; top:0; left:0; bottom:0; right:0; width:100%; height:100%; border:none; margin:0; padding:0; overflow:hidden; z-index:999999;" frameborder="0" marginheight="0" marginwidth="0">Loading...</iframe>'

class Redirect(BaseHTTPRequestHandler):
    def do_GET(self):
        path = self.path.strip("/")

        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(bytes("%s" % main, "utf-8"))

        if path == "":
            self.wfile.write(bytes("<h1>Welcome to aepi.me!</h1>", "utf-8"))
            self.wfile.write(bytes("</html>", "utf-8"))
        elif path == "add":
            self.wfile.write(bytes("%s" % addiframe, "utf-8"))
            self.wfile.write(bytes("</html>", "utf-8"))
        else:
            destination = ""
            with closing(requests.get(spreadsheet_url, stream=True)) as r:
                f = (line.decode('utf-8') for line in r.iter_lines())
                reader = csv.reader(f, delimiter=',', quotechar='"')
                for row in reader:
                    if row[1].strip() == path.strip():
                        destination = row[2]
        
            if destination != "":
                self.wfile.write(bytes('<script>window.location = "%s";</script>' % destination, "utf-8"))
                self.wfile.write(bytes("</html>", "utf-8"))
            else:
                self.wfile.write(bytes("<h1>URL could not be found :(</h1>", "utf-8"))
                self.wfile.write(bytes("</html>", "utf-8"))

httpd = socketserver.TCPServer(("", port), Redirect)
print("serving at port", port)
httpd.serve_forever()