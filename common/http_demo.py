import json
import time

import cherrypy
from typing import final
from http import HTTPMethod


class HTTPClient(object):
    exposed = True

    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.routes = {}
        self.conf = {
            '/': {
                'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
                'tools.sessions.on': True
            }
        }
        cherrypy.tree.mount(self, '/', self.conf)
        cherrypy.config.update({'server.socket_port': self.port})
        self.client = cherrypy.engine

    def start(self):
        self.client.start()

    def stop(self):
        self.client.stop()

    def add_route(self, path, method, handler):
        self.routes[path] = {
            'method': method,
            'func': handler,
        }

    def remove_route(self, path):
        del self.routes[path]

    def _parse_request(self, uri, method):
        path = '/' + '/'.join(uri)
        if path not in self.routes:
            return None, 'path not found'
        info = self.routes[path]
        if info['method'] != method:
            return None, 'method not match'

        return info['func'], ''

    @final
    def GET(self, *uri, **params):
        func, err = self._parse_request(uri, HTTPMethod.GET)
        if func is None:
            return print(err)

        return func(params)

    @final
    def POST(self, *uri, **params):
        func, err = self._parse_request(uri, HTTPMethod.POST)
        if func is None:
            return print(err)

        data = json.loads(cherrypy.request.body.read().decode('utf-8'))
        return func(data)

    @final
    def PUT(self, *uri, **params):
        func, err = self._parse_request(uri, HTTPMethod.PUT)
        if func is None:
            return print(err)

        data = json.loads(cherrypy.request.body.read().decode('utf-8'))
        return func(data)

    @final
    def DELETE(self, *uri, **params):
        func, err = self._parse_request(uri, HTTPMethod.DELETE)
        if func is None:
            return print(err)

        return func(params)


def test_logic(data):
    return str(int(data['a']) + int(data['b']))


if __name__ == '__main__':
    c = HTTPClient('localhost', 8080)
    c.add_route('/123/456', HTTPMethod.GET, test_logic)
    c.start()

    while True:
        time.sleep(5)
