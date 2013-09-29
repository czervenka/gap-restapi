from gap.utils.tests import TestBase, WebAppTestBase


class TestWebApp(WebAppTestBase):

    @classmethod
    def getApp(cls):
        # import have to come after test initialization
        import webapp2

        class Handler(webapp2.RequestHandler):
            def get(self):
                self.response.write(self.request.GET['ping'])

        return [('/', Handler)]

    def test_ping(self):
        self.assertEqual(self.app.get('/', {'ping': 'test'}).body, 'test')


class TestRestapi(WebAppTestBase):

    @classmethod
    def getApp(cls):
        from stricttype import Message, StringType
        from restapi import JsonRequestHandler, api_method

        class Request(Message):
            s = StringType()

        class Response(Message):
            s = StringType()

        class JsonTest(JsonRequestHandler):

            @api_method(Request, Response)
            def get(self, data):
                return data.as_dict()

            post = get

        return [('/', JsonTest)]

    def test_ping(self):

        req_data = {'s': 'test'}

        self.assertNotEqual(self.app.get('/', req_data).body, None)
        self.assertEqual(self.app.get('/', req_data).json, req_data)
