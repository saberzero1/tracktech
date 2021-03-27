import json
import re
import logging
from detection.bounding_box import BoundingBox

skipped_lines = 0


class PreAnnotations:
    def __init__(self, file_path: str, nr_frames: int):
        """Constructor for the preAnnotations object.

        Creates list of lists, for each frame it contains a list of bounding boxes.

        Args:
            file_path (str): Path to the file containing the annotations.
            nr_frames (int): The amount of frames of which annotated data will get extracted.

        Raises:
            When number of frames is negative it raises an error.
        """
        self.file_path = file_path
        # Cannot contain negative frames.
        if nr_frames < 0:
            raise AttributeError('Cannot have negative number of frames')
        self.nr_frames = nr_frames
        # Foreach frame create a list.
        self.boxes = [[] for _ in range(nr_frames)]

    def parse_file(self) -> None:
        """Parses file containing annotations.

        Raises:
            Exception is raised when the file type does not have a handler.
        """
        is_txt_file = re.search('^.*.txt$', self.file_path)
        is_json_file = re.search('^.*.json$', self.file_path)
        # Switch statement
        if is_txt_file:
            self.parse_text_file()
        elif is_json_file:
            self.parse_json_file()
        else:
            raise NotImplementedError('No implementation exists for this file type')

    def parse_text_file(self) -> None:
        """Parses text file containing annotations

        Reads file line by line and puts it inside a bounding box object
        """
        global skipped_lines
        # Read file
        with open(self.file_path) as file:
            lines = [line.rstrip('\n') for line in file]

        # Determine delimiter automatically
        delimiter = ' '
        if lines[0].__contains__(','):
            delimiter = ','

        # Extract information from lines
        for line in lines:
            (frame_nr, person_id, x, y, w, h) = self.parse_line(line, delimiter)
            if frame_nr - 1 >= self.nr_frames:
                skipped_lines = skipped_lines + 1
                continue

            # Create bounding box
            rectangle = (x, y, x + w, y + h)
            box = BoundingBox(person_id, rectangle, "UFO", 1)
            self.boxes[frame_nr - 1].append(box)

        # Logs when lines skipped
        if skipped_lines > 0:
            logging.info(f'Skipped lines: {skipped_lines}')

    @staticmethod
    def parse_line(line: str, delimiter: str) -> [int]:
        """Parse line from file given a delimiter.

        Args:
            line (str): line in file.
            delimiter (str): delimiter values in line are separated with.

        Returns:
            Integer values of line parsed and put inside string.
        """
        return [int(i) for i in line.split(delimiter)[:6]]

    def parse_json_file(self) -> None:
        """Parses JSON file
        """
        # Open file.
        with open(self.file_path) as json_file:
            # Every json object
            data = [x for x in json.load(json_file)]
            for json_obj in data:
                self.parse_json_object(json_obj)

    def parse_json_object(self, json_object) -> None:
        """Extracts data from json object and puts them in class.

        JSON object (subject) has a path containing coordinates for each frame.
        Looping goes through each path and adds box for each frame.

        Args:
            json_object: A single json object.
        """
        global skipped_lines
        first_frame = list(json_object['boxes'])[0]
        # A rectangle
        x0, y0, x1, y1 = json_object['boxes'][first_frame]
        half_width = int((x1 - x0) / 2)
        half_height = int((y1 - y0) / 2)
        # Add bounding box for each frame
        for frame_nr in json_object['path']:
            # Skips frame when it does exceed list length
            if frame_nr - 1 >= self.nr_frames:
                skipped_lines = skipped_lines + 1
                continue

            # Create bounding box for a frame
            (x, y) = json_object['path'][frame_nr]
            rectangle = (x - half_width, y - half_height, x + half_width, y + half_height)
            box = BoundingBox(1, rectangle, 'UFO', 1)
            # Append to list
            self.boxes[int(frame_nr) - 1].append(box)
