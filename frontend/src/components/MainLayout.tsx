import React, { useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { useNavigate } from 'react-router-dom';
import { logout } from '../store/authSlice';
import { setProjects, setCurrentProject, setLayers } from '../store/projectSlice';
import { projectService } from '../services/api';
import { RootState, AppDispatch } from '../store/store';

import {
  Box,
  AppBar,
  Toolbar,
  Typography,
  IconButton,
  Drawer,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Button,
  Menu,
  MenuItem,
} from '@mui/material';
import {
  Map as MapIcon,
  Layers as LayersIcon,
  Folder as FolderIcon,
  AccountCircle,
  Logout,
  Add as AddIcon,
} from '@mui/icons-material';

import MapComponent from './MapComponent';
import LayerPanel from './LayerPanel';

const drawerWidth = 280;

const MainLayout: React.FC = () => {
  const dispatch = useDispatch<AppDispatch>();
  const navigate = useNavigate();
  const { user, isAuthenticated } = useSelector((state: RootState) => state.auth);
  const { projects, currentProject } = useSelector((state: RootState) => state.projects);
  
  const [anchorEl, setAnchorEl] = React.useState<null | HTMLElement>(null);
  const [mobileOpen, setMobileOpen] = React.useState(false);

  useEffect(() => {
    if (isAuthenticated) {
      loadProjects();
    }
  }, [isAuthenticated]);

  const loadProjects = async () => {
    try {
      const data = await projectService.getProjects();
      dispatch(setProjects(data));
    } catch (error) {
      console.error('Failed to load projects:', error);
    }
  };

  const handleLogout = () => {
    dispatch(logout());
    navigate('/login');
  };

  const handleMenuOpen = (event: React.MouseEvent<HTMLElement>) => {
    setAnchorEl(event.currentTarget);
  };

  const handleMenuClose = () => {
    setAnchorEl(null);
  };

  const handleCreateProject = async () => {
    const name = prompt('Enter project name:');
    if (name) {
      try {
        const newProject = await projectService.createProject(name);
        dispatch(setCurrentProject(newProject));
        const layers = await projectService.getLayers(newProject.id);
        dispatch(setLayers(layers));
      } catch (error) {
        console.error('Failed to create project:', error);
      }
    }
  };

  const handleSelectProject = async (project: any) => {
    dispatch(setCurrentProject(project));
    try {
      const layers = await projectService.getLayers(project.id);
      dispatch(setLayers(layers));
    } catch (error) {
      console.error('Failed to load layers:', error);
    }
  };

  const drawer = (
    <div>
      <Toolbar>
        <Typography variant="h6" noWrap>
          GIS Platform
        </Typography>
      </Toolbar>
      <List>
        <ListItem button onClick={handleCreateProject}>
          <ListItemIcon>
            <AddIcon />
          </ListItemIcon>
          <ListItemText primary="New Project" />
        </ListItem>
        <ListItem>
          <ListItemText primary="Projects" />
        </ListItem>
        {projects.map((project) => (
          <ListItem
            key={project.id}
            button
            selected={currentProject?.id === project.id}
            onClick={() => handleSelectProject(project)}
          >
            <ListItemIcon>
              <FolderIcon />
            </ListItemIcon>
            <ListItemText primary={project.name} />
          </ListItem>
        ))}
      </List>
    </div>
  );

  return (
    <Box sx={{ display: 'flex' }}>
      <AppBar
        position="fixed"
        sx={{
          width: { sm: `calc(100% - ${drawerWidth}px)` },
          ml: { sm: `${drawerWidth}px` },
        }}
      >
        <Toolbar>
          <IconButton
            color="inherit"
            edge="start"
            sx={{ mr: 2, display: { sm: 'none' } }}
            onClick={() => setMobileOpen(!mobileOpen)}
          >
            <LayersIcon />
          </IconButton>
          <Typography variant="h6" noWrap component="div" sx={{ flexGrow: 1 }}>
            {currentProject ? currentProject.name : 'Select a Project'}
          </Typography>
          <IconButton color="inherit" onClick={handleMenuOpen}>
            <AccountCircle />
          </IconButton>
          <Menu
            anchorEl={anchorEl}
            open={Boolean(anchorEl)}
            onClose={handleMenuClose}
          >
            <MenuItem disabled>{user?.username || 'User'}</MenuItem>
            <MenuItem onClick={handleLogout}>
              <ListItemIcon>
                <Logout fontSize="small" />
              </ListItemIcon>
              Logout
            </MenuItem>
          </Menu>
        </Toolbar>
      </AppBar>
      
      <Box
        component="nav"
        sx={{ width: { sm: drawerWidth }, flexShrink: { sm: 0 } }}
      >
        <Drawer
          variant="permanent"
          sx={{
            display: { xs: 'none', sm: 'block' },
            '& .MuiDrawer-paper': { boxSizing: 'border-box', width: drawerWidth },
          }}
          open
        >
          {drawer}
        </Drawer>
      </Box>
      
      <Box
        component="main"
        sx={{
          flexGrow: 1,
          p: 3,
          width: { sm: `calc(100% - ${drawerWidth}px)` },
          height: '100vh',
          overflow: 'auto',
        }}
      >
        <Toolbar />
        {currentProject ? (
          <Box sx={{ display: 'flex', height: 'calc(100vh - 64px)' }}>
            <Box sx={{ flex: 1, mr: 2 }}>
              <MapComponent />
            </Box>
            <Box sx={{ width: 300 }}>
              <LayerPanel />
            </Box>
          </Box>
        ) : (
          <Box sx={{ textAlign: 'center', mt: 8 }}>
            <MapIcon sx={{ fontSize: 80, color: 'text.secondary' }} />
            <Typography variant="h5" gutterBottom>
              Welcome to GIS Platform
            </Typography>
            <Typography variant="body1" color="text.secondary">
              Select a project from the sidebar or create a new one to get started
            </Typography>
            <Button
              variant="contained"
              startIcon={<AddIcon />}
              onClick={handleCreateProject}
              sx={{ mt: 2 }}
            >
              Create New Project
            </Button>
          </Box>
        )}
      </Box>
    </Box>
  );
};

export default MainLayout;
