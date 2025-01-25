from enum import Enum
from typing import Optional, Dict, Any, List
from datetime import datetime
from pydantic import BaseModel, Field

class MachineStatus(str, Enum):
    IDLE = "idle"
    PROCESSING = "processing"
    READY = "ready"
    BUSY = "busy"
    ERROR = "error"
    MAINTENANCE = "maintenance"

class QueueMode(str, Enum):
    NOTIFICATION = "notification"
    READY = "ready"
    PAUSED = "paused"
    SCHEDULED = "scheduled"

class AgentStatus(str, Enum):
    AVAILABLE = "available"
    ON_CALL = "on_call"
    BREAK = "break"
    OFFLINE = "offline"

class MachineState(BaseModel):
    status: MachineStatus = Field(default=MachineStatus.IDLE)
    queue_mode: QueueMode = Field(default=QueueMode.NOTIFICATION)
    active_agents: Dict[str, AgentStatus] = Field(default_factory=dict)
    current_tasks: List[str] = Field(default_factory=list)
    error_state: Optional[Dict[str, Any]] = Field(default=None)
    last_updated: datetime = Field(default_factory=datetime.utcnow)
    metrics: Dict[str, Any] = Field(default_factory=dict)

    class Config:
        use_enum_values = True

    def update_status(self, new_status: MachineStatus) -> None:
        self.status = new_status
        self.last_updated = datetime.utcnow()

    def set_queue_mode(self, mode: QueueMode) -> None:
        self.queue_mode = mode
        self.last_updated = datetime.utcnow()

    def update_agent_status(self, agent_id: str, status: AgentStatus) -> None:
        self.active_agents[agent_id] = status
        self.last_updated = datetime.utcnow()

    def add_task(self, task_id: str) -> None:
        self.current_tasks.append(task_id)
        self.last_updated = datetime.utcnow()

    def remove_task(self, task_id: str) -> None:
        if task_id in self.current_tasks:
            self.current_tasks.remove(task_id)
            self.last_updated = datetime.utcnow()

    def set_error(self, error_data: Dict[str, Any]) -> None:
        self.error_state = error_data
        self.status = MachineStatus.ERROR
        self.last_updated = datetime.utcnow()

    def clear_error(self) -> None:
        self.error_state = None
        self.status = MachineStatus.IDLE
        self.last_updated = datetime.utcnow()

    def update_metrics(self, metrics_update: Dict[str, Any]) -> None:
        self.metrics.update(metrics_update)
        self.last_updated = datetime.utcnow()