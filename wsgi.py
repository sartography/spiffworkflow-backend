"""This is my docstring."""
from werkzeug.exceptions import NotFound
from werkzeug.middleware.dispatcher import DispatcherMiddleware
from werkzeug.middleware.proxy_fix import ProxyFix

from spiffworkflow_backend import create_app

app = create_app()

if __name__ == "__main__":

    def no_app(environ, start_response):
        """This is."""
        return NotFound()(environ, start_response)

    # Remove trailing slash, but add leading slash
    base_url = "/" + app.config["APPLICATION_ROOT"].strip("/")
    routes = {"/": app.wsgi_app}

    if base_url != "/":
        routes[base_url] = app.wsgi_app

    app.wsgi_app = DispatcherMiddleware(no_app, routes)
    app.wsgi_app = ProxyFix(app.wsgi_app)

    flask_port = app.config["FLASK_PORT"]

    app.run(host="0.0.0.0", port=flask_port)
