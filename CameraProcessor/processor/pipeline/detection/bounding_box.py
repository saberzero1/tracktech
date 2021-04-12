import json
from typing import List



class BoundingBox:
    """Contains information about a single bounding box
    """
    def __init__(self, identifier: int, rectangle: List[int], classification: str, certainty: float):
        """

        Args:
            identifier (int):
            rectangle :
            classification:
            certainty:
        """
        self.identifier = identifier
        self.rectangle = rectangle
        if len(rectangle) != 4:
            raise AttributeError('Invalid length for bounding box in BoundingBox.rectangle')
        self.feature = None
        self.classification = classification
        self.certainty = certainty

    def to_json(self) -> json:
        """Converts the object to JSON format
        Returns: JSON representation of the object

        """
        string = json.dumps({
            "boxId": self.identifier,
            "rect": self.rectangle,
        })

        # We need to decode the string so we don't get top-level double encoding
        return json.JSONDecoder().decode(string)