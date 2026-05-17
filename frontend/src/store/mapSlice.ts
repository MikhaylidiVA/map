import { createSlice, PayloadAction } from '@reduxjs/toolkit';

interface MapState {
  center: [number, number];
  zoom: number;
  layers: any[];
  selectedFeature: any | null;
  drawMode: string | null;
  measureMode: boolean;
}

const initialState: MapState = {
  center: [0, 0],
  zoom: 2,
  layers: [],
  selectedFeature: null,
  drawMode: null,
  measureMode: false,
};

const mapSlice = createSlice({
  name: 'map',
  initialState,
  reducers: {
    setCenter(state, action: PayloadAction<[number, number]>) {
      state.center = action.payload;
    },
    setZoom(state, action: PayloadAction<number>) {
      state.zoom = action.payload;
    },
    setMapLayers(state, action: PayloadAction<any[]>) {
      state.layers = action.payload;
    },
    setSelectedFeature(state, action: PayloadAction<any | null>) {
      state.selectedFeature = action.payload;
    },
    setDrawMode(state, action: PayloadAction<string | null>) {
      state.drawMode = action.payload;
    },
    toggleMeasureMode(state) {
      state.measureMode = !state.measureMode;
    },
    setMeasureMode(state, action: PayloadAction<boolean>) {
      state.measureMode = action.payload;
    },
  },
});

export const {
  setCenter,
  setZoom,
  setMapLayers,
  setSelectedFeature,
  setDrawMode,
  toggleMeasureMode,
  setMeasureMode,
} = mapSlice.actions;

export default mapSlice.reducer;
