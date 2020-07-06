class StrategyLookAheadException(Exception):
    """ Unknown lookahead strategy Exception
    """
    def __init__(self, message):
        # Call the base class constructor with the parameters it needs
        super().__init__("Incorrect lookahead strategy given : " + str(message))
