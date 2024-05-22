# The code is not related to the project
# This is just a simple WSGI script
import json


def simple_app(environ, start_response):
    """Simplest possible application object"""
    status = '200 OK'
    response_headers = [('Content-type', 'text/plain')]
    query_data = None
    post_data = None
    if environ['REQUEST_METHOD'] == 'GET' and environ['QUERY_STRING']:
        query_data = [i.split('=') for i in environ['QUERY_STRING'].split('&')]
    elif environ['REQUEST_METHOD'] == 'POST':
        post_data_as_string = environ['wsgi.input'].read().decode('utf-8')
        post_data = json.loads(post_data_as_string)

    print('-----QUERY STRING-----')
    print(query_data)
    if query_data:
        for key, val in query_data:
            print(key, val, sep=' = ')

    print('-----POST DATA-----')
    if post_data:
        for key, val in post_data.items():
            print(key, val, sep=' = ')

    start_response(status, response_headers)
    return [b'QUERY STRING: ' + str(query_data).encode(), b'\nPOST DATA: ' + str(post_data).encode()]

application = simple_app
