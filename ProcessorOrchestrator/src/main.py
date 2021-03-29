import os
import ssl
from pathlib import Path

from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop
from tornado.web import Application, StaticFileHandler
from client import ClientSocket
from processor import ProcessorSocket
from logger import LogHandler
import pdoc


def main():
    """Entry point of the application

    The main method is used to set up the tornado application, which includes routing, setting up SSL certificates
    and compiling the documentation.
    """
    # Get ssl ready, if provided in the environment variables
    cert = os.environ.get('SSL_CERT')
    key = os.environ.get('SSL_KEY')
    use_tls = cert is not None and key is not None

    # Create documentation page
    pdoc.render.configure(docformat="google")
    pdoc.pdoc(
        'main',
        'client',
        'processor',
        'objectManager',
        'logger',
        output_directory=Path(os.path.join(os.path.dirname(__file__), "../docs"))
    )

    # Define socket for both client and processor
    handlers = [
        ('/client', ClientSocket),
        ('/processor', ProcessorSocket),
        ('/logs', LogHandler),
        ('/docs/(.*)', StaticFileHandler, {'path': os.path.join(os.path.dirname(__file__), "../docs"), 'default_filename': "index.html"})
    ]

    # Construct and serve the tornado application.
    app = Application(handlers)

    if use_tls:
        # Create a ssl context
        ssl_ctx = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
        ssl_ctx.load_cert_chain(cert, key)

        # Create a http server, with optional ssl.
        http_server = HTTPServer(app, ssl_options=ssl_ctx)
        http_server.listen(443)
        print('listening over https')

    else:
        # Create a http server, with optional ssl.
        http_server = HTTPServer(app)
        http_server.listen(80)
        print('listening over http')

    IOLoop.current().start()


if __name__ == "__main__":
    main()
