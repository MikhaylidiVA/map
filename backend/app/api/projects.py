from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.models.database import get_db, Project, ProjectMember, User, Layer
from app.schemas import (
    ProjectCreate, 
    ProjectUpdate, 
    ProjectResponse,
    ProjectMemberCreate,
    ProjectMemberResponse,
    LayerCreate,
    LayerResponse
)
from app.utils.security import oauth2_scheme, decode_access_token

router = APIRouter(prefix="/api/projects", tags=["Projects"])


def get_current_user_from_token(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    """Helper to get current user from token."""
    token_data = decode_access_token(token)
    if token_data is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user = db.query(User).filter(User.username == token_data.username).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return user


@router.get("", response_model=List[ProjectResponse])
def list_projects(
    skip: int = 0,
    limit: int = 100,
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    """List all projects accessible by the current user."""
    current_user = get_current_user_from_token(token, db)
    
    # Get projects owned by user or where user is a member
    owned_projects = db.query(Project).filter(Project.owner_id == current_user.id)
    
    member_project_ids = db.query(ProjectMember.project_id).filter(
        ProjectMember.user_id == current_user.id
    )
    member_projects = db.query(Project).filter(Project.id.in_(member_project_ids))
    
    # Also include public projects
    public_projects = db.query(Project).filter(Project.is_public == True)
    
    all_projects = owned_projects.union(member_projects).union(public_projects).offset(skip).limit(limit).all()
    
    return all_projects


@router.post("", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
def create_project(
    project_data: ProjectCreate,
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    """Create a new project."""
    current_user = get_current_user_from_token(token, db)
    
    db_project = Project(
        name=project_data.name,
        description=project_data.description,
        owner_id=current_user.id,
        is_public=project_data.is_public,
        crs=project_data.crs
    )
    
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    
    # Add creator as admin member
    membership = ProjectMember(
        project_id=db_project.id,
        user_id=current_user.id,
        role="admin"
    )
    db.add(membership)
    db.commit()
    
    return db_project


@router.get("/{project_id}", response_model=ProjectResponse)
def get_project(
    project_id: int,
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    """Get project details."""
    current_user = get_current_user_from_token(token, db)
    
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    # Check access
    if project.owner_id != current_user.id and not project.is_public:
        membership = db.query(ProjectMember).filter(
            ProjectMember.project_id == project_id,
            ProjectMember.user_id == current_user.id
        ).first()
        
        if not membership:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have access to this project"
            )
    
    return project


@router.put("/{project_id}", response_model=ProjectResponse)
def update_project(
    project_id: int,
    project_data: ProjectUpdate,
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    """Update project."""
    current_user = get_current_user_from_token(token, db)
    
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    # Check if user is owner or admin
    if project.owner_id != current_user.id:
        membership = db.query(ProjectMember).filter(
            ProjectMember.project_id == project_id,
            ProjectMember.user_id == current_user.id,
            ProjectMember.role == "admin"
        ).first()
        
        if not membership:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only project owner or admin can update the project"
            )
    
    # Update fields
    update_data = project_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(project, field, value)
    
    db.commit()
    db.refresh(project)
    
    return project


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(
    project_id: int,
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    """Delete project."""
    current_user = get_current_user_from_token(token, db)
    
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    # Only owner can delete
    if project.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only project owner can delete the project"
        )
    
    db.delete(project)
    db.commit()
    
    return None


@router.get("/{project_id}/layers", response_model=List[LayerResponse])
def get_project_layers(
    project_id: int,
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    """Get all layers in a project."""
    current_user = get_current_user_from_token(token, db)
    
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    layers = db.query(Layer).filter(Layer.project_id == project_id).order_by(Layer.order_index).all()
    
    return layers


@router.post("/{project_id}/layers", response_model=LayerResponse, status_code=status.HTTP_201_CREATED)
def add_layer_to_project(
    project_id: int,
    layer_data: LayerCreate,
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    """Add a new layer to project."""
    current_user = get_current_user_from_token(token, db)
    
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    # Check if user has edit permissions
    if project.owner_id != current_user.id:
        membership = db.query(ProjectMember).filter(
            ProjectMember.project_id == project_id,
            ProjectMember.user_id == current_user.id
        ).first()
        
        if not membership or membership.role == "viewer":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to add layers"
            )
    
    import json
    db_layer = Layer(
        project_id=project_id,
        name=layer_data.name,
        layer_type=layer_data.layer_type,
        source_type=layer_data.source_type,
        source_config=json.dumps(layer_data.source_config) if layer_data.source_config else None,
        style_config=json.dumps(layer_data.style_config) if layer_data.style_config else None,
        visible=layer_data.visible,
        opacity=layer_data.opacity,
        order_index=layer_data.order_index
    )
    
    db.add(db_layer)
    db.commit()
    db.refresh(db_layer)
    
    return db_layer
