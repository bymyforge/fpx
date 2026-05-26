from classes.runner.subclasses.router import Router


class Handlers(Router):
    def __init__(self, runner):
        super().__init__()
        self.runner = runner

    def include_router(self, router: Router):
        '''Метод для подключения плагинов и сторонних роутеров'''
        for event_type, funcs in router._handlers.items():
            if event_type in self._handlers:
                self._handlers[event_type].extend(funcs)