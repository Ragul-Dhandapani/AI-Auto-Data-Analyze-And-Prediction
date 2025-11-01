import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Loader2, Home, TrendingUp, TrendingDown, RefreshCw, Calendar, Database, ArrowUp, Download } from 'lucide-react';
import { toast } from 'sonner';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const TrainingMetadataPage = () => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [metadata, setMetadata] = useState([]);
  const [viewMode, setViewMode] = useState('dataset'); // 'dataset' or 'workspace'
  const [selectedDatasetForWorkspace, setSelectedDatasetForWorkspace] = useState(null);
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
      // Auto-select first dataset for workspace view
      if (data.length > 0) {
        setSelectedDatasetForWorkspace(data[0].dataset_id);
      }
    } catch (error) {
      toast.error('Failed to fetch training metadata');
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  const downloadPdf = async (datasetId, datasetName) => {
    setDownloadingPdf(datasetId);
    try {
      const response = await axios.get(`${API}/training/metadata/download-pdf/${datasetId}`, {
        responseType: 'blob'
      });
      
      // Create blob link to download
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `training_metadata_${datasetName.replace(/\s+/g, '_')}.pdf`);
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

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-50 flex items-center justify-center">
        <div className="text-center">
          <Loader2 className="w-12 h-12 animate-spin text-blue-600 mx-auto mb-4" />
          <p className="text-gray-600">Loading training metadata...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-50">
      {/* Header */}
      <div className="bg-white border-b shadow-sm sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
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
                <h1 className="text-2xl font-bold bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent">
                  Training Metadata Dashboard
                </h1>
                <p className="text-sm text-gray-600">
                  Comprehensive model performance and training analytics
                </p>
              </div>
            </div>
            <div className="flex items-center gap-3">
              <Button onClick={fetchMetadata} variant="outline" size="sm">
                <RefreshCw className="w-4 h-4 mr-2" />
                Refresh
              </Button>
            </div>
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="max-w-7xl mx-auto px-6 py-6">
        {/* View Mode Tabs */}
        <Tabs value={viewMode} onValueChange={setViewMode} className="mb-6">
          <TabsList className="bg-white">
            <TabsTrigger value="dataset">Dataset-wise View</TabsTrigger>
            <TabsTrigger value="workspace">Workspace-wise View</TabsTrigger>
          </TabsList>
        </Tabs>

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
          <>
            {/* Global Summary */}
            <div className="bg-white rounded-lg shadow-sm p-6 mb-6 border-2 border-blue-200">
              <h2 className="text-lg font-bold text-gray-800 mb-4">Dataset Summary</h2>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                {metadata.slice(0, 3).map((dataset, idx) => (
                  <div key={idx} className="space-y-2">
                    <div className="flex items-center justify-between">
                      <span className="text-sm font-semibold text-gray-700">Dataset:</span>
                      <span className="text-sm text-gray-600">{dataset.dataset_name}</span>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-sm font-semibold text-gray-700">Last trained:</span>
                      <span className="text-sm text-gray-600">
                        {dataset.last_trained_at 
                          ? new Date(dataset.last_trained_at).toLocaleDateString()
                          : 'Never'}
                      </span>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-sm font-semibold text-gray-700">Total Trainings:</span>
                      <span className="text-sm font-bold text-blue-600">{dataset.training_count} Times</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Dataset Cards */}
            {viewMode === 'dataset' && (
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {metadata.map((dataset, idx) => (
                  <Card key={idx} className="p-6 bg-white border-2 border-gray-200 hover:border-blue-400 transition-all">
                    {/* Dataset Header */}
                    <div className="mb-6 flex items-start justify-between">
                      <div className="flex-1">
                        <h3 className="text-xl font-bold text-gray-800 mb-1">{dataset.dataset_name}</h3>
                        <p className="text-xs text-gray-500">Dataset ID: {dataset.dataset_id}</p>
                        {dataset.last_trained_at && (
                          <p className="text-xs text-gray-500 flex items-center gap-1 mt-1">
                            <Calendar className="w-3 h-3" />
                            Last trained: {new Date(dataset.last_trained_at).toLocaleString()}
                          </p>
                        )}
                      </div>
                      <Button
                        onClick={() => downloadPdf(dataset.dataset_id, dataset.dataset_name)}
                        disabled={downloadingPdf === dataset.dataset_id}
                        variant="outline"
                        size="sm"
                        className="flex items-center gap-2"
                      >
                        {downloadingPdf === dataset.dataset_id ? (
                          <>
                            <Loader2 className="w-4 h-4 animate-spin" />
                            Downloading...
                          </>
                        ) : (
                          <>
                            <Download className="w-4 h-4" />
                            PDF
                          </>
                        )}
                      </Button>
                    </div>

                    {/* Score Summary */}
                    <div className="grid grid-cols-2 gap-4 mb-6">
                      <div className="bg-gradient-to-br from-blue-50 to-blue-100 p-4 rounded-lg border border-blue-200">
                        <p className="text-xs text-blue-700 font-semibold mb-1">Initial Score</p>
                        <p className="text-3xl font-bold text-blue-800">
                          {(dataset.initial_score !== null && dataset.initial_score !== undefined) 
                            ? Number(dataset.initial_score).toFixed(3) 
                            : 'N/A'}
                        </p>
                      </div>
                      <div className="bg-gradient-to-br from-green-50 to-green-100 p-4 rounded-lg border border-green-200">
                        <p className="text-xs text-green-700 font-semibold mb-1">
                          {(dataset.improvement_percentage !== null && dataset.improvement_percentage !== undefined) 
                            ? 'Improvement' 
                            : 'Current Score'}
                        </p>
                        <p className="text-3xl font-bold text-green-800 flex items-center gap-2">
                          {(dataset.improvement_percentage !== null && dataset.improvement_percentage !== undefined) ? (
                            <>
                              {Math.abs(Number(dataset.improvement_percentage)).toFixed(1)}%
                              {dataset.improvement_percentage >= 0 && <TrendingUp className="w-5 h-5 text-green-600" />}
                            </>
                          ) : (
                            (dataset.current_score !== null && dataset.current_score !== undefined) 
                              ? Number(dataset.current_score).toFixed(3) 
                              : 'N/A'
                          )}
                        </p>
                      </div>
                    </div>

                    {/* Model Performance Table */}
                    {dataset.initial_scores && Object.keys(dataset.initial_scores).length > 0 && (
                      <div className="mb-4">
                        <h4 className="text-sm font-bold text-gray-700 mb-3">Model Performance Breakdown</h4>
                        <div className="space-y-2">
                          {Object.entries(dataset.initial_scores).map(([modelName, initialScore], mIdx) => {
                            const currentScore = dataset.current_scores?.[modelName] || initialScore;
                            const improvementPct = dataset.improvement?.[modelName];
                            
                            return (
                              <div key={mIdx} className="flex items-center justify-between bg-gray-50 p-3 rounded border">
                                <div className="flex-1">
                                  <p className="text-sm font-semibold text-gray-800">{modelName}</p>
                                </div>
                                <div className="flex items-center gap-4">
                                  <div className="text-right">
                                    <p className="text-xs text-gray-500">Score</p>
                                    <p className="text-sm font-bold text-blue-600">
                                      {(currentScore * 100).toFixed(1)}%
                                    </p>
                                  </div>
                                  {improvementPct !== undefined && (
                                    <div className="text-right">
                                      <p className="text-xs text-gray-500">Improvement</p>
                                      <p className={`text-sm font-bold flex items-center gap-1 ${improvementPct >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                                        <ArrowUp className={`w-3 h-3 ${improvementPct < 0 ? 'rotate-180' : ''}`} />
                                        {improvementPct >= 0 ? '+' : ''}{improvementPct.toFixed(1)}%
                                      </p>
                                    </div>
                                  )}
                                </div>
                              </div>
                            );
                          })}
                        </div>
                      </div>
                    )}

                    {/* Workspaces */}
                    {dataset.workspaces.length > 0 && (
                      <div className="mt-4 pt-4 border-t">
                        <p className="text-xs font-semibold text-gray-600 mb-2">
                          Saved Workspaces ({dataset.workspaces.length})
                        </p>
                        <div className="space-y-1">
                          {dataset.workspaces.map((ws, wIdx) => (
                            <div key={wIdx} className="text-xs text-gray-600 flex items-center justify-between">
                              <span className="font-medium">{ws.workspace_name}</span>
                              <span className="text-gray-400">{new Date(ws.saved_at).toLocaleDateString()}</span>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                  </Card>
                ))}
              </div>
            )}

            {/* Workspace-wise View */}
            {viewMode === 'workspace' && (
              <div className="space-y-6">
                {/* Dataset Selector */}
                <Card className="p-6 bg-white">
                  <h3 className="text-lg font-bold text-gray-800 mb-4">Select Dataset</h3>
                  <select
                    value={selectedDatasetForWorkspace || ''}
                    onChange={(e) => setSelectedDatasetForWorkspace(e.target.value)}
                    className="w-full md:w-1/2 p-3 border-2 border-blue-300 rounded-lg focus:outline-none focus:border-blue-500"
                  >
                    {metadata.map((dataset) => (
                      <option key={dataset.dataset_id} value={dataset.dataset_id}>
                        {dataset.dataset_name} ({dataset.workspaces.length} workspaces)
                      </option>
                    ))}
                  </select>
                </Card>

                {/* Workspaces for Selected Dataset */}
                {selectedDatasetForWorkspace && (() => {
                  const selectedDataset = metadata.find(d => d.dataset_id === selectedDatasetForWorkspace);
                  if (!selectedDataset || selectedDataset.workspaces.length === 0) {
                    return (
                      <Card className="p-12 text-center">
                        <p className="text-gray-500">No saved workspaces for this dataset</p>
                      </Card>
                    );
                  }

                  return (
                    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                      {selectedDataset.workspaces.map((workspace, wIdx) => (
                        <Card key={wIdx} className="p-6 bg-white border-2 border-blue-200 hover:border-blue-400 transition-all">
                          {/* Workspace Header */}
                          <div className="mb-6">
                            <h3 className="text-xl font-bold text-blue-800 mb-1">{workspace.workspace_name}</h3>
                            <p className="text-xs text-gray-500">Workspace ID: {workspace.workspace_id}</p>
                            <p className="text-xs text-gray-500 flex items-center gap-1 mt-1">
                              <Calendar className="w-3 h-3" />
                              Saved: {new Date(workspace.saved_at).toLocaleString()}
                            </p>
                          </div>

                          {/* Dataset Info */}
                          <div className="mb-4 p-3 bg-gray-50 rounded">
                            <p className="text-xs text-gray-600">Dataset: <span className="font-semibold">{selectedDataset.dataset_name}</span></p>
                            <p className="text-xs text-gray-600">Training Count: <span className="font-semibold">{selectedDataset.training_count} times</span></p>
                          </div>

                          {/* Score Summary */}
                          <div className="grid grid-cols-2 gap-4 mb-6">
                            <div className="bg-gradient-to-br from-blue-50 to-blue-100 p-4 rounded-lg border border-blue-200">
                              <p className="text-xs text-blue-700 font-semibold mb-1">Initial Score</p>
                              <p className="text-3xl font-bold text-blue-800">
                                {(selectedDataset.initial_score !== null && selectedDataset.initial_score !== undefined) 
                                  ? Number(selectedDataset.initial_score).toFixed(3) 
                                  : 'N/A'}
                              </p>
                            </div>
                            <div className="bg-gradient-to-br from-green-50 to-green-100 p-4 rounded-lg border border-green-200">
                              <p className="text-xs text-green-700 font-semibold mb-1">Current Score</p>
                              <p className="text-3xl font-bold text-green-800">
                                {(selectedDataset.current_score !== null && selectedDataset.current_score !== undefined) 
                                  ? Number(selectedDataset.current_score).toFixed(3) 
                                  : 'N/A'}
                              </p>
                            </div>
                          </div>

                          {/* Improvement Badge */}
                          {(selectedDataset.improvement_percentage !== null && selectedDataset.improvement_percentage !== undefined) && (
                            <div className={`p-3 rounded-lg mb-4 ${selectedDataset.improvement_percentage >= 0 ? 'bg-green-50 border border-green-200' : 'bg-red-50 border border-red-200'}`}>
                              <p className={`text-sm font-semibold flex items-center justify-center gap-2 ${selectedDataset.improvement_percentage >= 0 ? 'text-green-700' : 'text-red-700'}`}>
                                {selectedDataset.improvement_percentage >= 0 ? <TrendingUp className="w-5 h-5" /> : <TrendingDown className="w-5 h-5" />}
                                Overall Improvement: {Math.abs(Number(selectedDataset.improvement_percentage)).toFixed(1)}%
                              </p>
                            </div>
                          )}

                          {/* Model Performance Breakdown */}
                          {selectedDataset.initial_scores && Object.keys(selectedDataset.initial_scores).length > 0 && (
                            <div className="mb-4">
                              <h4 className="text-sm font-bold text-gray-700 mb-3">Model Performance</h4>
                              <div className="space-y-2">
                                {Object.entries(selectedDataset.initial_scores).map(([modelName, initialScore], mIdx) => {
                                  const currentScore = selectedDataset.current_scores?.[modelName] || initialScore;
                                  const improvementPct = selectedDataset.improvement?.[modelName];
                                  
                                  return (
                                    <div key={mIdx} className="flex items-center justify-between bg-gray-50 p-3 rounded border">
                                      <div className="flex-1">
                                        <p className="text-sm font-semibold text-gray-800">{modelName}</p>
                                      </div>
                                      <div className="flex items-center gap-4">
                                        <div className="text-right">
                                          <p className="text-xs text-gray-500">Score</p>
                                          <p className="text-sm font-bold text-blue-600">
                                            {(currentScore * 100).toFixed(1)}%
                                          </p>
                                        </div>
                                        <div className="text-right">
                                          <p className="text-xs text-gray-500">Initial</p>
                                          <p className="text-sm font-medium text-gray-600">
                                            {(initialScore * 100).toFixed(1)}%
                                          </p>
                                        </div>
                                        {improvementPct !== undefined && (
                                          <div className="text-right">
                                            <p className="text-xs text-gray-500">Change</p>
                                            <p className={`text-sm font-bold flex items-center gap-1 ${improvementPct >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                                              <ArrowUp className={`w-3 h-3 ${improvementPct < 0 ? 'rotate-180' : ''}`} />
                                              {improvementPct >= 0 ? '+' : ''}{improvementPct.toFixed(1)}%
                                            </p>
                                          </div>
                                        )}
                                      </div>
                                    </div>
                                  );
                                })}
                              </div>
                            </div>
                          )}
                        </Card>
                      ))}
                    </div>
                  );
                })()}
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
};

export default TrainingMetadataPage;
