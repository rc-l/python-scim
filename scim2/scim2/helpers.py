# Helper functions

def inheritors(klass):
    """Get all the classes that have inherited from the given class.
    (i.e. have the given klass as a parent).

    Args:
        klass (type): the class to inspect.

    Returns:
          list (type): all the classes that have inherited from the given class.
    """
    subclasses = set()
    work = [klass]
    while work:
        parent = work.pop()
        for child in parent.__subclasses__():
            if child not in subclasses:
                subclasses.add(child)
                work.append(child)
    return subclasses

class classproperty:
    def __init__(self, func):
        self.fget = func
    def __get__(self, instance, owner):
        return self.fget(owner)