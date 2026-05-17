from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey, Boolean, Text, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from geoalchemy2 import Geometry
from datetime import datetime

Base = declarative_base()


class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    projects = relationship("Project", back_populates="owner", cascade="all, delete-orphan")
    project_memberships = relationship("ProjectMember", back_populates="user", cascade="all, delete-orphan")
    edits = relationship("EditHistory", back_populates="user", cascade="all, delete-orphan")
    comments = relationship("Comment", back_populates="user", cascade="all, delete-orphan")


class Project(Base):
    __tablename__ = "projects"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(Text)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_public = Column(Boolean, default=False)
    crs = Column(String, default="EPSG:3857")  # Coordinate Reference System
    
    # Relationships
    owner = relationship("User", back_populates="projects")
    layers = relationship("Layer", back_populates="project", cascade="all, delete-orphan")
    members = relationship("ProjectMember", back_populates="project", cascade="all, delete-orphan")


class ProjectMember(Base):
    __tablename__ = "project_members"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    role = Column(String, nullable=False)  # 'admin', 'editor', 'viewer'
    joined_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    project = relationship("Project", back_populates="members")
    user = relationship("User", back_populates="project_memberships")


class Layer(Base):
    __tablename__ = "layers"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    name = Column(String, nullable=False)
    layer_type = Column(String, nullable=False)  # 'vector', 'raster', 'wms', 'wfs', 'xyz'
    source_type = Column(String, nullable=False)  # 'postgis', 'file', 'wms', 'wfs', 'xyz'
    source_config = Column(Text)  # JSON configuration for the data source
    style_config = Column(Text)  # JSON styling configuration
    visible = Column(Boolean, default=True)
    opacity = Column(Float, default=1.0)
    order_index = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    project = relationship("Project", back_populates="layers")
    features = relationship("Feature", back_populates="layer", cascade="all, delete-orphan")
    edits = relationship("EditHistory", back_populates="layer", cascade="all, delete-orphan")


class Feature(Base):
    __tablename__ = "features"
    
    id = Column(Integer, primary_key=True, index=True)
    layer_id = Column(Integer, ForeignKey("layers.id"), nullable=False)
    geometry = Column(Geometry(geometry_type="GEOMETRY", srid=3857))
    properties = Column(Text)  # JSON properties/attributes
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(Integer, ForeignKey("users.id"))
    version = Column(Integer, default=1)
    
    # Relationships
    layer = relationship("Layer", back_populates="features")
    edits = relationship("EditHistory", back_populates="feature", cascade="all, delete-orphan")
    comments = relationship("Comment", back_populates="feature", cascade="all, delete-orphan")


class EditHistory(Base):
    __tablename__ = "edit_history"
    
    id = Column(Integer, primary_key=True, index=True)
    feature_id = Column(Integer, ForeignKey("features.id"), nullable=False)
    layer_id = Column(Integer, ForeignKey("layers.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    action = Column(String, nullable=False)  # 'create', 'update', 'delete'
    old_geometry = Column(Geometry(geometry_type="GEOMETRY", srid=3857))
    new_geometry = Column(Geometry(geometry_type="GEOMETRY", srid=3857))
    old_properties = Column(Text)  # JSON
    new_properties = Column(Text)  # JSON
    edited_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    feature = relationship("Feature", back_populates="edits")
    layer = relationship("Layer", back_populates="edits")
    user = relationship("User", back_populates="edits")


class Comment(Base):
    __tablename__ = "comments"
    
    id = Column(Integer, primary_key=True, index=True)
    feature_id = Column(Integer, ForeignKey("features.id"))
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_resolved = Column(Boolean, default=False)
    
    # Relationships
    feature = relationship("Feature", back_populates="comments")
    user = relationship("User", back_populates="comments")


class Lock(Base):
    __tablename__ = "locks"
    
    id = Column(Integer, primary_key=True, index=True)
    feature_id = Column(Integer, ForeignKey("features.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    locked_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=False)
    
    # Prevent multiple users from editing the same feature simultaneously


# Database connection setup
engine = None
SessionLocal = None


def init_db(database_url: str):
    global engine, SessionLocal
    engine = create_engine(database_url)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
