import { useState, useEffect, useRef } from "react";
import axios from "axios";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { toast } from "sonner";
import { Loader2, TrendingUp, AlertCircle, ChevronDown, ChevronUp, MessageSquare, X, Send, RefreshCw, Save, FolderOpen, Trash2 } from "lucide-react";
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from "@/components/ui/collapsible";
import { Input } from "@/components/ui/input";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Load Plotly
const loadPlotly = () => {
  return new Promise((resolve) => {
    if (window.Plotly) {
      resolve(window.Plotly);
      return;
    }
    const script = document.createElement('script');
    script.src = 'https://cdn.plot.ly/plotly-2.27.0.min.js';
    script.async = true;
    script.onload = () => resolve(window.Plotly);
    document.head.appendChild(script);
  });
};

const PredictiveAnalysis = ({ dataset, analysisCache, onAnalysisUpdate }) => {
  const [loading, setLoading] = useState(false);
  const [analysisResults, setAnalysisResults] = useState(analysisCache || null);
  const [collapsed, setCollapsed] = useState({});
  const [showChat, setShowChat] = useState(false);
  const [chatMinimized, setChatMinimized] = useState(false);
  const [chatMessages, setChatMessages] = useState([]);
  const [chatInput, setChatInput] = useState("");
  const [chatLoading, setChatLoading] = useState(false);
  const [pendingAction, setPendingAction] = useState(null);
  const [showSaveDialog, setShowSaveDialog] = useState(false);
  const [stateName, setStateName] = useState("");
  const [savedStates, setSavedStates] = useState([]);
  const [showLoadDialog, setShowLoadDialog] = useState(false);
  const chatEndRef = useRef(null);

  // Use cached data if available
  useEffect(() => {
    if (analysisCache) {
      setAnalysisResults(analysisCache);
    } else if (dataset && !analysisResults) {
      runHolisticAnalysis();
    }
  }, [dataset, analysisCache]);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [chatMessages]);

  // Render correlation heatmap when available
  useEffect(() => {
    if (analysisResults?.correlation_heatmap) {
      loadPlotly().then((Plotly) => {
        const heatmapDiv = document.getElementById('correlation-heatmap');
        if (heatmapDiv) {
          const plotlyData = analysisResults.correlation_heatmap;
          Plotly.newPlot('correlation-heatmap', plotlyData.data, plotlyData.layout, {
            responsive: true,
            displayModeBar: true,
            modeBarButtonsToRemove: ['lasso2d', 'select2d']
          });
        }
      });
    }
  }, [analysisResults?.correlation_heatmap]);

  // Render custom charts when available
  useEffect(() => {
    if (analysisResults?.custom_charts && analysisResults.custom_charts.length > 0) {
      loadPlotly().then((Plotly) => {
        analysisResults.custom_charts.forEach((chart, idx) => {
          const chartDiv = document.getElementById(`custom-chart-${idx}`);
          if (chartDiv && chart.plotly_data) {
            const plotlyData = chart.plotly_data;
            Plotly.newPlot(`custom-chart-${idx}`, plotlyData.data, plotlyData.layout, {
              responsive: true,
              displayModeBar: true,
              modeBarButtonsToRemove: ['lasso2d', 'select2d']
            });
          }
        });
      });
    }
  }, [analysisResults?.custom_charts]);

  const runHolisticAnalysis = async () => {
    setLoading(true);
    toast.info("Running comprehensive AI/ML analysis...");
    
    try {
      const response = await axios.post(`${API}/analysis/holistic`, {
        dataset_id: dataset.id
      });

      setAnalysisResults(response.data);
      onAnalysisUpdate(response.data); // Cache the results
      toast.success("Comprehensive analysis complete!");
    } catch (error) {
      const errorMsg = error.response?.data?.detail || error.message || "Unknown error";
      console.error("Analysis error:", error);
      toast.error("Analysis failed: " + errorMsg);
      
      const errorResult = {
        error: true,
        message: errorMsg
      };
      setAnalysisResults(errorResult);
      onAnalysisUpdate(errorResult);
    } finally {
      setLoading(false);
    }
  };

  const refreshAnalysis = () => {
    setAnalysisResults(null);
    onAnalysisUpdate(null);
    runHolisticAnalysis();
  };

  const toggleSection = (section) => {
    setCollapsed(prev => ({ ...prev, [section]: !prev[section] }));
  };

  const expandAll = () => {
    setCollapsed({});
  };

  const collapseAll = () => {
    const allSections = ['summary', 'volume', 'trends', 'correlations', 'predictions', 'forecasts', 'custom_charts', 'ml_models'];
    const newCollapsed = {};
    allSections.forEach(s => newCollapsed[s] = true);
    setCollapsed(newCollapsed);
  };

  const sendChatMessage = async () => {
    if (!chatInput.trim()) return;

    const userMessage = chatInput;
    setChatInput("");
    setChatMessages(prev => [...prev, { role: "user", content: userMessage }]);
    setChatLoading(true);

    try {
      const response = await axios.post(`${API}/analysis/chat-action`, {
        dataset_id: dataset.id,
        message: userMessage,
        conversation_history: chatMessages,
        current_analysis: analysisResults
      });

      // Check if response contains actions - show confirmation instead of auto-execute
      if (response.data.action) {
        setPendingAction(response.data);
        setChatMessages(prev => [...prev, { 
          role: "assistant", 
          content: response.data.message || "I can help with that!",
          pendingAction: true,
          actionData: response.data
        }]);
      } else {
        setChatMessages(prev => [...prev, { role: "assistant", content: response.data.response }]);
      }
    } catch (error) {
      toast.error("Chat failed: " + (error.response?.data?.detail || error.message));
      setChatMessages(prev => [...prev, { 
        role: "assistant", 
        content: "Sorry, I encountered an error. Please try again or use the 'Refresh Analysis' button." 
      }]);
    } finally {
      setChatLoading(false);
    }
  };

  const executeAction = async (actionData) => {
    setChatLoading(true);
    try {
      if (actionData.action === 'refresh_analysis') {
        toast.info("Updating analysis...");
        await refreshAnalysis();
        setChatMessages(prev => [...prev, { 
          role: "assistant", 
          content: "✓ Analysis refreshed successfully! Check the updated results above." 
        }]);
      } else if (actionData.action === 'remove_section') {
        // Remove section from analysis
        const updatedResults = { ...analysisResults };
        const sectionToRemove = actionData.section_to_remove;
        
        if (sectionToRemove === 'correlations') {
          delete updatedResults.correlations;
          delete updatedResults.correlation_heatmap;
          toast.success("Correlation section removed!");
          setChatMessages(prev => [...prev, { 
            role: "assistant", 
            content: "✓ Correlation section has been removed." 
          }]);
        } else if (sectionToRemove === 'custom_chart' && updatedResults.custom_charts) {
          // Remove last custom chart
          updatedResults.custom_charts.pop();
          toast.success("Custom chart removed!");
          setChatMessages(prev => [...prev, { 
            role: "assistant", 
            content: "✓ Last custom chart has been removed." 
          }]);
        }
        
        setAnalysisResults(updatedResults);
        onAnalysisUpdate(updatedResults);
      } else if (actionData.action === 'add_chart') {
        // Add correlation or custom chart
        if (actionData.chart_data?.type === 'correlation') {
          // Add correlations to the analysis results
          const updatedResults = {
            ...analysisResults,
            correlations: actionData.chart_data.correlations || [],
            correlation_heatmap: actionData.chart_data.heatmap || null
          };
          setAnalysisResults(updatedResults);
          onAnalysisUpdate(updatedResults);
          
          // Auto-expand correlations section
          setCollapsed(prev => ({ ...prev, correlations: false }));
          
          toast.success("Correlation analysis added!");
          setChatMessages(prev => [...prev, { 
            role: "assistant", 
            content: "✓ Correlation analysis has been added! Scroll up to the 'Key Correlations' section to see the results." 
          }]);
        } else {
          // Generic custom chart (pie, bar, line, etc.)
          const updatedResults = {
            ...analysisResults,
            custom_charts: [...(analysisResults.custom_charts || []), actionData.chart_data]
          };
          setAnalysisResults(updatedResults);
          onAnalysisUpdate(updatedResults);
          
          // Auto-expand custom charts section
          setCollapsed(prev => ({ ...prev, custom_charts: false }));
          
          toast.success("Chart added successfully!");
          setChatMessages(prev => [...prev, { 
            role: "assistant", 
            content: "✓ Chart has been added to your analysis. Scroll up to see it!" 
          }]);
        }
      } else if (actionData.action === 'modify_analysis') {
        const updatedResults = {
          ...analysisResults,
          ...actionData.updated_data
        };
        setAnalysisResults(updatedResults);
        onAnalysisUpdate(updatedResults);
        toast.success("Analysis updated!");
        setChatMessages(prev => [...prev, { 
          role: "assistant", 
          content: "✓ Analysis has been updated based on your request." 
        }]);
      }
      setPendingAction(null);
    } catch (error) {
      toast.error("Action failed: " + error.message);
    } finally {
      setChatLoading(false);
    }
  };

  const cancelAction = () => {
    setPendingAction(null);
    setChatMessages(prev => [...prev, { 
      role: "assistant", 
      content: "Action cancelled. Let me know if you need anything else!" 
    }]);
  };


  // Load saved states on mount
  useEffect(() => {
    if (dataset) {
      loadSavedStates();
    }
  }, [dataset]);

  const loadSavedStates = async () => {
    try {
      const response = await axios.get(`${API}/analysis/saved-states/${dataset.id}`);
      setSavedStates(response.data.states || []);
    } catch (error) {
      console.error("Failed to load saved states:", error);
    }
  };

  const saveAnalysisState = async () => {
    if (!stateName.trim()) {
      toast.error("Please enter a name for this analysis state");
      return;
    }

    try {
      await axios.post(`${API}/analysis/save-state`, {
        dataset_id: dataset.id,
        state_name: stateName,
        analysis_data: analysisResults,
        chat_history: chatMessages
      });
      
      toast.success(`Analysis saved as "${stateName}"`);
      setStateName("");
      setShowSaveDialog(false);
      loadSavedStates();
    } catch (error) {
      toast.error("Failed to save analysis: " + (error.response?.data?.detail || error.message));
    }
  };

  const loadAnalysisState = async (stateId) => {
    try {
      const response = await axios.get(`${API}/analysis/load-state/${stateId}`);
      setAnalysisResults(response.data.analysis_data);
      setChatMessages(response.data.chat_history || []);
      onAnalysisUpdate(response.data.analysis_data);
      toast.success("Analysis state loaded successfully");
      setShowLoadDialog(false);
    } catch (error) {
      toast.error("Failed to load analysis: " + (error.response?.data?.detail || error.message));
    }
  };

  const deleteState = async (stateId, event) => {
    event.stopPropagation();
    if (!confirm("Are you sure you want to delete this saved state?")) {
      return;
    }
    
    try {
      await axios.delete(`${API}/analysis/delete-state/${stateId}`);
      toast.success("Saved state deleted");
      loadSavedStates();
    } catch (error) {
      toast.error("Failed to delete state: " + (error.response?.data?.detail || error.message));
    }
  };


  if (loading && !analysisResults) {
    return (
      <div className="flex items-center justify-center py-12" data-testid="predictive-analysis">
        <Loader2 className="w-8 h-8 animate-spin text-blue-600" />
        <span className="ml-3 text-lg">Running AI/ML analysis on entire dataset...</span>
      </div>
    );
  }

  if (!analysisResults) {
    return (
      <div className="flex items-center justify-center py-12">
        <p className="text-gray-600">Loading analysis...</p>
      </div>
    );
  }

  if (analysisResults.error) {
    return (
      <div className="space-y-6" data-testid="predictive-analysis">
        <Card className="p-6 bg-red-50 border-red-200">
          <h3 className="text-lg font-semibold text-red-800 mb-2">Analysis Error</h3>
          <p className="text-sm text-red-700 mb-4">{analysisResults.message}</p>
          <p className="text-sm text-gray-600">
            This may happen if you selected an old dataset. Please try uploading a new file.
          </p>
          <Button
            data-testid="retry-analysis-btn"
            onClick={refreshAnalysis}
            className="mt-4"
            variant="outline"
          >
            Retry Analysis
          </Button>
        </Card>
      </div>
    );
  }

  return (
    <div className="relative space-y-6" data-testid="predictive-analysis">
      {/* Header with Controls */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold">Predictive Analysis & Forecasting</h2>
          <p className="text-sm text-gray-600">AI-powered predictions, trends, and future forecasts</p>
        </div>
        <div className="flex gap-2">
          <Button onClick={expandAll} variant="outline" size="sm">
            <ChevronDown className="w-4 h-4 mr-2" />
            Expand All
          </Button>
          <Button onClick={collapseAll} variant="outline" size="sm">
            <ChevronUp className="w-4 h-4 mr-2" />
            Collapse All
          </Button>
          <Button
            data-testid="refresh-analysis-btn"
            onClick={refreshAnalysis}
            disabled={loading}
            variant="default"
          >
            {loading ? <Loader2 className="w-4 h-4 animate-spin mr-2" /> : <RefreshCw className="w-4 h-4 mr-2" />}
            Refresh
          </Button>
          <Button
            data-testid="toggle-chat-btn"
            onClick={() => setShowChat(!showChat)}
            variant="outline"
          >
            <MessageSquare className="w-4 h-4 mr-2" />
            Chat
          </Button>
          <Button
            onClick={() => setShowSaveDialog(true)}
            variant="outline"
            size="sm"
          >
            <Save className="w-4 h-4 mr-2" />
            Save
          </Button>
          {savedStates.length > 0 && (
            <Button
              onClick={() => setShowLoadDialog(true)}
              variant="outline"
              size="sm"
            >
              <FolderOpen className="w-4 h-4 mr-2" />
              Load ({savedStates.length})
            </Button>
          )}
        </div>
      </div>

      {/* AI Summary - TOP POSITION */}
      {analysisResults.ai_summary && !collapsed.summary && (
        <Card className="p-6 bg-gradient-to-br from-purple-50 to-blue-50 border-purple-200">
          <div className="flex items-start justify-between mb-3">
            <h3 className="text-lg font-semibold flex items-center gap-2">
              <AlertCircle className="w-5 h-5 text-purple-600" />
              AI Executive Summary
            </h3>
            <Button onClick={() => toggleSection('summary')} variant="ghost" size="sm">
              <ChevronUp className="w-4 h-4" />
            </Button>
          </div>
          <p className="text-sm text-gray-600 italic mb-3">AI-generated overview of key findings and insights</p>
          <div className="prose prose-sm max-w-none">
            <p className="whitespace-pre-wrap text-gray-700">{String(analysisResults.ai_summary)}</p>
          </div>
        </Card>
      )}

      {analysisResults.ai_summary && collapsed.summary && (
        <Card className="p-4 cursor-pointer hover:bg-gray-50" onClick={() => toggleSection('summary')}>
          <div className="flex items-center justify-between">
            <h3 className="text-lg font-semibold">AI Executive Summary</h3>
            <ChevronDown className="w-5 h-5" />
          </div>
        </Card>
      )}

      {/* Rest of sections with collapse... */}
      {/* Volume Analysis */}
      {analysisResults.volume_analysis && analysisResults.volume_analysis.by_dimensions && analysisResults.volume_analysis.by_dimensions.length > 0 && !collapsed.volume && (
        <Card className="p-6">
          <div className="flex items-start justify-between mb-4">
            <div>
              <h3 className="text-lg font-semibold">📊 Volume Analysis</h3>
              <p className="text-sm text-gray-600 italic mt-1">Analysis of data distribution across different dimensions</p>
            </div>
            <Button onClick={() => toggleSection('volume')} variant="ghost" size="sm">
              <ChevronUp className="w-4 h-4" />
            </Button>
          </div>
          <div className="space-y-4">
            {analysisResults.volume_analysis.by_dimensions.map((item, idx) => (
              <div key={idx} className="p-4 bg-blue-50 rounded-lg border border-blue-200">
                <h4 className="font-semibold mb-2">{String(item.dimension)}</h4>
                <p className="text-sm text-gray-700">{String(item.insights)}</p>
              </div>
            ))}
          </div>
        </Card>
      )}

      {analysisResults.volume_analysis && collapsed.volume && (
        <Card className="p-4 cursor-pointer hover:bg-gray-50" onClick={() => toggleSection('volume')}>
          <div className="flex items-center justify-between">
            <h3 className="text-lg font-semibold">📊 Volume Analysis</h3>
            <ChevronDown className="w-5 h-5" />
          </div>
        </Card>
      )}

      {/* Correlations */}
      {analysisResults.correlations && analysisResults.correlations.length > 0 && !collapsed.correlations && (
        <Card className="p-6">
          <div className="flex items-start justify-between mb-4">
            <div>
              <h3 className="text-lg font-semibold">🔗 Key Correlations</h3>
              <p className="text-sm text-gray-600 italic mt-1">Statistical relationships between variables in your dataset</p>
            </div>
            <Button onClick={() => toggleSection('correlations')} variant="ghost" size="sm">
              <ChevronUp className="w-4 h-4" />
            </Button>
          </div>
          
          {/* Correlation Heatmap */}
          {analysisResults.correlation_heatmap && (
            <div className="mb-6">
              <h4 className="font-semibold mb-3">Correlation Matrix Heatmap</h4>
              <div className="bg-white rounded-lg p-4 border border-gray-200">
                <div id="correlation-heatmap" style={{ width: '100%', height: '500px' }}></div>
              </div>
            </div>
          )}
          
          {/* Correlation List */}
          <div className="space-y-3">
            {analysisResults.correlations.map((corr, idx) => (
              <div key={idx} className="flex items-center gap-3 p-3 bg-purple-50 rounded-lg border border-purple-200">
                <div className="flex-1">
                  <p className="font-medium">{String(corr.feature1)} ↔ {String(corr.feature2)}</p>
                  <p className="text-sm text-gray-600">{String(corr.interpretation)}</p>
                </div>
                <div className="text-right">
                  <div className="text-2xl font-bold text-purple-600">{Number(corr.value).toFixed(2)}</div>
                  <div className="text-xs text-gray-500">{String(corr.strength)}</div>
                </div>
              </div>
            ))}
          </div>
        </Card>
      )}

      {analysisResults.correlations && analysisResults.correlations.length > 0 && collapsed.correlations && (
        <Card className="p-4 cursor-pointer hover:bg-gray-50" onClick={() => toggleSection('correlations')}>
          <div className="flex items-center justify-between">
            <h3 className="text-lg font-semibold">🔗 Key Correlations ({analysisResults.correlations.length} found)</h3>
            <ChevronDown className="w-5 h-5" />
          </div>
        </Card>
      )}

      {/* Custom Charts Section */}
      {analysisResults.custom_charts && analysisResults.custom_charts.length > 0 && !collapsed.custom_charts && (
        <Card className="p-6">
          <div className="flex items-start justify-between mb-4">
            <div>
              <h3 className="text-lg font-semibold">📈 Custom Analysis Charts</h3>
              <p className="text-sm text-gray-600 italic mt-1">Additional charts added via chat assistant</p>
            </div>
            <Button onClick={() => toggleSection('custom_charts')} variant="ghost" size="sm">
              <ChevronUp className="w-4 h-4" />
            </Button>
          </div>
          
          <div className="space-y-6">
            {analysisResults.custom_charts.map((chart, idx) => (
              <div key={idx} className="bg-white rounded-lg p-4 border border-gray-200">
                <h4 className="font-semibold mb-2">{chart.title}</h4>
                {chart.description && (
                  <p className="text-sm text-gray-600 italic mb-3">{chart.description}</p>
                )}
                <div id={`custom-chart-${idx}`} style={{ width: '100%', height: '500px' }}></div>
              </div>
            ))}
          </div>
        </Card>
      )}

      {analysisResults.custom_charts && analysisResults.custom_charts.length > 0 && collapsed.custom_charts && (
        <Card className="p-4 cursor-pointer hover:bg-gray-50" onClick={() => toggleSection('custom_charts')}>
          <div className="flex items-center justify-between">
            <h3 className="text-lg font-semibold">📈 Custom Analysis Charts ({analysisResults.custom_charts.length})</h3>
            <ChevronDown className="w-5 h-5" />
          </div>
        </Card>
      )}

      {/* Rest of sections... */}


      {/* ML Models Section */}
      {analysisResults.ml_models && analysisResults.ml_models.length > 0 && !collapsed.ml_models && (
        <Card className="p-6">
          <div className="flex items-start justify-between mb-4">
            <div>
              <h3 className="text-lg font-semibold">🤖 ML Model Comparison</h3>
              <p className="text-sm text-gray-600 italic mt-1">Compare performance of different machine learning models</p>
            </div>
            <Button onClick={() => toggleSection('ml_models')} variant="ghost" size="sm">
              <ChevronUp className="w-4 h-4" />
            </Button>
          </div>
          
          {/* Group models by target column */}
          {(() => {
            const modelsByTarget = {};
            analysisResults.ml_models.forEach(model => {
              if (!modelsByTarget[model.target_column]) {
                modelsByTarget[model.target_column] = [];
              }
              modelsByTarget[model.target_column].push(model);
            });
            
            return Object.entries(modelsByTarget).map(([targetCol, models]) => (
              <div key={targetCol} className="mb-6">
                <h4 className="font-semibold mb-3">Predicting: {targetCol}</h4>
                <Tabs defaultValue={models[0].model_name} className="w-full">
                  <TabsList className="grid w-full grid-cols-4 mb-4">
                    {models.map((model) => (
                      <TabsTrigger key={model.model_name} value={model.model_name}>
                        {model.model_name}
                      </TabsTrigger>
                    ))}
                  </TabsList>
                  
                  {models.map((model) => (
                    <TabsContent key={model.model_name} value={model.model_name}>
                      <div className="bg-gradient-to-br from-blue-50 to-indigo-50 rounded-lg p-6 border border-blue-200">
                        <div className="grid md:grid-cols-3 gap-4 mb-4">
                          <div className="bg-white rounded-lg p-4 shadow-sm">
                            <div className="text-sm text-gray-600">R² Score</div>
                            <div className="text-2xl font-bold text-blue-600">{model.r2_score.toFixed(3)}</div>
                          </div>
                          <div className="bg-white rounded-lg p-4 shadow-sm">
                            <div className="text-sm text-gray-600">RMSE</div>
                            <div className="text-2xl font-bold text-purple-600">{model.rmse.toFixed(3)}</div>
                          </div>
                          <div className="bg-white rounded-lg p-4 shadow-sm">
                            <div className="text-sm text-gray-600">Confidence</div>
                            <div className={`text-2xl font-bold ${
                              model.confidence === 'High' ? 'text-green-600' : 
                              model.confidence === 'Medium' ? 'text-yellow-600' : 'text-red-600'
                            }`}>{model.confidence}</div>
                          </div>
                        </div>
                        
                        {model.feature_importance && Object.keys(model.feature_importance).length > 0 && (
                          <div className="mt-4">
                            <h5 className="font-semibold mb-2">Feature Importance</h5>
                            <div className="space-y-2">
                              {Object.entries(model.feature_importance).slice(0, 5).map(([feature, importance]) => (
                                <div key={feature} className="flex items-center gap-2">
                                  <span className="text-sm w-32 truncate">{feature}</span>
                                  <div className="flex-1 bg-gray-200 rounded-full h-2">
                                    <div 
                                      className="bg-blue-600 rounded-full h-2" 
                                      style={{width: `${importance * 100}%`}}
                                    ></div>
                                  </div>
                                  <span className="text-sm text-gray-600 w-16 text-right">{(importance * 100).toFixed(1)}%</span>
                                </div>
                              ))}
                            </div>
                          </div>
                        )}
                      </div>
                    </TabsContent>
                  ))}
                </Tabs>
              </div>
            ));
          })()}
        </Card>
      )}

      {analysisResults.ml_models && analysisResults.ml_models.length > 0 && collapsed.ml_models && (
        <Card className="p-4 cursor-pointer hover:bg-gray-50" onClick={() => toggleSection('ml_models')}>
          <div className="flex items-center justify-between">
            <h3 className="text-lg font-semibold">🤖 ML Model Comparison ({analysisResults.ml_models.length} models)</h3>
            <ChevronDown className="w-5 h-5" />
          </div>
        </Card>
      )}

      {/* Chat Panel */}
      {showChat && !chatMinimized && (
        <div className="fixed right-6 bottom-6 w-96 h-[500px] bg-white rounded-xl shadow-2xl border border-gray-200 flex flex-col z-50">
          <div className="p-4 border-b flex items-center justify-between bg-gradient-to-r from-blue-600 to-indigo-600 text-white rounded-t-xl">
            <h3 className="font-semibold">Analysis Assistant</h3>
            <div className="flex gap-2">
              <Button
                onClick={() => setChatMinimized(true)}
                variant="ghost"
                size="sm"
                className="text-white hover:bg-white/20"
                data-testid="minimize-chat-btn"
              >
                <ChevronDown className="w-4 h-4" />
              </Button>
              <Button
                onClick={() => setShowChat(false)}
                variant="ghost"
                size="sm"
                className="text-white hover:bg-white/20"
                data-testid="close-chat-btn"
              >
                <X className="w-4 h-4" />
              </Button>
            </div>
          </div>
          
          <div className="flex-1 overflow-y-auto p-4 space-y-3">
            {chatMessages.length === 0 && (
              <div className="text-center text-gray-500 mt-8">
                <MessageSquare className="w-12 h-12 mx-auto mb-3 text-gray-400" />
                <p className="text-sm">Ask me to:</p>
                <ul className="text-xs mt-2 space-y-1">
                  <li>• Add new charts or analysis</li>
                  <li>• Modify existing visualizations</li>
                  <li>• Explain specific results</li>
                  <li>• Refresh with latest data</li>
                </ul>
              </div>
            )}
            {chatMessages.map((msg, idx) => (
              <div key={idx} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                <div className={`max-w-[80%] ${
                  msg.role === 'user' 
                    ? 'bg-blue-600 text-white p-3 rounded-lg' 
                    : 'space-y-2'
                }`}>
                  {msg.role === 'assistant' && (
                    <div className="bg-gray-100 text-gray-800 p-3 rounded-lg">
                      <p className="text-sm whitespace-pre-wrap">{msg.content}</p>
                    </div>
                  )}
                  {msg.role === 'user' && (
                    <p className="text-sm whitespace-pre-wrap">{msg.content}</p>
                  )}
                  {msg.pendingAction && msg.actionData && (
                    <div className="flex gap-2 mt-2">
                      <Button
                        onClick={() => executeAction(msg.actionData)}
                        disabled={chatLoading}
                        size="sm"
                        className="bg-green-600 hover:bg-green-700 text-white"
                        data-testid="append-chart-btn"
                      >
                        ✓ Append to Analysis
                      </Button>
                      <Button
                        onClick={cancelAction}
                        disabled={chatLoading}
                        size="sm"
                        variant="outline"
                        data-testid="cancel-action-btn"
                      >
                        Cancel
                      </Button>
                    </div>
                  )}
                </div>
              </div>
            ))}
            {chatLoading && (
              <div className="flex justify-start">
                <div className="bg-gray-100 p-3 rounded-lg">
                  <Loader2 className="w-4 h-4 animate-spin text-gray-600" />
                </div>
              </div>
            )}
            <div ref={chatEndRef} />
          </div>
          
          <div className="p-4 border-t">
            <div className="flex gap-2">
              <Input
                value={chatInput}
                onChange={(e) => setChatInput(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && sendChatMessage()}
                placeholder="Ask about your data..."
                disabled={chatLoading}
              />
              <Button onClick={sendChatMessage} disabled={chatLoading || !chatInput.trim()}>
                <Send className="w-4 h-4" />
              </Button>
            </div>
          </div>
        </div>
      )}

      {/* Minimized Chat Button */}
      {showChat && chatMinimized && (
        <div className="fixed right-6 bottom-6 z-50">
          <Button
            onClick={() => setChatMinimized(false)}
            className="bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 text-white shadow-2xl"
            size="lg"
            data-testid="restore-chat-btn"
          >
            <MessageSquare className="w-5 h-5 mr-2" />
            Chat Assistant {chatMessages.length > 0 && `(${chatMessages.length})`}
          </Button>
        </div>
      )}
    </div>
  );
};

export default PredictiveAnalysis;