import os
B="C:/Users/corin/Desktop/LEVIATHANV2/leviathan"
def w(p,c):
    open(os.path.join(B,p),"w").write(c)
    print("Wrote",p)
EVENTS_PY = '''
import logging
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum, auto
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


class EventType(Enum):
    SIGNAL_GENERATED = auto()
    TRADE_EXECUTED = auto()
    ORDER_FILLED = auto()
    POSITION_OPENED = auto()
    POSITION_CLOSED = auto()
    RISK_ALERT = auto()
    CIRCUIT_BREAKER = auto()
    MARKET_OPEN = auto()
    MARKET_CLOSE = auto()
    DATA_UPDATE = auto()
    ERROR = auto()


@dataclass
class Event:
    type: EventType
    data: Dict[str, Any]
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    source: str = "unknown"
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    metadata: Optional[Dict[str, Any]] = None

    def __post_init__(self):
        if not isinstance(self.type, EventType):
            raise ValueError(f"Event type must be EventType enum, got {type(self.type)}")
        if not isinstance(self.data, dict):
            raise TypeError(f"Event data must be a dict, got {type(self.data)}")
        logger.debug("Event created: type=%s source=%s id=%s", self.type.name, self.source, self.event_id[:8])

    def to_dict(self) -> Dict[str, Any]:
        return {"type": self.type.name, "data": self.data, "timestamp": self.timestamp.isoformat(), "source": self.source, "event_id": self.event_id, "metadata": self.metadata}

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "Event":
        return cls(type=EventType[d["type"]], data=d["data"], timestamp=datetime.fromisoformat(d["timestamp"]), source=d.get("source", "unknown"), event_id=d.get("event_id", str(uuid.uuid4())), metadata=d.get("metadata"))

    def __str__(self) -> str:
        return f"Event({self.type.name}, source={self.source}, id={self.event_id[:8]})"


def signal_event(symbol, action, confidence, source="signal_generator"):
    return Event(type=EventType.SIGNAL_GENERATED, data={"symbol": symbol, "action": action, "confidence": confidence}, source=source)

def trade_event(symbol, side, qty, price, source="executor"):
    return Event(type=EventType.TRADE_EXECUTED, data={"symbol": symbol, "side": side, "qty": qty, "price": price}, source=source)

def risk_alert_event(message, severity="warning", source="risk_manager"):
    return Event(type=EventType.RISK_ALERT, data={"message": message, "severity": severity}, source=source)

def error_event(error, module, details=None):
    return Event(type=EventType.ERROR, data={"error": error, "module": module, "details": details or {}}, source=module)
'''
w("core/events.py", EVENTS_PY)
MESSAGE_BUS_PY = '''
import logging
import asyncio
import threading
from typing import Callable, Dict, List, Any
from collections import defaultdict

logger = logging.getLogger(__name__)


class MessageBus:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._subscribers: Dict[str, List[Callable]] = defaultdict(list)
        self._async_subscribers: Dict[str, List[Callable]] = defaultdict(list)
        self._event_history: List[Any] = []
        self._max_history = 1000
        self._initialized = True
        logger.info("MessageBus initialized (singleton)")

    def subscribe(self, event_type, callback: Callable):
        self._subscribers[event_type].append(callback)
        logger.debug("Subscriber added for %s: %s", event_type, callback.__name__)

    def subscribe_async(self, event_type, callback: Callable):
        self._async_subscribers[event_type].append(callback)
        logger.debug("Async subscriber added for %s: %s", event_type, callback.__name__)

    def unsubscribe(self, event_type, callback: Callable):
        if callback in self._subscribers[event_type]:
            self._subscribers[event_type].remove(callback)
        if callback in self._async_subscribers[event_type]:
            self._async_subscribers[event_type].remove(callback)
