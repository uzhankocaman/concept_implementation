
class Observer:
    def handle_event(self, data):
        raise NotImplementedError("Implement in subclass")
    
class Event:
    def __init__(self):
        self._observers = []

    def subscribe(self, observer):
        self._observers.append(observer)

    def emit(self, data):
        for observer in self._observers:
            observer.handle_event(data)