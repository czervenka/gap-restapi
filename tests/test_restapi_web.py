import json
from gap.utils.tests import TestBase, WebAppTestBase

from stricttype import Message, StringType, IntegerType
from restapi import JsonRequestHandler, api_method, exceptions as exc

class Void(Message):
    pass

class Request(Message):
    payload = StringType()

class Response(Message):
    payload = StringType()


class TestRestapi(WebAppTestBase):

    @classmethod
    def getApp(cls):

        class ApiTest(JsonRequestHandler):
            'the simplest restapi handler does ping'

            @api_method(Request, Response)
            def get(self, data):
                return {'payload': data.payload}

            post = get

        return [('/', ApiTest)]

    def test_ping(self):
        'ping returns sent data'

        req_data = {'payload': 'test'}

        self.assertNotEqual(self.app.get('/', req_data).body, None)
        self.assertEquals(self.app.get('/', req_data).json, req_data)


from restapi import routed_api_method, RoutedJsonRequestHandler


class TestRoutedRestapi(WebAppTestBase):

    @classmethod
    def getApp(cls):

        class ApiTest(RoutedJsonRequestHandler):
            'routed api test app'

            @routed_api_method(Request, Response, path='ping')
            def ping(self, data):
                return data.as_dict()

            @routed_api_method(Void, Response, name='my-ping')
            def my_ping(self, data):
                return {'payload': 'my-ping'}

            @routed_api_method(Request, Response, path='ping-path/<payload:.*>')
            def ping_path(self, data):
                return {'payload': data.payload}

            @routed_api_method(Request, Response, http_method='POST')
            def ping_post(self, data):
                return data.as_dict()

            @routed_api_method(Request, Response)
            def method_name_as_path(self, data):
                return {'payload': 'ok'}

            @routed_api_method(Void, Void)
            def exception(self, data):
                raise Exception('Test exception')

            @routed_api_method(Void, Void)
            def exception_without_traceback(self, data):
                self.app.debug = False
                raise Exception('Test exception')

            @routed_api_method(Void, Response, path='my-get-post', http_method='GET')
            def MyGet(self, data):
                return {'payload': 'get'}

            @routed_api_method(Void, Response, path='my-get-post', http_method='POST')
            def MyPost(self, data):
                return {'payload': 'post'}

            @routed_api_method(Void, Response, path='my-get-post', http_method=('PUT', 'DELETE'))
            def MyPatchDelete(self, data):
                return {'payload': 'put-delete'}

            def dispatch(self):
                self.app.debug = True
                return super(ApiTest, self).dispatch()



        return [('/.*', ApiTest), ]

    def test_ping(self):
        'ping returns sent data'
        req_data = {'payload': 'abc'}
        self.assertEquals(self.app.get('/ping', req_data).json, req_data)

    def test_404(self):
        '404 response'
        self.assertEquals(self.app.get('/pingg', {}, status=404).json['code'], 404,
                msg='routed call returns "404 Not Found" and body countains valid json')

    def test_function_name(self):
        'func.__name__ as path'
        self.assertEquals(self.app.get('/my-ping', {}).json['payload'], 'my-ping')

    def test_http_method(self):
        'same path but different http_method'
        self.assertEquals(self.app.get('/my-get-post').json['payload'], 'get')
        self.assertEquals(self.app.post('/my-get-post').json['payload'], 'post')
        self.assertEquals(self.app.delete('/my-get-post').json['payload'], 'put-delete')
        self.assertEquals(self.app.put('/my-get-post').json['payload'], 'put-delete')

    def test_invalid_request(self):
        'request with put/post data must be application/json'
        req_data = {'payload': 'abc'}
        resp = self.app.post('/ping_post', req_data, status=400, headers={'content-type': 'text/html'})
        self.assertEquals(resp.json['code'], 400)

        resp = self.app.post_json('/ping_post', req_data)
        self.assertEquals(resp.json['payload'], req_data['payload'])

    def test_internal_server_error(self):
        'internal server error'
        self.assertEquals(self.app.get('/exception', status=500).json['code'], 500)
        self.assertNotEquals(self.app.get('/exception', status=500).json['traceback'], None)
        self.assertEquals(self.app.get('/exception_without_traceback', status=500).json['traceback'], None)

    def test_path_parameters(self):
        'parameter in path'
        # valid data in path parameter
        self.assertEquals(self.app.get('/ping-path/abc').json['payload'], 'abc')
        # missing data in path parameter
        self.assertEquals(self.app.get('/ping-path/', status=400).json['code'], 400)


class TestInternals(TestBase):

    def test_exception_str(self):
        self.assertEquals(str(exc.ApiException("Some message", code=456)), '456 Some message')

