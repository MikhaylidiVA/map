import React, { useEffect, useRef } from 'react';
import { useSelector, useDispatch } from 'react-redux';
import { Map, View, Feature } from 'ol';
import TileLayer from 'ol/layer/Tile';
import VectorLayer from 'ol/layer/Vector';
import OSM from 'ol/source/OSM';
import VectorSource from 'ol/source/Vector';
import GeoJSON from 'ol/format/GeoJSON';
import { fromLonLat } from 'ol/proj';
import { Draw, Modify, Select, Snap } from 'ol/interaction';
import { click as clickCondition } from 'ol/events/condition';

import { RootState, AppDispatch } from '../store/store';
import { setCenter, setZoom, setSelectedFeature, setDrawMode } from '../store/mapSlice';
import { featureService } from '../services/api';

import Box from '@mui/material/Box';
import Toolbar from '@mui/material/Toolbar';
import IconButton from '@mui/material/IconButton';
import Tooltip from '@mui/material/Tooltip';
import {
  AddLocation,
  Draw as DrawIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  Straighten,
  SquareFoot,
  PanTool,
} from '@mui/icons-material';

const MapComponent: React.FC = () => {
  const dispatch = useDispatch<AppDispatch>();
  const mapRef = useRef<HTMLDivElement>(null);
  const mapInstance = useRef<Map | null>(null);
  const vectorSource = useRef<VectorSource | null>(null);
  
  const { currentProject, layers } = useSelector((state: RootState) => state.projects);
  const { drawMode, measureMode } = useSelector((state: RootState) => state.map);

  useEffect(() => {
    if (!mapRef.current || mapInstance.current) return;

    // Initialize vector source
    vectorSource.current = new VectorSource({
      wrapX: false,
    });

    // Create base map layer (OpenStreetMap)
    const baseLayer = new TileLayer({
      source: new OSM(),
    });

    // Create vector layer for features
    const vectorLayer = new VectorLayer({
      source: vectorSource.current,
      style: {
        'circle-radius': 6,
        'circle-fill-color': '#3399CC',
        'stroke-width': 2,
        'stroke-color': '#3399CC',
        'fill-color': 'rgba(51, 153, 204, 0.3)',
      },
    });

    // Initialize map
    mapInstance.current = new Map({
      target: mapRef.current,
      layers: [baseLayer, vectorLayer],
      view: new View({
        center: fromLonLat([0, 0]),
        zoom: 2,
      }),
    });

    // Update store on map movement
    mapInstance.current.on('moveend', () => {
      const view = mapInstance.current!.getView();
      dispatch(setCenter(view.getCenter() as [number, number]));
      dispatch(setZoom(view.getZoom()!));
    });

    // Load features for all layers
    loadFeatures();

    return () => {
      if (mapInstance.current) {
        mapInstance.current.setTarget(undefined);
      }
    };
  }, []);

  const loadFeatures = async () => {
    if (!layers.length) return;
    
    try {
      vectorSource.current?.clear();
      
      for (const layer of layers) {
        if (layer.layer_type === 'vector') {
          const features = await featureService.getFeatures(layer.id);
          const geojsonFormat = new GeoJSON();
          
          features.forEach((feature: any) => {
            const olFeature = geojsonFormat.readFeature(feature, {
              featureProjection: 'EPSG:3857',
            });
            olFeature.setId(feature.id);
            vectorSource.current?.addFeature(olFeature);
          });
        }
      }
    } catch (error) {
      console.error('Failed to load features:', error);
    }
  };

  const handleDraw = (type: string) => {
    if (!mapInstance.current) return;

    // Remove existing interactions
    mapInstance.current.getInteractions().forEach((interaction) => {
      if (interaction instanceof Draw || interaction instanceof Modify || interaction instanceof Select) {
        mapInstance.current?.removeInteraction(interaction);
      }
    });

    if (type === 'none') {
      dispatch(setDrawMode(null));
      return;
    }

    const draw = new Draw({
      source: vectorSource.current!,
      type: type as any,
    });

    draw.on('drawend', async (evt) => {
      const feature = evt.feature;
      const geojsonFormat = new GeoJSON();
      const geojson = geojsonFormat.writeFeatureObject(feature, {
        featureProjection: 'EPSG:3857',
      });

      try {
        // Save to backend
        const layerId = layers[0]?.id; // Use first layer for now
        if (layerId) {
          await featureService.createFeature(layerId, geojson.geometry, geojson.properties);
        }
      } catch (error) {
        console.error('Failed to save feature:', error);
      }
    });

    mapInstance.current.addInteraction(draw);
    dispatch(setDrawMode(type));
  };

  const handleDelete = async () => {
    const selectedFeatures = vectorSource.current?.getFeatures().filter(f => f.get('selected'));
    if (!selectedFeatures || selectedFeatures.length === 0) {
      alert('No feature selected');
      return;
    }

    try {
      for (const feature of selectedFeatures) {
        const id = feature.getId();
        if (id) {
          await featureService.deleteFeature(id as number);
          vectorSource.current?.removeFeature(feature);
        }
      }
    } catch (error) {
      console.error('Failed to delete feature:', error);
    }
  };

  return (
    <Box sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      <Toolbar variant="dense" sx={{ bgcolor: 'background.paper', mb: 1 }}>
        <Tooltip title="Pan">
          <IconButton onClick={() => handleDraw('none')} color={drawMode === null ? 'primary' : 'default'}>
            <PanTool />
          </IconButton>
        </Tooltip>
        <Tooltip title="Draw Point">
          <IconButton onClick={() => handleDraw('Point')} color={drawMode === 'Point' ? 'primary' : 'default'}>
            <AddLocation />
          </IconButton>
        </Tooltip>
        <Tooltip title="Draw Line">
          <IconButton onClick={() => handleDraw('LineString')} color={drawMode === 'LineString' ? 'primary' : 'default'}>
            <Straighten />
          </IconButton>
        </Tooltip>
        <Tooltip title="Draw Polygon">
          <IconButton onClick={() => handleDraw('Polygon')} color={drawMode === 'Polygon' ? 'primary' : 'default'}>
            <SquareFoot />
          </IconButton>
        </Tooltip>
        <Tooltip title="Edit">
          <IconButton onClick={() => handleDraw('modify')} color={drawMode === 'modify' ? 'primary' : 'default'}>
            <EditIcon />
          </IconButton>
        </Tooltip>
        <Tooltip title="Delete Selected">
          <IconButton onClick={handleDelete} color="error">
            <DeleteIcon />
          </IconButton>
        </Tooltip>
      </Toolbar>
      <Box ref={mapRef} sx={{ flex: 1, bgcolor: '#e0e0e0' }} />
    </Box>
  );
};

export default MapComponent;
