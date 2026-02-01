"""
Event Type Definitions for the Message Bus.

Defines all event types and typed event wrappers used throughout
the Leviathan trading system.
"""
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto
from typing import Any, Optional, Dict


class EventType(Enum):
    """All event types in the system."""
    # Trading signals
    SIGNAL_GENERATED = auto()
    SIGNAL_CONFIRMED = auto()

    # Trade lifecycle
    TRADE_SUBMITTED = auto()
    TRADE_EXECUTED = auto()
    TRADE_CLOSED = auto()
    TRADE_REJECTED = auto()
    TRADE_CANCELLED = auto()

    # Position updates
    POSITION_UPDATE = auto()
    POSITION_EXIT_SIGNAL = auto()

    # Risk events
    RISK_ALERT = auto()
    RISK_LIMIT_BREACH = auto()
    CIRCUIT_BREAKER = auto()
    PDT_WARNING = auto()

    # Market data
    MARKET_DATA = auto()
    MARKET_OPEN = auto()
    MARKET_CLOSE = auto()

    # Model events
    MODEL_RETRAINED = auto()
    MODEL_PREDICTION = auto()
    ENSEMBLE_SIGNAL = auto()

    # System events
    SYSTEM_STATUS = auto()
    SYSTEM_START = auto()
    SYSTEM_STOP = auto()
    ERROR = auto()

    # Opus brain
    OPUS_DECISION = auto()
    OPUS_EXIT_DECISION = auto()

    # Learning
    LEARNING_UPDATE = auto()
    PERFORMANCE_UPDATE = auto()


@dataclass
class Event:
    """Base event class for the message bus."""
    type: EventType
    data: Any = None
    timestamp: datetime = field(default_factory=datetime.now)
    source: str = ""
    correlation_id: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            "type": self.type.name,
            "data": self.data,
            "timestamp": self.timestamp.isoformat(),
            "source": self.source,
        }


@dataclass
class SignalEvent(Event):
    """Trading signal event."""
    symbol: str = ""
    direction: str = ""  # BUY, SELL, HOLD
    confidence: float = 0.0
    model_source: str = ""

    def __post_init__(self):
        self.type = EventType.SIGNAL_GENERATED


@dataclass
class TradeEvent(Event):
    """Trade execution event."""
    symbol: str = ""
    side: str = ""
    qty: float = 0.0
    price: float = 0.0
    order_id: str = ""
    pnl: Optional[float] = None

    def __post_init__(self):
        if self.type is None:
            self.type = EventType.TRADE_EXECUTED


@dataclass
class RiskEvent(Event):
    """Risk alert event."""
    risk_type: str = ""  # circuit_breaker, pdt, drawdown, concentration
    severity: str = "warning"  # warning, critical
    message: str = ""

    def __post_init__(self):
        self.type = EventType.RISK_ALERT


@dataclass
class OpusDecisionEvent(Event):
    """Opus brain decision event."""
    symbol: str = ""
    decision: str = ""  # BUY, SELL, HOLD, SKIP
    reasoning: str = ""
    confidence: float = 0.0

    def __post_init__(self):
        self.type = EventType.OPUS_DECISION
