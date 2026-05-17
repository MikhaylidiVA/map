from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


# User schemas
class UserBase(BaseModel):
    email: EmailStr
    username: str


class UserCreate(UserBase):
    password: str


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    password: Optional[str] = None
    is_active: Optional[bool] = None


class UserResponse(UserBase):
    id: int
    is_active: bool
    is_superuser: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


# Authentication schemas
class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


# Project schemas
class ProjectBase(BaseModel):
    name: str
    description: Optional[str] = None
    is_public: bool = False
    crs: str = "EPSG:3857"


class ProjectCreate(ProjectBase):
    pass


class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    is_public: Optional[bool] = None
    crs: Optional[str] = None


class ProjectResponse(ProjectBase):
    id: int
    owner_id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class ProjectMemberCreate(BaseModel):
    user_id: int
    role: str  # 'admin', 'editor', 'viewer'


class ProjectMemberResponse(BaseModel):
    id: int
    project_id: int
    user_id: int
    role: str
    joined_at: datetime
    
    class Config:
        from_attributes = True


# Layer schemas
class LayerBase(BaseModel):
    name: str
    layer_type: str  # 'vector', 'raster', 'wms', 'wfs', 'xyz'
    source_type: str  # 'postgis', 'file', 'wms', 'wfs', 'xyz'
    source_config: Optional[Dict[str, Any]] = None
    style_config: Optional[Dict[str, Any]] = None
    visible: bool = True
    opacity: float = 1.0
    order_index: int = 0


class LayerCreate(LayerBase):
    pass


class LayerUpdate(BaseModel):
    name: Optional[str] = None
    source_config: Optional[Dict[str, Any]] = None
    style_config: Optional[Dict[str, Any]] = None
    visible: Optional[bool] = None
    opacity: Optional[float] = None
    order_index: Optional[int] = None


class LayerResponse(LayerBase):
    id: int
    project_id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# Feature schemas
class FeatureBase(BaseModel):
    geometry: Dict[str, Any]  # GeoJSON geometry
    properties: Optional[Dict[str, Any]] = None


class FeatureCreate(FeatureBase):
    pass


class FeatureUpdate(BaseModel):
    geometry: Optional[Dict[str, Any]] = None
    properties: Optional[Dict[str, Any]] = None


class FeatureResponse(FeatureBase):
    id: int
    layer_id: int
    created_at: datetime
    updated_at: datetime
    created_by: Optional[int] = None
    version: int
    
    class Config:
        from_attributes = True


# Comment schemas
class CommentBase(BaseModel):
    content: str


class CommentCreate(CommentBase):
    pass


class CommentUpdate(BaseModel):
    content: Optional[str] = None
    is_resolved: Optional[bool] = None


class CommentResponse(CommentBase):
    id: int
    feature_id: Optional[int] = None
    user_id: int
    created_at: datetime
    updated_at: datetime
    is_resolved: bool
    
    class Config:
        from_attributes = True


# Edit history schemas
class EditHistoryResponse(BaseModel):
    id: int
    feature_id: int
    layer_id: int
    user_id: int
    action: str
    edited_at: datetime
    
    class Config:
        from_attributes = True


# Geoprocessing schemas
class BufferRequest(BaseModel):
    layer_id: int
    distance: float
    segments: int = 8
    output_layer_name: Optional[str] = None


class IntersectRequest(BaseModel):
    layer_ids: List[int]
    output_layer_name: Optional[str] = None


class UnionRequest(BaseModel):
    layer_ids: List[int]
    output_layer_name: Optional[str] = None
