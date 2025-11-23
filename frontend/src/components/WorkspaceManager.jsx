import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { toast } from 'sonner';
import { Loader2, Plus, Trash2, FolderOpen, TrendingUp, Database, Activity, Home, ChevronDown, ChevronRight, FileText, BarChart3, Eye } from 'lucide-react';

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
  const [loadingDatasets, setLoadingDatasets] = useState({});

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
      
      const response = await axios.get(`${BACKEND_URL}/api/datasource/datasets`);
      const allDatasets = response.data.datasets || [];
      
      const workspaceDatasetsList = allDatasets.filter(d => d.workspace_id === workspaceId);
      
      setWorkspaceDatasets(prev => ({
        ...prev,
        [workspaceId]: workspaceDatasetsList
      }));
      
      for (const dataset of workspaceDatasetsList) {
        await loadDatasetAnalyses(dataset.id);
      }
    } catch (error) {
      console.error('Failed to load datasets:', error);
      toast.error('Failed to load datasets for workspace');
    } finally {
      setLoadingDatasets(prev => ({ ...prev, [workspaceId]: false }));
    }
  };

  const loadDatasetAnalyses = async (datasetId) => {
    try {
      const response = await axios.get(`${BACKEND_URL}/api/analysis/saved-states/${datasetId}`);
      setSavedAnalyses(prev => ({
        ...prev,
        [datasetId]: response.data.states || []
      }));
    } catch (error) {
      console.error(`Failed to load analyses for dataset ${datasetId}:`, error);
    }
  };

  const viewAnalysis = (analysis, dataset) => {
    navigate('/', {
      state: {
        loadStateId: analysis.id,
        datasetId: dataset.id
      }
    });
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
          <p className="text-gray-600 mt-1 ml-32">Manage workspaces, datasets, and saved analyses</p>
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

      {/* Search */}
      <div className="max-w-md">
        <Input
          placeholder="Search workspaces..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          className="w-full"
        />
      </div>

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
                <div className="p-6 bg-gray-50 border-b">
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
                  <div className="grid grid-cols-3 gap-4 mt-4 ml-8">
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
                  </div>
                </div>

                {/* Expanded Content - Datasets and Analyses */}
                {isExpanded && (
                  <div className="p-6 bg-white">
                    {isLoadingDatasets ? (
                      <div className="flex items-center justify-center py-8">
                        <Loader2 className="w-6 h-6 animate-spin text-blue-600" />
                        <span className="ml-2 text-gray-600">Loading datasets...</span>
                      </div>
                    ) : datasets.length === 0 ? (
                      <div className="text-center py-8 text-gray-500">
                        <Database className="w-12 h-12 mx-auto mb-3 text-gray-400" />
                        <p>No datasets in this workspace yet</p>
                        <p className="text-sm mt-1">Upload a dataset from the main dashboard</p>
                      </div>
                    ) : (
                      <div className="space-y-4">
                        {datasets.map((dataset) => {
                          const analyses = savedAnalyses[dataset.id] || [];
                          
                          return (
                            <div key={dataset.id} className="border rounded-lg p-4 bg-gray-50">
                              <div className="flex items-center gap-3 mb-3">
                                <FileText className="w-5 h-5 text-blue-600" />
                                <div className="flex-1">
                                  <h4 className="font-semibold">{dataset.file_name}</h4>
                                  <p className="text-xs text-gray-500">
                                    Uploaded: {new Date(dataset.created_at).toLocaleDateString()}
                                  </p>
                                </div>
                              </div>

                              {/* Saved Analyses for this dataset */}
                              {analyses.length > 0 ? (
                                <div className="space-y-2 mt-3 pl-8">
                                  <p className="text-sm font-medium text-gray-700 mb-2">
                                    📊 Saved Analyses ({analyses.length}):
                                  </p>
                                  {analyses.map((analysis) => {
                                    const analysisData = analysis.analysis_data || {};
                                    const models = analysisData.ml_models || [];
                                    const bestScore = getBestModelScore(models);
                                    
                                    return (
                                      <div
                                        key={analysis.id}
                                        className="bg-white border rounded p-3 hover:shadow-md transition-shadow"
                                      >
                                        <div className="flex justify-between items-start">
                                          <div className="flex-1">
                                            <div className="flex items-center gap-2 mb-2">
                                              <BarChart3 className="w-4 h-4 text-purple-600" />
                                              <span className="font-semibold text-sm">{analysis.state_name || analysis.workspace_name || 'Unnamed'}</span>
                                            </div>
                                            
                                            {models.length > 0 && (
                                              <div className="space-y-1 text-xs text-gray-600">
                                                <p>🤖 Models: {models.map(m => m.model_name).join(', ')}</p>
                                                <p>🎯 Best Score: {bestScore > 0 ? bestScore.toFixed(4) : 'N/A'}</p>
                                                <p>📅 Saved: {new Date(analysis.created_at).toLocaleString()}</p>
                                              </div>
                                            )}
                                          </div>
                                          
                                          <Button
                                            size="sm"
                                            onClick={() => viewAnalysis(analysis, dataset)}
                                            className="bg-blue-600 hover:bg-blue-700"
                                          >
                                            <Eye className="w-4 h-4 mr-1" />
                                            View
                                          </Button>
                                        </div>
                                      </div>
                                    );
                                  })}
                                </div>
                              ) : (
                                <div className="text-center py-4 text-gray-400 text-sm pl-8">
                                  No saved analyses for this dataset
                                </div>
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
