from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.models.database import get_db, Layer, Feature, User, EditHistory, Lock, Comment
from app.schemas import (
    FeatureCreate,
    FeatureUpdate,
    FeatureResponse,
    CommentCreate,
    CommentResponse,
    BufferRequest
)
from app.utils.security import oauth2_scheme, decode_access_token
from datetime import datetime, timedelta
import json

router = APIRouter(prefix="/api/features", tags=["Features"])


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


@router.get("/layer/{layer_id}", response_model=List[FeatureResponse])
def get_layer_features(
    layer_id: int,
    skip: int = 0,
    limit: int = 1000,
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    """Get all features in a layer."""
    current_user = get_current_user_from_token(token, db)
    
    layer = db.query(Layer).filter(Layer.id == layer_id).first()
    if not layer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Layer not found"
        )
    
    # Check project access
    project = db.query(Layer).filter(Layer.id == layer_id).first().project
    if project.owner_id != current_user.id and not project.is_public:
        membership = db.query(ProjectMember).filter(
            ProjectMember.project_id == project.id,
            ProjectMember.user_id == current_user.id
        ).first()
        
        if not membership:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have access to this layer"
            )
    
    features = db.query(Feature).filter(Feature.layer_id == layer_id).offset(skip).limit(limit).all()
    
    return features


@router.post("/layer/{layer_id}", response_model=FeatureResponse, status_code=status.HTTP_201_CREATED)
def create_feature(
    layer_id: int,
    feature_data: FeatureCreate,
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    """Create a new feature in a layer."""
    current_user = get_current_user_from_token(token, db)
    
    layer = db.query(Layer).filter(Layer.id == layer_id).first()
    if not layer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Layer not found"
        )
    
    # Check edit permissions
    project = layer.project
    if project.owner_id != current_user.id:
        membership = db.query(ProjectMember).filter(
            ProjectMember.project_id == project.id,
            ProjectMember.user_id == current_user.id
        ).first()
        
        if not membership or membership.role == "viewer":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to edit this layer"
            )
    
    # Create WKT geometry from GeoJSON
    from shapely.geometry import shape
    from shapely.wkt import dumps
    
    try:
        geom_obj = shape(feature_data.geometry)
        wkt_geometry = dumps(geom_obj)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid geometry: {str(e)}"
        )
    
    db_feature = Feature(
        layer_id=layer_id,
        geometry=wkt_geometry,
        properties=json.dumps(feature_data.properties) if feature_data.properties else None,
        created_by=current_user.id
    )
    
    db.add(db_feature)
    db.commit()
    db.refresh(db_feature)
    
    # Record edit history
    edit_history = EditHistory(
        feature_id=db_feature.id,
        layer_id=layer_id,
        user_id=current_user.id,
        action="create",
        new_geometry=wkt_geometry,
        new_properties=db_feature.properties
    )
    db.add(edit_history)
    db.commit()
    
    return db_feature


@router.put("/{feature_id}", response_model=FeatureResponse)
def update_feature(
    feature_id: int,
    feature_data: FeatureUpdate,
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    """Update an existing feature."""
    current_user = get_current_user_from_token(token, db)
    
    feature = db.query(Feature).filter(Feature.id == feature_id).first()
    if not feature:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Feature not found"
        )
    
    # Check edit permissions
    layer = feature.layer
    project = layer.project
    
    if project.owner_id != current_user.id:
        membership = db.query(ProjectMember).filter(
            ProjectMember.project_id == project.id,
            ProjectMember.user_id == current_user.id
        ).first()
        
        if not membership or membership.role == "viewer":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to edit this feature"
            )
    
    # Check if feature is locked by another user
    active_lock = db.query(Lock).filter(
        Lock.feature_id == feature_id,
        Lock.expires_at > datetime.utcnow()
    ).first()
    
    if active_lock and active_lock.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_423_LOCKED,
            detail="Feature is locked by another user"
        )
    
    # Update fields
    old_geometry = feature.geometry
    old_properties = feature.properties
    
    if feature_data.geometry:
        from shapely.geometry import shape
        from shapely.wkt import dumps
        
        try:
            geom_obj = shape(feature_data.geometry)
            feature.geometry = dumps(geom_obj)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid geometry: {str(e)}"
            )
    
    if feature_data.properties is not None:
        feature.properties = json.dumps(feature_data.properties)
    
    feature.updated_at = datetime.utcnow()
    feature.version += 1
    
    db.commit()
    db.refresh(feature)
    
    # Record edit history
    edit_history = EditHistory(
        feature_id=feature_id,
        layer_id=layer.id,
        user_id=current_user.id,
        action="update",
        old_geometry=old_geometry,
        new_geometry=feature.geometry,
        old_properties=old_properties,
        new_properties=feature.properties
    )
    db.add(edit_history)
    db.commit()
    
    return feature


