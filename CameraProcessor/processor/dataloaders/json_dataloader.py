"""JSON dataloader class.

This program has been developed by students from the bachelor Computer Science at
Utrecht University within the Software Project course.
© Copyright Utrecht University (Department of Information and Computing Sciences)
"""
import json
from processor.data_object.bounding_box import BoundingBox
from processor.data_object.bounding_boxes import BoundingBoxes
from processor.data_object.rectangle import Rectangle
from processor.dataloaders.i_dataloader import IDataloader


class JsonDataloader(IDataloader):
    """JSON Dataloader, formats MOT Data."""

    def parse_file(self):
        """Parses a file into a BoundingBoxes object.

        Returns:
            bounding_boxes_list (list): a BoundingBoxes object.
        """
        annotations = self.__get_annotations()
        bounding_boxes_list = self.__parse_boxes(annotations)
        return bounding_boxes_list

    def __parse_boxes(self, annotations):
        """Parses bounding boxes.

        Args:
            annotations ([(str)]): Annotations tuples in a list.

        Returns:
            bounding_boxes_list ([BoundingBox]): List of BoundingBox objects.
        """
        bounding_boxes_list = []
        current_boxes = []
        current_image_id = annotations[0][0]
        # Extract information from lines.
        for annotation in annotations:
            (image_id, person_id, certainty, object_type, pos_x, pos_y, pos_x2, pos_y2) = annotation
            if not current_image_id == image_id:
                bounding_boxes_list.append(BoundingBoxes(current_boxes, current_image_id))
                current_boxes = []
                current_image_id = image_id
            current_boxes.append(BoundingBox(classification=object_type,
                                             rectangle=Rectangle(x1=pos_x,
                                                                 y1=pos_y,
                                                                 x2=pos_x2,
                                                                 y2=pos_y2),
                                             identifier=person_id,
                                             certainty=certainty
                                             ))
        return bounding_boxes_list

    def __get_annotations(self):
        """Reads the annotations from a file.

        Returns:
            annotations ([(str)]): Annotations tuples in a list.
        """
        # Read file.
        with open(self.file_path) as file:
            lines = [line.rstrip('\n') for line in file]

        annotations = []
        # Extract information from lines.
        for line in lines:
            json_line = json.loads(line)
            image_id = json_line['imageId']
            boxes = json_line['boxes']
            for box in boxes:
                person_id = box['boxId']
                certainty = box['certainty']
                object_type = box['objectType']
                x_left_top = box['rect'][0]
                y_left_top = box['rect'][1]
                x_right_bottom = box['rect'][2]
                y_right_bottom = box['rect'][3]
                annotations.append((image_id, person_id, certainty, object_type,
                                    x_left_top, y_left_top, x_right_bottom, y_right_bottom))
        return annotations