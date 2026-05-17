# GIS Platform - Web-based QGIS Alternative with Multi-user Support

## Overview
This project is a web-based Geographic Information System (GIS) platform inspired by QGIS functionality with multi-user collaboration capabilities, similar to the example shown at https://sush.nextgis.com/resource/65/display?panel=layers.

## 🚀 Quick Deploy

### One-command deployment:

```bash
./deploy.sh dev    # For development
./deploy.sh prod   # For production
```

### Manual deployment:

```bash
# 1. Configure environment
cp .env.example .env
nano .env  # Edit passwords and settings

# 2. Generate secret key
openssl rand -hex 32  # Add to .env as SECRET_KEY

# 3. Start all services
docker-compose up -d --build

# 4. Check status
docker-compose ps

# 5. View logs
docker-compose logs -f
```

## 📍 Access Points

After deployment, services are available at:

- **Frontend**: http://localhost
- **Backend API**: http://localhost/api
- **API Documentation**: http://localhost/api/docs
- **GeoServer**: http://localhost/geoserver (admin / your password from .env)
- **Database**: localhost:5432 (internal only in production)

## Architecture

### Backend (Python/FastAPI + PostgreSQL/PostGIS)
- **FastAPI**: Modern async web framework for API development
- **PostgreSQL + PostGIS**: Spatial database for storing geographic data
- **GeoServer**: Map tile server for rendering layers (WMS/WFS)
- **Redis**: Caching and task queue broker
- **JWT Authentication**: Secure user authentication and authorization
- **Nginx**: Reverse proxy, load balancing, SSL termination

### Frontend (React + OpenLayers)
- **React 18**: Modern UI framework
- **OpenLayers 7**: Professional mapping library with full GIS capabilities
- **Redux Toolkit**: State management for multi-user synchronization
- **WebSocket**: Real-time collaboration features
- **Material-UI**: Component library for consistent UI

### Infrastructure
- **Docker & Docker Compose**: Container orchestration
- **Nginx**: Reverse proxy, static file serving, rate limiting
- **PostgreSQL + PostGIS**: Spatial database
- **Redis**: Caching layer
- **GeoServer**: OGC-compliant map server

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
├── nginx/                  # Nginx configuration
│   ├── nginx.conf
│   └── ssl/                # SSL certificates
├── docs/                   # Documentation
│   ├── QUICKSTART.md
│   ├── DEPLOYMENT.md
│   └── CI_CD.md
├── docker-compose.yml      # Docker orchestration
├── .env.example            # Environment variables template
└── deploy.sh               # Deployment script
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
   # Edit .env with your settings
   ```

3. Generate secret key:
   ```bash
   openssl rand -hex 32
   # Add to .env as SECRET_KEY
   ```

4. Run deployment script:
   ```bash
   ./deploy.sh dev    # For development
   ./deploy.sh prod   # For production
   ```

   Or start manually:
   ```bash
   docker-compose up -d --build
   ```

5. Access the application:
   - Frontend: http://localhost
   - Backend API: http://localhost/api
   - API Docs: http://localhost/api/docs
   - GeoServer: http://localhost/geoserver

## Documentation

- **[DEPLOYMENT.md](DEPLOYMENT.md)** - Detailed deployment instructions for production
- **[CI_CD.md](CI_CD.md)** - CI/CD configuration and automation
- **[docs/QUICKSTART.md](docs/QUICKSTART.md)** - Quick start guide for developers

## Security Checklist for Production

- [ ] Change all default passwords in `.env`
- [ ] Generate secure SECRET_KEY
- [ ] Configure SSL/TLS certificates
- [ ] Set up firewall rules
- [ ] Enable rate limiting (configured in nginx)
- [ ] Configure regular backups
- [ ] Set up monitoring and alerts
- [ ] Update Docker images regularly
- [ ] Restrict database access to internal network only
- [ ] Enable audit logging

## Troubleshooting

### Common Issues

**Container won't start:**
```bash
docker-compose logs <service_name>
docker stats  # Check resource usage
```

**Database connection issues:**
```bash
docker-compose exec db pg_isready -U qgis_admin
docker-compose restart db
```

**GeoServer unavailable:**
```bash
docker stats geoserver  # Check memory usage
# Increase memory allocation if needed
```

### Support

For issues and questions:
1. Check logs: `docker-compose logs -f`
2. Verify environment variables in `.env`
3. Check port availability
4. Ensure sufficient system resources (CPU, RAM, disk)

Additional resources:
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [PostGIS Documentation](https://postgis.net/documentation/)
- [GeoServer Documentation](https://docs.geoserver.org/)
- [Nginx Documentation](https://nginx.org/en/docs/)
- [OpenLayers Documentation](https://openlayers.org/doc/)

## License
MIT License

## Contributing
Contributions are welcome! Please read our contributing guidelines before submitting PRs.
