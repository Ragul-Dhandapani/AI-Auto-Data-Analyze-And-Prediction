import { useState, useRef } from "react";
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

const DataSourceSelector = ({ onDatasetLoaded }) => {
  const [loading, setLoading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(null);
  const [estimatedTime, setEstimatedTime] = useState(null);
  const cancelTokenRef = useRef(null);
  const [useConnectionString, setUseConnectionString] = useState(false);
  const [connectionString, setConnectionString] = useState("");
  const [dbConfig, setDbConfig] = useState({
    source_type: "postgresql",
    host: "",
    port: "",
    database: "",
    username: "",
    password: "",
    service_name: ""
  });
  const [connectionTested, setConnectionTested] = useState(false);
  const [tables, setTables] = useState([]);
  const [selectedTable, setSelectedTable] = useState("");
  const [customQuery, setCustomQuery] = useState("");

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
      
      toast.success(`File uploaded in ${uploadTime.toFixed(1)}s!`);
      onDatasetLoaded(response.data);
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

    setLoading(true);
    const formData = new FormData();
    formData.append("source_type", dbConfig.source_type);
    formData.append("config", JSON.stringify(dbConfig));
    formData.append("table_name", selectedTable);

    try {
      const response = await axios.post(`${API}/datasource/load-table`, formData);
      toast.success("Table loaded successfully!");
      onDatasetLoaded(response.data);
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
      const queryConfig = useConnectionString 
        ? { 
            db_type: dbConfig.source_type,
            query: customQuery,
            ...(await parseConnectionString())
          }
        : {
            db_type: dbConfig.source_type,
            query: customQuery,
            host: dbConfig.host,
            port: dbConfig.port || getDefaultPort(),
            database: dbConfig.database,
            username: dbConfig.username,
            password: dbConfig.password,
            service_name: dbConfig.service_name
          };

      const response = await axios.post(`${API}/datasource/execute-query`, queryConfig);
      
      toast.success(`Query executed successfully! Loaded ${response.data.row_count} rows`, {
        description: response.data.size_mb ? `Size: ${response.data.size_mb} MB` : undefined
      });
      
      onDatasetLoaded(response.data);
      
      // Clear query after successful execution
      setCustomQuery("");
    } catch (error) {
      console.error("Query execution error:", error);
      toast.error("Query execution failed: " + (error.response?.data?.detail || error.message));
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

            <div className="grid md:grid-cols-2 gap-4">
              <div>
                <Label>Username</Label>
                <Input 
                  data-testid="db-username-input"
                  value={dbConfig.username}
                  onChange={(e) => setDbConfig({...dbConfig, username: e.target.value})}
                  placeholder="user"
                />
              </div>
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

            <div className="grid md:grid-cols-2 gap-4">
              <div>
                <Label>Username</Label>
                <Input 
                  value={dbConfig.username}
                  onChange={(e) => {
                    setDbConfig({...dbConfig, username: e.target.value});
                    setConnectionTested(false);
                  }}
                  placeholder="username"
                />
              </div>
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
                    <><Code className="w-4 h-4 mr-2" /> Execute Query & Load Data</>
                  )}
                </Button>
              </div>
            )}
          </div>
        </TabsContent>
      </Tabs>
    </Card>
  );
};

export default DataSourceSelector;