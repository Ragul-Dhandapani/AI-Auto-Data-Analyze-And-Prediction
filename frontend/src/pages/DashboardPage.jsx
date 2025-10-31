import { useState, useEffect } from "react";
import axios from "axios";
import { toast } from "sonner";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import DataSourceSelector from "@/components/DataSourceSelector";
import DataProfiler from "@/components/DataProfiler";
import PredictiveAnalysis from "@/components/PredictiveAnalysis";
import VisualizationPanel from "@/components/VisualizationPanel";
import { Sparkles, ArrowLeft, Home } from "lucide-react";
import { useNavigate } from "react-router-dom";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const DashboardPage = () => {
  const navigate = useNavigate();
  const [currentStep, setCurrentStep] = useState("data-source");
  const [selectedDataset, setSelectedDataset] = useState(null);
  const [datasets, setDatasets] = useState([]);

  useEffect(() => {
    loadDatasets();
  }, []);

  const loadDatasets = async () => {
    try {
      const response = await axios.get(`${API}/datasets`);
      setDatasets(response.data.datasets || []);
    } catch (error) {
      console.error("Failed to load datasets", error);
    }
  };

  const handleDatasetLoaded = (dataset) => {
    setSelectedDataset(dataset);
    loadDatasets();
    toast.success("Dataset loaded successfully!");
  };

  const handleDatasetSelect = (dataset) => {
    setSelectedDataset(dataset);
    setCurrentStep("analysis");
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-100">
      {/* Navigation */}
      <nav className="fixed top-0 left-0 right-0 z-50 backdrop-blur-md bg-white/80 border-b border-gray-200 shadow-sm">
        <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <Button
              data-testid="back-to-home-btn"
              variant="ghost"
              onClick={() => navigate('/')}
              className="gap-2"
            >
              <ArrowLeft className="w-4 h-4" />
              Back
            </Button>
            <div className="flex items-center gap-2">
              <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-blue-600 to-indigo-600 flex items-center justify-center">
                <Sparkles className="w-6 h-6 text-white" />
              </div>
              <span className="text-2xl font-bold bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent">
                PROMISE
              </span>
            </div>
          </div>
          <div className="text-sm text-gray-600">
            {selectedDataset && (
              <span data-testid="current-dataset-name">
                Current: <strong>{selectedDataset.name}</strong>
              </span>
            )}
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <div className="pt-24 pb-12 px-6">
        <div className="max-w-7xl mx-auto">
          <div className="mb-8">
            <h1 className="text-4xl font-bold mb-2">Data Analysis Dashboard</h1>
            <p className="text-gray-600">Upload data, analyze, and get AI-powered insights</p>
          </div>

          {!selectedDataset ? (
            <div>
              <DataSourceSelector onDatasetLoaded={handleDatasetLoaded} />
              
              {datasets.length > 0 && (
                <Card className="mt-8 p-6 bg-white/90 backdrop-blur-sm">
                  <h2 className="text-xl font-semibold mb-4">Recent Datasets</h2>
                  <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
                    {datasets.map((dataset) => (
                      <div
                        key={dataset.id}
                        data-testid={`dataset-card-${dataset.id}`}
                        className="p-4 border border-gray-200 rounded-xl hover:shadow-lg hover:border-blue-400 cursor-pointer transition-all bg-white"
                        onClick={() => handleDatasetSelect(dataset)}
                      >
                        <h3 className="font-semibold text-lg mb-2 truncate">{dataset.name}</h3>
                        <div className="text-sm text-gray-600 space-y-1">
                          <p>Rows: {dataset.row_count.toLocaleString()}</p>
                          <p>Columns: {dataset.column_count}</p>
                          {dataset.file_size && (
                            <p className="text-xs text-gray-500">
                              Size: {(dataset.file_size / 1024 / 1024).toFixed(2)} MB
                            </p>
                          )}
                          <p className="text-xs text-gray-400">
                            {new Date(dataset.created_at).toLocaleString()}
                          </p>
                        </div>
                      </div>
                    ))}
                  </div>
                </Card>
              )}
            </div>
          ) : (
            <div>
              <Card className="p-6 bg-white/90 backdrop-blur-sm">
                <Tabs defaultValue="profile" className="w-full">
                  <TabsList className="grid w-full grid-cols-3 mb-6">
                    <TabsTrigger value="profile" data-testid="tab-profile">Data Profile</TabsTrigger>
                    <TabsTrigger value="predict" data-testid="tab-predict">Predictive Analysis</TabsTrigger>
                    <TabsTrigger value="visualize" data-testid="tab-visualize">Visualizations</TabsTrigger>
                  </TabsList>

                  <TabsContent value="profile">
                    <DataProfiler dataset={selectedDataset} onLoadNewDataset={() => setSelectedDataset(null)} />
                  </TabsContent>

                  <TabsContent value="predict">
                    <PredictiveAnalysis dataset={selectedDataset} />
                  </TabsContent>

                  <TabsContent value="visualize">
                    <VisualizationPanel dataset={selectedDataset} />
                  </TabsContent>
                </Tabs>
              </Card>

              <div className="mt-6 text-center">
                <Button
                  data-testid="load-new-dataset-btn"
                  variant="outline"
                  onClick={() => setSelectedDataset(null)}
                >
                  Load New Dataset
                </Button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default DashboardPage;