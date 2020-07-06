class StrategyCostFException(Exception):
    """ Unknown costF strategy Exception
    """
    def __init__(self, message):
        # Call the base class constructor with the parameters it needs
        super().__init__("Incorrect costF strategy given : " + str(message))
