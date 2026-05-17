import React, { useState } from 'react';
import { useSelector, useDispatch } from 'react-redux';
import { RootState, AppDispatch } from '../store/store';
import { updateLayerVisibility, addLayer } from '../store/projectSlice';
import { projectService } from '../services/api';

import {
  Box,
  Paper,
  Typography,
  List,
  ListItem,
  ListItemText,
  ListItemSecondaryAction,
  IconButton,
  Checkbox,
  Slider,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
} from '@mui/material';
import {
  Visibility,
  VisibilityOff,
  Add as AddIcon,
  Layers as LayersIcon,
} from '@mui/icons-material';

const LayerPanel: React.FC = () => {
  const dispatch = useDispatch<AppDispatch>();
  const { layers, currentProject } = useSelector((state: RootState) => state.projects);
  
  const [dialogOpen, setDialogOpen] = useState(false);
  const [newLayerName, setNewLayerName] = useState('');
  const [newLayerType, setNewLayerType] = useState('vector');

  const handleToggleVisibility = (layerId: number, visible: boolean) => {
    dispatch(updateLayerVisibility({ id: layerId, visible: !visible }));
  };

  const handleAddLayer = async () => {
    if (!currentProject || !newLayerName) return;

    try {
      const layerData = {
        name: newLayerName,
        layer_type: newLayerType,
        source_type: newLayerType === 'wms' ? 'wms' : 'postgis',
        visible: true,
        opacity: 1.0,
        order_index: layers.length,
        source_config: {},
        style_config: {},
      };

      const newLayer = await projectService.addLayer(currentProject.id, layerData);
      dispatch(addLayer(newLayer));
      setDialogOpen(false);
      setNewLayerName('');
    } catch (error) {
      console.error('Failed to add layer:', error);
      alert('Failed to add layer');
    }
  };

  if (!currentProject) {
    return (
      <Paper sx={{ p: 2, height: '100%' }}>
        <Typography variant="body2" color="text.secondary">
          Select a project to view layers
        </Typography>
      </Paper>
    );
  }

  return (
    <Paper sx={{ p: 2, height: '100%', overflow: 'auto' }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
        <Typography variant="h6">Layers</Typography>
        <IconButton onClick={() => setDialogOpen(true)} color="primary">
          <AddIcon />
        </IconButton>
      </Box>

      {layers.length === 0 ? (
        <Typography variant="body2" color="text.secondary">
          No layers yet. Click + to add a layer.
        </Typography>
      ) : (
        <List dense>
          {layers.map((layer) => (
            <ListItem key={layer.id}>
              <ListItemIcon>
                <LayersIcon fontSize="small" />
              </ListItemIcon>
              <ListItemText 
                primary={layer.name} 
                secondary={`${layer.layer_type} • ${layer.source_type}`}
              />
              <ListItemSecondaryAction>
                <IconButton
                  edge="end"
                  onClick={() => handleToggleVisibility(layer.id, layer.visible)}
                  size="small"
                >
                  {layer.visible ? <Visibility fontSize="small" /> : <VisibilityOff fontSize="small" />}
                </IconButton>
              </ListItemSecondaryAction>
            </ListItem>
          ))}
        </List>
      )}

      <Dialog open={dialogOpen} onClose={() => setDialogOpen(false)}>
        <DialogTitle>Add New Layer</DialogTitle>
        <DialogContent>
          <TextField
            autoFocus
            margin="dense"
            label="Layer Name"
            fullWidth
            value={newLayerName}
            onChange={(e) => setNewLayerName(e.target.value)}
          />
          <TextField
            select
            margin="dense"
            label="Layer Type"
            fullWidth
            value={newLayerType}
            onChange={(e) => setNewLayerType(e.target.value)}
            SelectProps={{ native: true }}
          >
            <option value="vector">Vector</option>
            <option value="raster">Raster</option>
            <option value="wms">WMS</option>
            <option value="xyz">XYZ Tiles</option>
          </TextField>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDialogOpen(false)}>Cancel</Button>
          <Button onClick={handleAddLayer} variant="contained">
            Add Layer
          </Button>
        </DialogActions>
      </Dialog>
    </Paper>
  );
};

export default LayerPanel;
