import { useState, useEffect } from 'react';
import axios from 'axios';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { toast } from 'sonner';
import { Loader2, Plus, Trash2, FolderOpen, TrendingUp, Database, Activity } from 'lucide-react';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;

const WorkspaceManager = () => {
  const [workspaces, setWorkspaces] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [createModalOpen, setCreateModalOpen] = useState(false);
  const [newWorkspace, setNewWorkspace] = useState({ name: '', description: '', tags: '' });
  const [creating, setCreating] = useState(false);

  useEffect(() => {
    loadWorkspaces();
  }, []);

  const loadWorkspaces = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`${BACKEND_URL}/api/workspace/list`);
      setWorkspaces(response.data.workspaces || []);
    } catch (error) {
      console.error('Failed to load workspaces:', error);
      toast.error('Failed to load workspaces');
    } finally {
      setLoading(false);
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

  const filteredWorkspaces = workspaces.filter(ws =>
    ws.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    ws.description?.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const getScoreColor = (score) => {
    if (score >= 80) return 'text-green-600 bg-green-50';
    if (score >= 50) return 'text-yellow-600 bg-yellow-50';
    return 'text-red-600 bg-red-50';
  };

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold">Workspace Manager</h1>
          <p className="text-gray-600 mt-1">Organize your datasets and track ML training projects</p>
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

      {/* Workspaces Grid */}
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
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredWorkspaces.map((workspace) => (
            <Card key={workspace.id} className="p-6 hover:shadow-lg transition-shadow">
              <div className="flex justify-between items-start mb-4">
                <div className="flex-1">
                  <h3 className="text-lg font-semibold mb-1">{workspace.name}</h3>
                  <p className="text-sm text-gray-600 line-clamp-2">
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
              <div className="grid grid-cols-2 gap-4 mb-4">
                <div className="flex items-center gap-2">
                  <Database className="w-4 h-4 text-blue-600" />
                  <div>
                    <div className="text-2xl font-bold">{workspace.dataset_count || 0}</div>
                    <div className="text-xs text-gray-600">Datasets</div>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <Activity className="w-4 h-4 text-green-600" />
                  <div>
                    <div className="text-2xl font-bold">{workspace.training_count || 0}</div>
                    <div className="text-xs text-gray-600">Trainings</div>
                  </div>
                </div>
              </div>

              {/* Tags */}
              {workspace.tags && workspace.tags.length > 0 && (
                <div className="flex flex-wrap gap-1 mb-4">
                  {workspace.tags.map((tag, idx) => (
                    <span key={idx} className="px-2 py-1 bg-blue-100 text-blue-700 text-xs rounded">
                      {tag}
                    </span>
                  ))}
                </div>
              )}

              {/* Holistic Score (Placeholder) */}
              <div className="pt-4 border-t">
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-600">Holistic Score</span>
                  <div className={`px-3 py-1 rounded-full font-semibold text-sm ${getScoreColor(0)}`}>
                    Coming Soon
                  </div>
                </div>
              </div>

              {/* Actions */}
              <div className="mt-4">
                <Button variant="outline" className="w-full" onClick={() => window.location.href = `/workspace/${workspace.id}`}>
                  <FolderOpen className="w-4 h-4 mr-2" />
                  Open Workspace
                </Button>
              </div>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
};

export default WorkspaceManager;
