"""Inter-module communication via publish/subscribe."""
import logging
import asyncio
from collections import defaultdict

logger = logging.getLogger('leviathan.bus')


class MessageBus:
    """Singleton message bus for event-driven communication."""
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._subscribers = defaultdict(list)
        return cls._instance

    def subscribe(self, event_type: str, callback):
        self._subscribers[event_type].append(callback)

    def unsubscribe(self, event_type: str, callback):
        if callback in self._subscribers[event_type]:
            self._subscribers[event_type].remove(callback)

    def publish(self, event):
        event_type = event.get('type', event.__class__.__name__ if hasattr(event, '__class__') else 'unknown')
        for cb in self._subscribers.get(event_type, []):
            try:
                if asyncio.iscoroutinefunction(cb):
                    asyncio.create_task(cb(event))
                else:
                    cb(event)
            except Exception as e:
                logger.error(f"Event handler error for {event_type}: {e}")

    def clear(self):
        self._subscribers.clear()
