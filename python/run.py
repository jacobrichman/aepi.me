import os

from http.server import BaseHTTPRequestHandler
import socketserver

import urllib.request
from urllib.parse import urlparse
from urllib.parse import parse_qs
import csv

port = int(os.getenv('PORT', '5000'))
spreadsheet_url = os.getenv('SPREADSHEET_URL')
aepi_password = os.getenv('AEPI_PASSWORD')
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

password = '''
<td> Enter Password </td>  
<input type = "password" id = "pswd" value = "">   
<button value = "Submit" id = "button" >Submit</button> 
'''
password_javascript = '''
<script>  
document.getElementById("button").onclick = function(){
var pw = document.getElementById("pswd").value;  
location.href = "/auth?pw=" + pw + "&dst=%s";
}
</script>  
'''
addiframe = '<iframe src="https://docs.google.com/forms/d/e/1FAIpQLSdi1ZPs-cvVq1Wiy1dfnCxoGT-8vTcDvP6jR9VQA6pdgmTNYg/viewform?embedded=true" style="position:fixed; top:0; left:0; bottom:0; right:0; width:100%; height:100%; border:none; margin:0; padding:0; overflow:hidden; z-index:999999;" frameborder="0" marginheight="0" marginwidth="0">Loading...</iframe>'

class Redirect(BaseHTTPRequestHandler):
    def find_destination(self, dst):
        response = urllib.request.urlopen(spreadsheet_url)
        lines = [l.decode('utf-8') for l in response.readlines()]
        cr = csv.reader(lines)
        for row in cr:
            if row[1].strip() == dst:
                return row
        return ["","",""]

    def do_GET(self):
        path = self.path.strip("/")
        parsedpath = urlparse(self.path)
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
        elif parsedpath.path == "/auth":
            parse_query = parse_qs(parsedpath.query)
            pw = parse_query.get("pw", "unknown")[0]
            dst = parse_query.get("dst", "unknown")[0]
            row = self.find_destination(dst)
            destination = row[2]
            if pw == aepi_password and destination != "":
                self.wfile.write(bytes('<script>location.href = "%s"</script>' % destination, "utf-8"))
                self.wfile.write(bytes("</html>", "utf-8"))
            else:
                self.wfile.write(bytes("<h1>URL could not be found :(</h1>", "utf-8"))
                self.wfile.write(bytes("</html>", "utf-8"))
        else:
            route = path.split('?')[0].strip()
            row = self.find_destination(route)
            private = ""
            destination = row[2]
            if len(row) >= 4:
                private = row[3]
            if private == "P" or destination == "":
                self.wfile.write(bytes(password, "utf-8"))
                self.wfile.write(bytes(password_javascript % route, "utf-8"))
                self.wfile.write(bytes("</html>", "utf-8"))
            else:
                self.wfile.write(bytes('<script>location.href = "%s"</script>' % destination, "utf-8"))
                self.wfile.write(bytes("</html>", "utf-8"))


httpd = socketserver.TCPServer(("", port), Redirect)
print("serving at port", port)
httpd.serve_forever()
