import { useState, useEffect } from "react";
import axios from "axios";
import { toast } from "sonner";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import DataSourceSelector from "@/components/DataSourceSelector";
import DataProfiler from "@/components/DataProfiler";
import PredictiveAnalysis from "@/components/PredictiveAnalysis";
import VisualizationPanel from "@/components/VisualizationPanel";
import { Sparkles, ArrowLeft, Home, Trash2, ChevronDown, ChevronUp, Save, FolderOpen } from "lucide-react";
import { useNavigate } from "react-router-dom";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const DashboardPage = () => {
  const navigate = useNavigate();
  const [currentStep, setCurrentStep] = useState("data-source");
  const [selectedDataset, setSelectedDataset] = useState(null);
  const [datasets, setDatasets] = useState([]);
  const [showRecentDatasets, setShowRecentDatasets] = useState(true);
  
  // Lift analysis state to prevent re-analysis on tab switch
  const [predictiveAnalysisCache, setPredictiveAnalysisCache] = useState({});
  const [visualizationCache, setVisualizationCache] = useState({});
  const [dataProfilerCache, setDataProfilerCache] = useState({});
  
  // Save/Load state management
  const [showSaveDialog, setShowSaveDialog] = useState(false);
  const [stateName, setStateName] = useState("");
  const [savedStates, setSavedStates] = useState([]);
  const [showLoadDialog, setShowLoadDialog] = useState(false);

  useEffect(() => {
    loadDatasets();
  }, []);

  const loadDatasets = async () => {
    try {
      const response = await axios.get(`${API}/datasets`);
      setDatasets(response.data.datasets || []);
    } catch (error) {
      console.error("Failed to load datasets", error);
    }
  };

  const handleDatasetLoaded = (dataset) => {
    setSelectedDataset(dataset);
    loadDatasets();
    toast.success("Dataset loaded successfully!");
  };

  const handleDatasetSelect = (dataset) => {
    setSelectedDataset(dataset);
    setCurrentStep("analysis");
  };

  const deleteDataset = async (datasetId, event) => {
    event.stopPropagation(); // Prevent card click
    
    if (!confirm("Are you sure you want to delete this dataset?")) {
      return;
    }

    try {
      await axios.delete(`${API}/datasets/${datasetId}`);
      toast.success("Dataset deleted successfully!");
      loadDatasets();
    } catch (error) {
      toast.error("Failed to delete dataset: " + (error.response?.data?.detail || error.message));
    }
  };


  // Load saved states when dataset changes
  useEffect(() => {
    if (selectedDataset) {
      loadSavedStates();
    }
  }, [selectedDataset]);

  const loadSavedStates = async () => {
    if (!selectedDataset) return;
    try {
      const response = await axios.get(`${API}/analysis/saved-states/${selectedDataset.id}`);
      setSavedStates(response.data.states || []);
    } catch (error) {
      console.error("Failed to load saved states:", error);
    }
  };

  const saveWorkspaceState = async () => {
    if (!stateName.trim()) {
      toast.error("Please enter a name for this workspace state");
      return;
    }

    try {
      await axios.post(`${API}/analysis/save-state`, {
        dataset_id: selectedDataset.id,
        state_name: stateName,
        analysis_data: {
          predictive_analysis: predictiveAnalysisCache,
          visualization: visualizationCache,
          data_profiler: dataProfilerCache
        },
        chat_history: []
      });
      
      toast.success(`Workspace saved as "${stateName}"`);
      setStateName("");
      setShowSaveDialog(false);
      loadSavedStates();
    } catch (error) {
      const errorMessage = error.response?.data?.detail 
        ? (typeof error.response.data.detail === 'string' 
            ? error.response.data.detail 
            : JSON.stringify(error.response.data.detail))
        : error.message || "Unknown error occurred";
      toast.error("Failed to save workspace: " + errorMessage);
      console.error("Save error:", error);
    }
  };

  const loadWorkspaceState = async (stateId) => {
    try {
      const response = await axios.get(`${API}/analysis/load-state/${stateId}`);
      const loadedData = response.data.analysis_data;
      
      // Restore all cached states
      if (loadedData.predictive_analysis) {
        setPredictiveAnalysisCache(loadedData.predictive_analysis);
      }
      if (loadedData.visualization) {
        setVisualizationCache(loadedData.visualization);
      }
      if (loadedData.data_profiler) {
        setDataProfilerCache(loadedData.data_profiler);
      }
      
      toast.success("Workspace loaded successfully");
      setShowLoadDialog(false);
    } catch (error) {
      toast.error("Failed to load workspace: " + (error.response?.data?.detail || error.message));
    }
  };

  const deleteState = async (stateId, event) => {
    event.stopPropagation();
    if (!confirm("Are you sure you want to delete this saved workspace?")) {
      return;
    }
    
    try {
      await axios.delete(`${API}/analysis/delete-state/${stateId}`);
      toast.success("Saved workspace deleted");
      loadSavedStates();
    } catch (error) {
      toast.error("Failed to delete workspace: " + (error.response?.data?.detail || error.message));
    }
  };


  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-100">
      {/* Navigation */}
      <nav className="fixed top-0 left-0 right-0 z-50 backdrop-blur-md bg-white/80 border-b border-gray-200 shadow-sm">
        <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <Button
              data-testid="back-to-home-btn"
              variant="ghost"
              onClick={() => navigate('/')}
              className="gap-2"
            >
              <ArrowLeft className="w-4 h-4" />
              Back
            </Button>
            <div className="flex items-center gap-2">
              <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-blue-600 to-indigo-600 flex items-center justify-center">
                <Sparkles className="w-6 h-6 text-white" />
              </div>
              <span className="text-2xl font-bold bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent">
                PROMISE
              </span>
            </div>
          </div>
          <div className="flex items-center gap-3">
            {selectedDataset && (
              <>
                <Button
                  onClick={() => setShowSaveDialog(true)}
                  variant="outline"
                  size="sm"
                  className="gap-2"
                >
                  <Save className="w-4 h-4" />
                  Save Workspace
                </Button>
                {savedStates.length > 0 && (
                  <Button
                    onClick={() => setShowLoadDialog(true)}
                    variant="outline"
                    size="sm"
                    className="gap-2"
                  >
                    <FolderOpen className="w-4 h-4" />
                    Load ({savedStates.length})
                  </Button>
                )}
              </>
            )}
          </div>
          <div className="text-sm text-gray-600">
            {selectedDataset && (
              <span data-testid="current-dataset-name">
                Current: <strong>{selectedDataset.name}</strong>
              </span>
            )}
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <div className="pt-24 pb-12 px-6">
        <div className="max-w-7xl mx-auto">
          <div className="mb-8">
            <h1 className="text-4xl font-bold mb-2">Data Analysis Dashboard</h1>
            <p className="text-gray-600">Upload data, analyze, and get AI-powered insights</p>
          </div>

          {!selectedDataset ? (
            <div>
              <DataSourceSelector onDatasetLoaded={handleDatasetLoaded} />
              
              {datasets.length > 0 && (
                <Card className="mt-8 p-6 bg-white/90 backdrop-blur-sm">
                  <div className="flex items-center justify-between mb-4">
                    <h2 className="text-xl font-semibold">Recent Datasets ({datasets.length})</h2>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => setShowRecentDatasets(!showRecentDatasets)}
                      data-testid="toggle-recent-datasets"
                    >
                      {showRecentDatasets ? (
                        <>
                          <ChevronUp className="w-4 h-4 mr-2" />
                          Collapse
                        </>
                      ) : (
                        <>
                          <ChevronDown className="w-4 h-4 mr-2" />
                          Expand
                        </>
                      )}
                    </Button>
                  </div>
                  
                  {showRecentDatasets && (
                    <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
                      {datasets.map((dataset) => (
                        <div
                          key={dataset.id}
                          data-testid={`dataset-card-${dataset.id}`}
                          className="relative p-4 border border-gray-200 rounded-xl hover:shadow-lg hover:border-blue-400 cursor-pointer transition-all bg-white group"
                          onClick={() => handleDatasetSelect(dataset)}
                        >
                          <Button
                            variant="destructive"
                            size="sm"
                            className="absolute top-2 right-2 opacity-0 group-hover:opacity-100 transition-opacity"
                            onClick={(e) => deleteDataset(dataset.id, e)}
                            data-testid={`delete-dataset-${dataset.id}`}
                          >
                            <Trash2 className="w-4 h-4" />
                          </Button>
                          
                          <h3 className="font-semibold text-lg mb-2 truncate pr-10">{dataset.name}</h3>
                          <div className="text-sm text-gray-600 space-y-1">
                            <p>Rows: {dataset.row_count.toLocaleString()}</p>
                            <p>Columns: {dataset.column_count}</p>
                            {dataset.file_size && (
                              <p className="text-xs text-gray-500">
                                Size: {(dataset.file_size / 1024 / 1024).toFixed(2)} MB
                              </p>
                            )}
                            {dataset.upload_time && (
                              <p className="text-xs text-green-600 font-medium">
                                Upload time: {dataset.upload_time.toFixed(1)}s
                              </p>
                            )}
                            <p className="text-xs text-gray-400">
                              {new Date(dataset.created_at).toLocaleString()}
                            </p>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </Card>
              )}
            </div>
          ) : (
            <div>
              <Card className="p-6 bg-white/90 backdrop-blur-sm">
                <Tabs defaultValue="profile" className="w-full">
                  <TabsList className="grid w-full grid-cols-3 mb-6">
                    <TabsTrigger value="profile" data-testid="tab-profile">Data Profile</TabsTrigger>
                    <TabsTrigger value="predict" data-testid="tab-predict">Predictive Analysis</TabsTrigger>
                    <TabsTrigger value="visualize" data-testid="tab-visualize">Visualizations</TabsTrigger>
                  </TabsList>

                  <TabsContent value="profile">
                    <DataProfiler dataset={selectedDataset} onLoadNewDataset={() => setSelectedDataset(null)} />
                  </TabsContent>

                  <TabsContent value="predict">
                    <PredictiveAnalysis 
                      dataset={selectedDataset}
                      analysisCache={predictiveAnalysisCache[selectedDataset.id]}
                      onAnalysisUpdate={(data) => {
                        setPredictiveAnalysisCache(prev => ({
                          ...prev,
                          [selectedDataset.id]: data
                        }));
                      }}
                    />
                  </TabsContent>

                  <TabsContent value="visualize">
                    <VisualizationPanel 
                      dataset={selectedDataset}
                      chartsCache={visualizationCache[selectedDataset.id]}
                      onChartsUpdate={(data) => {
                        setVisualizationCache(prev => ({
                          ...prev,
                          [selectedDataset.id]: data
                        }));
                      }}
                    />
                  </TabsContent>
                </Tabs>
              </Card>

              <div className="mt-6 text-center">
                <Button
                  data-testid="load-new-dataset-btn"
                  variant="outline"
                  onClick={() => setSelectedDataset(null)}
                >
                  Load New Dataset
                </Button>
              </div>
            </div>
          )}
        </div>
      </div>


      {/* Save Dialog */}
      {showSaveDialog && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <Card className="w-96 p-6">
            <h3 className="text-lg font-semibold mb-4">Save Workspace State</h3>
            <p className="text-sm text-gray-600 mb-4">
              This will save Data Profiler, Predictive Analysis, and Visualizations
            </p>
            <input
              type="text"
              value={stateName}
              onChange={(e) => setStateName(e.target.value)}
              placeholder="Enter workspace name..."
              className="w-full px-3 py-2 border border-gray-300 rounded-md mb-4"
              onKeyPress={(e) => e.key === 'Enter' && saveWorkspaceState()}
            />
            <div className="flex gap-2 justify-end">
              <Button variant="outline" onClick={() => setShowSaveDialog(false)}>
                Cancel
              </Button>
              <Button onClick={saveWorkspaceState} disabled={!stateName.trim()}>
                Save
              </Button>
            </div>
          </Card>
        </div>
      )}

      {/* Load Dialog */}
      {showLoadDialog && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <Card className="w-[500px] p-6 max-h-[600px] overflow-y-auto">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold">Load Saved Workspace</h3>
              <Button variant="ghost" size="sm" onClick={() => setShowLoadDialog(false)}>
                ×
              </Button>
            </div>
            <div className="space-y-2">
              {savedStates.length === 0 ? (
                <p className="text-gray-600 text-center py-4">No saved workspace states found</p>
              ) : (
                savedStates.map((state) => (
                  <div
                    key={state.id}
                    className="p-4 border border-gray-200 rounded-lg hover:bg-gray-50 cursor-pointer flex items-center justify-between group"
                    onClick={() => loadWorkspaceState(state.id)}
                  >
                    <div>
                      <h4 className="font-semibold">{state.state_name}</h4>
                      <p className="text-xs text-gray-500">
                        Saved: {new Date(state.created_at).toLocaleString()}
                      </p>
                    </div>
                    <Button
                      variant="destructive"
                      size="sm"
                      className="opacity-0 group-hover:opacity-100 transition-opacity"
                      onClick={(e) => deleteState(state.id, e)}
                    >
                      <Trash2 className="w-4 h-4" />
                    </Button>
                  </div>
                ))
              )}
            </div>
          </Card>
        </div>
      )}

    </div>
  );
};

export default DashboardPage;