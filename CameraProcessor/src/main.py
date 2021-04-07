import sys
import logging
import os
import asyncio
import configparser
from absl import app
from src.pipeline.detection.detection_obj import DetectionObj
from src.pipeline.detection.yolov5_runner import Detector
from src.input.video_capture import VideoCapture
from src.input.hls_capture import HlsCapture
import src.websocket_client as client
from src.pipeline.process_frames import process_stream


def main(_):
    """Setup for logging and starts pipeline by reading in config information.

    Args:
        _ (list): list of arguments passed to main, contains file path per default.
    """
    # Logging doesn't work in main function without this,
    # but it must be in main as it gets removed by documentation.py otherwise.
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)

    logging.basicConfig(filename='main.log', filemode='w',
                        format='%(asctime)s %(levelname)s %(name)s - %(message)s',
                        level=logging.INFO,
                        datefmt='%Y-%m-%d %H:%M:%S')

    logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))

    # Load the config file, take the relevant Yolov5 section
    configs = configparser.ConfigParser(allow_no_value=True)
    configs.read('../configs.ini')
    yolo_config = configs['Yolov5']

    # Instantiate the Detection Object
    det_obj = DetectionObj(None, None, 0)

    # Instantiate the detector
    logging.info("Instantiating detector...")
    detector = Detector(yolo_config)

    # Frame counter starts at 0. Will probably work differently for streams
    logging.info("Starting video stream...")

    hls_config = configs['HLS']
    orchestrator_config = configs['Orchestrator']

    hls_enabled = hls_config.getboolean('enabled')

    # Capture the video stream
    if hls_enabled:
        vid_stream = HlsCapture(hls_config['url'])
    else:
        vid_stream = VideoCapture(os.path.join('..', yolo_config['source']))

    asyncio.get_event_loop().run_until_complete(initialize(vid_stream, det_obj, detector, orchestrator_config['url']))


async def initialize(vid_stream, det_obj, detector, url):
    """Initialize the websocket client connecting to the processor orchestrator when a HLS stream is used.

    Args:
        vid_stream (ICapture): video stream object.
        det_obj (DetectionObj): stores detections with all necessary information.
        detector (Detector): detector object performing yolov5 detections.
        url (str): url to the processor orchestrator.

    Returns:
    """
    if isinstance(vid_stream, HlsCapture):
        ws_client = await client.create_client(url)
        ws_client.write_message(vid_stream.to_json())
    else:
        ws_client = None

    await process_stream(vid_stream, det_obj, detector, ws_client)


if __name__ == '__main__':
    try:
        app.run(main)
    except SystemExit:
        pass
