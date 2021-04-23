import logging
import asyncio
import cv2
# pylint: disable=unused-import
import processor.websocket_client as client
from processor.pipeline.detection.detection_obj import DetectionObj
from processor.pipeline.detection.idetector import IDetector as Detector
from processor.pipeline.tracking.tracking_obj import TrackingObj
from processor.input.hls_capture import HlsCapture
# pylint: enable=unused-import


async def process_stream(capture, detector, tracker, ws_client=None):
    """Processes a stream of frames, outputs to frame or sends to client.

    Outputs to frame using OpenCV if not client is used.
    Sends detections to client if client is used (HlsCapture).

    Args:
        capture (ICapture): capture object to process a stream of frames.
        detector (Detector): Yolov5 detector performing the detection using det_obj.
        tracker (SortTracker): tracker performing SORT tracking.
        ws_client (WebsocketClient): processor orchestrator to pass through detections.
    """
    track_obj = TrackingObj()

    frame_nr = 0

    while capture.opened():
        ret, frame, timestamp = capture.get_next_frame()

        if not ret:
            if frame_nr == capture.get_capture_length():
                logging.info("End of file reached")
                break
            continue

        # Create detection object for this frame.
        det_obj = DetectionObj(timestamp, frame, frame_nr)

        detector.detect(det_obj)

        track_obj.update(det_obj)

        tracker.track(track_obj)

        # Write to client if client is used (should only be done when vid_stream is HlsCapture)
        if ws_client:
            ws_client.write_message(track_obj.to_json())
            logging.info(track_obj.to_json())
        else:
            # Draw bounding boxes with ID
            track_obj.draw_rectangles()

            # Play the video in a window called "Output Video"
            try:
                cv2.imshow("Output Video", det_obj.frame)
            except OSError as err:
                # Figure out how to get Docker to use GUI
                raise OSError("Error displaying video. Are you running this in Docker perhaps?")\
                    from err

            # This next line is **ESSENTIAL** for the video to actually play
            if cv2.waitKey(1) & 0xFF == ord('q'):
                return

        frame_nr += 1
        await asyncio.sleep(0)

    logging.info(f'capture object stopped after {frame_nr} frames')
