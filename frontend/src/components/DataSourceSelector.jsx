import { useState, useRef, useEffect } from "react";
import axios from "axios";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { toast } from "sonner";
import { useDropzone } from "react-dropzone";
import { Upload, Database, Loader2, Check, X, Clock, Code, AlertTriangle } from "lucide-react";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const DataSourceSelector = ({ onDatasetLoaded, onWorkspaceChange, selectedWorkspace: propSelectedWorkspace, onAutoMLChange }) => {
  const [loading, setLoading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(null);
  const [estimatedTime, setEstimatedTime] = useState(null);
  const cancelTokenRef = useRef(null);
  const [useConnectionString, setUseConnectionString] = useState(false);
  const [connectionString, setConnectionString] = useState("");
  const [enableAutoML, setEnableAutoML] = useState(false); // AutoML hyperparameter tuning flag
  const [selectedWorkspace, setSelectedWorkspace] = useState(null); // Selected workspace
  const [showWorkspaceDialog, setShowWorkspaceDialog] = useState(false); // Workspace creation dialog
  const [workspaces, setWorkspaces] = useState([]); // Available workspaces
  const [newWorkspaceName, setNewWorkspaceName] = useState(""); // New workspace name

  // Wrapper function to update workspace and notify parent
  const handleWorkspaceSelect = (workspace) => {
    setSelectedWorkspace(workspace);
    if (onWorkspaceChange) {
      onWorkspaceChange(workspace);
    }
  };

  // Notify parent when AutoML setting changes
  const handleAutoMLToggle = (checked) => {
    setEnableAutoML(checked);
    if (onAutoMLChange) {
      onAutoMLChange(checked);
    }
  };

  const [dbConfig, setDbConfig] = useState({
    source_type: "postgresql",
    host: "",
    port: "",
    database: "",
    username: "",
    password: "",
    service_name: "",
    use_kerberos: false
  });
  const [connectionTested, setConnectionTested] = useState(false);
  const [tables, setTables] = useState([]);
  const [selectedTable, setSelectedTable] = ""