class StrategyPlacementException(Exception):
    """ Unknown placement strategy Exception
    """
    def __init__(self, message):
        # Call the base class constructor with the parameters it needs
        super().__init__("Incorrect placement strategy given : " + message)
