from typing import Any, Callable


class Dependency:
    def __init__(self, dependency: Callable[..., Any]):
        self.dependency = dependency
