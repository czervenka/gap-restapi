import logging
import webapp2

import stricttype
from stricttype.message import dumps
import exceptions as exc
import webob

CONTENT_TYPE = 'application/json; charset: utf-8'


class JsonRequestHandler(webapp2.RequestHandler):

    def get_request_data(self, method, **kwargs):
        data = self.request.body.strip()
        if data and not self.request.headers.get('Content-Type', '').startswith('application/json'):
                raise exc.InvalidRequestException("Content-type header must be application/json.")

        logging.debug('Request body: %r' % data)
        try:
            if data:
                data = loads(data)
            else:
                data = {}
        except Exception, exception:
            raise exc.InvalidRequestException("Request data is not valid json string.")
        logging.debug('request quargs: %r' % kwargs)
        data.update(dict([ (key, value) for key, value in kwargs.items() if value != '']))
        data.update(self.request.GET)
        try:
            data = method.in_type(**data)
        except stricttype.ValidationError, exception:
            raise exc.InvalidRequestException(exception.message, 400)
        return data

    def write_response_data(self, method, response):
        out_type = method.out_type
        if getattr(response, '_type', None) != out_type:
            if isinstance(response, stricttype.MessageInstance):
                raise ValueError('Invalid type for returned value. Expected %r but got %r.' % (response._type.__name__, out_type.__name__))
            if not hasattr(response, 'items'):
                raise ValueError('Return value should be a mapping but was %r.' % type(response).__name__)
            response = out_type(**response)
        self.response.headers['content-type'] = CONTENT_TYPE
        self.response.write(dumps(response))


    def handle_exception(self, exception, debug):
        from traceback import format_exc
        self.response.clear()
        if isinstance(exception, exc.ApiException):
            if debug:
                logging.exception(exception)
            code = exception.code
            message = exception.message
            description = exception.description
        else:
            logging.exception(exception)
            code = 500
            message = "Internal Server Error"
            description = None

        self.response.headers['content-type'] = CONTENT_TYPE
        self.response.set_status(code)
        if debug:
            traceback = format_exc()
        else:
            traceback = None
        self.response.write(dumps(ErrorResponse(
            code=code,
            message=message,
            description=description,
            traceback=traceback,
        )))
        return

    def _dispatch(self):
        """Dispatches the request.

        This will first check if there's a handler_method defined in the
        matched route, and if not it'll use the method correspondent to the
        request method (``get()``, ``post()`` etc).
        """
        request = self.request
        handler = request.route.handler_method
        if handler is None:
            handler_name = request.method
            handler_name = handler_name.lower().replace('-', '_')

            handler = getattr(self, handler_name, None)
        if handler is None or not handler.api_method:  # method must be registered as api method
            raise exc.NotFoundException("Not found")

        # The handler only receives *args if no named variables are set.
        args, kwargs = request.route_args, request.route_kwargs
        if args:
            raise exc.InternalServerError("JsonRequestHandler does not allow unnamed parameters.")
        try:
            return self.write_response_data(handler, handler(self.get_request_data(handler, **kwargs)))
        except Exception, e:
            return self.handle_exception(e, self.app.debug)

    def dispatch(self):

        try:
            return self._dispatch()
        except BaseException, exception:
            self.handle_exception(exception, self.app.debug)

class RoutedJsonRequestHandler(JsonRequestHandler):

    @staticmethod
    def _merge_routes(a, b):
        return "%s%s" % (a.replace('.*$', '').replace('^', ''), b)

    @property
    def routes(self):
        path_prefix = self.request.route.template
        if not hasattr(self, '_routes'):
            routes = []
            for fname, f in [ (fname, f) for fname, f in type(self).__dict__.items() if getattr(f, 'api_method', False) ]:
                path = self._merge_routes(path_prefix, f.path)
                routes.append(RouteEx(path, f, methods=f.http_method))
            self._routes = routes
        return self._routes

    def find_matching_route(self):
        match = None
        for route in self.routes:
            try:
                match = route.match(self.request)
            except webob.exc.HTTPMethodNotAllowed, exception:
                continue
                # raise exc.MethodNotAllowedException("Method %s not allowed for %s." % (self.request.method, self.request.path))
            if match:
                break
        return match


    def _dispatch(self):
        match = self.find_matching_route()
        if match:
            route, args, kwargs = match
            try:
                return route.handler(self, *args, **kwargs)
            except Exception, e:
                return self.handle_exception(e, self.app.debug)
        else:
            raise exc.NotFoundException("Resource does not exist.")

class RouteEx(webapp2.Route):
    '''
    Adds strict_slash parameter which allows to control wheter urls with and
    without slash will lead to the same handler.
    '''

    def __init__(self, *args, **kwargs):
        self._strict_slash = kwargs.pop('strict_slash', False)
        super(RouteEx, self).__init__(*args, **kwargs)
        if not self._strict_slash:
            self.template += '<__slash:/?>'

    def match(self, request):
        res = super(RouteEx, self).match(request)
        if res and not self._strict_slash:
            self, args, kwargs = res
            kwargs.pop('__slash')
            res = (self, args, kwargs)
        return res


class ErrorResponse(stricttype.Message):
    code = stricttype.IntegerType()
    message = stricttype.StringType()
    traceback = stricttype.StringType(required=False)
