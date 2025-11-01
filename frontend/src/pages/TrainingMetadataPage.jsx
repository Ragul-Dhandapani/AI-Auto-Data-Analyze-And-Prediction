import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Loader2, Home, TrendingUp, Calendar, Database, Download, ChevronDown } from 'lucide-react';
import { toast } from 'sonner';
import Select from 'react-select';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const TrainingMetadataPage = () => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [metadata, setMetadata] = useState([]);
  const [selectedDataset, setSelectedDataset] = useState(null);
  const [selectedWorkspaces, setSelectedWorkspaces] = useState([]);
  const [downloadingPdf, setDownloadingPdf] = useState(null);

  useEffect(() => {
    fetchMetadata();
  }, []);

  const fetchMetadata = async () => {
    setLoading(true);
    try {
      const response = await axios.get(`${API}/training-metadata`);
      const data = response.data.metadata || [];
      setMetadata(data);
      
      // Auto-select first dataset with workspaces
      const firstWithWorkspaces = data.find(d => d.workspaces && d.workspaces.length > 0);
      if (firstWithWorkspaces) {
        setSelectedDataset({
          value: firstWithWorkspaces.dataset_id,
          label: firstWithWorkspaces.dataset_name,
          data: firstWithWorkspaces
        });
      }
    } catch (error) {
      toast.error('Failed to fetch training metadata');
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  const downloadPdf = async (datasetId, datasetName, workspaceIds = null) => {
    setDownloadingPdf(datasetId);
    try {
      const url = workspaceIds 
        ? `${API}/training/metadata/download-pdf/${datasetId}?workspaces=${workspaceIds.join(',')}`
        : `${API}/training/metadata/download-pdf/${datasetId}`;
        
      const response = await axios.get(url, { responseType: 'blob' });
      
      const blobUrl = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = blobUrl;
      const filename = workspaceIds && workspaceIds.length > 0
        ? `training_metadata_${datasetName.replace(/\s+/g, '_')}_workspaces.pdf`
        : `training_metadata_${datasetName.replace(/\s+/g, '_')}_complete.pdf`;
      link.setAttribute('download', filename);
      document.body.appendChild(link);
      link.click();
      link.remove();
      
      toast.success('PDF downloaded successfully!');
    } catch (error) {
      toast.error('Failed to download PDF');
      console.error(error);
    } finally {
      setDownloadingPdf(null);
    }
  };

  // Prepare dataset options for dropdown
  const datasetOptions = metadata.map(ds => ({
    value: ds.dataset_id,
    label: `${ds.dataset_name} (${ds.workspaces?.length || 0} workspaces)`,
    data: ds
  }));

  // Prepare workspace options for selected dataset
  const workspaceOptions = selectedDataset?.data?.workspaces?.map(ws => ({
    value: ws.workspace_id,
    label: `${ws.workspace_name} - ${new Date(ws.saved_at).toLocaleDateString()}`,
    data: ws
  })) || [];

  // Get data to display based on selections
  const getDisplayData = () => {
    if (!selectedDataset) return null;
    
    const dataset = selectedDataset.data;
    
    if (selectedWorkspaces.length === 0) {
      // Show complete dataset data
      return {
        title: `Complete Dataset: ${dataset.dataset_name}`,
        training_count: dataset.workspaces?.length || 0,
        last_trained: dataset.last_trained,
        initial_scores: dataset.initial_scores,
        current_scores: dataset.current_scores,
        initial_score: dataset.initial_score,
        current_score: dataset.current_score,
        improvement_percentage: dataset.improvement_percentage,
        row_count: dataset.row_count,
        column_count: dataset.column_count,
        isComplete: true
      };
    } else {
      // Show combined workspace data
      const selectedWsData = selectedWorkspaces.map(ws => ws.data);
      const allModels = {};
      
      selectedWsData.forEach(ws => {
        // Extract model scores from workspace (would need to be added to API)
        // For now, show workspace names
      });
      
      return {
        title: `${selectedWorkspaces.length} Workspace(s) Selected`,
        workspaces: selectedWsData,
        training_count: selectedWsData.length,
        isComplete: false
      };
    }
  };

  const displayData = getDisplayData();

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50 p-8">
        <div className="flex items-center justify-center h-64">
          <Loader2 className="w-8 h-8 animate-spin text-blue-600" />
          <p className="ml-3 text-gray-600">Loading training metadata...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50 p-8">
      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center gap-4">
            <Button
              variant="outline"
              size="sm"
              onClick={() => navigate('/')}
              className="flex items-center gap-2"
            >
              <Home className="w-4 h-4" />
              Home
            </Button>
            <div>
              <h1 className="text-3xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                Training Metadata Dashboard
              </h1>
              <p className="text-gray-600 mt-1">
                Analyze model performance across datasets and workspaces
              </p>
            </div>
          </div>
        </div>
      </div>

      {metadata.length === 0 ? (
        <Card className="p-12 text-center">
          <Database className="w-16 h-16 mx-auto mb-4 text-gray-400" />
          <h3 className="text-xl font-semibold text-gray-600 mb-2">No Training Data Available</h3>
          <p className="text-gray-500">Run analysis on datasets to see training metadata here.</p>
          <Button onClick={() => navigate('/dashboard')} className="mt-4">
            Go to Dashboard
          </Button>
        </Card>
      ) : (
        <div className="space-y-6">
          {/* Selection Controls */}
          <Card className="p-6">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Dataset Selection */}
              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-3">
                  Select Dataset
                </label>
                <Select
                  value={selectedDataset}
                  onChange={setSelectedDataset}
                  options={datasetOptions}
                  placeholder="Choose a dataset..."
                  className="react-select-container"
                  classNamePrefix="react-select"
                  isClearable
                />
              </div>

              {/* Workspace Selection */}
              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-3">
                  Select Workspaces (Optional)
                </label>
                <Select
                  value={selectedWorkspaces}
                  onChange={setSelectedWorkspaces}
                  options={workspaceOptions}
                  placeholder="Choose workspaces or leave empty for complete dataset..."
                  className="react-select-container"
                  classNamePrefix="react-select"
                  isMulti
                  isClearable
                  isDisabled={!selectedDataset}
                />
                <p className="text-xs text-gray-500 mt-2">
                  Leave empty to view complete dataset analysis, or select specific workspaces
                </p>
              </div>
            </div>
          </Card>

          {/* Display Data */}
          {displayData && (
            <Card className="p-6">
              {/* Header with Download */}
              <div className="flex items-center justify-between mb-6">
                <div>
                  <h2 className="text-xl font-bold text-gray-800">{displayData.title}</h2>
                  <p className="text-sm text-gray-600 mt-1">
                    {displayData.isComplete 
                      ? `Complete dataset analysis with ${displayData.training_count} workspace(s)`
                      : `Analysis of ${displayData.training_count} selected workspace(s)`
                    }
                  </p>
                </div>
                <Button
                  onClick={() => downloadPdf(
                    selectedDataset.value, 
                    selectedDataset.data.dataset_name,
                    selectedWorkspaces.length > 0 ? selectedWorkspaces.map(ws => ws.value) : null
                  )}
                  disabled={downloadingPdf === selectedDataset.value}
                  className="flex items-center gap-2"
                >
                  {downloadingPdf === selectedDataset.value ? (
                    <>
                      <Loader2 className="w-4 h-4 animate-spin" />
                      Generating PDF...
                    </>
                  ) : (
                    <>
                      <Download className="w-4 h-4" />
                      Download PDF
                    </>
                  )}
                </Button>
              </div>

              {displayData.isComplete ? (
                /* Complete Dataset View */
                <div className="space-y-6">
                  {/* Dataset Info & Training History */}
                  <div className="bg-white p-5 rounded-lg border border-gray-200">
                    <div className="flex items-center gap-2 mb-3">
                      <Database className="w-5 h-5 text-blue-600" />
                      <h3 className="text-lg font-bold text-gray-800">{selectedDataset.data.dataset_name}</h3>
                    </div>
                    <div className="text-sm text-gray-600 space-y-1">
                      <p>
                        <span className="font-medium">Dataset ID:</span> {selectedDataset.value}
                      </p>
                      <p>
                        <span className="font-medium">Last trained:</span>{' '}
                        {displayData.last_trained ? new Date(displayData.last_trained).toLocaleString() : 'N/A'}
                      </p>
                    </div>
                  </div>

                  {/* Key Metrics - Initial Score & Improvement */}
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div className="bg-gradient-to-br from-blue-50 to-blue-100 p-6 rounded-lg border border-blue-200">
                      <div className="flex items-center gap-2 mb-2">
                        <TrendingUp className="w-5 h-5 text-blue-600" />
                        <span className="text-sm font-semibold text-blue-700">Initial Score</span>
                      </div>
                      <p className="text-4xl font-bold text-blue-800">
                        {displayData.initial_score !== null && displayData.initial_score !== undefined
                          ? Number(displayData.initial_score).toFixed(3)
                          : 'N/A'}
                      </p>
                    </div>

                    <div className="bg-gradient-to-br from-green-50 to-green-100 p-6 rounded-lg border border-green-200">
                      <div className="flex items-center gap-2 mb-2">
                        <TrendingUp className="w-5 h-5 text-green-600" />
                        <span className="text-sm font-semibold text-green-700">Improvement</span>
                      </div>
                      <p className="text-4xl font-bold text-green-800">
                        {displayData.improvement_percentage !== null && displayData.improvement_percentage !== undefined
                          ? `${displayData.improvement_percentage >= 0 ? '+' : ''}${Number(displayData.improvement_percentage).toFixed(1)}%`
                          : 'N/A'}
                      </p>
                      <div className="mt-2 text-xs text-green-700">
                        {displayData.training_count > 0 && `Trained ${displayData.training_count} times`}
                      </div>
                    </div>
                  </div>

                  {/* Model Performance Breakdown - Table Format */}
                  {displayData.initial_scores && Object.keys(displayData.initial_scores).length > 0 && (
                    <div>
                      <h3 className="text-lg font-bold text-gray-800 mb-4">Model Performance Breakdown</h3>
                      <div className="space-y-3">
                        {Object.entries(displayData.initial_scores).map(([modelName, initialScore], idx) => {
                          const currentScore = displayData.current_scores?.[modelName] || initialScore;
                          const improvement = displayData.current_scores?.[modelName] 
                            ? ((currentScore - initialScore) / initialScore * 100)
                            : 0;
                          
                          return (
                            <div key={idx} className="bg-white p-4 rounded-lg border border-gray-200 shadow-sm">
                              <div className="flex items-center justify-between">
                                <h4 className="font-semibold text-gray-800 text-base">{modelName}</h4>
                                <div className="flex gap-8">
                                  <div className="text-right">
                                    <p className="text-xs text-gray-500 mb-1">Score</p>
                                    <p className="text-xl font-bold text-blue-600">
                                      {(currentScore * 100).toFixed(1)}%
                                    </p>
                                  </div>
                                  <div className="text-right">
                                    <p className="text-xs text-gray-500 mb-1">Improvement</p>
                                    <p className={`text-xl font-bold ${improvement >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                                      <span className="inline-flex items-center gap-1">
                                        {improvement >= 0 ? '↑' : '↓'} {improvement >= 0 ? '+' : ''}{improvement.toFixed(1)}%
                                      </span>
                                    </p>
                                  </div>
                                </div>
                              </div>
                            </div>
                          );
                        })}
                      </div>
                    </div>
                  )}
                </div>
              ) : (
                /* Selected Workspaces View */
                <div className="space-y-6">
                  <div className="bg-blue-50 p-4 rounded-lg border border-blue-200">
                    <h3 className="font-semibold text-blue-800 mb-2">Selected Workspaces</h3>
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
                      {displayData.workspaces.map((ws, idx) => (
                        <div key={idx} className="bg-white p-3 rounded border">
                          <p className="font-medium text-gray-800">{ws.workspace_name}</p>
                          <p className="text-xs text-gray-500">
                            Saved: {new Date(ws.saved_at).toLocaleDateString()}
                          </p>
                        </div>
                      ))}
                    </div>
                  </div>
                  
                  <div className="text-center py-8">
                    <p className="text-gray-600 mb-4">
                      Workspace-specific analysis will be available in the PDF report
                    </p>
                    <p className="text-sm text-gray-500">
                      The PDF will contain detailed performance metrics for the selected workspaces
                    </p>
                  </div>
                </div>
              )}
            </Card>
          )}
        </div>
      )}
    </div>
  );
};

export default TrainingMetadataPage;
