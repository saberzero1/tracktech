"""Integration testing of forwarder with a dummy interface

"""

import time
import os
import pytest
import runpy
import tornado.web


class MainHandler(tornado.web.RequestHandler):
    """Tornado web application

    """
    def get(self):
        """Empty get

        """
        self.write("")


application = tornado.web.Application([
    (r"/", MainHandler),
])


@pytest.fixture
def app():
    """Creates application

    Return:
         application: tornado application
    """
    return application


# pylint: disable=attribute-defined-outside-init
class TestVideoForwarder:
    """Tests video forwarder http requests, headers and file behavior

    """
    def setup_method(self):
        """Setup method for testing

        """
        self.base_url = 'http://video-forwarder-service:80/testvid'
        self.extension = '.m3u8'

        # Complete url of camera
        self.camera_url = self.base_url + self.extension
        self.stream_dir = '/streams'

    @pytest.mark.gen_test(timeout=15)
    def test_valid_http_request(self, http_client):
        """Checks connection between forwarder and mock client with valid url

        Args:
            http_client: Httpclient that connects

        """
        # Wait until main.py is up and running
        response = yield http_client.fetch(self.camera_url)

        # OK
        assert response.code == 200

    @pytest.mark.gen_test(timeout=15)
    def test_invalid_http_request(self, http_client):
        """Checks connection between forwarder and mock client with invalid url

        Does not use pytest.raises since it cannot yield

        Args:
            http_client: Httpclient that connects

        """

        # Create connection with invalid url
        try:
            yield http_client.fetch(f'{self.base_url}jibberish{self.extension}')
            assert False
        # Asserts exception is raised
        except Exception:
            assert True

    @pytest.mark.gen_test(timeout=15)
    def test_headers(self, http_client):
        """Tests hls stream header on certain properties

        Args:
            http_client: Httpclient that connects

        """
        response = yield http_client.fetch(self.camera_url)
        assert response.headers['Cache-control'] == 'no-store'
        assert response.headers['Access-Control-Allow-Origin'] == '*'

    @pytest.mark.gen_test(timeout=15)
    def test_generate_multiple_video_outputs(self, http_client):
        """Tests whether the stream generates several headers

        Args:
            http_client: Httpclient that connects

        """
        # Create a connection
        response_low_res = yield http_client.fetch(f'{self.base_url}_V0{self.extension}')
        response_med_res = yield http_client.fetch(f'{self.base_url}_V1{self.extension}')
        response_high_res = yield http_client.fetch(f'{self.base_url}_V2{self.extension}')

        # Assert response is OK
        assert response_low_res.code == 200
        assert response_med_res.code == 200
        assert response_high_res.code == 200


if __name__ == '__main__':
    pytest.main(TestVideoForwarder)
