# def application(env, start_response):
#     start_response('200 OK', [('Content-Type', 'text/html')])
#     return [b"Hello World"]

# gunicorn --bind 127.0.0.1:8001 test
# curl -X POST --data "email=emailaddress@gmail.com&password=passwordhere&rememberMe=false" "http://127.0.0.1:8001?dd=ff"


def application(environ, start_response):

    # Returns a dictionary in which the values are lists
    try:
        request_body_size = int(environ.get('CONTENT_LENGTH', 0))
    except (ValueError):
        request_body_size = 0

    response_body = [
        "Hello, world!"
    ]

    get_params = environ['QUERY_STRING']
    post_params = environ['wsgi.input'].read(request_body_size).decode()

    for name, params in [("GET", get_params), ("POST", post_params)]:
        params = params.split('&')
        response_body.append(f"{name} parameters: ")
        for item in params:
            if len(item):
                key, value = item.split("=")
                response_body.append(f"{key}:{value}")

    response_body = '\n<br>'.join(response_body)

    start_response('200 OK', [('Content-Type', 'text/html')])
    return [response_body.encode()]
