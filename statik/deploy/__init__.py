
from .sftp import SFTP
from .netlify import Netlify


DEPLOYMENT_METHOD_REGISTRY = {
    "sftp": SFTP,
    "netlify": Netlify,
}


def new_deployment_method_instance(method, config, error_context=None):
    """Creates a deployment method instance for the given method. Returns None if no such method
    exists."""
    if method not in DEPLOYMENT_METHOD_REGISTRY:
        return None
    return DEPLOYMENT_METHOD_REGISTRY[method](config, error_context=error_context)

