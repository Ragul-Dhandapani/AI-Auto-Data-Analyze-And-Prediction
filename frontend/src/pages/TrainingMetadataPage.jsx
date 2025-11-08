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
  const [filterProblemType, setFilterProblemType] = useState('all');
  const [sortBy, setSortBy] = useState('date');
  const [dateRange, setDateRange] = useState({ start: '', end: '' });
  const [comparisonMode, setComparisonMode] = useState(false);
  const [selectedRuns, setSelectedRuns] = useState([]);
  const [showComparisonModal, setShowComparisonModal] = useState(false);
  const [expandedRunDetails, setExpandedRunDetails] = useState({});

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
      return `${(accuracy * 100).toFixed(1)}%`;
    }
    if (r2 !== undefined && r2 !== null) {
      return `${(r2 * 100).toFixed(1)}%`;
    }
    return 'N/A';
  };

  const getAllMetrics = (metrics) => {
    if (!metrics) return {};
    
    return {
      // Classification metrics
      accuracy: metrics.accuracy,
      precision: metrics.precision,
      recall: metrics.recall,
      f1_score: metrics.f1_score,
      roc_auc: metrics.roc_auc,
      // Regression metrics
      r2_score: metrics.r2_score,
      rmse: metrics.rmse,
      mae: metrics.mae,
      mse: metrics.mse
    };
  };

  const getMetricColor = (metrics) => {
    if (!metrics) return 'text-gray-500';
    
    const value = metrics.accuracy || metrics.r2_score || 0;
    if (value >= 0.8) return 'text-green-600';
    if (value >= 0.6) return 'text-yellow-600';
    return 'text-red-600';
  };
  
  const getBestRun = (workspace) => {
    if (!workspace.training_runs || workspace.training_runs.length === 0) return null;
    
    return workspace.training_runs.reduce((best, run) => {
      const bestMetric = best.metrics?.accuracy || best.metrics?.r2_score || 0;
      const runMetric = run.metrics?.accuracy || run.metrics?.r2_score || 0;
      return runMetric > bestMetric ? run : best;
    }, workspace.training_runs[0]);
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
  
  // Filtered and sorted datasets
  const filteredData = useMemo(() => {
    if (!data || !data.datasets) return null;
    
    let filtered = data.datasets.map(dataset => {
      // Filter workspaces and training runs
      const filteredWorkspaces = dataset.workspaces
        .map(workspace => {
          let filteredRuns = workspace.training_runs.filter(run => {
            // Search filter
            if (searchQuery) {
              const query = searchQuery.toLowerCase();
              const matches = 
                dataset.dataset_name.toLowerCase().includes(query) ||
                workspace.workspace_name.toLowerCase().includes(query) ||
                run.model_type.toLowerCase().includes(query) ||
                run.target_variable.toLowerCase().includes(query);
              if (!matches) return false;
            }
            
            // Problem type filter
            if (filterProblemType !== 'all' && run.problem_type !== filterProblemType) {
              return false;
            }
            
            // Date range filter
            if (dateRange.start && new Date(run.created_at) < new Date(dateRange.start)) {
              return false;
            }
            if (dateRange.end && new Date(run.created_at) > new Date(dateRange.end)) {
              return false;
            }
            
            return true;
          });
          
          return {
            ...workspace,
            training_runs: filteredRuns,
            total_models: filteredRuns.length
          };
        })
        .filter(ws => ws.training_runs.length > 0); // Only show workspaces with matching runs
      
      return {
        ...dataset,
        workspaces: filteredWorkspaces,
        total_workspaces: filteredWorkspaces.length
      };
    }).filter(ds => ds.workspaces.length > 0); // Only show datasets with matching workspaces
    
    // Sort datasets
    if (sortBy === 'accuracy') {
      filtered.sort((a, b) => {
        const aAvg = calculateAvgAccuracy(a);
        const bAvg = calculateAvgAccuracy(b);
        return bAvg - aAvg;
      });
    } else if (sortBy === 'models') {
      filtered.sort((a, b) => {
        const aCount = a.workspaces.reduce((sum, ws) => sum + ws.total_models, 0);
        const bCount = b.workspaces.reduce((sum, ws) => sum + ws.total_models, 0);
        return bCount - aCount;
      });
    } else if (sortBy === 'date') {
      filtered.sort((a, b) => {
        const aDate = a.workspaces[0]?.training_runs[0]?.created_at || '';
        const bDate = b.workspaces[0]?.training_runs[0]?.created_at || '';
        return new Date(bDate) - new Date(aDate);
      });
    }
    
    return { ...data, datasets: filtered };
  }, [data, searchQuery, filterProblemType, dateRange, sortBy]);
  
  const calculateAvgAccuracy = (dataset) => {
    let totalAcc = 0;
    let count = 0;
    dataset.workspaces.forEach(ws => {
      ws.training_runs.forEach(run => {
        const acc = run.metrics?.accuracy || run.metrics?.r2_score;
        if (acc) {
          totalAcc += acc;
          count++;
        }
      });
    });
    return count > 0 ? totalAcc / count : 0;
  };

  const exportToCSV = (dataset) => {
    // Export training history as CSV
    const rows = [];
    rows.push(['Dataset', 'Workspace', 'Model Type', 'Target', 'Problem Type', 'Accuracy/R²', 'Precision', 'Recall', 'F1', 'RMSE', 'MAE', 'Duration', 'Date']);
    
    dataset.workspaces.forEach(workspace => {
      workspace.training_runs.forEach(run => {
        const metrics = getAllMetrics(run.metrics);
        rows.push([
          dataset.dataset_name,
          workspace.workspace_name,
          run.model_type,
          run.target_variable,
          run.problem_type || 'N/A',
          getMetricDisplay(run.metrics),
          metrics.precision?.toFixed(3) || 'N/A',
          metrics.recall?.toFixed(3) || 'N/A',
          metrics.f1_score?.toFixed(3) || 'N/A',
          metrics.rmse?.toFixed(3) || 'N/A',
          metrics.mae?.toFixed(3) || 'N/A',
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
  
  const toggleRunSelection = (run, datasetName, workspaceName) => {
    const runKey = `${run.id}-${run.model_type}`;
    const existing = selectedRuns.find(r => `${r.id}-${r.model_type}` === runKey);
    
    if (existing) {
      setSelectedRuns(selectedRuns.filter(r => `${r.id}-${r.model_type}` !== runKey));
    } else {
      setSelectedRuns([...selectedRuns, { ...run, _dataset: datasetName, _workspace: workspaceName }]);
    }
  };
  
  const isRunSelected = (run) => {
    const runKey = `${run.id}-${run.model_type}`;
    return selectedRuns.some(r => `${r.id}-${r.model_type}` === runKey);
  };
  
  const toggleRunDetails = (runKey) => {
    setExpandedRunDetails(prev => ({
      ...prev,
      [runKey]: !prev[runKey]
    }));
  };

  // Calculate summary stats using filtered data
  const stats = filteredData ? {
    totalDatasets: filteredData.datasets?.length || 0,
    totalWorkspaces: filteredData.datasets?.reduce((sum, ds) => sum + ds.total_workspaces, 0) || 0,
    totalModels: filteredData.datasets?.reduce((sum, ds) => 
      sum + ds.workspaces.reduce((wsum, ws) => wsum + ws.total_models, 0), 0
    ) || 0,
    avgAccuracy: (() => {
      let totalAcc = 0;
      let count = 0;
      filteredData.datasets?.forEach(ds => {
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
          <div className="flex gap-2">
            <Button 
              onClick={() => {
                setComparisonMode(!comparisonMode);
                if (comparisonMode) setSelectedRuns([]);
              }}
              variant={comparisonMode ? "default" : "outline"}
              className={comparisonMode ? "bg-blue-600 text-white" : ""}
            >
              <GitCompare className="w-4 h-4 mr-2" />
              {comparisonMode ? 'Exit Compare' : 'Compare Models'}
            </Button>
            {comparisonMode && selectedRuns.length > 1 && (
              <Button onClick={() => setShowComparisonModal(true)} className="bg-green-600 text-white">
                Compare ({selectedRuns.length})
              </Button>
            )}
            <Button onClick={loadMetadata} variant="outline">
              <RefreshCw className="w-4 h-4 mr-2" />
              Refresh
            </Button>
          </div>
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
        <div className="grid grid-cols-12 gap-4 mb-6">
          <div className="col-span-5">
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
          
          <div className="col-span-2">
            <select
              value={filterProblemType}
              onChange={(e) => setFilterProblemType(e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            >
              <option value="all">All Types</option>
              <option value="classification">Classification</option>
              <option value="regression">Regression</option>
              <option value="clustering">Clustering</option>
            </select>
          </div>
          
          <div className="col-span-2">
            <input
              type="date"
              placeholder="Start Date"
              value={dateRange.start}
              onChange={(e) => setDateRange({...dateRange, start: e.target.value})}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            />
          </div>
          
          <div className="col-span-2">
            <input
              type="date"
              placeholder="End Date"
              value={dateRange.end}
              onChange={(e) => setDateRange({...dateRange, end: e.target.value})}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            />
          </div>
          
          <div className="col-span-1">
            {(searchQuery || filterProblemType !== 'all' || dateRange.start || dateRange.end) && (
              <Button 
                onClick={() => {
                  setSearchQuery('');
                  setFilterProblemType('all');
                  setDateRange({ start: '', end: '' });
                }}
                variant="outline"
                className="w-full"
              >
                <X className="w-4 h-4" />
              </Button>
            )}
          </div>
        </div>
        
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center gap-2 text-sm text-gray-600">
            <Filter className="w-4 h-4" />
            <span>Showing {stats.totalModels} training runs across {stats.totalWorkspaces} workspaces</span>
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
        {!filteredData || !filteredData.datasets || filteredData.datasets.length === 0 ? (
          <Card className="p-12 text-center">
            <Database className="w-16 h-16 mx-auto text-gray-400 mb-4" />
            <h3 className="text-xl font-semibold text-gray-700 mb-2">
              {(searchQuery || filterProblemType !== 'all' || dateRange.start || dateRange.end) 
                ? 'No Matching Training Runs' 
                : 'No Training History Yet'}
            </h3>
            <p className="text-gray-600">
              {(searchQuery || filterProblemType !== 'all' || dateRange.start || dateRange.end)
                ? 'Try adjusting your filters or search query'
                : 'Upload a dataset and run Predictive Analysis to see training metadata here'}
            </p>
          </Card>
        ) : (
          filteredData.datasets.map((dataset) => (
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
                                workspace.training_runs.map((run, runIdx) => {
                                  const runKey = `${run.id}-${runIdx}`;
                                  const bestRun = getBestRun(workspace);
                                  const isBest = bestRun && bestRun.id === run.id && bestRun.model_type === run.model_type;
                                  const allMetrics = getAllMetrics(run.metrics);
                                  const isExpanded = expandedRunDetails[runKey];
                                  
                                  return (
                                    <div
                                      key={runIdx}
                                      className={`bg-white rounded border ${
                                        isBest ? 'border-green-400 shadow-md' : 'border-gray-200'
                                      } hover:border-blue-300 transition overflow-hidden`}
                                    >
                                      <div className="flex items-center justify-between p-3">
                                        <div className="flex items-center gap-4 flex-1">
                                          {comparisonMode && (
                                            <input
                                              type="checkbox"
                                              checked={isRunSelected(run)}
                                              onChange={() => toggleRunSelection(run, dataset.dataset_name, workspace.workspace_name)}
                                              className="w-4 h-4 text-blue-600 cursor-pointer"
                                            />
                                          )}
                                          <div className={`w-2 h-2 rounded-full ${getMetricColor(run.metrics).replace('text-', 'bg-')}`}></div>
                                          <div className="flex-1">
                                            <div className="flex items-center gap-2">
                                              <p className="font-medium text-gray-900">{run.model_type}</p>
                                              {isBest && (
                                                <span className="text-xs bg-green-500 text-white px-2 py-0.5 rounded-full flex items-center gap-1">
                                                  <Award className="w-3 h-3" />
                                                  Best
                                                </span>
                                              )}
                                              <span className="text-xs bg-blue-100 text-blue-700 px-2 py-0.5 rounded">
                                                {run.problem_type || 'N/A'}
                                              </span>
                                            </div>
                                            <p className="text-xs text-gray-600">Target: {run.target_variable}</p>
                                          </div>
                                        </div>
                                        <div className="flex items-center gap-4">
                                          <div className="text-right">
                                            <p className={`font-semibold text-lg ${getMetricColor(run.metrics)}`}>
                                              {getMetricDisplay(run.metrics)}
                                            </p>
                                            <p className="text-xs text-gray-500">
                                              <Clock className="w-3 h-3 inline mr-1" />
                                              {run.training_duration?.toFixed(1)}s
                                            </p>
                                          </div>
                                          <div className="text-xs text-gray-500 min-w-[80px] text-right">
                                            {formatDate(run.created_at)}
                                          </div>
                                          <Button
                                            onClick={() => toggleRunDetails(runKey)}
                                            variant="ghost"
                                            size="sm"
                                          >
                                            {isExpanded ? <ChevronDown className="w-4 h-4" /> : <ChevronRight className="w-4 h-4" />}
                                          </Button>
                                        </div>
                                      </div>
                                      
                                      {/* Expanded Details */}
                                      {isExpanded && (
                                        <div className="px-6 pb-4 bg-gray-50 border-t border-gray-200">
                                          <div className="grid grid-cols-3 gap-4 mt-3">
                                            {/* Classification Metrics */}
                                            {allMetrics.accuracy !== undefined && (
                                              <>
                                                <div className="bg-white p-3 rounded shadow-sm">
                                                  <p className="text-xs text-gray-600 mb-1">Accuracy</p>
                                                  <p className="text-lg font-semibold text-green-600">
                                                    {(allMetrics.accuracy * 100).toFixed(2)}%
                                                  </p>
                                                </div>
                                                {allMetrics.precision !== undefined && (
                                                  <div className="bg-white p-3 rounded shadow-sm">
                                                    <p className="text-xs text-gray-600 mb-1">Precision</p>
                                                    <p className="text-lg font-semibold text-blue-600">
                                                      {(allMetrics.precision * 100).toFixed(2)}%
                                                    </p>
                                                  </div>
                                                )}
                                                {allMetrics.recall !== undefined && (
                                                  <div className="bg-white p-3 rounded shadow-sm">
                                                    <p className="text-xs text-gray-600 mb-1">Recall</p>
                                                    <p className="text-lg font-semibold text-purple-600">
                                                      {(allMetrics.recall * 100).toFixed(2)}%
                                                    </p>
                                                  </div>
                                                )}
                                                {allMetrics.f1_score !== undefined && (
                                                  <div className="bg-white p-3 rounded shadow-sm">
                                                    <p className="text-xs text-gray-600 mb-1">F1 Score</p>
                                                    <p className="text-lg font-semibold text-indigo-600">
                                                      {(allMetrics.f1_score * 100).toFixed(2)}%
                                                    </p>
                                                  </div>
                                                )}
                                                {allMetrics.roc_auc !== undefined && (
                                                  <div className="bg-white p-3 rounded shadow-sm">
                                                    <p className="text-xs text-gray-600 mb-1">ROC AUC</p>
                                                    <p className="text-lg font-semibold text-pink-600">
                                                      {(allMetrics.roc_auc * 100).toFixed(2)}%
                                                    </p>
                                                  </div>
                                                )}
                                              </>
                                            )}
                                            
                                            {/* Regression Metrics */}
                                            {allMetrics.r2_score !== undefined && (
                                              <>
                                                <div className="bg-white p-3 rounded shadow-sm">
                                                  <p className="text-xs text-gray-600 mb-1">R² Score</p>
                                                  <p className="text-lg font-semibold text-green-600">
                                                    {(allMetrics.r2_score * 100).toFixed(2)}%
                                                  </p>
                                                </div>
                                                {allMetrics.rmse !== undefined && (
                                                  <div className="bg-white p-3 rounded shadow-sm">
                                                    <p className="text-xs text-gray-600 mb-1">RMSE</p>
                                                    <p className="text-lg font-semibold text-orange-600">
                                                      {allMetrics.rmse.toFixed(4)}
                                                    </p>
                                                  </div>
                                                )}
                                                {allMetrics.mae !== undefined && (
                                                  <div className="bg-white p-3 rounded shadow-sm">
                                                    <p className="text-xs text-gray-600 mb-1">MAE</p>
                                                    <p className="text-lg font-semibold text-red-600">
                                                      {allMetrics.mae.toFixed(4)}
                                                    </p>
                                                  </div>
                                                )}
                                              </>
                                            )}
                                          </div>
                                          
                                          {/* Model Parameters */}
                                          {run.model_params_json && (
                                            <div className="mt-3 bg-white p-3 rounded shadow-sm">
                                              <div className="flex items-center gap-2 mb-2">
                                                <Settings className="w-4 h-4 text-gray-600" />
                                                <p className="text-xs font-semibold text-gray-700">Hyperparameters</p>
                                              </div>
                                              <pre className="text-xs text-gray-600 overflow-x-auto">
                                                {JSON.stringify(JSON.parse(run.model_params_json), null, 2)}
                                              </pre>
                                            </div>
                                          )}
                                        </div>
                                      )}
                                    </div>
                                  );
                                })
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
      
      {/* Comparison Modal */}
      {showComparisonModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-6">
          <div className="bg-white rounded-lg max-w-7xl w-full max-h-[90vh] overflow-y-auto">
            <div className="sticky top-0 bg-white border-b border-gray-200 p-4 flex items-center justify-between">
              <div className="flex items-center gap-3">
                <GitCompare className="w-6 h-6 text-blue-600" />
                <h2 className="text-2xl font-bold text-gray-900">Model Comparison</h2>
                <span className="text-sm text-gray-600">({selectedRuns.length} models)</span>
              </div>
              <Button onClick={() => setShowComparisonModal(false)} variant="ghost">
                <X className="w-5 h-5" />
              </Button>
            </div>
            
            <div className="p-6">
              {/* Comparison Table */}
              <div className="overflow-x-auto">
                <table className="w-full border-collapse">
                  <thead>
                    <tr className="bg-gray-100">
                      <th className="p-3 text-left text-sm font-semibold text-gray-700 border">Attribute</th>
                      {selectedRuns.map((run, idx) => (
                        <th key={idx} className="p-3 text-left text-sm font-semibold text-gray-700 border">
                          Model {idx + 1}
                        </th>
                      ))}
                    </tr>
                  </thead>
                  <tbody>
                    <tr>
                      <td className="p-3 font-medium text-gray-700 border bg-gray-50">Dataset</td>
                      {selectedRuns.map((run, idx) => (
                        <td key={idx} className="p-3 text-sm border">{run._dataset}</td>
                      ))}
                    </tr>
                    <tr>
                      <td className="p-3 font-medium text-gray-700 border bg-gray-50">Workspace</td>
                      {selectedRuns.map((run, idx) => (
                        <td key={idx} className="p-3 text-sm border">{run._workspace}</td>
                      ))}
                    </tr>
                    <tr>
                      <td className="p-3 font-medium text-gray-700 border bg-gray-50">Model Type</td>
                      {selectedRuns.map((run, idx) => (
                        <td key={idx} className="p-3 text-sm border font-semibold">{run.model_type}</td>
                      ))}
                    </tr>
                    <tr>
                      <td className="p-3 font-medium text-gray-700 border bg-gray-50">Problem Type</td>
                      {selectedRuns.map((run, idx) => (
                        <td key={idx} className="p-3 text-sm border">
                          <span className="bg-blue-100 text-blue-700 px-2 py-1 rounded text-xs">
                            {run.problem_type || 'N/A'}
                          </span>
                        </td>
                      ))}
                    </tr>
                    <tr>
                      <td className="p-3 font-medium text-gray-700 border bg-gray-50">Target Variable</td>
                      {selectedRuns.map((run, idx) => (
                        <td key={idx} className="p-3 text-sm border">{run.target_variable}</td>
                      ))}
                    </tr>
                    <tr className="bg-yellow-50">
                      <td className="p-3 font-medium text-gray-700 border">Primary Metric</td>
                      {selectedRuns.map((run, idx) => {
                        const metric = run.metrics?.accuracy || run.metrics?.r2_score;
                        return (
                          <td key={idx} className={`p-3 text-lg font-bold border ${getMetricColor(run.metrics)}`}>
                            {metric ? (metric * 100).toFixed(2) + '%' : 'N/A'}
                          </td>
                        );
                      })}
                    </tr>
                    
                    {/* Classification Metrics */}
                    {selectedRuns.some(r => r.metrics?.accuracy !== undefined) && (
                      <>
                        <tr>
                          <td className="p-3 font-medium text-gray-700 border bg-gray-50">Precision</td>
                          {selectedRuns.map((run, idx) => {
                            const m = getAllMetrics(run.metrics);
                            return (
                              <td key={idx} className="p-3 text-sm border">
                                {m.precision !== undefined ? (m.precision * 100).toFixed(2) + '%' : 'N/A'}
                              </td>
                            );
                          })}
                        </tr>
                        <tr>
                          <td className="p-3 font-medium text-gray-700 border bg-gray-50">Recall</td>
                          {selectedRuns.map((run, idx) => {
                            const m = getAllMetrics(run.metrics);
                            return (
                              <td key={idx} className="p-3 text-sm border">
                                {m.recall !== undefined ? (m.recall * 100).toFixed(2) + '%' : 'N/A'}
                              </td>
                            );
                          })}
                        </tr>
                        <tr>
                          <td className="p-3 font-medium text-gray-700 border bg-gray-50">F1 Score</td>
                          {selectedRuns.map((run, idx) => {
                            const m = getAllMetrics(run.metrics);
                            return (
                              <td key={idx} className="p-3 text-sm border">
                                {m.f1_score !== undefined ? (m.f1_score * 100).toFixed(2) + '%' : 'N/A'}
                              </td>
                            );
                          })}
                        </tr>
                      </>
                    )}
                    
                    {/* Regression Metrics */}
                    {selectedRuns.some(r => r.metrics?.r2_score !== undefined) && (
                      <>
                        <tr>
                          <td className="p-3 font-medium text-gray-700 border bg-gray-50">RMSE</td>
                          {selectedRuns.map((run, idx) => {
                            const m = getAllMetrics(run.metrics);
                            return (
                              <td key={idx} className="p-3 text-sm border">
                                {m.rmse !== undefined ? m.rmse.toFixed(4) : 'N/A'}
                              </td>
                            );
                          })}
                        </tr>
                        <tr>
                          <td className="p-3 font-medium text-gray-700 border bg-gray-50">MAE</td>
                          {selectedRuns.map((run, idx) => {
                            const m = getAllMetrics(run.metrics);
                            return (
                              <td key={idx} className="p-3 text-sm border">
                                {m.mae !== undefined ? m.mae.toFixed(4) : 'N/A'}
                              </td>
                            );
                          })}
                        </tr>
                      </>
                    )}
                    
                    <tr>
                      <td className="p-3 font-medium text-gray-700 border bg-gray-50">Training Duration</td>
                      {selectedRuns.map((run, idx) => (
                        <td key={idx} className="p-3 text-sm border">
                          {run.training_duration ? run.training_duration.toFixed(2) + 's' : 'N/A'}
                        </td>
                      ))}
                    </tr>
                    <tr>
                      <td className="p-3 font-medium text-gray-700 border bg-gray-50">Trained At</td>
                      {selectedRuns.map((run, idx) => (
                        <td key={idx} className="p-3 text-sm border">{formatDate(run.created_at)}</td>
                      ))}
                    </tr>
                  </tbody>
                </table>
              </div>
              
              {/* Performance Comparison Chart */}
              <div className="mt-6">
                <h3 className="text-lg font-semibold mb-4">Performance Comparison</h3>
                <Plot
                  data={[
                    {
                      x: selectedRuns.map((r, i) => `Model ${i + 1}: ${r.model_type}`),
                      y: selectedRuns.map(r => {
                        const metric = r.metrics?.accuracy || r.metrics?.r2_score || 0;
                        return (metric * 100).toFixed(2);
                      }),
                      type: 'bar',
                      marker: {
                        color: selectedRuns.map(r => {
                          const metric = r.metrics?.accuracy || r.metrics?.r2_score || 0;
                          if (metric >= 0.8) return '#16a34a';
                          if (metric >= 0.6) return '#ca8a04';
                          return '#dc2626';
                        })
                      },
                      text: selectedRuns.map(r => {
                        const metric = r.metrics?.accuracy || r.metrics?.r2_score || 0;
                        return `${(metric * 100).toFixed(2)}%`;
                      }),
                      textposition: 'auto',
                    }
                  ]}
                  layout={{
                    title: 'Model Performance Comparison',
                    xaxis: { title: 'Models' },
                    yaxis: { title: 'Accuracy/R² Score (%)' },
                    height: 400,
                    showlegend: false
                  }}
                  config={{ responsive: true }}
                  style={{ width: '100%' }}
                />
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default TrainingMetadataPage;