@router.delete("/{feature_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_feature(
    feature_id: int,
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    """Delete a feature."""
    current_user = get_current_user_from_token(token, db)
    
    feature = db.query(Feature).filter(Feature.id == feature_id).first()
    if not feature:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Feature not found"
        )
    
    # Check edit permissions
    layer = feature.layer
    project = layer.project
    
    if project.owner_id != current_user.id:
        membership = db.query(ProjectMember).filter(
            ProjectMember.project_id == project.id,
            ProjectMember.user_id == current_user.id
        ).first()
        
        if not membership or membership.role == "viewer":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to delete this feature"
            )
    
    db.delete(feature)
    db.commit()
    
    return None


@router.post("/{feature_id}/lock")
def lock_feature(
    feature_id: int,
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    """Lock a feature for editing."""
    current_user = get_current_user_from_token(token, db)
    
    # Check if feature exists
    feature = db.query(Feature).filter(Feature.id == feature_id).first()
    if not feature:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Feature not found"
        )
    
    # Remove expired locks
    db.query(Lock).filter(
        Lock.feature_id == feature_id,
        Lock.expires_at < datetime.utcnow()
    ).delete()
    
    # Check if already locked
    active_lock = db.query(Lock).filter(
        Lock.feature_id == feature_id,
        Lock.expires_at > datetime.utcnow()
    ).first()
    
    if active_lock:
        if active_lock.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_423_LOCKED,
                detail="Feature is locked by another user"
            )
        # Already locked by current user, extend lock
        active_lock.expires_at = datetime.utcnow() + timedelta(minutes=30)
        db.commit()
        return {"message": "Lock extended", "expires_at": active_lock.expires_at}
    
    # Create new lock
    new_lock = Lock(
        feature_id=feature_id,
        user_id=current_user.id,
        expires_at=datetime.utcnow() + timedelta(minutes=30)
    )
    db.add(new_lock)
    db.commit()
    
    return {"message": "Feature locked", "expires_at": new_lock.expires_at}


@router.post("/{feature_id}/unlock")
def unlock_feature(
    feature_id: int,
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    """Unlock a feature."""
    current_user = get_current_user_from_token(token, db)
    
    lock = db.query(Lock).filter(
        Lock.feature_id == feature_id,
        Lock.user_id == current_user.id,
        Lock.expires_at > datetime.utcnow()
    ).first()
    
    if not lock:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No active lock found for this feature"
        )
    
    db.delete(lock)
    db.commit()
    
    return {"message": "Feature unlocked"}


@router.get("/{feature_id}/comments", response_model=List[CommentResponse])
def get_feature_comments(
    feature_id: int,
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    """Get all comments for a feature."""
    current_user = get_current_user_from_token(token, db)
    
    feature = db.query(Feature).filter(Feature.id == feature_id).first()
    if not feature:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Feature not found"
        )
    
    comments = db.query(Comment).filter(Comment.feature_id == feature_id).all()
    
    return comments


@router.post("/{feature_id}/comments", response_model=CommentResponse, status_code=status.HTTP_201_CREATED)
def add_comment_to_feature(
    feature_id: int,
    comment_data: CommentCreate,
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    """Add a comment to a feature."""
    current_user = get_current_user_from_token(token, db)
    
    feature = db.query(Feature).filter(Feature.id == feature_id).first()
    if not feature:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Feature not found"
        )
    
    db_comment = Comment(
        feature_id=feature_id,
        user_id=current_user.id,
        content=comment_data.content
    )
    
    db.add(db_comment)
    db.commit()
    db.refresh(db_comment)
    
    return db_comment
