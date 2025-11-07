import { useState, useEffect } from "react";
import axios from "axios";
import { toast } from "sonner";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import DataSourceSelector from "@/components/DataSourceSelector";
import DataProfiler from "@/components/DataProfiler";
import PredictiveAnalysis from "@/components/PredictiveAnalysis";
import AnalysisTabs from "@/components/AnalysisTabs";
import VisualizationPanel from "@/components/VisualizationPanel";
import VariableSelectionModal from "@/components/VariableSelectionModal";
import CompactDatabaseToggle from "@/components/CompactDatabaseToggle";
import { Sparkles, ArrowLeft, Home, Trash2, ChevronDown, ChevronUp, Save, FolderOpen, RefreshCw, Database } from "lucide-react";
import { useNavigate } from "react-router-dom";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const DashboardPage = () => {
  const navigate = useNavigate();
  const [currentStep, setCurrentStep] = useState("data-source");
  const [selectedDataset, setSelectedDataset] = useState(null);
  const [datasets, setDatasets] = useState([]);
  const [showRecentDatasets, setShowRecentDatasets] = useState(true);
  const [selectedDatasetIds, setSelectedDatasetIds] = useState(new Set());
  const [isMultiSelectMode, setIsMultiSelectMode] = useState(false);
  const [datasetSavedStates, setDatasetSavedStates] = useState({}); // Track saved states per dataset
  
  // Variable selection state
  const [showVariableSelection, setShowVariableSelection] = useState(false);
  const [pendingDataset, setPendingDataset] = useState(null);
  const [variableSelection, setVariableSelection] = useState(null);
  
  // Lift analysis state to prevent re-analysis on tab switch
  const [predictiveAnalysisCache, setPredictiveAnalysisCache] = useState({});
  const [visualizationCache, setVisualizationCache] = useState({});
  const [dataProfilerCache, setDataProfilerCache] = useState({});
  
  // Save/Load state management
  const [showSaveDialog, setShowSaveDialog] = useState(false);
  const [stateName, setStateName] = useState("");
  const [savedStates, setSavedStates] = useState([]);
  const [showLoadDialog, setShowLoadDialog] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [saveProgress, setSaveProgress] = useState(0);

  useEffect(() => {
    loadDatasets();
  }, []);

  const loadDatasets = async () => {
    try {
      console.log('Loading datasets from:', `${API}/datasets`);
      const response = await axios.get(`${API}/datasets`);
      console.log('Datasets response:', response.data);
      const loadedDatasets = response.data.datasets || [];
      console.log('Loaded datasets count:', loadedDatasets.length);
      setDatasets(loadedDatasets);
      
      // Load saved states for each dataset
      const statesMap = {};
      for (const dataset of loadedDatasets) {
        try {
          const statesResponse = await axios.get(`${API}/analysis/saved-states/${dataset.id}`);
          statesMap[dataset.id] = statesResponse.data.states || [];
        } catch (error) {
          statesMap[dataset.id] = [];
        }
      }
      setDatasetSavedStates(statesMap);
    } catch (error) {
      console.error("Failed to load datasets", error);
      toast.error("Failed to load datasets. Please refresh the page.");
    }
  };

  const handleDatasetLoaded = (dataset) => {
    // Show variable selection modal after dataset is loaded
    setPendingDataset(dataset);
    setShowVariableSelection(true);
    loadDatasets();
  };

  const handleVariableSelectionConfirm = (selection) => {
    console.log('handleVariableSelectionConfirm received:', selection);
    
    setVariableSelection(selection);
    
    // Transform selection format for backend
    let transformedSelection;
    if (selection.is_multi_target && selection.targets) {
      // Multiple targets format
      transformedSelection = {
        target_variables: selection.targets.map(t => ({
          target: t.target,
          features: t.features
        })),
        mode: selection.mode,
        problem_type: selection.problem_type || "auto"
      };
      console.log('Transformed to multi-target format:', transformedSelection);
    } else if (selection.target) {
      // Single target format (backward compatible)
      transformedSelection = {
        target_variable: selection.target,
        selected_features: selection.features,
        mode: selection.mode,
        problem_type: selection.problem_type || "auto",
        time_column: selection.time_column,
        ai_suggestions: selection.aiSuggestions
      };
      console.log('Transformed to single-target format:', transformedSelection);
    } else {
      // Skip mode
      transformedSelection = null;
      console.log('Skip mode - no selection');
    }
    
    console.log('Setting dataset variableSelection to:', transformedSelection);
    
    setSelectedDataset({
      ...pendingDataset,
      variableSelection: transformedSelection
    });
    setShowVariableSelection(false);
    setCurrentStep("analysis");
    
    if (selection.mode === "skip") {
      toast.success("Dataset loaded successfully!");
    } else if (selection.is_multi_target) {
      toast.success(`${selection.targets.length} targets selected with features`);
    } else {
      toast.success(`Target: ${selection.target}, Features: ${selection.features.length} selected`);
    }
  };

  const handleVariableSelectionClose = () => {
    // User closed modal without confirming - still load dataset
    setSelectedDataset(pendingDataset);
    setShowVariableSelection(false);
    setCurrentStep("analysis");
    toast.info("Dataset loaded without variable selection");
  };

  const handleDatasetSelect = (dataset) => {
    setSelectedDataset(dataset);
    setCurrentStep("analysis");
    // Update savedStates for the Load button
    if (datasetSavedStates[dataset.id]) {
      setSavedStates(datasetSavedStates[dataset.id]);
    } else {
      setSavedStates([]);
    }
  };

  const deleteDataset = async (datasetId, event) => {
    event?.stopPropagation();
    if (window.confirm("Are you sure you want to delete this dataset?")) {
      try {
        await axios.delete(`${API}/datasets/${datasetId}`);
        loadDatasets();
        toast.success("Dataset deleted successfully");
        if (selectedDataset?.id === datasetId) {
          setSelectedDataset(null);
          setCurrentStep("data-source");
        }
      } catch (error) {
        toast.error("Failed to delete dataset: " + (error.response?.data?.detail || "Not Found"));
      }
    }
  };

  const toggleDatasetSelection = (datasetId) => {
    const newSelection = new Set(selectedDatasetIds);
    if (newSelection.has(datasetId)) {
      newSelection.delete(datasetId);
    } else {
      newSelection.add(datasetId);
    }
    setSelectedDatasetIds(newSelection);
  };

  const selectAllDatasets = () => {
    if (selectedDatasetIds.size === datasets.length) {
      setSelectedDatasetIds(new Set());
    } else {
      setSelectedDatasetIds(new Set(datasets.map(d => d.id)));
    }
  };

  const bulkDeleteDatasets = async () => {
    if (selectedDatasetIds.size === 0) {
      toast.error("No datasets selected");
      return;
    }
    
    if (window.confirm(`Are you sure you want to delete ${selectedDatasetIds.size} dataset(s)?`)) {
      try {
        const deletePromises = Array.from(selectedDatasetIds).map(id => 
          axios.delete(`${API}/datasets/${id}`).catch(err => ({ error: err, id }))
        );
        
        // Use Promise.allSettled to handle partial failures
        const results = await Promise.allSettled(deletePromises);
        
        // Count successes and failures
        const succeeded = results.filter(r => r.status === 'fulfilled' && !r.value?.error).length;
        const failed = results.filter(r => r.status === 'rejected' || r.value?.error).length;
        
        if (failed > 0) {
          toast.warning(`Deleted ${succeeded} dataset(s). Failed to delete ${failed} dataset(s).`);
        } else {
          toast.success(`${succeeded} dataset(s) deleted successfully`);
        }
        
        setSelectedDatasetIds(new Set());
        setIsMultiSelectMode(false);
        loadDatasets();
        
        if (selectedDataset && selectedDatasetIds.has(selectedDataset.id)) {
          setSelectedDataset(null);
          setCurrentStep("data-source");
        }
      } catch (error) {
        toast.error("Failed to delete datasets: " + error.message);
      }
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

    setIsSaving(true);
    setSaveProgress(0);

    try {
      // Simulate progress for better UX
      setSaveProgress(20);
      await new Promise(resolve => setTimeout(resolve, 100));
      
      setSaveProgress(40);
      toast.info("Preparing workspace data...");
      
      // Make the API call
      const response = await axios.post(`${API}/analysis/save-state`, {
        dataset_id: selectedDataset.id,
        state_name: stateName,
        analysis_data: {
          predictive_analysis: predictiveAnalysisCache,
          visualization: visualizationCache,
          data_profiler: dataProfilerCache
        },
        chat_history: []
      });
      
      setSaveProgress(80);
      await new Promise(resolve => setTimeout(resolve, 200));
      
      setSaveProgress(100);
      
      const savedInfo = response.data;
      const sizeInfo = savedInfo.size_mb ? ` (${savedInfo.size_mb} MB)` : '';
      const optimizedInfo = savedInfo.optimized ? ' - Optimized & Compressed' : '';
      
      toast.success(`✅ Workspace saved as "${stateName}"${sizeInfo}${optimizedInfo}`);
      setStateName("");
      setShowSaveDialog(false);
      loadSavedStates();
    } catch (error) {
      const errorMessage = error.response?.data?.detail 
        ? (typeof error.response.data.detail === 'string' 
            ? error.response.data.detail 
            : JSON.stringify(error.response.data.detail))
        : error.message || "Unknown error occurred";
      toast.error("❌ Failed to save workspace: " + errorMessage);
      console.error("Save error:", error);
    } finally {
      setTimeout(() => {
        setIsSaving(false);
        setSaveProgress(0);
      }, 500);
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
                PROMISE AI
              </span>
            </div>
          </div>
          <div className="flex items-center gap-3">
            {/* Compact Database Toggle */}
            <CompactDatabaseToggle />
            
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
            
            {selectedDataset && (
              <div className="text-sm text-gray-600">
                <span data-testid="current-dataset-name">
                  Current: <strong>{selectedDataset.name}</strong>
                </span>
              </div>
            )}
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <div className="pt-24 pb-12 px-6">
        <div className="max-w-7xl mx-auto">
          <div className="mb-8">
            <h1 className="text-4xl font-bold mb-2">Intelligent Data Analysis & Prediction Dashboard</h1>
            <p className="text-gray-600">Upload data, analyze, and get AI-powered insights</p>
          </div>

          {!selectedDataset ? (
            <div>
              <DataSourceSelector onDatasetLoaded={handleDatasetLoaded} />
              
              {datasets.length > 0 ? (
                <Card className="mt-8 p-6 bg-white/90 backdrop-blur-sm">
                  <div className="flex items-center justify-between mb-4">
                    <div className="flex items-center gap-4">
                      <h2 className="text-xl font-semibold">Recent Datasets ({datasets.length})</h2>
                      {datasets.length > 0 && (
                        <Button
                          variant={isMultiSelectMode ? "default" : "outline"}
                          size="sm"
                          onClick={() => {
                            setIsMultiSelectMode(!isMultiSelectMode);
                            if (isMultiSelectMode) {
                              setSelectedDatasetIds(new Set());
                            }
                          }}
                          data-testid="toggle-multi-select"
                        >
                          {isMultiSelectMode ? "Done" : "Select Multiple"}
                        </Button>
                      )}
                      {isMultiSelectMode && selectedDatasetIds.size > 0 && (
                        <>
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={selectAllDatasets}
                          >
                            {selectedDatasetIds.size === datasets.length ? "Deselect All" : "Select All"}
                          </Button>
                          <Button
                            variant="destructive"
                            size="sm"
                            onClick={bulkDeleteDatasets}
                            data-testid="bulk-delete-btn"
                          >
                            <Trash2 className="w-4 h-4 mr-2" />
                            Delete ({selectedDatasetIds.size})
                          </Button>
                        </>
                      )}
                    </div>
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
                    <div className="grid sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4 max-h-[600px] overflow-y-auto pr-2">
                      {datasets.map((dataset) => {
                        const isSelected = selectedDatasetIds.has(dataset.id);
                        return (
                        <div
                          key={dataset.id}
                          data-testid={`dataset-card-${dataset.id}`}
                          className={`relative p-4 border-2 rounded-xl transition-all bg-white ${
                            isSelected 
                              ? 'border-blue-500 bg-blue-50' 
                              : 'border-gray-200 hover:border-blue-400'
                          } ${isMultiSelectMode ? 'cursor-pointer' : 'cursor-pointer hover:shadow-lg'} group`}
                          onClick={(e) => {
                            if (isMultiSelectMode) {
                              toggleDatasetSelection(dataset.id);
                            } else {
                              handleDatasetSelect(dataset);
                            }
                          }}
                        >
                          {isMultiSelectMode && (
                            <div className="absolute top-2 left-2 z-10">
                              <input
                                type="checkbox"
                                checked={isSelected}
                                onChange={() => toggleDatasetSelection(dataset.id)}
                                className="w-5 h-5 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                                onClick={(e) => e.stopPropagation()}
                              />
                            </div>
                          )}
                          
                          {!isMultiSelectMode && (
                            <Button
                              variant="destructive"
                              size="sm"
                              className="absolute top-2 right-2 opacity-0 group-hover:opacity-100 transition-opacity z-10"
                              onClick={(e) => deleteDataset(dataset.id, e)}
                              data-testid={`delete-dataset-${dataset.id}`}
                            >
                              <Trash2 className="w-4 h-4" />
                            </Button>
                          )}
                          
                          <h3 className={`font-semibold text-base mb-2 truncate ${isMultiSelectMode ? 'pl-6 pr-2' : 'pr-10'}`}>
                            {dataset.name}
                          </h3>
                          <div className="text-xs text-gray-600 space-y-1">
                            <p className="flex justify-between">
                              <span>Rows:</span> 
                              <span className="font-medium">{dataset.row_count.toLocaleString()}</span>
                            </p>
                            <p className="flex justify-between">
                              <span>Columns:</span> 
                              <span className="font-medium">{dataset.column_count}</span>
                            </p>
                            {dataset.file_size && (
                              <p className="flex justify-between text-gray-500">
                                <span>Size:</span> 
                                <span>{(dataset.file_size / 1024 / 1024).toFixed(2)} MB</span>
                              </p>
                            )}
                            {dataset.training_count && dataset.training_count > 0 && (
                              <div className="mt-2 pt-2 border-t border-green-200 bg-green-50 -mx-2 px-2 py-1 rounded">
                                <p className="text-xs font-semibold text-green-700 flex items-center gap-1">
                                  <RefreshCw className="w-3 h-3" />
                                  Trained {dataset.training_count}x
                                </p>
                              </div>
                            )}
                            <p className="text-[10px] text-gray-400 pt-1">
                              {new Date(dataset.created_at).toLocaleDateString()}
                            </p>
                            {datasetSavedStates[dataset.id] && datasetSavedStates[dataset.id].length > 0 && (
                              <div className="mt-1 pt-1 border-t border-gray-200">
                                <p className="text-xs font-semibold text-blue-600 flex items-center gap-1">
                                  <FolderOpen className="w-3 h-3" />
                                  {datasetSavedStates[dataset.id].length} Workspace(s)
                                </p>
                              </div>
                            )}
                          </div>
                        </div>
                        );
                      })}
                    </div>
                  )}
                </Card>
              ) : (
                <Card className="mt-8 p-6 bg-gray-50 text-center">
                  <Database className="w-12 h-12 mx-auto mb-3 text-gray-400" />
                  <p className="text-gray-600 font-medium">No datasets yet</p>
                  <p className="text-sm text-gray-500 mt-1">Upload a file or connect to a database above to get started</p>
                  <p className="text-xs text-gray-400 mt-3">Note: If you uploaded data but don't see it, try refreshing the page</p>
                </Card>
              )}
            </div>
          ) : (
            <div>
              <Card className="p-6 bg-white/90 backdrop-blur-sm">
                <Tabs defaultValue="profile" className="w-full">
                  <TabsList className="grid w-full grid-cols-3 mb-6">
                    <TabsTrigger value="profile" data-testid="tab-profile">Data Profile</TabsTrigger>
                    <TabsTrigger value="predict" data-testid="tab-predict">Predictive Analysis & Forecasting</TabsTrigger>
                    <TabsTrigger value="visualize" data-testid="tab-visualize">Visualizations</TabsTrigger>
                  </TabsList>

                  <TabsContent value="profile">
                    <DataProfiler dataset={selectedDataset} onLoadNewDataset={() => setSelectedDataset(null)} />
                  </TabsContent>

                  <TabsContent value="predict">
                    {console.log('Rendering PredictiveAnalysis with:', {
                      'selectedDataset.variableSelection': selectedDataset?.variableSelection,
                      'variableSelection state': variableSelection,
                      'final prop value': selectedDataset?.variableSelection || variableSelection
                    })}
                    <AnalysisTabs
                      dataset={selectedDataset}
                      analysisCache={predictiveAnalysisCache[selectedDataset.id]}
                      variableSelection={selectedDataset?.variableSelection || variableSelection}
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
                      variableSelection={variableSelection}
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
            
            {isSaving ? (
              <div className="space-y-4">
                <div className="text-center">
                  <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mb-3"></div>
                  <p className="text-sm text-gray-600 mb-2">Saving workspace...</p>
                  <div className="w-full bg-gray-200 rounded-full h-3 mb-2">
                    <div 
                      className="bg-gradient-to-r from-blue-600 to-green-600 h-3 rounded-full transition-all duration-500"
                      style={{ width: `${saveProgress}%` }}
                    ></div>
                  </div>
                  <p className="text-sm font-semibold text-blue-600">{saveProgress}%</p>
                </div>
              </div>
            ) : (
              <>
                <p className="text-sm text-gray-600 mb-4">
                  This will save Data Profiler, Predictive Analysis, and Visualizations
                </p>
                <input
                  type="text"
                  value={stateName}
                  onChange={(e) => setStateName(e.target.value)}
                  placeholder="Enter workspace name..."
                  className="w-full px-3 py-2 border border-gray-300 rounded-md mb-4"
                  onKeyPress={(e) => e.key === 'Enter' && !isSaving && saveWorkspaceState()}
                  disabled={isSaving}
                />
                <div className="flex gap-2 justify-end">
                  <Button variant="outline" onClick={() => setShowSaveDialog(false)} disabled={isSaving}>
                    Cancel
                  </Button>
                  <Button onClick={saveWorkspaceState} disabled={!stateName.trim() || isSaving}>
                    {isSaving ? 'Saving...' : 'Save'}
                  </Button>
                </div>
              </>
            )}
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

      {/* Variable Selection Modal */}
      {showVariableSelection && pendingDataset && (
        <VariableSelectionModal
          dataset={pendingDataset}
          onClose={handleVariableSelectionClose}
          onConfirm={handleVariableSelectionConfirm}
        />
      )}

    </div>
  );
};

export default DashboardPage;