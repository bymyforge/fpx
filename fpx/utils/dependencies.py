from typing import Callable, Any



class Dependency:
    def __init__(self, dependency: Callable[..., Any]):
        self.dependency = dependency