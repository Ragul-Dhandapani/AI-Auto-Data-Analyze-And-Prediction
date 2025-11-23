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
import { Upload, Database, Loader2, Check, X, Clock, Code } from "lucide-react";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const DataSourceSelector = ({ onDatasetLoaded, onWorkspaceChange, selectedWorkspace: propSelectedWorkspace }) => {
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
  const [selectedTable, setSelectedTable] = useState("");
  const [customQuery, setCustomQuery] = useState("");
  const [queryResults, setQueryResults] = useState(null); // Store query execution results
  const [showNameDialog, setShowNameDialog] = useState(false); // Show dataset naming dialog
  const [datasetName, setDatasetName] = useState(""); // User-provided dataset name

  // Load workspaces on mount
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
    if (!newWorkspaceName.trim()) {
      toast.error("Workspace name is required");
      return;
    }

    try {
      const response = await axios.post(`${API}/workspace/create`, {
        name: newWorkspaceName.trim(),
        description: "",
        tags: []
      });
      toast.success(`Workspace "${newWorkspaceName}" created!`);
      setNewWorkspaceName("");
      setShowWorkspaceDialog(false);
      await loadWorkspaces();
      handleWorkspaceSelect(response.data.workspace);
    } catch (error) {
      toast.error("Failed to create workspace: " + (error.response?.data?.detail || error.message));
    }
  };

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    accept: {
      'text/csv': ['.csv'],
      'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': ['.xlsx'],
      'application/vnd.ms-excel': ['.xls']
    },
    maxFiles: 1,
    onDrop: async (acceptedFiles) => {
      if (acceptedFiles.length > 0) {
        await handleFileUpload(acceptedFiles[0]);
      }
    }
  });

  const estimateUploadTime = (fileSize) => {
    // Get historical upload times from localStorage
    const history = JSON.parse(localStorage.getItem('uploadHistory') || '[]');
    
    if (history.length > 0) {
      // Calculate average speed from history
      const avgSpeed = history.reduce((sum, item) => sum + (item.size / item.time), 0) / history.length;
      const estimatedSeconds = Math.ceil(fileSize / avgSpeed);
      return estimatedSeconds;
    }
    
    // Default estimation: 1MB per second
    return Math.ceil(fileSize / (1024 * 1024));
  };

  const handleFileUpload = async (file) => {
    const startTime = Date.now();
    setLoading(true);
    setUploadProgress(0);
    
    const estimated = estimateUploadTime(file.size);
    setEstimatedTime(estimated);
    
    const formData = new FormData();
    formData.append("file", file);
    if (selectedWorkspace) {
      formData.append("workspace_id", selectedWorkspace.id);
    }

    // Create cancel token
    const CancelToken = axios.CancelToken;
    const source = CancelToken.source();
    cancelTokenRef.current = source;

    try {
      const response = await axios.post(`${API}/datasource/upload-file`, formData, {
        headers: { "Content-Type": "multipart/form-data" },
        cancelToken: source.token,
        timeout: 300000, // 5 minutes timeout for large files
        onUploadProgress: (progressEvent) => {
          const percentCompleted = Math.round((progressEvent.loaded * 100) / progressEvent.total);
          setUploadProgress(percentCompleted);
        }
      });
      
      const uploadTime = (Date.now() - startTime) / 1000; // seconds
      
      // Save to history for learning
      const history = JSON.parse(localStorage.getItem('uploadHistory') || '[]');
      history.push({ size: file.size, time: uploadTime });
      if (history.length > 10) history.shift(); // Keep last 10
      localStorage.setItem('uploadHistory', JSON.stringify(history));
      
      // Add upload time to response
      response.data.upload_time = uploadTime;
      
      // Format upload time for display (min/hr format)
      let timeDisplay;
      if (uploadTime < 60) {
        timeDisplay = `${uploadTime.toFixed(1)}s`;
      } else if (uploadTime < 3600) {
        const minutes = Math.floor(uploadTime / 60);
        const seconds = Math.floor(uploadTime % 60);
        timeDisplay = `${minutes}m ${seconds}s`;
      } else {
        const hours = Math.floor(uploadTime / 3600);
        const minutes = Math.floor((uploadTime % 3600) / 60);
        timeDisplay = `${hours}h ${minutes}m`;
      }
      
      toast.success(`File uploaded in ${timeDisplay}!`);
      // Pass the dataset object, not the wrapper
      onDatasetLoaded(response.data.dataset || response.data);
    } catch (error) {
      if (axios.isCancel(error)) {
        toast.info("Upload cancelled");
      } else {
        toast.error("File upload failed: " + (error.response?.data?.detail || error.message));
      }
    } finally {
      setLoading(false);
      setUploadProgress(null);
      setEstimatedTime(null);
      cancelTokenRef.current = null;
    }
  };

  const cancelUpload = () => {
    if (cancelTokenRef.current) {
      cancelTokenRef.current.cancel('Upload cancelled by user');
    }
  };

  const testConnection = async () => {
    setLoading(true);
    try {
      let configToUse = dbConfig;
      
      // If using connection string, parse it first
      if (useConnectionString && connectionString) {
        const formData = new FormData();
        formData.append("source_type", dbConfig.source_type);
        formData.append("connection_string", connectionString);
        
        const parseResponse = await axios.post(`${API}/datasource/parse-connection-string`, formData);
        
        if (!parseResponse.data.success) {
          toast.error("Invalid connection string: " + parseResponse.data.message);
          setLoading(false);
          return;
        }
        
        configToUse = parseResponse.data.config;
        // Update dbConfig with parsed values for display
        setDbConfig({...dbConfig, ...configToUse});
      }
      
      const response = await axios.post(`${API}/datasource/test-connection`, {
        source_type: dbConfig.source_type,
        config: configToUse
      });
      
      if (response.data.success) {
        toast.success("Connection successful!");
        setConnectionTested(true);
        await loadTables(configToUse);
      } else {
        toast.error("Connection failed: " + response.data.message);
        setConnectionTested(false);
      }
    } catch (error) {
      toast.error("Connection test failed: " + (error.response?.data?.detail || error.message));
      setConnectionTested(false);
    } finally {
      setLoading(false);
    }
  };

  const loadTables = async (configToUse = dbConfig) => {
    try {
      const response = await axios.post(`${API}/datasource/list-tables`, {
        source_type: dbConfig.source_type,
        config: configToUse
      });
      setTables(response.data.tables || []);
    } catch (error) {
      toast.error("Failed to load tables: " + (error.response?.data?.detail || error.message));
    }
  };

  const loadTable = async () => {
    if (!selectedTable) {
      toast.error("Please select a table");
      return;
    }

    if (!connectionTested) {
      toast.error("Please test the connection first");
      return;
    }

    setLoading(true);
    
    try {
      const requestBody = {
        source_type: dbConfig.source_type,
        config: {
          host: dbConfig.host,
          port: dbConfig.port || (dbConfig.source_type === 'postgresql' ? 5432 : dbConfig.source_type === 'mysql' ? 3306 : 1521),
          database: dbConfig.database,
          username: dbConfig.username,
          password: dbConfig.password,
          service_name: dbConfig.service_name // For Oracle
        }
      };

      const response = await axios.post(
        `${API}/datasource/load-table?table_name=${encodeURIComponent(selectedTable)}`,
        requestBody
      );
      
      toast.success(`Table loaded successfully! (${response.data.row_count} rows)`, {
        description: response.data.storage_type === 'gridfs' ? 'Stored in GridFS' : 'Stored directly'
      });
      
      onDatasetLoaded(response.data.dataset || response.data);
    } catch (error) {
      console.error("Table load error:", error.response?.data);
      let errorMsg = "Table load failed";
      if (error.response?.data?.detail) {
        // Handle detail being string, object, or array
        if (typeof error.response.data.detail === 'string') {
          errorMsg += `: ${error.response.data.detail}`;
        } else if (Array.isArray(error.response.data.detail)) {
          errorMsg += `: ${error.response.data.detail.map(e => e.msg || e).join(', ')}`;
        } else if (typeof error.response.data.detail === 'object') {
          errorMsg += `: ${JSON.stringify(error.response.data.detail)}`;
        }
      } else if (error.message) {
        errorMsg += `: ${error.message}`;
      }
      toast.error(errorMsg);
    } finally {
      setLoading(false);
    }
  };

  const executeCustomQuery = async () => {
    if (!customQuery.trim()) {
      toast.error("Please enter a SQL query");
      return;
    }

    if (!connectionTested) {
      toast.error("Please test the connection first");
      return;
    }

    setLoading(true);
    try {
      let queryConfig;
      
      if (useConnectionString && connectionString) {
        // Parse connection string first
        const formData = new FormData();
        formData.append("source_type", dbConfig.source_type);
        formData.append("connection_string", connectionString);
        
        const parseResponse = await axios.post(`${API}/datasource/parse-connection-string`, formData);
        const parsedConfig = parseResponse.data.config;
        
        queryConfig = {
          db_type: dbConfig.source_type,
          query: customQuery,
          ...parsedConfig
        };
      } else {
        queryConfig = {
          db_type: dbConfig.source_type,
          query: customQuery,
          host: dbConfig.host,
          port: dbConfig.port || getDefaultPort(),
          database: dbConfig.database,
          username: dbConfig.username,
          password: dbConfig.password,
          service_name: dbConfig.service_name
        };
      }

      // Execute query to validate and get preview
      const response = await axios.post(`${API}/datasource/execute-query-preview`, queryConfig);
      
      // Store results for loading later
      setQueryResults({
        row_count: response.data.row_count,
        column_count: response.data.column_count,
        columns: response.data.columns,
        preview: response.data.data_preview,
        queryConfig: queryConfig
      });
      
      toast.success(`Query executed successfully! Found ${response.data.row_count} rows`, {
        description: `Click "Load Data" to save this dataset`
      });
      
    } catch (error) {
      console.error("Query execution error:", error);
      toast.error("Query execution failed: " + (error.response?.data?.detail || error.message));
      setQueryResults(null);
    } finally {
      setLoading(false);
    }
  };
  
  const loadQueryResults = () => {
    // Prompt user for dataset name
    setShowNameDialog(true);
  };
  
  const saveQueryDataset = async () => {
    if (!datasetName.trim()) {
      toast.error("Please enter a dataset name");
      return;
    }
    
    setLoading(true);
    setShowNameDialog(false);
    
    try {
      // Call backend to save the query results with the custom name
      const response = await axios.post(`${API}/datasource/save-query-dataset`, {
        ...queryResults.queryConfig,
        dataset_name: datasetName.trim()
      });
      
      toast.success(`Dataset "${datasetName}" loaded successfully!`);
      
      onDatasetLoaded(response.data.dataset || response.data);
      
      // Clear state
      setCustomQuery("");
      setQueryResults(null);
      setDatasetName("");
      
    } catch (error) {
      console.error("Save dataset error:", error);
      toast.error("Failed to save dataset: " + (error.response?.data?.detail || error.message));
    } finally {
      setLoading(false);
    }
  };

  const getDefaultPort = () => {
    const ports = {
      postgresql: 5432,
      mysql: 3306,
      oracle: 1521,
      sqlserver: 1433,
      mongodb: 27017
    };
    return ports[dbConfig.source_type] || "";
  };

  return (
    <Card className="p-6 bg-white/90 backdrop-blur-sm" data-testid="data-source-selector">
      <h2 className="text-2xl font-bold mb-6">Select Data Source</h2>
      
      <Tabs defaultValue="file">
        <TabsList className="grid w-full grid-cols-3 mb-6">
          <TabsTrigger value="file" data-testid="tab-file-upload">File Upload</TabsTrigger>
          <TabsTrigger value="database" data-testid="tab-database">Database Connection</TabsTrigger>
          <TabsTrigger value="custom-query" data-testid="tab-custom-query">
            <Code className="w-4 h-4 mr-2" />
            Custom SQL Query
          </TabsTrigger>
        </TabsList>

        <TabsContent value="file">
          {/* Workspace Selection */}
          <div className="mb-4 p-4 bg-gradient-to-r from-blue-50 to-cyan-50 rounded-lg border-2 border-blue-200">
            <div className="flex items-start gap-3">
              <div className="text-2xl">📁</div>
              <div className="flex-1">
                <h4 className="font-semibold text-blue-900 mb-2">Select or Create Workspace</h4>
                <p className="text-sm text-blue-700 mb-3">
                  Organize datasets and track model performance over time (30-day trends, best model recommendations).
                </p>
                
                <div className="flex gap-2 items-center">
                  <select
                    value={selectedWorkspace?.id || ""}
                    onChange={(e) => {
                      const ws = workspaces.find(w => w.id === e.target.value);
                      handleWorkspaceSelect(ws);
                    }}
                    className={`flex-1 p-2 border rounded-md ${!selectedWorkspace ? 'border-red-300 bg-red-50' : 'border-gray-300'}`}
                  >
                    <option value="">⚠️ Select a workspace (Required)</option>
                    {workspaces.map(ws => (
                      <option key={ws.id} value={ws.id}>{ws.name}</option>
                    ))}
                  </select>
                  <Button
                    type="button"
                    onClick={() => setShowWorkspaceDialog(true)}
                    className="whitespace-nowrap"
                    size="sm"
                  >
                    + New Workspace
                  </Button>
                </div>
                
                {selectedWorkspace && (
                  <p className="text-xs text-green-700 mt-2">
                    ✓ Dataset will be added to: <strong>{selectedWorkspace.name}</strong>
                  </p>
                )}
              </div>
            </div>
          </div>

          {/* AutoML Toggle */}
          <div className="mb-4 p-4 bg-gradient-to-r from-purple-50 to-indigo-50 rounded-lg border-2 border-purple-200">
            <div className="flex items-start space-x-3">
              <input 
                type="checkbox"
                id="enable-automl"
                checked={enableAutoML}
                onChange={(e) => setEnableAutoML(e.target.checked)}
                className="w-5 h-5 text-purple-600 rounded focus:ring-purple-500 mt-0.5"
              />
              <div className="flex-1">
                <Label htmlFor="enable-automl" className="cursor-pointer font-semibold text-purple-900">
                  🤖 Enable AutoML Hyperparameter Tuning
                </Label>
                <p className="text-sm text-purple-700 mt-1">
                  Automatically optimize model parameters for best performance. May increase training time by 2-3x.
                </p>
              </div>
            </div>
          </div>

          <div
            {...getRootProps()}
            data-testid="file-dropzone"
            className={`border-2 border-dashed rounded-xl p-12 text-center cursor-pointer transition-all ${
              isDragActive 
                ? 'border-blue-500 bg-blue-50' 
                : 'border-gray-300 hover:border-blue-400 hover:bg-gray-50'
            }`}
          >
            <input {...getInputProps()} />
            <Upload className="w-12 h-12 mx-auto mb-4 text-gray-400" />
            <p className="text-lg font-medium mb-2">
              {isDragActive ? "Drop file here" : "Drag & drop file here"}
            </p>
            <p className="text-sm text-gray-500 mb-4">or click to browse</p>
            <p className="text-xs text-gray-400">Supports CSV, XLSX, XLS files</p>
          </div>
          
          {loading && uploadProgress !== null && (
            <div className="mt-4 space-y-3">
              <div className="flex items-center justify-between text-sm">
                <div className="flex items-center gap-2 text-blue-600">
                  <Loader2 className="w-4 h-4 animate-spin" />
                  <span>Uploading... {uploadProgress}%</span>
                </div>
                {estimatedTime && (
                  <div className="flex items-center gap-2 text-gray-600">
                    <Clock className="w-4 h-4" />
                    <span>Est. {estimatedTime}s</span>
                  </div>
                )}
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div 
                  className="bg-blue-600 h-2 rounded-full transition-all"
                  style={{ width: `${uploadProgress}%` }}
                />
              </div>
              <Button
                data-testid="cancel-upload-btn"
                onClick={cancelUpload}
                variant="destructive"
                size="sm"
                className="w-full"
              >
                <X className="w-4 h-4 mr-2" />
                Cancel Upload
              </Button>
            </div>
          )}
        </TabsContent>

        <TabsContent value="database">
          <div className="space-y-4">
            {/* Workspace Selection */}
            <div className="p-4 bg-gradient-to-r from-blue-50 to-cyan-50 rounded-lg border-2 border-blue-200">
              <div className="flex items-start gap-3">
                <div className="text-2xl">📁</div>
                <div className="flex-1">
                  <h4 className="font-semibold text-blue-900 mb-2">Select or Create Workspace</h4>
                  <div className="flex gap-2 items-center">
                    <select
                      value={selectedWorkspace?.id || ""}
                      onChange={(e) => {
                        const ws = workspaces.find(w => w.id === e.target.value);
                        handleWorkspaceSelect(ws);
                      }}
                      className="flex-1 p-2 border rounded-md"
                    >
                      <option value="">No Workspace (Optional)</option>
                      {workspaces.map(ws => (
                        <option key={ws.id} value={ws.id}>{ws.name}</option>
                      ))}
                    </select>
                    <Button
                      type="button"
                      onClick={() => setShowWorkspaceDialog(true)}
                      className="whitespace-nowrap"
                      size="sm"
                    >
                      + New Workspace
                    </Button>
                  </div>
                  {selectedWorkspace && (
                    <p className="text-xs text-green-700 mt-2">
                      ✓ Dataset will be added to: <strong>{selectedWorkspace.name}</strong>
                    </p>
                  )}
                </div>
              </div>
            </div>

            <div>
              <Label>Database Type</Label>
              <Select 
                value={dbConfig.source_type} 
                onValueChange={(value) => {
                  setDbConfig({...dbConfig, source_type: value});
                  setConnectionTested(false);
                  setTables([]);
                }}
              >
                <SelectTrigger data-testid="db-type-select">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="postgresql">PostgreSQL</SelectItem>
                  <SelectItem value="mysql">MySQL</SelectItem>
                  <SelectItem value="oracle">Oracle</SelectItem>
                  <SelectItem value="sqlserver">SQL Server</SelectItem>
                  <SelectItem value="mongodb">MongoDB</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div className="flex items-center space-x-2">
              <input
                type="checkbox"
                id="use-connection-string"
                checked={useConnectionString}
                onChange={(e) => {
                  setUseConnectionString(e.target.checked);
                  setConnectionTested(false);
                }}
                className="w-4 h-4"
              />
              <Label htmlFor="use-connection-string" className="cursor-pointer">
                Use Connection String
              </Label>
            </div>

            {useConnectionString ? (
              <div>
                <Label>Connection String</Label>
                <Input 
                  data-testid="connection-string-input"
                  value={connectionString}
                  onChange={(e) => {
                    setConnectionString(e.target.value);
                    setConnectionTested(false);
                  }}
                  placeholder="postgresql://user:password@host:port/database"
                  className="font-mono"
                />
                <p className="text-xs text-gray-500 mt-1">
                  Enter a connection string in the format appropriate for your database type
                </p>
              </div>
            ) : (
              <>
            <div className="grid md:grid-cols-2 gap-4">
              <div>
                <Label>Host</Label>
                <Input 
                  data-testid="db-host-input"
                  value={dbConfig.host}
                  onChange={(e) => setDbConfig({...dbConfig, host: e.target.value})}
                  placeholder="localhost"
                />
              </div>
              <div>
                <Label>Port</Label>
                <Input 
                  data-testid="db-port-input"
                  value={dbConfig.port}
                  onChange={(e) => setDbConfig({...dbConfig, port: e.target.value})}
                  placeholder={
                    dbConfig.source_type === 'oracle' ? '1521' : 
                    dbConfig.source_type === 'mysql' ? '3306' :
                    dbConfig.source_type === 'sqlserver' ? '1433' :
                    dbConfig.source_type === 'mongodb' ? '27017' : '5432'
                  }
                />
              </div>
            </div>

            {dbConfig.source_type === 'oracle' ? (
              <div>
                <Label>Service Name</Label>
                <Input 
                  data-testid="db-service-input"
                  value={dbConfig.service_name}
                  onChange={(e) => setDbConfig({...dbConfig, service_name: e.target.value})}
                  placeholder="ORCL"
                />
              </div>
            ) : (
              <div>
                <Label>Database Name</Label>
                <Input 
                  data-testid="db-name-input"
                  value={dbConfig.database}
                  onChange={(e) => setDbConfig({...dbConfig, database: e.target.value})}
                  placeholder="mydb"
                />
              </div>
            )}

            {/* Kerberos Authentication Toggle */}
            {!useConnectionString && (
              <div className="flex items-center space-x-2 p-3 bg-blue-50 rounded-lg border border-blue-200">
                <input 
                  type="checkbox"
                  id="use-kerberos"
                  checked={dbConfig.use_kerberos}
                  onChange={(e) => setDbConfig({...dbConfig, use_kerberos: e.target.checked})}
                  className="w-4 h-4 text-blue-600 rounded focus:ring-blue-500"
                />
                <Label htmlFor="use-kerberos" className="cursor-pointer flex-1">
                  <span className="font-semibold">🔐 Use Kerberos Authentication</span>
                  <span className="block text-xs text-gray-600 mt-1">
                    Enable for enterprise-level secure authentication via GSSAPI
                    {dbConfig.source_type === 'oracle' && ' (External Auth)'}
                    {dbConfig.source_type === 'sqlserver' && ' (Windows Integrated Auth)'}
                  </span>
                </Label>
              </div>
            )}

            <div className="grid md:grid-cols-2 gap-4">
              <div>
                <Label>Username</Label>
                <Input 
                  data-testid="db-username-input"
                  value={dbConfig.username}
                  onChange={(e) => setDbConfig({...dbConfig, username: e.target.value})}
                  placeholder={dbConfig.use_kerberos ? "Kerberos principal" : "user"}
                />
              </div>
              {!dbConfig.use_kerberos && (
                <div>
                  <Label>Password</Label>
                  <Input 
                    data-testid="db-password-input"
                    type="password"
                    value={dbConfig.password}
                    onChange={(e) => setDbConfig({...dbConfig, password: e.target.value})}
                    placeholder="********"
                  />
                </div>
              )}
            </div>
            </>
            )}

            <Button 
              data-testid="test-connection-btn"
              onClick={testConnection}
              disabled={loading}
              className="w-full"
            >
              {loading ? (
                <><Loader2 className="w-4 h-4 animate-spin mr-2" /> Testing...</>
              ) : connectionTested ? (
                <><Check className="w-4 h-4 mr-2" /> Connection Successful</>
              ) : (
                <><Database className="w-4 h-4 mr-2" /> Test Connection</>
              )}
            </Button>

            {connectionTested && tables.length > 0 && (
              <div>
                <Label>Select Table</Label>
                <Select value={selectedTable} onValueChange={setSelectedTable}>
                  <SelectTrigger data-testid="table-select">
                    <SelectValue placeholder="Choose a table" />
                  </SelectTrigger>
                  <SelectContent>
                    {tables.map((table) => (
                      <SelectItem key={table} value={table}>{table}</SelectItem>
                    ))}
                  </SelectContent>
                </Select>
                <Button 
                  data-testid="load-table-btn"
                  onClick={loadTable}
                  disabled={loading || !selectedTable}
                  className="w-full mt-4"
                >
                  {loading ? (
                    <><Loader2 className="w-4 h-4 animate-spin mr-2" /> Loading...</>
                  ) : (
                    "Load Table"
                  )}
                </Button>
              </div>
            )}
          </div>
        </TabsContent>

        <TabsContent value="custom-query">
          <div className="space-y-4">
            {/* Workspace Selection */}
            <div className="p-4 bg-gradient-to-r from-blue-50 to-cyan-50 rounded-lg border-2 border-blue-200">
              <div className="flex items-start gap-3">
                <div className="text-2xl">📁</div>
                <div className="flex-1">
                  <h4 className="font-semibold text-blue-900 mb-2">Select or Create Workspace</h4>
                  <div className="flex gap-2 items-center">
                    <select
                      value={selectedWorkspace?.id || ""}
                      onChange={(e) => {
                        const ws = workspaces.find(w => w.id === e.target.value);
                        handleWorkspaceSelect(ws);
                      }}
                      className="flex-1 p-2 border rounded-md"
                    >
                      <option value="">No Workspace (Optional)</option>
                      {workspaces.map(ws => (
                        <option key={ws.id} value={ws.id}>{ws.name}</option>
                      ))}
                    </select>
                    <Button
                      type="button"
                      onClick={() => setShowWorkspaceDialog(true)}
                      className="whitespace-nowrap"
                      size="sm"
                    >
                      + New Workspace
                    </Button>
                  </div>
                  {selectedWorkspace && (
                    <p className="text-xs text-green-700 mt-2">
                      ✓ Dataset will be added to: <strong>{selectedWorkspace.name}</strong>
                    </p>
                  )}
                </div>
              </div>
            </div>

            <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-4">
              <h3 className="font-semibold text-blue-900 mb-2">💡 Custom SQL Query</h3>
              <p className="text-sm text-blue-800">
                Write complex SQL queries including JOINs, WHERE clauses, aggregations, etc.
                Query results will be loaded for full analysis.
              </p>
            </div>

            <div>
              <Label>Database Type</Label>
              <Select 
                value={dbConfig.source_type} 
                onValueChange={(value) => {
                  setDbConfig({...dbConfig, source_type: value});
                  setConnectionTested(false);
                }}
              >
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="postgresql">PostgreSQL</SelectItem>
                  <SelectItem value="mysql">MySQL</SelectItem>
                  <SelectItem value="oracle">Oracle</SelectItem>
                  <SelectItem value="sqlserver">SQL Server</SelectItem>
                  <SelectItem value="mongodb">MongoDB (Collection Name)</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div className="flex items-center space-x-2">
              <input
                type="checkbox"
                id="query-use-connection-string"
                checked={useConnectionString}
                onChange={(e) => {
                  setUseConnectionString(e.target.checked);
                  setConnectionTested(false);
                }}
                className="w-4 h-4"
              />
              <Label htmlFor="query-use-connection-string" className="cursor-pointer">
                Use Connection String
              </Label>
            </div>

            {useConnectionString ? (
              <div>
                <Label>Connection String</Label>
                <Input 
                  value={connectionString}
                  onChange={(e) => {
                    setConnectionString(e.target.value);
                    setConnectionTested(false);
                  }}
                  placeholder="postgresql://user:password@host:port/database"
                  className="font-mono"
                />
              </div>
            ) : (
              <>
            <div className="grid md:grid-cols-2 gap-4">
              <div>
                <Label>Host</Label>
                <Input 
                  value={dbConfig.host}
                  onChange={(e) => {
                    setDbConfig({...dbConfig, host: e.target.value});
                    setConnectionTested(false);
                  }}
                  placeholder="localhost"
                />
              </div>
              <div>
                <Label>Port</Label>
                <Input 
                  value={dbConfig.port}
                  onChange={(e) => {
                    setDbConfig({...dbConfig, port: e.target.value});
                    setConnectionTested(false);
                  }}
                  placeholder={getDefaultPort()}
                />
              </div>
            </div>

            {/* Kerberos Authentication Toggle - Custom Query */}
            {!useConnectionString && (
              <div className="flex items-center space-x-2 p-3 bg-blue-50 rounded-lg border border-blue-200">
                <input 
                  type="checkbox"
                  id="use-kerberos-query"
                  checked={dbConfig.use_kerberos}
                  onChange={(e) => setDbConfig({...dbConfig, use_kerberos: e.target.checked})}
                  className="w-4 h-4 text-blue-600 rounded focus:ring-blue-500"
                />
                <Label htmlFor="use-kerberos-query" className="cursor-pointer flex-1">
                  <span className="font-semibold">🔐 Use Kerberos Authentication</span>
                  <span className="block text-xs text-gray-600 mt-1">
                    Enable for enterprise-level secure authentication via GSSAPI
                    {dbConfig.source_type === 'oracle' && ' (External Auth)'}
                    {dbConfig.source_type === 'sqlserver' && ' (Windows Integrated Auth)'}
                  </span>
                </Label>
              </div>
            )}

            <div className="grid md:grid-cols-2 gap-4">
              <div>
                <Label>Username</Label>
                <Input 
                  value={dbConfig.username}
                  onChange={(e) => {
                    setDbConfig({...dbConfig, username: e.target.value});
                    setConnectionTested(false);
                  }}
                  placeholder={dbConfig.use_kerberos ? "Kerberos principal" : "username"}
                />
              </div>
              {!dbConfig.use_kerberos && (
                <div>
                  <Label>Password</Label>
                  <Input 
                    type="password"
                    value={dbConfig.password}
                    onChange={(e) => {
                      setDbConfig({...dbConfig, password: e.target.value});
                      setConnectionTested(false);
                    }}
                    placeholder="password"
                  />
                </div>
              )}
            </div>

            <div>
              <Label>{dbConfig.source_type === 'oracle' ? 'Service Name' : 'Database'}</Label>
              <Input 
                value={dbConfig.source_type === 'oracle' ? dbConfig.service_name : dbConfig.database}
                onChange={(e) => {
                  if (dbConfig.source_type === 'oracle') {
                    setDbConfig({...dbConfig, service_name: e.target.value});
                  } else {
                    setDbConfig({...dbConfig, database: e.target.value});
                  }
                  setConnectionTested(false);
                }}
                placeholder={dbConfig.source_type === 'oracle' ? 'XEPDB1' : 'database_name'}
              />
            </div>
              </>
            )}

            <Button
              onClick={testConnection}
              disabled={loading}
              variant="outline"
              className="w-full"
            >
              {loading ? (
                <><Loader2 className="w-4 h-4 animate-spin mr-2" /> Testing...</>
              ) : connectionTested ? (
                <><Check className="w-4 h-4 mr-2 text-green-600" /> Connected</>
              ) : (
                <><Database className="w-4 h-4 mr-2" /> Test Connection</>
              )}
            </Button>

            {connectionTested && (
              <div className="space-y-4">
                <div>
                  <Label>SQL Query</Label>
                  <textarea
                    value={customQuery}
                    onChange={(e) => setCustomQuery(e.target.value)}
                    placeholder={`Example:\nSELECT e.name, e.salary, d.department_name\nFROM employees e\nJOIN departments d ON e.dept_id = d.id\nWHERE e.salary > 50000\nORDER BY e.salary DESC\nLIMIT 1000`}
                    className="w-full h-40 p-3 border rounded-md font-mono text-sm"
                    style={{ resize: 'vertical' }}
                  />
                  <p className="text-xs text-gray-500 mt-1">
                    {dbConfig.source_type === 'mongodb' 
                      ? 'For MongoDB, enter collection name (SQL not applicable)'
                      : 'Enter your SQL query. Results limited to 10,000 rows.'}
                  </p>
                </div>

                <Button
                  onClick={executeCustomQuery}
                  disabled={loading || !customQuery.trim()}
                  className="w-full"
                >
                  {loading ? (
                    <><Loader2 className="w-4 h-4 animate-spin mr-2" /> Executing Query...</>
                  ) : (
                    <><Code className="w-4 h-4 mr-2" /> Execute Query</>
                  )}
                </Button>
                
                {/* Query Results Preview */}
                {queryResults && (
                  <div className="mt-4 p-4 bg-green-50 border border-green-200 rounded-md space-y-3">
                    <div className="flex items-start justify-between">
                      <div>
                        <h4 className="font-semibold text-green-900">✓ Query Executed Successfully</h4>
                        <p className="text-sm text-green-700 mt-1">
                          Found {queryResults.row_count} rows × {queryResults.column_count} columns
                        </p>
                      </div>
                      <X 
                        className="w-5 h-5 text-green-600 cursor-pointer hover:text-green-800" 
                        onClick={() => setQueryResults(null)}
                      />
                    </div>
                    
                    {queryResults.preview && queryResults.preview.length > 0 && (
                      <div className="mt-2">
                        <p className="text-xs text-green-700 mb-2">Preview (first 3 rows):</p>
                        <div className="bg-white p-2 rounded border border-green-300 overflow-x-auto">
                          <table className="text-xs w-full">
                            <thead>
                              <tr className="border-b">
                                {queryResults.columns.slice(0, 6).map((col, idx) => (
                                  <th key={idx} className="text-left p-1 font-semibold">{col}</th>
                                ))}
                                {queryResults.columns.length > 6 && <th className="text-left p-1">...</th>}
                              </tr>
                            </thead>
                            <tbody>
                              {queryResults.preview.slice(0, 3).map((row, rowIdx) => (
                                <tr key={rowIdx} className="border-b">
                                  {queryResults.columns.slice(0, 6).map((col, colIdx) => (
                                    <td key={colIdx} className="p-1">{String(row[col]).substring(0, 30)}</td>
                                  ))}
                                  {queryResults.columns.length > 6 && <td className="p-1">...</td>}
                                </tr>
                              ))}
                            </tbody>
                          </table>
                        </div>
                      </div>
                    )}
                    
                    <Button
                      onClick={loadQueryResults}
                      className="w-full bg-green-600 hover:bg-green-700"
                    >
                      <Database className="w-4 h-4 mr-2" /> Load Data
                    </Button>
                  </div>
                )}
              </div>
            )}
          </div>
        </TabsContent>
      </Tabs>
      
      {/* Dataset Naming Dialog */}
      {showNameDialog && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-md w-full mx-4">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Name Your Dataset</h3>
            <p className="text-sm text-gray-600 mb-4">
              Give this query result a meaningful name for easy identification in analysis.
            </p>
            <Input
              value={datasetName}
              onChange={(e) => setDatasetName(e.target.value)}
              placeholder="e.g., Customer Orders Analysis"
              className="mb-4"
              autoFocus
              onKeyDown={(e) => {
                if (e.key === 'Enter' && datasetName.trim()) {
                  saveQueryDataset();
                }
              }}
            />
            <div className="flex gap-3">
              <Button
                onClick={() => {
                  setShowNameDialog(false);
                  setDatasetName("");
                }}
                variant="outline"
                className="flex-1"
              >
                Cancel
              </Button>
              <Button
                onClick={saveQueryDataset}
                disabled={!datasetName.trim() || loading}
                className="flex-1"
              >
                {loading ? (
                  <><Loader2 className="w-4 h-4 animate-spin mr-2" /> Saving...</>
                ) : (
                  'Save Dataset'
                )}
              </Button>
            </div>
          </div>
        </div>
      )}

      {/* Workspace Creation Dialog */}
      {showWorkspaceDialog && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <Card className="w-full max-w-md p-6">
            <h3 className="text-lg font-semibold mb-4">Create New Workspace</h3>
            <div className="space-y-4">
              <div>
                <Label htmlFor="workspace-name">Workspace Name</Label>
                <Input
                  id="workspace-name"
                  value={newWorkspaceName}
                  onChange={(e) => setNewWorkspaceName(e.target.value)}
                  placeholder="e.g., Sales Forecasting Q4 2024"
                  autoFocus
                  onKeyPress={(e) => e.key === 'Enter' && createWorkspace()}
                />
                <p className="text-xs text-gray-500 mt-1">
                  Use descriptive names like "Customer Churn Analysis" or "Revenue Prediction 2024"
                </p>
              </div>
              <div className="flex gap-3">
                <Button
                  variant="outline"
                  onClick={() => {
                    setShowWorkspaceDialog(false);
                    setNewWorkspaceName("");
                  }}
                  className="flex-1"
                >
                  Cancel
                </Button>
                <Button
                  onClick={createWorkspace}
                  disabled={!newWorkspaceName.trim()}
                  className="flex-1"
                >
                  Create Workspace
                </Button>
              </div>
            </div>
          </Card>
        </div>
      )}
    </Card>
  );
};

export default DataSourceSelector;