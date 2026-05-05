from typing import Callable


def mutation_surface(
    mutation_class: str,
    persistence_type: str,
    advisory_only: bool,
):
    def decorator(func: Callable):
        setattr(func, "mutation_class", mutation_class)
        setattr(func, "persistence_type", persistence_type)
        setattr(func, "advisory_only", advisory_only)
        return func
    return decorator