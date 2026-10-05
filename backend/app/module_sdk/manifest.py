from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

class ConfigFieldType(str):
    STRING = "string"
    SECRET = "secret"
    INTEGER = "integer"
    BOOLEAN = "boolean"
    URL = "url"

class ModuleConfigField(BaseModel):
    key: str
    label: str
    type: str = "string"
    required: bool = False
    default: Optional[Any] = None
    description: str = ""

class ModuleManifest(BaseModel):
    id: str
    name: str
    version: str = "1.0.0"
    description: str = ""
    capabilities: List[str] = Field(default_factory=list)
    permissions: List[str] = Field(default_factory=list)
    providers: List[str] = Field(default_factory=list)
    configuration_schema: List[ModuleConfigField] = Field(default_factory=list)
    ui_metadata: Dict[str, Any] = Field(default_factory=dict)
