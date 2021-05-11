"""The request handler that serves the actual HLS index and segment files
It handles authentication/authorization and makes sure conversion processes of cameras are started and stopped

This program has been developed by students from the bachelor Computer Science at
Utrecht University within the Software Project course.
© Copyright Utrecht University (Department of Information and Computing Sciences)

"""

import os
import re
import threading
import time
from subprocess import TimeoutExpired
import tornado.web
from auth.auth import Auth, AuthenticationError, AuthorizationError

from src.camera import Camera
from src.conversion_process import get_conversion_process
from src.stream_options import StreamOptions


# pylint: disable=attribute-defined-outside-init
class CameraHandler(tornado.web.StaticFileHandler):
    """The camera file request handler

    cameras (dict): Dictionary containing all the cameras registered to this VideoForwarder

    """

    # pylint: disable=arguments-differ
    def initialize(self, path, default_filename=None):
        """Set the root path and load the public key from application settings, run at the start of every request

        Args:
            path (str): path to root where files are stored
            default_filename (Optional[str] = None): Optional file name
        """

        # noinspection PyAttributeOutsideInit
        # Needed for the library
        super().initialize(path, default_filename)

        # Set properties of the handler
        self.remove_delay : float = self.application.settings.get('remove_delay')
        self.timeout_delay : int = self.application.settings.get('timeout_delay')

        self.stream_options : StreamOptions = self.application.settings.get('stream_options')

        # Load the public key from application settings
        self.authenticator : Auth = self.application.settings.get('authenticator')

        # Load the public key from application settings
        self.camera : Camera = self.application.settings.get('camera')

    def set_default_headers(self):
        """Set the headers to allow cors and disable caching
        """
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Cache-control", "no-store")

    def start_stream(self, root):
        """Creates stream conversion and starts the stream

        Args:
            root (str): Path to the streams folder
        """

        # If there is no current conversion, start one
        if self.camera.conversion is None:
            tornado.log.access_log.info('starting stream')

            # Configure entry conversion
            self.camera.conversion = get_conversion_process(
                self.camera.url,
                self.camera.audio,
                root,
                self.stream_options
            )

            # Wait and if not created, stop the conversion
            started = self.stream_active(root)
            if not started:
                self.stop_stream(root)

    def stream_active(self, root):
        """Wait a maximum of x seconds for the file to be created, otherwise

        Args:
             root (path): path of the folder that contains the stream segments and index files
        """

        index_file_path = os.path.join(root, 'stream.m3u8')

        for _ in range(0, self.timeout_delay):

            # See whether file exists
            if os.path.exists(index_file_path):
                return True

            # Sleep and check again
            time.sleep(1)

        return False

    def restart_stop_callback(self, root):
        """Starts the HLS stream by using the conversion process that was created

        Args:
            root (str): Path to the where the stream files are located
        """

        # Cancel any current callbacks
        if self.camera.callback is not None:
            self.camera.callback.cancel()
            self.camera.callback = None

        # If there is an conversion
        if self.camera.conversion is not None:
            # Reschedule a new callback to stop the stream
            self.camera.callback = threading.Timer(
                self.remove_delay, self.stop_stream, [root])
            self.camera.callback.start()

    def stop_stream(self, root):
        """Function to stop a given camera stream, will be called once a stream is no longer used for a specific
        amount of time

        Args:
            root (str): Root directory of the stream
        """

        # Print stopping for logging purposes
        tornado.log.access_log.info('stopping stream')

        # Stopping the conversion
        self.camera.conversion.terminate()

        try:
            # Wait a few seconds for it stop, so it does not lock any files
            self.camera.conversion.wait(60)
        except TimeoutExpired:
            # Handle a timeout exception if the process does not stop
            pass
        finally:
            # Remove the conversion
            self.camera.conversion = None

            # Remove the old segment and index files
            for file in os.listdir(root):
                os.remove(os.path.join(root, file))

    # pylint: disable=broad-except
    def prepare(self):
        """Validate and check the header token if a public key is specified
        """

        # Validate the token and act accordingly if it is not good.
        if self.authenticator is not None:
            try:
                self.authenticator.validate(self.request.headers.get('Authorization').split()[1])
            except AuthenticationError as exc:
                # Authentication (validating token) failed
                tornado.log.access_log.info(exc)
                self.set_status(403)
                raise tornado.web.Finish() from exc
            except AuthorizationError as exc:
                # Authorization failed (authentication succeeded, but the action is not allowed)
                tornado.log.access_log.info(exc)
                self.set_status(401)
                raise tornado.web.Finish() from exc
            except Exception as exc:
                # Any other error, no token added e.g.
                tornado.log.access_log.info(exc)
                self.set_status(400)
                raise tornado.web.Finish() from exc

    def get_absolute_path(self, root, path):
        """Gets the path of the camera stream, when the camera is not yet started it does so automatically

        Args:
            root (str): path to the root of the system
            path (str): Name of the file searched, which should be a camera stream

        """

        # Get the path on the file system
        abspath = os.path.abspath(os.path.join(root, path))

        # Regex the file path
        match = re.search(r'stream(?:_V.*)?\.(m3u8|ts)', path)

        # If there is no match, return the path as usual
        if match is None:
            return abspath

        # Otherwise, grab the camera and extension information
        extension = match.group(1)

        # If the request is for an index file of an existing camera
        if extension == 'm3u8':
            self.start_stream(root)

        # If it requests a stream file
        if extension in ('m3u8', 'ts'):
            self.restart_stop_callback(root)

        # Return path to files
        return abspath
