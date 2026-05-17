# GIS Platform - Quick Start Guide

## Overview
This is a web-based GIS platform with QGIS-like functionality and multi-user collaboration support, inspired by NextGIS Web.

## Architecture
- **Backend**: FastAPI (Python) + PostgreSQL/PostGIS
- **Frontend**: React + OpenLayers + Material-UI
- **Map Server**: GeoServer for WMS/WFS services
- **Cache**: Redis for session management and task queues

## Quick Start

### Option 1: Docker Compose (Recommended)

1. **Start all services**:
   ```bash
   cd /workspace
   docker-compose up -d
   ```

2. **Access the application**:
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs
   - GeoServer: http://localhost:8080/geoserver

3. **Stop services**:
   ```bash
   docker-compose down
   ```

### Option 2: Local Development

#### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export POSTGRES_HOST=localhost
export POSTGRES_USER=postgres
export POSTGRES_PASSWORD=postgres
export POSTGRES_DB=gis_platform

# Run the server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm start
```

#### Database Setup

You need PostgreSQL with PostGIS extension:

```bash
# Using Docker
docker run -d --name postgres-gis \
  -e POSTGRES_PASSWORD=postgres \
  -e POSTGRES_DB=gis_platform \
  -p 5432:5432 \
  postgis/postgis:15-3.3
```

## Features Implemented

### Authentication & Authorization
- User registration and login
- JWT token-based authentication
- Role-based access control (Admin, Editor, Viewer)
- Protected routes in frontend

### Project Management
- Create, read, update, delete projects
- Public/private project sharing
- Project members with different roles
- Layer management within projects

### Map Functionality
- OpenStreetMap base layer
- Vector layer support (points, lines, polygons)
- Draw tools (point, line, polygon)
- Edit and delete features
- Layer visibility toggle
- Layer ordering

### Multi-user Collaboration
- Feature locking to prevent edit conflicts
- Edit history tracking
- Comments on features
- Real-time permission checks

### Geoprocessing
- Distance measurement
- Area measurement
- Buffer operation (basic)
- Intersection and union (placeholders for PostGIS implementation)

## API Endpoints

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login
- `GET /api/auth/me` - Get current user

### Projects
- `GET /api/projects` - List projects
- `POST /api/projects` - Create project
- `GET /api/projects/{id}` - Get project
- `PUT /api/projects/{id}` - Update project
- `DELETE /api/projects/{id}` - Delete project
- `GET /api/projects/{id}/layers` - Get layers
- `POST /api/projects/{id}/layers` - Add layer

### Features
- `GET /api/features/layer/{layer_id}` - Get features
- `POST /api/features/layer/{layer_id}` - Create feature
- `PUT /api/features/{id}` - Update feature
- `DELETE /api/features/{id}` - Delete feature
- `POST /api/features/{id}/lock` - Lock feature
- `POST /api/features/{id}/unlock` - Unlock feature
- `GET /api/features/{id}/comments` - Get comments
- `POST /api/features/{id}/comments` - Add comment

### Geoprocessing
- `GET /api/geoprocess/measure/distance` - Measure distance
- `GET /api/geoprocess/measure/area` - Measure area
- `POST /api/geoprocess/buffer` - Buffer operation
- `POST /api/geoprocess/intersect` - Intersect operation
- `POST /api/geoprocess/union` - Union operation

## File Structure

```
/workspace
├── README.md                 # Project documentation
├── docker-compose.yml        # Docker orchestration
├── backend/
│   ├── app/
│   │   ├── api/             # API endpoints
│   │   │   ├── auth.py
│   │   │   ├── projects.py
│   │   │   ├── features.py
│   │   │   └── geoprocessing.py
│   │   ├── models/          # Database models
│   │   │   └── database.py
│   │   ├── schemas/         # Pydantic schemas
│   │   │   └── schemas.py
│   │   ├── utils/           # Utilities
│   │   │   └── security.py
│   │   ├── config.py        # Configuration
│   │   └── main.py          # Application entry
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── components/      # React components
│   │   │   ├── Login.tsx
│   │   │   ├── Register.tsx
│   │   │   ├── MainLayout.tsx
│   │   │   ├── MapComponent.tsx
│   │   │   └── LayerPanel.tsx
│   │   ├── store/           # Redux store
│   │   │   ├── store.ts
│   │   │   ├── authSlice.ts
│   │   │   ├── projectSlice.ts
│   │   │   └── mapSlice.ts
│   │   ├── services/        # API services
│   │   │   └── api.ts
│   │   ├── App.tsx
│   │   └── index.tsx
│   ├── package.json
│   └── Dockerfile
└── database/
    └── init.sql             # Database initialization
```

## Next Steps for Production

1. **Security**
   - Change default SECRET_KEY in production
   - Use HTTPS/TLS
   - Implement rate limiting
   - Add input validation and sanitization

2. **Performance**
   - Implement spatial indexing on geometry columns
   - Add caching for frequently accessed data
   - Use CDN for static assets
   - Optimize database queries

3. **Features to Add**
   - File upload (Shapefile, GeoJSON, KML)
   - Advanced styling editor
   - Print layout/export
   - Advanced geoprocessing with PostGIS
   - WebSocket for real-time collaboration
   - Search and query tools
   - Basemap selector
   - Coordinate system transformation

4. **Deployment**
   - Configure production database
   - Set up monitoring and logging
   - Configure backup strategy
   - Set up CI/CD pipeline

## License
MIT License

## Support
For issues and questions, please create an issue in the repository.
