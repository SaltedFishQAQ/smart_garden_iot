import json
import time

import cherrypy
from typing import final
from http import HTTPMethod


def cors():
    cherrypy.response.headers['Access-Control-Allow-Origin'] = '*'
    cherrypy.response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
    cherrypy.response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'


class HTTPClient(object):
    exposed = True

    def __init__(self, host, port, conf=None):
        self.host = host
        self.port = port
        self.routes = {}
        if conf is None:
            self.conf = {
                '/': {
                    'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
                    'tools.sessions.on': True,
                    'tools.cors.on': True
                }
            }
        else:
            self.conf = conf
        cherrypy.tree.mount(self, '/', self.conf)
        cherrypy.tools.cors = cherrypy.Tool('before_handler', cors)
        cherrypy.config.update({
            'server.socket_host': self.host,
            'server.socket_port': self.port
        })
        self.client = cherrypy.engine

    def start(self):
        self.client.start()

    def stop(self):
        self.client.stop()

    def add_route(self, path, method, handler):
        if path not in self.routes:
            self.routes[path] = {}

        self.routes[path][method] = handler

    def remove_route(self, path, method=None):
        if path not in self.routes:
            return

        if method is None:
            del self.routes[path]
        else:
            del self.routes[path][method]

    def _parse_request(self, uri, method):
        path = '/' + '/'.join(uri)
        if path not in self.routes:
            return None, cherrypy.HTTPError(404, 'path not found')
        info = self.routes[path]
        if method not in info:
            return None, cherrypy.HTTPError(405, 'method not match')

        return info[method], ''

    @final
    @cherrypy.tools.json_out()
    def GET(self, *uri, **params):
        func, err = self._parse_request(uri, HTTPMethod.GET)
        if func is None:
            raise err

        return func(params)

    @final
    @cherrypy.tools.json_out()
    @cherrypy.tools.json_in()
    def POST(self, *uri, **params):
        func, err = self._parse_request(uri, HTTPMethod.POST)
        if func is None:
            raise err

        data = cherrypy.request.json
        return func(data)

    @final
    @cherrypy.tools.json_out()
    @cherrypy.tools.json_in()
    def PUT(self, *uri, **params):
        func, err = self._parse_request(uri, HTTPMethod.PUT)
        if func is None:
            raise err

        data = cherrypy.request.json
        return func(data)

    @final
    @cherrypy.tools.json_out()
    def DELETE(self, *uri, **params):
        func, err = self._parse_request(uri, HTTPMethod.DELETE)
        if func is None:
            raise err

        return func(params)

    @final
    def OPTIONS(self, *uri, **params):
        cherrypy.response.headers['Access-Control-Allow-Origin'] = 'http://localhost:8080'
        cherrypy.response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
        cherrypy.response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
        return ''
