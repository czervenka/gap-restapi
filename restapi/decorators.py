def api_method(in_type, out_type):

    def api_method_decorator(f):

        f.in_type = in_type
        f.out_type = out_type
        f.api_method = True

        return f
    return api_method_decorator

def routed_api_method(in_type, out_type, name=None, path=None, http_method='GET'):

    def api_method_decorator(f):
        f.in_type = in_type
        f.out_type = out_type
        f.api_method = True

        if name is None:
            f.name = f.__name__
        else:
            f.name = name
        if path is None:
            f.path = f.name
        else:
            f.path = path
        if isinstance(http_method, (tuple, list)):
            f.http_method = [ m.upper() for m in http_method ]
        else:
            f.http_method = http_method.upper()
        return f
    return api_method_decorator
