import { useState } from "react";
import axios from "axios";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { toast } from "sonner";
import { useDropzone } from "react-dropzone";
import { Upload, Database, Loader2, Check, X } from "lucide-react";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const DataSourceSelector = ({ onDatasetLoaded }) => {
  const [loading, setLoading] = useState(false);
  const [dbConfig, setDbConfig] = useState({
    source_type: "postgresql",
    host: "",
    port: "",
    database: "",
    username: "",
    password: "",
    service_name: "" // for Oracle
  });
  const [connectionTested, setConnectionTested] = useState(false);
  const [tables, setTables] = useState([]);
  const [selectedTable, setSelectedTable] = useState("");

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

  const handleFileUpload = async (file) => {
    setLoading(true);
    const formData = new FormData();
    formData.append("file", file);

    try {
      const response = await axios.post(`${API}/datasource/upload-file`, formData, {
        headers: { "Content-Type": "multipart/form-data" }
      });
      toast.success("File uploaded successfully!");
      onDatasetLoaded(response.data);
    } catch (error) {
      toast.error("File upload failed: " + (error.response?.data?.detail || error.message));
    } finally {
      setLoading(false);
    }
  };

  const testConnection = async () => {
    setLoading(true);
    try {
      const response = await axios.post(`${API}/datasource/test-connection`, {
        source_type: dbConfig.source_type,
        config: dbConfig
      });
      
      if (response.data.success) {
        toast.success("Connection successful!");
        setConnectionTested(true);
        await loadTables();
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

  const loadTables = async () => {
    try {
      const response = await axios.post(`${API}/datasource/list-tables`, {
        source_type: dbConfig.source_type,
        config: dbConfig
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
      toast.error("Table load failed: " + (error.response?.data?.detail || error.message));
    } finally {
      setLoading(false);
    }
  };

  return (
    <Card className="p-6 bg-white/90 backdrop-blur-sm" data-testid="data-source-selector">
      <h2 className="text-2xl font-bold mb-6">Select Data Source</h2>
      
      <Tabs defaultValue="file">
        <TabsList className="grid w-full grid-cols-2 mb-6">
          <TabsTrigger value="file" data-testid="tab-file-upload">File Upload</TabsTrigger>
          <TabsTrigger value="database" data-testid="tab-database">Database Connection</TabsTrigger>
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
          {loading && (
            <div className="mt-4 flex items-center justify-center gap-2 text-blue-600">
              <Loader2 className="w-5 h-5 animate-spin" />
              <span>Uploading...</span>
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
                  <SelectItem value="oracle">Oracle</SelectItem>
                  <SelectItem value="mongodb">MongoDB</SelectItem>
                </SelectContent>
              </Select>
            </div>

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
                  placeholder={dbConfig.source_type === 'oracle' ? '1521' : '5432'}
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
      </Tabs>
    </Card>
  );
};

export default DataSourceSelector;