from enum import Enum


class StorageContainerPosition(Enum):
    """
    Define different hight settings for picking up a storage container with the fork lift.
    """

    Ground = -1.0
    WhiteBox = -0.5
    HorizontalWarehouse = 0.8
    VerticalWarehouse = -1.0
