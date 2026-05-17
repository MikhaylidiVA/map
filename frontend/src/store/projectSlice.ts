import { createSlice, PayloadAction } from '@reduxjs/toolkit';

interface Project {
  id: number;
  name: string;
  description: string | null;
  owner_id: number;
  is_public: boolean;
  crs: string;
  created_at: string;
  updated_at: string;
}

interface Layer {
  id: number;
  name: string;
  layer_type: string;
  source_type: string;
  visible: boolean;
  opacity: number;
  order_index: number;
}

interface ProjectsState {
  projects: Project[];
  currentProject: Project | null;
  layers: Layer[];
  loading: boolean;
  error: string | null;
}

const initialState: ProjectsState = {
  projects: [],
  currentProject: null,
  layers: [],
  loading: false,
  error: null,
};

const projectSlice = createSlice({
  name: 'projects',
  initialState,
  reducers: {
    setProjects(state, action: PayloadAction<Project[]>) {
      state.projects = action.payload;
    },
    setCurrentProject(state, action: PayloadAction<Project | null>) {
      state.currentProject = action.payload;
    },
    setLayers(state, action: PayloadAction<Layer[]>) {
      state.layers = action.payload;
    },
    addLayer(state, action: PayloadAction<Layer>) {
      state.layers.push(action.payload);
    },
    updateLayerVisibility(state, action: PayloadAction<{ id: number; visible: boolean }>) {
      const layer = state.layers.find(l => l.id === action.payload.id);
      if (layer) {
        layer.visible = action.payload.visible;
      }
    },
    setLoading(state, action: PayloadAction<boolean>) {
      state.loading = action.payload;
    },
    setError(state, action: PayloadAction<string | null>) {
      state.error = action.payload;
    },
  },
});

export const {
  setProjects,
  setCurrentProject,
  setLayers,
  addLayer,
  updateLayerVisibility,
  setLoading,
  setError,
} = projectSlice.actions;

export default projectSlice.reducer;
