import { useState, useEffect } from "react";
import axios from "axios";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { toast } from "sonner";
import { FolderPlus, Folder, TrendingUp, Trash2, Plus } from "lucide-react";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const WorkspaceManager = ({ onWorkspaceSelected }) => {
  const [workspaces, setWorkspaces] = useState([]);
  const [showCreateDialog, setShowCreateDialog] = useState(false);
  const [loading, setLoading] = useState(false);
  const [newWorkspace, setNewWorkspace] = useState({
    name: "",
    description: "",
    tags: ""
  });

  useEffect(() => {
    loadWorkspaces();
  }, []);

  const loadWorkspaces = async () => {
    try {
      const response = await axios.get(`${API}/workspace/list`);
      setWorkspaces(response.data.workspaces || []);
    } catch (error) {
      console.error("Failed to load workspaces:", error);
    }
  };

  const createWorkspace = async () => {
    if (!newWorkspace.name.trim()) {
      toast.error("Workspace name is required");
      return;
    }

    setLoading(true);
    try {
      const payload = {
        name: newWorkspace.name.trim(),
        description: newWorkspace.description.trim(),
        tags: newWorkspace.tags.split(",").map(t => t.trim()).filter(t => t)
      };

      const response = await axios.post(`${API}/workspace/create`, payload);
      toast.success(`Workspace "${newWorkspace.name}" created!`);
      
      setShowCreateDialog(false);
      setNewWorkspace({ name: "", description: "", tags: "" });
      loadWorkspaces();
      
      if (onWorkspaceSelected) {
        onWorkspaceSelected(response.data.workspace);
      }
    } catch (error) {
      toast.error("Failed to create workspace: " + (error.response?.data?.detail || error.message));
    } finally {
      setLoading(false);
    }
  };

  const deleteWorkspace = async (workspaceId, workspaceName) => {
    if (!confirm(`Delete workspace "${workspaceName}"? This cannot be undone.`)) {
      return;
    }

    try {
      await axios.delete(`${API}/workspace/${workspaceId}`);
      toast.success("Workspace deleted");
      loadWorkspaces();
    } catch (error) {
      toast.error("Failed to delete workspace: " + (error.response?.data?.detail || error.message));
    }
  };

  const selectWorkspace = (workspace) => {
    if (onWorkspaceSelected) {
      onWorkspaceSelected(workspace);
    }
  };

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold flex items-center gap-2">
          <Folder className="w-5 h-5" />
          Workspaces
        </h3>
        <Button onClick={() => setShowCreateDialog(true)} size="sm">
          <Plus className="w-4 h-4 mr-2" />
          New Workspace
        </Button>
      </div>

      {workspaces.length === 0 ? (
        <Card className="p-8 text-center bg-gradient-to-br from-blue-50 to-purple-50">
          <FolderPlus className="w-12 h-12 mx-auto mb-4 text-gray-400" />
          <h4 className="font-semibold text-gray-700 mb-2">No Workspaces Yet</h4>
          <p className="text-sm text-gray-600 mb-4">
            Create a workspace to organize your datasets and track model performance over time
          </p>
          <Button onClick={() => setShowCreateDialog(true)}>
            <Plus className="w-4 h-4 mr-2" />
            Create Your First Workspace
          </Button>
        </Card>
      ) : (
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
          {workspaces.map((workspace) => (
            <Card
              key={workspace.id}
              className="p-4 hover:shadow-lg transition-shadow cursor-pointer border-2 hover:border-blue-300"
              onClick={() => selectWorkspace(workspace)}
            >
              <div className="flex items-start justify-between mb-3">
                <div className="flex items-center gap-2">
                  <Folder className="w-5 h-5 text-blue-600" />
                  <h4 className="font-semibold text-gray-900">{workspace.name}</h4>
                </div>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={(e) => {
                    e.stopPropagation();
                    deleteWorkspace(workspace.id, workspace.name);
                  }}
                  className="h-8 w-8 p-0"
                >
                  <Trash2 className="w-4 h-4 text-red-500" />
                </Button>
              </div>

              {workspace.description && (
                <p className="text-sm text-gray-600 mb-3">{workspace.description}</p>
              )}

              <div className="flex items-center justify-between text-sm">
                <span className="text-gray-500">{workspace.dataset_count || 0} datasets</span>
                <span className="text-gray-500">{workspace.training_count || 0} trainings</span>
              </div>

              {workspace.tags && workspace.tags.length > 0 && (
                <div className="flex flex-wrap gap-1 mt-3">
                  {workspace.tags.map((tag, idx) => (
                    <span key={idx} className="px-2 py-1 bg-blue-100 text-blue-700 text-xs rounded">
                      {tag}
                    </span>
                  ))}
                </div>
              )}
            </Card>
          ))}
        </div>
      )}

      {/* Create Workspace Dialog */}
      <Dialog open={showCreateDialog} onOpenChange={setShowCreateDialog}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Create New Workspace</DialogTitle>
          </DialogHeader>

          <div className="space-y-4 py-4">
            <div>
              <Label htmlFor="workspace-name">Workspace Name *</Label>
              <Input
                id="workspace-name"
                value={newWorkspace.name}
                onChange={(e) => setNewWorkspace({ ...newWorkspace, name: e.target.value })}
                placeholder="e.g., Sales Forecasting Q4 2024"
                autoFocus
              />
            </div>

            <div>
              <Label htmlFor="workspace-desc">Description</Label>
              <textarea
                id="workspace-desc"
                value={newWorkspace.description}
                onChange={(e) => setNewWorkspace({ ...newWorkspace, description: e.target.value })}
                placeholder="Brief description of this workspace..."
                className="w-full h-20 p-2 border rounded-md"
              />
            </div>

            <div>
              <Label htmlFor="workspace-tags">Tags (comma-separated)</Label>
              <Input
                id="workspace-tags"
                value={newWorkspace.tags}
                onChange={(e) => setNewWorkspace({ ...newWorkspace, tags: e.target.value })}
                placeholder="e.g., sales, forecasting, Q4"
              />
            </div>
          </div>

          <div className="flex gap-3">
            <Button
              variant="outline"
              onClick={() => setShowCreateDialog(false)}
              className="flex-1"
            >
              Cancel
            </Button>
            <Button
              onClick={createWorkspace}
              disabled={loading || !newWorkspace.name.trim()}
              className="flex-1"
            >
              {loading ? "Creating..." : "Create Workspace"}
            </Button>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default WorkspaceManager;
