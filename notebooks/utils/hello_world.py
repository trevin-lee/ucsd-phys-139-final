"""
Simple hello world function for testing package imports.
"""


def hello_world(name: str = "World") -> str:
    """
    A simple hello world function to test package imports.
    
    Parameters
    ----------
    name : str, optional
        Name to greet, by default "World"
    
    Returns
    -------
    str
        Greeting message
    
    Examples
    --------
    >>> hello_world()
    'Hello, World!'
    >>> hello_world("TESS")
    'Hello, TESS!'
    """
    return f"Hello, {name}!"

