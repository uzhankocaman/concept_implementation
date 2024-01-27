
class Observer:
    def handle_event(self, data):
        raise NotImplementedError("Implement in subclass")
    
class Event:
    def __init__(self):
        self._observers = []

    def subscribe(self, observer):
        self._observers.append(observer)

    def emit(self, data):
        # loop = asyncio.get_event_loop()
        for observer in self._observers:
            # loop.create_task(observer.handle_event(data))
            observer.handle_event(data)