
class DeploymentMethod(object):
    """An abstract method for handling deployment."""

    def __init__(self, config, error_context=None):
        """Must validate the given configuration for this deployment method and raise an exception
        if it's invalid."""
        raise NotImplementedError

    def execute(self, source_path):
        """Must actually execute the implemented deployment method."""
        raise NotImplementedError

