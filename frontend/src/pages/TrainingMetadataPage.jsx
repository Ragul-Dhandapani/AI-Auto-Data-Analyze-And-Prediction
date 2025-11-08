import React, { useState, useEffect, useMemo } from 'react';
import axios from 'axios';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { ChevronDown, ChevronRight, Database, FolderOpen, TrendingUp, Clock, Award, Download, Loader, Search, Filter, RefreshCw, X, BarChart3, Calendar, ArrowUpDown, CheckCircle2, Settings, GitCompare } from 'lucide-react';
import { toast } from 'react-hot-toast';
import Plot from 'react-plotly.js';

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

const TrainingMetadataPage = () => {
  const [loading, setLoading] = useState(true);
  const [data, setData] = useState(null);
  const [expandedDatasets, setExpandedDatasets] = useState({});
  const [expandedWorkspaces, setExpandedWorkspaces] = useState({});
  const [searchQuery, setSearchQuery] = useState('');
  const [filterMetric, setFilterMetric] = useState('all');
  const [sortBy, setSortBy] = useState('date');

  useEffect(() => {
    loadMetadata();
  }, []);

  const loadMetadata = async () => {
    setLoading(true);
    try {
      const response = await axios.get(`${API}/training/metadata/by-workspace`);
      setData(response.data);
      
      // Auto-expand first dataset
      if (response.data.datasets && response.data.datasets.length > 0) {
        const firstDatasetId = response.data.datasets[0].dataset_id;
        setExpandedDatasets({ [firstDatasetId]: true });
      }
    } catch (error) {
      console.error('Failed to load training metadata:', error);
      toast.error('Failed to load training history');
    } finally {
      setLoading(false);
    }
  };

  const toggleDataset = (datasetId) => {
    setExpandedDatasets(prev => ({
      ...prev,
      [datasetId]: !prev[datasetId]
    }));
  };

  const toggleWorkspace = (workspaceKey) => {
    setExpandedWorkspaces(prev => ({
      ...prev,
      [workspaceKey]: !prev[workspaceKey]
    }));
  };

  const getMetricDisplay = (metrics) => {
    if (!metrics) return 'N/A';
    
    const accuracy = metrics.accuracy;
    const r2 = metrics.r2_score;
    
    if (accuracy !== undefined && accuracy !== null) {
      return `${(accuracy * 100).toFixed(1)}% Acc`;
    }
    if (r2 !== undefined && r2 !== null) {
      return `${(r2 * 100).toFixed(1)}% R²`;
    }
    return 'N/A';
  };

  const getMetricColor = (metrics) => {
    if (!metrics) return 'text-gray-500';
    
    const value = metrics.accuracy || metrics.r2_score || 0;
    if (value >= 0.8) return 'text-green-600';
    if (value >= 0.6) return 'text-yellow-600';
    return 'text-red-600';
  };

  const formatDate = (dateString) => {
    if (!dateString) return 'N/A';
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now - date;
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);
    
    if (diffMins < 60) return `${diffMins}m ago`;
    if (diffHours < 24) return `${diffHours}h ago`;
    if (diffDays < 7) return `${diffDays}d ago`;
    return date.toLocaleDateString();
  };

  const exportToCSV = (dataset) => {
    // Export training history as CSV
    const rows = [];
    rows.push(['Dataset', 'Workspace', 'Model Type', 'Target', 'Accuracy', 'Duration', 'Date']);
    
    dataset.workspaces.forEach(workspace => {
      workspace.training_runs.forEach(run => {
        rows.push([
          dataset.dataset_name,
          workspace.workspace_name,
          run.model_type,
          run.target_variable,
          getMetricDisplay(run.metrics),
          `${run.training_duration}s`,
          run.created_at
        ]);
      });
    });
    
    const csv = rows.map(row => row.join(',')).join('\n');
    const blob = new Blob([csv], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${dataset.dataset_name}_training_history.csv`;
    a.click();
    toast.success('Training history exported!');
  };

  // Calculate summary stats
  const stats = data ? {
    totalDatasets: data.total_datasets || 0,
    totalWorkspaces: data.datasets?.reduce((sum, ds) => sum + ds.total_workspaces, 0) || 0,
    totalModels: data.datasets?.reduce((sum, ds) => 
      sum + ds.workspaces.reduce((wsum, ws) => wsum + ws.total_models, 0), 0
    ) || 0,
    avgAccuracy: (() => {
      let totalAcc = 0;
      let count = 0;
      data.datasets?.forEach(ds => {
        ds.workspaces.forEach(ws => {
          ws.training_runs.forEach(run => {
            const acc = run.metrics?.accuracy || run.metrics?.r2_score;
            if (acc) {
              totalAcc += acc;
              count++;
            }
          });
        });
      });
      return count > 0 ? (totalAcc / count * 100).toFixed(1) : 0;
    })()
  } : {};

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 p-6 flex items-center justify-center">
        <div className="text-center">
          <Loader className="w-12 h-12 animate-spin mx-auto text-blue-600 mb-4" />
          <p className="text-gray-600">Loading training history...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      {/* Header */}
      <div className="max-w-7xl mx-auto mb-6">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-3">
              <Database className="w-8 h-8 text-blue-600" />
              Training Metadata & History
            </h1>
            <p className="text-gray-600 mt-2">Comprehensive view of all datasets, workspaces, and model training runs</p>
          </div>
          <Button onClick={loadMetadata} variant="outline">
            <RefreshCw className="w-4 h-4 mr-2" />
            Refresh
          </Button>
        </div>

        {/* Summary Stats */}
        <div className="grid grid-cols-4 gap-4 mb-6">
          <Card className="bg-gradient-to-br from-blue-50 to-blue-100 border-blue-200">
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-blue-600 font-medium">Total Datasets</p>
                  <p className="text-3xl font-bold text-blue-900">{stats.totalDatasets}</p>
                </div>
                <Database className="w-10 h-10 text-blue-600 opacity-50" />
              </div>
            </CardContent>
          </Card>

          <Card className="bg-gradient-to-br from-green-50 to-green-100 border-green-200">
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-green-600 font-medium">Total Workspaces</p>
                  <p className="text-3xl font-bold text-green-900">{stats.totalWorkspaces}</p>
                </div>
                <FolderOpen className="w-10 h-10 text-green-600 opacity-50" />
              </div>
            </CardContent>
          </Card>

          <Card className="bg-gradient-to-br from-purple-50 to-purple-100 border-purple-200">
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-purple-600 font-medium">Models Trained</p>
                  <p className="text-3xl font-bold text-purple-900">{stats.totalModels}</p>
                </div>
                <TrendingUp className="w-10 h-10 text-purple-600 opacity-50" />
              </div>
            </CardContent>
          </Card>

          <Card className="bg-gradient-to-br from-orange-50 to-orange-100 border-orange-200">
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-orange-600 font-medium">Avg Accuracy</p>
                  <p className="text-3xl font-bold text-orange-900">{stats.avgAccuracy}%</p>
                </div>
                <Award className="w-10 h-10 text-orange-600 opacity-50" />
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Search & Filter */}
        <div className="flex gap-4 mb-6">
          <div className="flex-1">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
              <input
                type="text"
                placeholder="Search datasets, workspaces, or models..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
          </div>
          <select
            value={sortBy}
            onChange={(e) => setSortBy(e.target.value)}
            className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
          >
            <option value="date">Sort by Date</option>
            <option value="accuracy">Sort by Accuracy</option>
            <option value="models">Sort by Models Count</option>
          </select>
        </div>
      </div>

      {/* Dataset Cards */}
      <div className="max-w-7xl mx-auto space-y-4">
        {!data || !data.datasets || data.datasets.length === 0 ? (
          <Card className="p-12 text-center">
            <Database className="w-16 h-16 mx-auto text-gray-400 mb-4" />
            <h3 className="text-xl font-semibold text-gray-700 mb-2">No Training History Yet</h3>
            <p className="text-gray-600">Upload a dataset and run Predictive Analysis to see training metadata here</p>
          </Card>
        ) : (
          data.datasets.map((dataset) => (
            <Card key={dataset.dataset_id} className="overflow-hidden">
              {/* Dataset Header */}
              <div
                className="p-4 bg-gradient-to-r from-blue-50 to-indigo-50 cursor-pointer hover:from-blue-100 hover:to-indigo-100 transition"
                onClick={() => toggleDataset(dataset.dataset_id)}
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    {expandedDatasets[dataset.dataset_id] ? (
                      <ChevronDown className="w-5 h-5 text-blue-600" />
                    ) : (
                      <ChevronRight className="w-5 h-5 text-blue-600" />
                    )}
                    <Database className="w-6 h-6 text-blue-600" />
                    <div>
                      <h3 className="text-lg font-semibold text-gray-900">{dataset.dataset_name}</h3>
                      <p className="text-sm text-gray-600">
                        {dataset.total_workspaces} workspace{dataset.total_workspaces !== 1 ? 's' : ''}
                      </p>
                    </div>
                  </div>
                  <div className="flex items-center gap-3">
                    <Button
                      onClick={(e) => {
                        e.stopPropagation();
                        exportToCSV(dataset);
                      }}
                      variant="outline"
                      size="sm"
                    >
                      <Download className="w-4 h-4 mr-2" />
                      Export
                    </Button>
                  </div>
                </div>
              </div>

              {/* Workspaces (Nested) */}
              {expandedDatasets[dataset.dataset_id] && (
                <div className="p-4 space-y-3">
                  {dataset.workspaces && dataset.workspaces.length > 0 ? (
                    dataset.workspaces.map((workspace, wsIdx) => {
                      const workspaceKey = `${dataset.dataset_id}-${workspace.workspace_name}`;
                      const isRecent = workspace.created_at && 
                        (new Date() - new Date(workspace.created_at)) < 86400000; // 24 hours
                      
                      return (
                        <Card
                          key={workspaceKey}
                          className={`border-l-4 ${isRecent ? 'border-l-green-500 bg-green-50' : 'border-l-gray-300'}`}
                        >
                          <div
                            className="p-3 cursor-pointer hover:bg-gray-50 transition"
                            onClick={() => toggleWorkspace(workspaceKey)}
                          >
                            <div className="flex items-center justify-between">
                              <div className="flex items-center gap-3">
                                {expandedWorkspaces[workspaceKey] ? (
                                  <ChevronDown className="w-4 h-4 text-gray-600" />
                                ) : (
                                  <ChevronRight className="w-4 h-4 text-gray-600" />
                                )}
                                <FolderOpen className={`w-5 h-5 ${isRecent ? 'text-green-600' : 'text-gray-600'}`} />
                                <div>
                                  <h4 className="font-semibold text-gray-900 flex items-center gap-2">
                                    {workspace.workspace_name}
                                    {isRecent && (
                                      <span className="text-xs bg-green-500 text-white px-2 py-0.5 rounded-full">New</span>
                                    )}
                                  </h4>
                                  <p className="text-xs text-gray-600">
                                    {workspace.total_models} model{workspace.total_models !== 1 ? 's' : ''} • 
                                    {formatDate(workspace.created_at)} • 
                                    {workspace.size_kb ? `${(workspace.size_kb / 1024).toFixed(1)} MB` : 'N/A'}
                                  </p>
                                </div>
                              </div>
                            </div>
                          </div>

                          {/* Training Runs (Nested) */}
                          {expandedWorkspaces[workspaceKey] && workspace.training_runs && (
                            <div className="px-6 pb-3 space-y-2">
                              {workspace.training_runs.length > 0 ? (
                                workspace.training_runs.map((run, runIdx) => (
                                  <div
                                    key={runIdx}
                                    className="flex items-center justify-between p-3 bg-white rounded border border-gray-200 hover:border-blue-300 transition"
                                  >
                                    <div className="flex items-center gap-4">
                                      <div className={`w-2 h-2 rounded-full ${getMetricColor(run.metrics).replace('text-', 'bg-')}`}></div>
                                      <div>
                                        <p className="font-medium text-gray-900">{run.model_type}</p>
                                        <p className="text-xs text-gray-600">Target: {run.target_variable}</p>
                                      </div>
                                    </div>
                                    <div className="flex items-center gap-6">
                                      <div className="text-right">
                                        <p className={`font-semibold ${getMetricColor(run.metrics)}`}>
                                          {getMetricDisplay(run.metrics)}
                                        </p>
                                        <p className="text-xs text-gray-500">
                                          <Clock className="w-3 h-3 inline mr-1" />
                                          {run.training_duration?.toFixed(1)}s
                                        </p>
                                      </div>
                                      <div className="text-xs text-gray-500">
                                        {formatDate(run.created_at)}
                                      </div>
                                    </div>
                                  </div>
                                ))
                              ) : (
                                <p className="text-sm text-gray-500 text-center py-4">No training runs yet</p>
                              )}
                            </div>
                          )}
                        </Card>
                      );
                    })
                  ) : (
                    <p className="text-sm text-gray-500 text-center py-4">No workspaces saved yet</p>
                  )}
                </div>
              )}
            </Card>
          ))
        )}
      </div>
    </div>
  );
};

export default TrainingMetadataPage;