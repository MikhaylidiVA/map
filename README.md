# GIS Platform - Web-based QGIS Alternative with Multi-user Support

## Overview
This project is a web-based Geographic Information System (GIS) platform inspired by QGIS functionality with multi-user collaboration capabilities, similar to the example shown at https://sush.nextgis.com/resource/65/display?panel=layers.

## Architecture

### Backend (Python/FastAPI + PostgreSQL/PostGIS)
- **FastAPI**: Modern async web framework for API development
- **PostgreSQL + PostGIS**: Spatial database for storing geographic data
- **GeoServer/MapServer**: Map tile server for rendering layers
- **Celery + Redis**: Task queue for heavy processing operations
- **JWT Authentication**: Secure user authentication and authorization

### Frontend (React + OpenLayers/Leaflet)
- **React**: Modern UI framework
- **OpenLayers**: Professional mapping library with full GIS capabilities
- **Redux**: State management for multi-user synchronization
- **WebSocket**: Real-time collaboration features
- **Material-UI**: Component library for consistent UI

### Database Schema
- Users and roles management
- Projects and workspaces
- Layers (vector, raster, WMS, WFS)
- Editing sessions and versioning
- Comments and annotations

## Features

### Core GIS Functionality
- [x] Map visualization with multiple layer support
- [x] Layer management (add, remove, reorder, styling)
- [x] Vector data editing (points, lines, polygons)
- [x] Attribute table viewing and editing
- [x] Spatial queries and filtering
- [x] Measurement tools (distance, area)
- [x] Coordinate system support (reprojection)
- [x] Print layout and export (PDF, PNG)
- [x] Geoprocessing tools (buffer, intersect, union, etc.)

### Multi-user Collaboration
- [x] User authentication and authorization
- [x] Role-based access control (Admin, Editor, Viewer)
- [x] Real-time collaborative editing
- [x] Version control for spatial data
- [x] Edit locking to prevent conflicts
- [x] Change tracking and history
- [x] Comments and annotations on features
- [x] Shared projects and workspaces

### Data Sources
- [x] PostGIS databases
- [x] GeoJSON, KML, GPX, Shapefile uploads
- [x] WMS/WFS/WMTS services
- [x] XYZ tile layers (OpenStreetMap, Satellite, etc.)
- [x] GeoPackage support

## Project Structure

```
/workspace
├── backend/                 # FastAPI backend
│   ├── app/
│   │   ├── api/            # API endpoints
│   │   ├── models/         # SQLAlchemy models
│   │   ├── schemas/        # Pydantic schemas
│   │   ├── services/       # Business logic
│   │   ├── utils/          # Utilities
│   │   └── main.py         # Application entry point
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/               # React frontend
│   ├── src/
│   │   ├── components/     # React components
│   │   ├── store/          # Redux store
│   │   ├── services/       # API services
│   │   ├── hooks/          # Custom hooks
│   │   └── App.tsx
│   ├── package.json
│   └── Dockerfile
├── database/               # Database migrations and scripts
│   ├── migrations/
│   └── init.sql
├── docs/                   # Documentation
└── docker-compose.yml      # Docker orchestration
```

## Quick Start

### Prerequisites
- Docker and Docker Compose
- Node.js 18+ (for local frontend development)
- Python 3.10+ (for local backend development)

### Installation

1. Clone the repository
2. Configure environment variables:
   ```bash
   cp .env.example .env
   ```

3. Start all services:
   ```bash
   docker-compose up -d
   ```

4. Access the application:
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/docs

## API Endpoints

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login
- `POST /api/auth/logout` - Logout
- `GET /api/auth/me` - Get current user info

### Projects
- `GET /api/projects` - List all projects
- `POST /api/projects` - Create new project
- `GET /api/projects/{id}` - Get project details
- `PUT /api/projects/{id}` - Update project
- `DELETE /api/projects/{id}` - Delete project

### Layers
- `GET /api/projects/{project_id}/layers` - List layers
- `POST /api/projects/{project_id}/layers` - Add layer
- `PUT /api/layers/{id}` - Update layer properties
- `DELETE /api/layers/{id}` - Remove layer

### Features (Vector Data)
- `GET /api/layers/{layer_id}/features` - Get features
- `POST /api/layers/{layer_id}/features` - Create feature
- `PUT /api/features/{id}` - Update feature
- `DELETE /api/features/{id}` - Delete feature

### Geoprocessing
- `POST /api/geoprocess/buffer` - Buffer operation
- `POST /api/geoprocess/intersect` - Intersect operation
- `POST /api/geoprocess/union` - Union operation

## Technology Stack

### Backend
- Python 3.10+
- FastAPI
- SQLAlchemy + GeoAlchemy2
- PostgreSQL + PostGIS
- Celery
- Redis
- GeoServer

### Frontend
- React 18
- TypeScript
- OpenLayers 7
- Redux Toolkit
- Material-UI
- Axios

### DevOps
- Docker & Docker Compose
- Nginx
- GitHub Actions (CI/CD)

## License
MIT License

## Contributing
Contributions are welcome! Please read our contributing guidelines before submitting PRs.
