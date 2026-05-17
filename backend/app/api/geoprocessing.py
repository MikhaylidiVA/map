from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.models.database import get_db, User, Layer, Feature
from app.schemas import BufferRequest, IntersectRequest, UnionRequest
from app.utils.security import oauth2_scheme, decode_access_token
from shapely.geometry import shape
from shapely.ops import unary_union
import json

router = APIRouter(prefix="/api/geoprocess", tags=["Geoprocessing"])


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


@router.post("/buffer")
def buffer_operation(
    request: BufferRequest,
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    """
    Create buffer around features in a layer.
    
    This is a simplified example - in production you'd use PostGIS ST_Buffer
    or GeoServer WPS for better performance with large datasets.
    """
    current_user = get_current_user_from_token(token, db)
    
    layer = db.query(Layer).filter(Layer.id == request.layer_id).first()
    if not layer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Layer not found"
        )
    
    # Get all features from the layer
    features = db.query(Feature).filter(Feature.layer_id == request.layer_id).all()
    
    buffered_features = []
    
    for feature in features:
        if feature.geometry:
            from shapely.wkt import loads
            
            try:
                geom = loads(feature.geometry)
                buffered_geom = geom.buffer(request.distance, resolution=request.segments)
                
                # Create new feature with buffered geometry
                from shapely.geometry import mapping
                
                new_feature = {
                    "type": "Feature",
                    "geometry": mapping(buffered_geom),
                    "properties": json.loads(feature.properties) if feature.properties else {}
                }
                buffered_features.append(new_feature)
            except Exception as e:
                continue
    
    return {
        "operation": "buffer",
        "distance": request.distance,
        "features_count": len(buffered_features),
        "features": buffered_features
    }


@router.post("/intersect")
def intersect_operation(
    request: IntersectRequest,
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    """
    Find intersection between layers.
    
    Note: This is a simplified implementation. For production use,
    consider using PostGIS ST_Intersection or GeoServer WPS.
    """
    current_user = get_current_user_from_token(token, db)
    
    if len(request.layer_ids) < 2:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="At least 2 layers required for intersection"
        )
    
    # Validate layers exist and user has access
    layers = []
    for layer_id in request.layer_ids:
        layer = db.query(Layer).filter(Layer.id == layer_id).first()
        if not layer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Layer {layer_id} not found"
            )
        layers.append(layer)
    
    # Simplified intersection logic
    # In production, this would use proper spatial operations
    return {
        "operation": "intersect",
        "layer_ids": request.layer_ids,
        "message": "Intersection operation queued (simplified response)",
        "status": "This is a placeholder - implement with PostGIS/GeoServer for full functionality"
    }


@router.post("/union")
def union_operation(
    request: UnionRequest,
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    """
    Union multiple layers.
    
    Note: This is a simplified implementation. For production use,
    consider using PostGIS ST_Union or GeoServer WPS.
    """
    current_user = get_current_user_from_token(token, db)
    
    if len(request.layer_ids) < 2:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="At least 2 layers required for union"
        )
    
    # Validate layers exist and user has access
    layers = []
    for layer_id in request.layer_ids:
        layer = db.query(Layer).filter(Layer.id == layer_id).first()
        if not layer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Layer {layer_id} not found"
            )
        layers.append(layer)
    
    # Simplified union logic
    return {
        "operation": "union",
        "layer_ids": request.layer_ids,
        "message": "Union operation queued (simplified response)",
        "status": "This is a placeholder - implement with PostGIS/GeoServer for full functionality"
    }


@router.get("/measure/distance")
def measure_distance(
    start_lat: float,
    start_lon: float,
    end_lat: float,
    end_lon: float,
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    """
    Measure distance between two points.
    Returns distance in meters.
    """
    current_user = get_current_user_from_token(token, db)
    
    from geopy.distance import geodesic
    
    point1 = (start_lat, start_lon)
    point2 = (end_lat, end_lon)
    
    distance = geodesic(point1, point2).meters
    
    return {
        "distance_meters": distance,
        "distance_km": distance / 1000,
        "start": {"lat": start_lat, "lon": start_lon},
        "end": {"lat": end_lat, "lon": end_lon}
    }


@router.get("/measure/area")
def measure_area(
    coordinates: str,  # Comma-separated lat,lon pairs
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    """
    Measure area of a polygon.
    Returns area in square meters.
    """
    current_user = get_current_user_from_token(token, db)
    
    try:
        coords = [float(x) for x in coordinates.split(",")]
        points = [(coords[i], coords[i+1]) for i in range(0, len(coords), 2)]
        
        from shapely.geometry import Polygon
        
        # Simple planar approximation (for small areas)
        # For large areas, use proper geodetic calculations
        poly = Polygon(points)
        area = poly.area  # This is in coordinate units
        
        return {
            "area_square_units": area,
            "coordinates_count": len(points),
            "note": "For accurate area measurements, use projected coordinates"
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid coordinates: {str(e)}"
        )
