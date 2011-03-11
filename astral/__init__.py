__version_info__ = ('0', '1', '0')
__version__ = '.'.join(__version_info__)

def Astral(*args, **kwargs):
    from astral.node import Node
    return Node(*args, **kwargs)
