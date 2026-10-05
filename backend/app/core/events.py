import asyncio
from datetime import datetime
from typing import Any, Callable, Coroutine, Dict, List
from pydantic import BaseModel, Field
from app.core.logging import app_logger

class DomainEvent(BaseModel):
    event_type: str
    tenant_id: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    payload: Dict[str, Any] = Field(default_factory=dict)
    trace_id: str = ""

# Type for event handler callbacks
EventHandler = Callable[[DomainEvent], Coroutine[Any, Any, None]]

class EventBus:
    """In-process asynchronous event bus supporting decoupled domain events."""
    
    def __init__(self):
        self._subscribers: Dict[str, List[EventHandler]] = {}
        self._global_subscribers: List[EventHandler] = []
        
    def subscribe(self, event_type: str, handler: EventHandler):
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        self._subscribers[event_type].append(handler)

    def subscribe_all(self, handler: EventHandler):
        self._global_subscribers.append(handler)
        
    async def publish(self, event: DomainEvent):
        """Asynchronously dispatches an event to all matching subscribers."""
        app_logger.info(
            f"DomainEvent: {event.event_type}",
            extra={"tenant_id": event.tenant_id, "event_type": event.event_type}
        )
        
        handlers = self._subscribers.get(event.event_type, []).copy()
        handlers.extend(self._global_subscribers)
        
        if not handlers:
            return
            
        tasks = []
        for handler in handlers:
            try:
                tasks.append(asyncio.create_task(handler(event)))
            except Exception as e:
                app_logger.error(f"Error initiating event handler for {event.event_type}: {e}")
                
        if tasks:
            # Shield to prevent subscriber exceptions from breaking caller
            await asyncio.gather(*tasks, return_exceptions=True)

# Singleton global domain event bus
event_bus = EventBus()
