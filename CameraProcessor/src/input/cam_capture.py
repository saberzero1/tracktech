import logging
from cv2 import VideoCapture
from src.input.icapture import ICapture

vcap = VideoCapture(0)


class CamCapture(ICapture):

    # Default init is public HLS stream
    def __init__(self):
        logging.info('connecting to webcam')
        self.cap = vcap

    # Sees whether stream has stopped
    def opened(self):
        return self.cap.isOpened()

    # When everything is done release the capture
    def close(self):
        self.cap.release()

    # Gets the next frame from the stream
    def get_next_frame(self):
        return *self.cap.read(), None
