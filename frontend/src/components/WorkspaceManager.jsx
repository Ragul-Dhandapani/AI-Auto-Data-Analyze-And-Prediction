import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { toast } from 'sonner';
import { Loader2, Plus, Trash2, FolderOpen, TrendingUp, Database, Activity, Home, ChevronDown, ChevronRight, FileText, BarChart3, Eye, Award, Settings, Calendar, Table as TableIcon, LineChart, Sparkles } from 'lucide-react';
import { LineChart as RechartsLine, Line, XAxis, YAxis, CartesianGrid, Tooltip as RechartsTooltip, Legend, ResponsiveContainer, BarChart as RechartsBar, Bar } from 'recharts';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;

const WorkspaceManager = () => {
  const navigate = useNavigate();
  const [workspaces, setWorkspaces] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [createModalOpen, setCreateModalOpen] = useState(false);
  const [newWorkspace, setNewWorkspace] = useState({ name: '', description: '', tags: '' });
  const [creating, setCreating] = useState(false);
  const [holisticScores, setHolisticScores] = useState({});
  const [loadingScores, setLoadingScores] = useState({});
  const [expandedWorkspaces, setExpandedWorkspaces] = useState({});
  const [workspaceDatasets, setWorkspaceDatasets] = useState({});
  const [savedAnalyses, setSavedAnalyses] = useState({});
  const [analysisDetails, setAnalysisDetails] = useState({});
  const [loadingDatasets, setLoadingDatasets] = useState({});
  const [dateRange, setDateRange] = useState('all'); // all, week, month, quarter
  const [viewMode, setViewMode] = useState('cards'); // cards, table, chart
  const [selectedQuery, setSelectedQuery] = useState(null);

  useEffect(() => {
    loadWorkspaces();
  }, []);

  const loadWorkspaces = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`${BACKEND_URL}/api/workspace/list`);
      const workspaceList = response.data.workspaces || [];
      setWorkspaces(workspaceList);
      
      await loadHolisticScores(workspaceList);
    } catch (error) {
      console.error('Failed to load workspaces:', error);
      toast.error('Failed to load workspaces');
    } finally {
      setLoading(false);
    }
  };

  const loadHolisticScores = async (workspaceList) => {
    const scores = {};
    const loadingStates = {};
    
    await Promise.all(
      workspaceList.map(async (workspace) => {
        try {
          loadingStates[workspace.id] = true;
          const response = await axios.get(`${BACKEND_URL}/api/workspace/${workspace.id}/holistic-score`);
          scores[workspace.id] = response.data;
        } catch (error) {
          console.error(`Failed to load holistic score for workspace ${workspace.id}:`, error);
          scores[workspace.id] = {
            score: 0,
            grade: 'N/A',
            message: 'No data available'
          };
        } finally {
          loadingStates[workspace.id] = false;
        }
      })
    );
    
    setHolisticScores(scores);
    setLoadingScores(loadingStates);
  };

  const toggleWorkspace = async (workspaceId) => {
    const isExpanded = expandedWorkspaces[workspaceId];
    
    if (!isExpanded) {
      await loadWorkspaceDatasets(workspaceId);
    }
    
    setExpandedWorkspaces(prev => ({
      ...prev,
      [workspaceId]: !isExpanded
    }));
  };

  const loadWorkspaceDatasets = async (workspaceId) => {
    try {
      setLoadingDatasets(prev => ({ ...prev, [workspaceId]: true }));
      
      console.log('🔍 Loading datasets for workspace:', workspaceId);
      const response = await axios.get(`${BACKEND_URL}/api/datasource/datasets`);
      const allDatasets = response.data.datasets || [];
      console.log('📊 Total datasets fetched:', allDatasets.length);
      
      const workspaceDatasetsList = allDatasets.filter(d => d.workspace_id === workspaceId);
      console.log('✅ Datasets in this workspace:', workspaceDatasetsList.length);
      console.log('📁 Dataset names:', workspaceDatasetsList.map(d => d.name));
      
      setWorkspaceDatasets(prev => ({
        ...prev,
        [workspaceId]: workspaceDatasetsList
      }));
      
      for (const dataset of workspaceDatasetsList) {
        console.log('🔄 Loading analyses for dataset:', dataset.id);
        await loadDatasetAnalyses(dataset.id);
      }
    } catch (error) {
      console.error('❌ Failed to load datasets:', error);
      toast.error('Failed to load datasets for workspace');
    } finally {
      setLoadingDatasets(prev => ({ ...prev, [workspaceId]: false }));
    }
  };

  const loadDatasetAnalyses = async (datasetId) => {
    try {
      console.log('📊 Fetching saved states for dataset:', datasetId);
      const response = await axios.get(`${BACKEND_URL}/api/analysis/saved-states/${datasetId}`);
      const states = response.data.states || [];
      console.log('💾 Saved states found:', states.length);
      console.log('📝 State names:', states.map(s => s.state_name || s.workspace_name));
      
      setSavedAnalyses(prev => ({
        ...prev,
        [datasetId]: states
      }));
      
      // Load full details for each analysis
      for (const state of states) {
        console.log('🔍 Loading details for state:', state.id, state.state_name);
        await loadAnalysisDetails(state.id);
      }
    } catch (error) {
      console.error(`❌ Failed to load analyses for dataset ${datasetId}:`, error);
    }
  };

  const loadAnalysisDetails = async (stateId) => {
    try {
      console.log('⏳ Fetching analysis details for:', stateId);
      const response = await axios.get(`${BACKEND_URL}/api/analysis/load-state/${stateId}`);
      const details = response.data;
      console.log('📦 Received details, keys:', Object.keys(details));
      
      // Parse analysis_results if it's a JSON string
      let analysisData = details.analysis_results || details.analysis_data || {};
      console.log('🔧 Analysis data type:', typeof analysisData);
      
      if (typeof analysisData === 'string') {
        console.log('📝 Parsing JSON string...');
        try {
          analysisData = JSON.parse(analysisData);
          console.log('✅ Parsed successfully, ml_models count:', analysisData.ml_models?.length || 0);
        } catch (e) {
          console.error('❌ Failed to parse analysis_results:', e);
          analysisData = {};
        }
      } else {
        console.log('✅ Already an object, ml_models count:', analysisData.ml_models?.length || 0);
      }
      
      // Normalize the structure
      const normalizedDetails = {
        ...details,
        analysis_data: analysisData
      };
      
      console.log('💾 Storing normalized details for:', stateId);
      setAnalysisDetails(prev => ({
        ...prev,
        [stateId]: normalizedDetails
      }));
    } catch (error) {
      console.error(`❌ Failed to load analysis details for ${stateId}:`, error);
    }
  };

  const viewAnalysis = async (analysis, dataset) => {
    try {
      // Load the analysis state first
      const response = await axios.get(`${BACKEND_URL}/api/analysis/load-state/${analysis.id}`);
      const stateData = response.data;
      
      // Parse analysis_results if it's a JSON string
      let analysisData = stateData.analysis_results || stateData.analysis_data;
      if (typeof analysisData === 'string') {
        try {
          analysisData = JSON.parse(analysisData);
        } catch (e) {
          console.error('Failed to parse analysis data:', e);
          toast.error('Failed to parse analysis data');
          return;
        }
      }
      
      // Store in localStorage for the dashboard to pick up
      localStorage.setItem('loadAnalysisOnMount', JSON.stringify({
        stateId: analysis.id,
        datasetId: dataset.id,
        stateName: analysis.state_name,
        analysisData: analysisData
      }));
      
      // Navigate to dashboard
      navigate('/');
      
      // Small delay then reload to trigger loading
      setTimeout(() => {
        window.location.reload();
      }, 100);
    } catch (error) {
      console.error('Failed to load analysis:', error);
      toast.error('Failed to load analysis. Please try again.');
    }
  };

  const createWorkspace = async () => {
    if (!newWorkspace.name.trim()) {
      toast.error('Workspace name is required');
      return;
    }

    try {
      setCreating(true);
      const tags = newWorkspace.tags.split(',').map(t => t.trim()).filter(t => t);
      await axios.post(`${BACKEND_URL}/api/workspace/create`, {
        name: newWorkspace.name,
        description: newWorkspace.description,
        tags
      });
      toast.success('Workspace created successfully');
      setCreateModalOpen(false);
      setNewWorkspace({ name: '', description: '', tags: '' });
      loadWorkspaces();
    } catch (error) {
      console.error('Failed to create workspace:', error);
      toast.error('Failed to create workspace');
    } finally {
      setCreating(false);
    }
  };

  const deleteWorkspace = async (workspaceId, workspaceName) => {
    if (!confirm(`Are you sure you want to delete "${workspaceName}"? This action cannot be undone.`)) {
      return;
    }

    try {
      await axios.delete(`${BACKEND_URL}/api/workspace/${workspaceId}`);
      toast.success('Workspace deleted successfully');
      loadWorkspaces();
    } catch (error) {
      console.error('Failed to delete workspace:', error);
      toast.error('Failed to delete workspace');
    }
  };

  const filterAnalysesByDate = (analyses) => {
    if (dateRange === 'all') return analyses;
    
    const now = new Date();
    const cutoff = new Date();
    
    if (dateRange === 'week') cutoff.setDate(now.getDate() - 7);
    else if (dateRange === 'month') cutoff.setMonth(now.getMonth() - 1);
    else if (dateRange === 'quarter') cutoff.setMonth(now.getMonth() - 3);
    
    return analyses.filter(a => new Date(a.created_at) >= cutoff);
  };

  const getDataSourceInfo = (dataset) => {
    // Check for file upload
    if (dataset.storage_type === 'file' || dataset.storage_type === 'gridfs' || dataset.name) {
      return {
        type: 'File Upload',
        detail: dataset.name || dataset.file_name || 'Unknown file',
        icon: '📁'
      };
    } else if (dataset.db_table || dataset.source_type === 'database') {
      return {
        type: 'Database Table',
        detail: dataset.db_table || dataset.name || 'Unknown table',
        icon: '🗄️'
      };
    } else if (dataset.custom_query) {
      return {
        type: 'Custom Query',
        detail: dataset.custom_query.length > 50 ? dataset.custom_query.substring(0, 50) + '...' : dataset.custom_query,
        fullQuery: dataset.custom_query,
        icon: '🔍'
      };
    }
    // Fallback to dataset name if available
    if (dataset.name) {
      return {
        type: 'Dataset',
        detail: dataset.name,
        icon: '📊'
      };
    }
    return { type: 'Unknown', detail: 'N/A', icon: '❓' };
  };

  const getBestModel = (models) => {
    if (!models || models.length === 0) return null;
    return models.reduce((best, current) => {
      const currentScore = current.metrics?.r2_score || current.metrics?.accuracy || 0;
      const bestScore = best.metrics?.r2_score || best.metrics?.accuracy || 0;
      return currentScore > bestScore ? current : best;
    });
  };

  const prepareHistoricalData = (analyses, datasetId) => {
    return analyses
      .filter(a => analysisDetails[a.id])
      .map(a => {
        const details = analysisDetails[a.id];
        const analysisData = details.analysis_data || {};
        const models = analysisData.ml_models || [];
        const bestModel = getBestModel(models);
        const bestScore = bestModel ? (bestModel.metrics?.r2_score || bestModel.metrics?.accuracy || 0) : 0;
        
        return {
          name: a.state_name || 'Unnamed',
          date: new Date(a.created_at).toLocaleDateString(),
          score: bestScore,
          modelCount: models.length,
          timestamp: new Date(a.created_at).getTime()
        };
      })
      .sort((a, b) => a.timestamp - b.timestamp);
  };

  const filteredWorkspaces = workspaces.filter(ws =>
    ws.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    ws.description?.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const getScoreColor = (score) => {
    if (score >= 80) return 'text-green-600 bg-green-50 border-green-200';
    if (score >= 60) return 'text-blue-600 bg-blue-50 border-blue-200';
    if (score >= 40) return 'text-yellow-600 bg-yellow-50 border-yellow-200';
    if (score > 0) return 'text-orange-600 bg-orange-50 border-orange-200';
    return 'text-gray-600 bg-gray-50 border-gray-200';
  };

  const getBestModelScore = (models) => {
    if (!models || models.length === 0) return 0;
    const scores = models.map(m => m.metrics?.r2_score || m.metrics?.accuracy || 0);
    return Math.max(...scores);
  };

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <div className="flex items-center gap-4 mb-2">
            <Button
              onClick={() => navigate('/')}
              variant="outline"
              className="border-gray-300 hover:bg-gray-50"
            >
              <Home className="w-4 h-4 mr-2" />
              Back Home
            </Button>
            <h1 className="text-3xl font-bold">Workspace Manager</h1>
          </div>
          <p className="text-gray-600 mt-1 ml-32">Comprehensive analytics dashboard for all workspaces</p>
        </div>
        <Dialog open={createModalOpen} onOpenChange={setCreateModalOpen}>
          <DialogTrigger asChild>
            <Button className="bg-blue-600 hover:bg-blue-700">
              <Plus className="w-4 h-4 mr-2" />
              New Workspace
            </Button>
          </DialogTrigger>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Create New Workspace</DialogTitle>
            </DialogHeader>
            <div className="space-y-4 mt-4">
              <div>
                <label className="text-sm font-medium">Name *</label>
                <Input
                  placeholder="e.g., Sales Forecasting Q4"
                  value={newWorkspace.name}
                  onChange={(e) => setNewWorkspace({ ...newWorkspace, name: e.target.value })}
                />
              </div>
              <div>
                <label className="text-sm font-medium">Description</label>
                <Input
                  placeholder="Brief description of this workspace"
                  value={newWorkspace.description}
                  onChange={(e) => setNewWorkspace({ ...newWorkspace, description: e.target.value })}
                />
              </div>
              <div>
                <label className="text-sm font-medium">Tags (comma-separated)</label>
                <Input
                  placeholder="e.g., sales, forecasting, Q4"
                  value={newWorkspace.tags}
                  onChange={(e) => setNewWorkspace({ ...newWorkspace, tags: e.target.value })}
                />
              </div>
              <Button
                onClick={createWorkspace}
                disabled={creating}
                className="w-full"
              >
                {creating ? <Loader2 className="w-4 h-4 animate-spin mr-2" /> : null}
                Create Workspace
              </Button>
            </div>
          </DialogContent>
        </Dialog>
      </div>

      {/* Filters and Controls */}
      <Card className="p-4">
        <div className="flex flex-wrap gap-4 items-center justify-between">
          <div className="flex gap-4 items-center flex-1">
            <Input
              placeholder="Search workspaces..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="max-w-md"
            />
            
            <Select value={dateRange} onValueChange={setDateRange}>
              <SelectTrigger className="w-[180px]">
                <SelectValue placeholder="Date Range" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Time</SelectItem>
                <SelectItem value="week">Last 7 Days</SelectItem>
                <SelectItem value="month">Last 30 Days</SelectItem>
                <SelectItem value="quarter">Last Quarter</SelectItem>
              </SelectContent>
            </Select>
          </div>
          
          <div className="flex gap-2">
            <Button
              variant={viewMode === 'cards' ? 'default' : 'outline'}
              size="sm"
              onClick={() => setViewMode('cards')}
            >
              <BarChart3 className="w-4 h-4 mr-2" />
              Cards
            </Button>
            <Button
              variant={viewMode === 'table' ? 'default' : 'outline'}
              size="sm"
              onClick={() => setViewMode('table')}
            >
              <TableIcon className="w-4 h-4 mr-2" />
              Table
            </Button>
            <Button
              variant={viewMode === 'chart' ? 'default' : 'outline'}
              size="sm"
              onClick={() => setViewMode('chart')}
            >
              <LineChart className="w-4 h-4 mr-2" />
              Charts
            </Button>
          </div>
        </div>
      </Card>

      {/* Custom Query Dialog */}
      {selectedQuery && (
        <Dialog open={!!selectedQuery} onOpenChange={() => setSelectedQuery(null)}>
          <DialogContent className="max-w-3xl">
            <DialogHeader>
              <DialogTitle>Custom SQL Query</DialogTitle>
            </DialogHeader>
            <div className="mt-4">
              <pre className="bg-gray-100 p-4 rounded text-sm overflow-x-auto">
                {selectedQuery}
              </pre>
            </div>
          </DialogContent>
        </Dialog>
      )}

      {/* Workspaces List */}
      {loading ? (
        <div className="flex items-center justify-center h-64">
          <Loader2 className="w-8 h-8 animate-spin text-blue-600" />
        </div>
      ) : filteredWorkspaces.length === 0 ? (
        <Card className="p-12 text-center">
          <FolderOpen className="w-16 h-16 mx-auto text-gray-400 mb-4" />
          <h3 className="text-lg font-semibold text-gray-700 mb-2">
            {searchTerm ? 'No workspaces found' : 'No workspaces yet'}
          </h3>
          <p className="text-gray-500 mb-4">
            {searchTerm ? 'Try a different search term' : 'Create your first workspace to get started'}
          </p>
          {!searchTerm && (
            <Button onClick={() => setCreateModalOpen(true)} className="bg-blue-600 hover:bg-blue-700">
              <Plus className="w-4 h-4 mr-2" />
              Create Workspace
            </Button>
          )}
        </Card>
      ) : (
        <div className="space-y-4">
          {filteredWorkspaces.map((workspace) => {
            const scoreData = holisticScores[workspace.id] || {};
            const score = scoreData.score || 0;
            const isExpanded = expandedWorkspaces[workspace.id];
            const datasets = workspaceDatasets[workspace.id] || [];
            const isLoadingDatasets = loadingDatasets[workspace.id];
            
            return (
              <Card key={workspace.id} className="overflow-hidden">
                {/* Workspace Header */}
                <div className="p-6 bg-gradient-to-r from-blue-50 to-purple-50 border-b">
                  <div className="flex justify-between items-start">
                    <div className="flex-1">
                      <div className="flex items-center gap-3 mb-2">
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => toggleWorkspace(workspace.id)}
                          className="p-0 h-auto hover:bg-transparent"
                        >
                          {isExpanded ? 
                            <ChevronDown className="w-5 h-5 text-gray-600" /> : 
                            <ChevronRight className="w-5 h-5 text-gray-600" />
                          }
                        </Button>
                        <h3 className="text-xl font-semibold">{workspace.name}</h3>
                      </div>
                      <p className="text-sm text-gray-600 ml-8">
                        {workspace.description || 'No description'}
                      </p>
                    </div>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => deleteWorkspace(workspace.id, workspace.name)}
                      className="text-red-600 hover:text-red-700 hover:bg-red-50"
                    >
                      <Trash2 className="w-4 h-4" />
                    </Button>
                  </div>

                  {/* Stats */}
                  <div className="grid grid-cols-4 gap-4 mt-4 ml-8">
                    <div className="flex items-center gap-2">
                      <Database className="w-4 h-4 text-blue-600" />
                      <div>
                        <div className="text-xl font-bold">{workspace.dataset_count || 0}</div>
                        <div className="text-xs text-gray-600">Datasets</div>
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      <Activity className="w-4 h-4 text-green-600" />
                      <div>
                        <div className="text-xl font-bold">{workspace.training_count || 0}</div>
                        <div className="text-xs text-gray-600">Trainings</div>
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      <TrendingUp className="w-4 h-4 text-purple-600" />
                      <div>
                        <div className={`text-xl font-bold px-2 py-1 rounded ${getScoreColor(score)}`}>
                          {score > 0 ? score.toFixed(1) : 'N/A'}
                        </div>
                        <div className="text-xs text-gray-600">Holistic Score</div>
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      <Award className="w-4 h-4 text-yellow-600" />
                      <div>
                        <div className="text-xl font-bold">{scoreData.grade || 'N/A'}</div>
                        <div className="text-xs text-gray-600">Grade</div>
                      </div>
                    </div>
                  </div>
                </div>

                {/* Expanded Content */}
                {isExpanded && (
                  <div className="p-6 bg-white">
                    {isLoadingDatasets ? (
                      <div className="flex items-center justify-center py-8">
                        <Loader2 className="w-6 h-6 animate-spin text-blue-600" />
                        <span className="ml-2 text-gray-600">Loading comprehensive analytics...</span>
                      </div>
                    ) : datasets.length === 0 ? (
                      <div className="text-center py-8 text-gray-500">
                        <Database className="w-12 h-12 mx-auto mb-3 text-gray-400" />
                        <p>No datasets in this workspace yet</p>
                        <p className="text-sm mt-1">Upload a dataset from the main dashboard</p>
                      </div>
                    ) : (
                      <div className="space-y-6">
                        {datasets.map((dataset) => {
                          const analyses = filterAnalysesByDate(savedAnalyses[dataset.id] || []);
                          const dataSource = getDataSourceInfo(dataset);
                          const historicalData = prepareHistoricalData(analyses, dataset.id);
                          
                          return (
                            <div key={dataset.id} className="border-2 border-gray-200 rounded-lg p-6 bg-gradient-to-br from-white to-gray-50">
                              {/* Dataset Header */}
                              <div className="flex items-start justify-between mb-4 pb-4 border-b-2 border-gray-200">
                                <div className="flex items-center gap-3 flex-1">
                                  <FileText className="w-6 h-6 text-blue-600" />
                                  <div>
                                    <h4 className="font-bold text-lg">{dataset.name || dataset.file_name || 'Unnamed Dataset'}</h4>
                                    <div className="flex items-center gap-4 mt-1 text-sm text-gray-600">
                                      <span>{dataSource.icon} <strong>{dataSource.type}:</strong> {dataSource.detail}</span>
                                      {dataSource.fullQuery && (
                                        <Button
                                          size="sm"
                                          variant="outline"
                                          onClick={() => setSelectedQuery(dataSource.fullQuery)}
                                          className="h-6 text-xs"
                                        >
                                          <Eye className="w-3 h-3 mr-1" />
                                          View Full Query
                                        </Button>
                                      )}
                                      <span>📅 Uploaded: {new Date(dataset.created_at).toLocaleDateString()}</span>
                                    </div>
                                  </div>
                                </div>
                              </div>

                              {analyses.length === 0 ? (
                                <div className="text-center py-8 text-gray-400">
                                  <BarChart3 className="w-12 h-12 mx-auto mb-2" />
                                  <p>No saved analyses for this dataset</p>
                                </div>
                              ) : (
                                <Tabs defaultValue="overview" className="w-full">
                                  <TabsList className="grid w-full grid-cols-4">
                                    <TabsTrigger value="overview">Overview</TabsTrigger>
                                    <TabsTrigger value="models">Models & Insights</TabsTrigger>
                                    <TabsTrigger value="trends">Historical Trends</TabsTrigger>
                                    <TabsTrigger value="details">Detailed Table</TabsTrigger>
                                  </TabsList>

                                  {/* Overview Tab */}
                                  <TabsContent value="overview" className="space-y-4">
                                    <div className="grid grid-cols-3 gap-4">
                                      {analyses.slice(0, 3).map((analysis) => {
                                        const details = analysisDetails[analysis.id];
                                        const analysisData = details?.analysis_data || {};
                                        const models = analysisData.ml_models || [];
                                        const bestModel = getBestModel(models);
                                        const bestScore = bestModel ? (bestModel.metrics?.r2_score || bestModel.metrics?.accuracy || 0) : 0;
                                        
                                        return (
                                          <Card key={analysis.id} className="p-4 bg-white hover:shadow-lg transition-shadow">
                                            <div className="flex items-center gap-2 mb-3">
                                              <BarChart3 className="w-5 h-5 text-purple-600" />
                                              <span className="font-bold">{analysis.state_name || 'Unnamed'}</span>
                                            </div>
                                            
                                            <div className="space-y-2 text-sm">
                                              <div className="flex justify-between">
                                                <span className="text-gray-600">Models:</span>
                                                <span className="font-semibold">{models.length}</span>
                                              </div>
                                              <div className="flex justify-between">
                                                <span className="text-gray-600">Best Score:</span>
                                                <span className="font-bold text-green-600">{bestScore.toFixed(4)}</span>
                                              </div>
                                              {bestModel && (
                                                <div className="flex justify-between">
                                                  <span className="text-gray-600">Best Model:</span>
                                                  <span className="font-semibold text-blue-600">{bestModel.model_name}</span>
                                                </div>
                                              )}
                                              <div className="text-xs text-gray-500 mt-2">
                                                {new Date(analysis.created_at).toLocaleString()}
                                              </div>
                                            </div>
                                            
                                            <Button
                                              size="sm"
                                              onClick={() => viewAnalysis(analysis, dataset)}
                                              className="w-full mt-3 bg-blue-600 hover:bg-blue-700"
                                            >
                                              <Eye className="w-4 h-4 mr-1" />
                                              View Full Analysis
                                            </Button>
                                          </Card>
                                        );
                                      })}
                                    </div>
                                  </TabsContent>

                                  {/* Models & Insights Tab */}
                                  <TabsContent value="models" className="space-y-6">
                                    {analyses.map((analysis) => {
                                      const details = analysisDetails[analysis.id];
                                      const analysisData = details?.analysis_data || {};
                                      const models = analysisData.ml_models || [];
                                      const bestModel = getBestModel(models);
                                      const insights = analysisData.insights || [];
                                      const forecasts = analysisData.predictions || [];
                                      const hyperparams = analysisData.hyperparameter_suggestions || [];
                                      const autoMLEnabled = analysisData.automl_enabled || false;
                                      
                                      return (
                                        <Card key={analysis.id} className="p-6 bg-gradient-to-br from-blue-50 to-white">
                                          <div className="flex items-center justify-between mb-4">
                                            <h5 className="text-lg font-bold flex items-center gap-2">
                                              <Sparkles className="w-5 h-5 text-yellow-600" />
                                              {analysis.state_name || 'Unnamed Analysis'}
                                            </h5>
                                            {autoMLEnabled && (
                                              <span className="px-3 py-1 bg-purple-100 text-purple-700 rounded-full text-sm font-semibold flex items-center gap-1">
                                                <Settings className="w-4 h-4" />
                                                AutoML Enabled
                                              </span>
                                            )}
                                          </div>

                                          {/* Best Model Highlight */}
                                          {bestModel && (
                                            <div className="mb-4 p-4 bg-yellow-50 border-2 border-yellow-200 rounded-lg">
                                              <div className="flex items-center gap-2 mb-2">
                                                <Award className="w-5 h-5 text-yellow-600" />
                                                <span className="font-bold text-yellow-900">Best Performing Model</span>
                                              </div>
                                              <div className="grid grid-cols-4 gap-4 text-sm">
                                                <div>
                                                  <div className="text-gray-600">Model</div>
                                                  <div className="font-bold text-blue-600">{bestModel.model_name}</div>
                                                </div>
                                                <div>
                                                  <div className="text-gray-600">Score</div>
                                                  <div className="font-bold text-green-600">
                                                    {(bestModel.metrics?.r2_score || bestModel.metrics?.accuracy || 0).toFixed(4)}
                                                  </div>
                                                </div>
                                                <div>
                                                  <div className="text-gray-600">RMSE</div>
                                                  <div className="font-bold">{(bestModel.metrics?.rmse || 0).toFixed(4)}</div>
                                                </div>
                                                <div>
                                                  <div className="text-gray-600">MAE</div>
                                                  <div className="font-bold">{(bestModel.metrics?.mae || 0).toFixed(4)}</div>
                                                </div>
                                              </div>
                                            </div>
                                          )}

                                          {/* All Models Table */}
                                          <div className="mb-4">
                                            <h6 className="font-semibold mb-2 flex items-center gap-2">
                                              <BarChart3 className="w-4 h-4" />
                                              All Models ({models.length})
                                            </h6>
                                            <div className="overflow-x-auto">
                                              <table className="w-full text-sm">
                                                <thead className="bg-gray-100">
                                                  <tr>
                                                    <th className="text-left p-2">Model</th>
                                                    <th className="text-left p-2">Score</th>
                                                    <th className="text-left p-2">RMSE</th>
                                                    <th className="text-left p-2">MAE</th>
                                                    <th className="text-left p-2">Training Time</th>
                                                  </tr>
                                                </thead>
                                                <tbody>
                                                  {models.map((model, idx) => (
                                                    <tr key={idx} className="border-b hover:bg-gray-50">
                                                      <td className="p-2 font-semibold">{model.model_name}</td>
                                                      <td className="p-2 text-green-600 font-bold">
                                                        {(model.metrics?.r2_score || model.metrics?.accuracy || 0).toFixed(4)}
                                                      </td>
                                                      <td className="p-2">{(model.metrics?.rmse || 0).toFixed(4)}</td>
                                                      <td className="p-2">{(model.metrics?.mae || 0).toFixed(4)}</td>
                                                      <td className="p-2">{model.training_time || 'N/A'}</td>
                                                    </tr>
                                                  ))}
                                                </tbody>
                                              </table>
                                            </div>
                                          </div>

                                          {/* Hyperparameter Suggestions (if AutoML) */}
                                          {autoMLEnabled && hyperparams.length > 0 && (
                                            <div className="mb-4 p-4 bg-purple-50 border border-purple-200 rounded-lg">
                                              <h6 className="font-semibold mb-2 flex items-center gap-2">
                                                <Settings className="w-4 h-4 text-purple-600" />
                                                AutoML Hyperparameter Suggestions
                                              </h6>
                                              <div className="space-y-2">
                                                {hyperparams.map((suggestion, idx) => (
                                                  <div key={idx} className="text-sm bg-white p-2 rounded">
                                                    <strong>{suggestion.model}:</strong> {JSON.stringify(suggestion.params)}
                                                  </div>
                                                ))}
                                              </div>
                                            </div>
                                          )}

                                          {/* Insights */}
                                          {insights.length > 0 && (
                                            <div className="mb-4">
                                              <h6 className="font-semibold mb-2 flex items-center gap-2">
                                                <Sparkles className="w-4 h-4 text-blue-600" />
                                                Key Insights
                                              </h6>
                                              <ul className="space-y-2">
                                                {insights.map((insight, idx) => (
                                                  <li key={idx} className="text-sm bg-blue-50 p-3 rounded-lg border-l-4 border-blue-600">
                                                    {insight.text || insight}
                                                  </li>
                                                ))}
                                              </ul>
                                            </div>
                                          )}

                                          {/* Forecasts */}
                                          {forecasts.length > 0 && (
                                            <div>
                                              <h6 className="font-semibold mb-2 flex items-center gap-2">
                                                <TrendingUp className="w-4 h-4 text-green-600" />
                                                Predictions/Forecasts
                                              </h6>
                                              <div className="text-sm bg-green-50 p-3 rounded-lg">
                                                {forecasts.length} predictions generated
                                              </div>
                                            </div>
                                          )}
                                        </Card>
                                      );
                                    })}
                                  </TabsContent>

                                  {/* Historical Trends Tab */}
                                  <TabsContent value="trends">
                                    {historicalData.length > 1 ? (
                                      <div className="space-y-6">
                                        <Card className="p-6">
                                          <h5 className="font-bold mb-4 flex items-center gap-2">
                                            <LineChart className="w-5 h-5 text-blue-600" />
                                            Performance Trend Over Time
                                          </h5>
                                          <ResponsiveContainer width="100%" height={300}>
                                            <RechartsLine data={historicalData}>
                                              <CartesianGrid strokeDasharray="3 3" />
                                              <XAxis dataKey="date" />
                                              <YAxis />
                                              <RechartsTooltip />
                                              <Legend />
                                              <Line type="monotone" dataKey="score" stroke="#3b82f6" strokeWidth={2} name="Best Score" />
                                            </RechartsLine>
                                          </ResponsiveContainer>
                                        </Card>

                                        <Card className="p-6">
                                          <h5 className="font-bold mb-4 flex items-center gap-2">
                                            <BarChart3 className="w-5 h-5 text-green-600" />
                                            Models Trained Per Analysis
                                          </h5>
                                          <ResponsiveContainer width="100%" height={300}>
                                            <RechartsBar data={historicalData}>
                                              <CartesianGrid strokeDasharray="3 3" />
                                              <XAxis dataKey="name" />
                                              <YAxis />
                                              <RechartsTooltip />
                                              <Legend />
                                              <Bar dataKey="modelCount" fill="#10b981" name="Models Count" />
                                            </RechartsBar>
                                          </ResponsiveContainer>
                                        </Card>
                                      </div>
                                    ) : (
                                      <div className="text-center py-12 text-gray-500">
                                        <LineChart className="w-12 h-12 mx-auto mb-3 text-gray-400" />
                                        <p>Need at least 2 analyses to show trends</p>
                                      </div>
                                    )}
                                  </TabsContent>

                                  {/* Detailed Table Tab */}
                                  <TabsContent value="details">
                                    <div className="overflow-x-auto">
                                      <table className="w-full text-sm">
                                        <thead className="bg-gray-100">
                                          <tr>
                                            <th className="text-left p-3">Analysis Name</th>
                                            <th className="text-left p-3">Date</th>
                                            <th className="text-left p-3">Models</th>
                                            <th className="text-left p-3">Best Score</th>
                                            <th className="text-left p-3">Best Model</th>
                                            <th className="text-left p-3">AutoML</th>
                                            <th className="text-left p-3">Actions</th>
                                          </tr>
                                        </thead>
                                        <tbody>
                                          {analyses.map((analysis) => {
                                            const details = analysisDetails[analysis.id];
                                            const analysisData = details?.analysis_data || {};
                                            const models = analysisData.ml_models || [];
                                            const bestModel = getBestModel(models);
                                            const bestScore = bestModel ? (bestModel.metrics?.r2_score || bestModel.metrics?.accuracy || 0) : 0;
                                            const autoMLEnabled = analysisData.automl_enabled || false;
                                            
                                            return (
                                              <tr key={analysis.id} className="border-b hover:bg-gray-50">
                                                <td className="p-3 font-semibold">{analysis.state_name || 'Unnamed'}</td>
                                                <td className="p-3 text-gray-600">{new Date(analysis.created_at).toLocaleDateString()}</td>
                                                <td className="p-3">{models.length}</td>
                                                <td className="p-3 font-bold text-green-600">{bestScore.toFixed(4)}</td>
                                                <td className="p-3 text-blue-600">{bestModel?.model_name || 'N/A'}</td>
                                                <td className="p-3">
                                                  {autoMLEnabled ? (
                                                    <span className="px-2 py-1 bg-purple-100 text-purple-700 rounded text-xs font-semibold">Yes</span>
                                                  ) : (
                                                    <span className="px-2 py-1 bg-gray-100 text-gray-600 rounded text-xs">No</span>
                                                  )}
                                                </td>
                                                <td className="p-3">
                                                  <Button
                                                    size="sm"
                                                    onClick={() => viewAnalysis(analysis, dataset)}
                                                    className="bg-blue-600 hover:bg-blue-700"
                                                  >
                                                    <Eye className="w-3 h-3 mr-1" />
                                                    View
                                                  </Button>
                                                </td>
                                              </tr>
                                            );
                                          })}
                                        </tbody>
                                      </table>
                                    </div>
                                  </TabsContent>
                                </Tabs>
                              )}
                            </div>
                          );
                        })}
                      </div>
                    )}
                  </div>
                )}
              </Card>
            );
          })}
        </div>
      )}
    </div>
  );
};

export default WorkspaceManager;
