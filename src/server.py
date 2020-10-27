from http.server import HTTPServer, SimpleHTTPRequestHandler
import logging
import time
import threading
import os
import json
import paramiko

handle_map = {}

class BaseActionHandler():

    def __init__(self):
        pass

    def handle(self, path, body):
        logging.debug("Handle {}".format(path))
        logging.debug("Handled {}".format(path))


class VcaActionHandler(BaseActionHandler):

    def __init__(self, vca_host, vca_model, vca_unit, vca_action):
        self.vca_host = vca_host
        self.vca_model = vca_model
        self.vca_unit = vca_unit
        self.vca_action = vca_action

    def handle(self, path, body):
        logging.debug("Handle {}".format(path))
        commmand = "juju -m {model} run-action --wait {unit}"
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(host, port, username, password)
        stdin, stdout, stderr = ssh.exec_command(command)
        lines = stdout.readlines()
        logging.debug(lines)
        logging.debug("Handled {}".format(path))

class OsmAlertHandler(SimpleHTTPRequestHandler):
    def log_message(self, format, *args):
        logging.info("%s %s\n" %
                         (self.address_string(),
                          format%args))

    def do_POST(self):
        logging.debug("Handling {} {}".format(self.address_string(), self.requestline))
        try:
            content_length = int(self.headers['Content-Length'])
            body = self.rfile.read(content_length)
            logging.debug("Body {}".format(body))
            try:
                handler = handle_map[self.path]
                thread = threading.Thread(target=handler.handle, args=(self.path, body))
                thread.start()
                self.send_response(200)
                self.end_headers()
                self.wfile.write(b'OK')
            except KeyError as ke:
                self.send_response(404)
                self.end_headers()
                self.wfile.write(b'Not found')
        except BaseException as e:
            logging.error(e)
            self.send_response(500)
            self.end_headers()
            self.wfile.write(b'Internal server error')

    def do_GET(self):
        logging.debug("Handling {} {}".format(self.address_string(), self.requestline))
        try:
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b'OK')
        except BaseException as e:
            logging.error(e)
            self.send_response(500)
            self.end_headers()
            self.wfile.write(b'Internal server error')


def run(server_class=HTTPServer, handler_class=OsmAlertHandler):
    server_address = ("0.0.0.0", 8080)
    httpd = server_class(server_address, handler_class)
    print("Launching server...")
    httpd.serve_forever()

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s [%(levelname)s] [%(threadName)s] %(message)s",
        handlers=[
            logging.StreamHandler()
        ]
    )
    if os.path.isfile('/etc/oah-map.json'):
        with open('/etc/oah-map.json', 'r') as f:
            data = json.load(f)
        for k in data:
            clazz = globals()[data[k]['handler']]
            if 'params' in data[k]:
                params = data[k]['params']
                handler_instance = clazz(**params)
            else:
                handler_instance = clazz()
            handle_map[k] = handler_instance
    logging.info(handle_map)
    run()
