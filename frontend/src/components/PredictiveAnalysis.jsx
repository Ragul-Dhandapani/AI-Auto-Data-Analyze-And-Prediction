import { useState, useEffect, useRef } from "react";
import axios from "axios";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { toast } from "sonner";
import { Loader2, TrendingUp, AlertCircle, ChevronDown, ChevronUp, MessageSquare, X, Send, RefreshCw, Info } from "lucide-react";
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
  const [analysisTime, setAnalysisTime] = useState(null);  // Track analysis time
  const [progress, setProgress] = useState(0);  // Track progress percentage
  const [collapsed, setCollapsed] = useState({});
  const [showChat, setShowChat] = useState(false);
  const [chatMinimized, setChatMinimized] = useState(false);
  const [chatMessages, setChatMessages] = useState([]);
  const [chatInput, setChatInput] = useState("");
  const [chatLoading, setChatLoading] = useState(false);
  const [pendingAction, setPendingAction] = useState(null);
  const [chatPosition, setChatPosition] = useState({ x: null, y: null });
  const [isDragging, setIsDragging] = useState(false);
  const [dragOffset, setDragOffset] = useState({ x: 0, y: 0 });
  const chatEndRef = useRef(null);
  const progressIntervalRef = useRef(null);
  const hasRunAnalysisRef = useRef(false);  // Track if analysis has been triggered

  // Use cached data if available
  useEffect(() => {
    if (analysisCache) {
      setAnalysisResults(analysisCache);
      hasRunAnalysisRef.current = true;
    } else if (dataset && !analysisResults && !hasRunAnalysisRef.current && !loading) {
      hasRunAnalysisRef.current = true;
      runHolisticAnalysis();
    }
  }, [dataset, analysisCache]);

  // Reset ref when dataset changes
  useEffect(() => {
    hasRunAnalysisRef.current = !!analysisCache;
  }, [dataset?.id]);

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

  // Render custom charts when available OR when collapsed state changes
  useEffect(() => {
    if (analysisResults?.custom_charts && analysisResults.custom_charts.length > 0 && !collapsed.custom_charts) {
      loadPlotly().then((Plotly) => {
        // Filter charts with valid plotly_data
        const validCharts = analysisResults.custom_charts.filter(chart => 
          chart && chart.plotly_data
        );
        
        validCharts.forEach((chart, idx) => {
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
  }, [analysisResults?.custom_charts, collapsed.custom_charts]);

  // Render auto-generated charts when available OR when collapsed state changes
  useEffect(() => {
    if (analysisResults?.auto_charts && analysisResults.auto_charts.length > 0 && !collapsed.auto_charts) {
      loadPlotly().then((Plotly) => {
        // Filter charts with valid plotly_data
        const validCharts = analysisResults.auto_charts.filter(chart => 
          chart && chart.plotly_data
        );
        
        validCharts.forEach((chart, idx) => {
          const chartDiv = document.getElementById(`auto-chart-${idx}`);
          if (chartDiv && chart.plotly_data) {
            const plotlyData = chart.plotly_data;
            Plotly.newPlot(`auto-chart-${idx}`, plotlyData.data, plotlyData.layout, {
              responsive: true,
              displayModeBar: true,
              modeBarButtonsToRemove: ['lasso2d', 'select2d']
            });
          }
        });
      });
    }
  }, [analysisResults?.auto_charts, collapsed.auto_charts]);

  // Cleanup progress interval on unmount
  useEffect(() => {
    return () => {
      if (progressIntervalRef.current) {
        clearInterval(progressIntervalRef.current);
      }
    };
  }, []);

  const runHolisticAnalysis = async () => {
    setLoading(true);
    setProgress(0);
    const startTime = Date.now();
    toast.info("Running comprehensive AI/ML analysis...");
    
    // Simulate progress for better UX - cap at 90% until response received
    progressIntervalRef.current = setInterval(() => {
      setProgress(prev => {
        if (prev >= 90) return 90; // Cap at 90% until actual completion
        // Slow down as we approach 90%
        if (prev < 30) return prev + 3;
        if (prev < 60) return prev + 2;
        if (prev < 85) return prev + 1;
        return prev + 0.5; // Very slow after 85%
      });
    }, 500);
    
    try {
      const response = await axios.post(`${API}/analysis/holistic`, {
        dataset_id: dataset.id
      });

      const endTime = Date.now();
      const timeTaken = ((endTime - startTime) / 1000).toFixed(1); // in seconds
      setAnalysisTime(timeTaken);

      // Complete progress
      setProgress(100);
      
      setAnalysisResults(response.data);
      onAnalysisUpdate(response.data); // Cache the results
      toast.success(`Analysis complete in ${timeTaken}s!`);
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
      if (progressIntervalRef.current) {
        clearInterval(progressIntervalRef.current);
      }
      setLoading(false);
      setTimeout(() => setProgress(0), 1000); // Reset progress after 1s
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
    const allSections = ['summary', 'volume', 'trends', 'correlations', 'predictions', 'forecasts', 'custom_charts', 'ml_models', 'auto_charts'];
    const newCollapsed = {};
    allSections.forEach(s => newCollapsed[s] = true);
    setCollapsed(newCollapsed);
  };

  const sendChatMessage = async () => {
    if (!chatInput.trim()) return;

    const userMsg = chatInput;
    setChatInput("");
    setChatMessages(prev => [...prev, { role: "user", content: userMsg }]);
    setChatLoading(true);

    try {
      // Prepare simplified analysis data (exclude large Plotly data)
      const simplifiedAnalysis = analysisResults ? {
        has_correlations: !!analysisResults.correlations,
        has_ml_models: !!analysisResults.ml_models,
        has_custom_charts: !!analysisResults.custom_charts,
        custom_charts_count: analysisResults.custom_charts?.length || 0,
        volume_analysis: analysisResults.volume_analysis,
        predictions: analysisResults.predictions
      } : null;

      const response = await axios.post(`${API}/analysis/chat-action`, {
        dataset_id: dataset.id,
        message: userMsg,
        conversation_history: chatMessages.slice(-5).map(m => ({ role: m.role, content: m.content })),
        current_analysis: simplifiedAnalysis
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
      console.error("Chat error:", error);
      console.error("Error response:", error.response?.data);
      const errorMsg = error.response?.data?.detail || error.message || "Unknown error";
      toast.error("Chat failed: " + errorMsg);
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


  // Drag handlers for chat
  const handleChatMouseDown = (e) => {
    if (e.target.closest('.chat-header')) {
      setIsDragging(true);
      const rect = e.currentTarget.getBoundingClientRect();
      setDragOffset({
        x: e.clientX - rect.left,
        y: e.clientY - rect.top
      });
    }
  };

  useEffect(() => {
    const handleMouseMove = (e) => {
      if (isDragging) {
        setChatPosition({
          x: e.clientX - dragOffset.x,
          y: e.clientY - dragOffset.y
        });
      }
    };

    const handleMouseUp = () => {
      setIsDragging(false);
    };

    if (isDragging) {
      document.addEventListener('mousemove', handleMouseMove);
      document.addEventListener('mouseup', handleMouseUp);
    }

    return () => {
      document.removeEventListener('mousemove', handleMouseMove);
      document.removeEventListener('mouseup', handleMouseUp);
    };
  }, [isDragging, dragOffset]);

  if (loading && !analysisResults) {
    return (
      <div className="flex flex-col items-center justify-center py-12 space-y-6" data-testid="predictive-analysis">
        <Loader2 className="w-8 h-8 animate-spin text-blue-600" />
        <span className="text-lg">Running AI/ML analysis on entire dataset...</span>
        
        {/* Progress Bar */}
        <div className="w-full max-w-md">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm text-gray-600">Analysis Progress</span>
            <span className="text-sm font-semibold text-blue-600">{Math.min(Math.round(progress), 100)}%</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-3 overflow-hidden">
            <div 
              className="bg-gradient-to-r from-blue-500 to-blue-600 h-3 rounded-full transition-all duration-500 ease-out"
              style={{ width: `${Math.min(progress, 100)}%` }}
            />
          </div>
          <p className="text-xs text-gray-500 mt-2 text-center">
            {progress < 30 ? "Loading data and preparing..." : 
             progress < 60 ? "Running statistical analysis..." :
             progress < 85 ? "Training ML models..." :
             progress >= 90 ? "Finalizing analysis and generating charts..." :
             "Generating visualizations..."}
          </p>
        </div>
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

  if (analysisResults && analysisResults.error) {
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
          <div className="flex items-center gap-2">
            <p className="text-sm text-gray-600">AI-powered predictions, trends, and future forecasts</p>
            {analysisTime && (
              <span className="text-xs bg-green-100 text-green-700 px-2 py-1 rounded-full font-medium">
                ⚡ Completed in {analysisTime}s
              </span>
            )}
          </div>
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

      {/* Training Metadata */}
      {analysisResults.training_metadata && (
        <Card className="p-4 bg-gradient-to-r from-green-50 to-teal-50 border-green-200">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-full bg-green-100 flex items-center justify-center">
                <RefreshCw className="w-5 h-5 text-green-600" />
              </div>
              <div>
                <h4 className="font-semibold text-gray-800">Self-Training Model</h4>
                <p className="text-sm text-gray-600">
                  Trained <span className="font-bold text-green-600">{analysisResults.training_metadata.training_count}</span> time{analysisResults.training_metadata.training_count !== 1 ? 's' : ''} on this dataset
                </p>
              </div>
            </div>
            <div className="text-right text-sm text-gray-600">
              <p>Dataset Size: {analysisResults.training_metadata.dataset_size?.toLocaleString()} rows</p>
              <p className="text-xs mt-1">Last trained: {new Date(analysisResults.training_metadata.last_trained_at).toLocaleString()}</p>
            </div>
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
      {analysisResults.custom_charts && analysisResults.custom_charts.filter(chart => chart && chart.plotly_data).length > 0 && !collapsed.custom_charts && (
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
            {analysisResults.custom_charts
              .filter(chart => chart && chart.plotly_data)
              .map((chart, idx) => (
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

      {analysisResults.custom_charts && analysisResults.custom_charts.filter(chart => chart && chart.plotly_data).length > 0 && collapsed.custom_charts && (
        <Card className="p-4 cursor-pointer hover:bg-gray-50" onClick={() => toggleSection('custom_charts')}>
          <div className="flex items-center justify-between">
            <h3 className="text-lg font-semibold">📈 Custom Analysis Charts ({analysisResults.custom_charts.filter(chart => chart && chart.plotly_data).length})</h3>
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
                  <TabsList className="grid w-full grid-cols-5 mb-4">
                    {models.map((model) => (
                      <TabsTrigger key={model.model_name} value={model.model_name}>
                        {model.model_name}
                      </TabsTrigger>
                    ))}
                  </TabsList>
                  
                  {models.map((model) => {
                    const modelDescriptions = {
                      "Linear Regression": "Simple model that assumes a linear relationship between features and target. Best for: Basic trends, interpretable results, linear patterns.",
                      "Random Forest": "Ensemble of decision trees that reduces overfitting. Best for: Complex patterns, handling non-linear relationships, robust predictions.",
                      "Decision Tree": "Tree-like model making decisions based on feature values. Best for: Interpretable results, categorical data, quick training.",
                      "XGBoost": "Advanced gradient boosting algorithm, highly accurate. Best for: Competition-level accuracy, complex datasets, handling missing values.",
                      "LSTM Neural Network": "Deep learning model that captures sequential patterns. Best for: Time-series data, long-term dependencies, complex sequences."
                    };
                    
                    return (
                    <TabsContent key={model.model_name} value={model.model_name}>
                      {/* Model Description */}
                      <div className="bg-blue-100 border-l-4 border-blue-600 p-3 mb-4 rounded">
                        <p className="text-sm text-blue-900">
                          <strong>{model.model_name}:</strong> {modelDescriptions[model.model_name] || "Advanced ML model for predictive analysis."}
                        </p>
                      </div>
                      
                      <div className="bg-gradient-to-br from-blue-50 to-indigo-50 rounded-lg p-6 border border-blue-200">
                        <div className="grid md:grid-cols-3 gap-4 mb-4">
                          <div className="bg-white rounded-lg p-4 shadow-sm">
                            <div className="flex items-center gap-1 text-sm text-gray-600 mb-1">
                              <span>R² Score</span>
                              <div className="group relative">
                                <Info className="w-3 h-3 text-gray-400 cursor-help" />
                                <div className="hidden group-hover:block absolute bottom-full left-0 mb-2 w-64 p-2 bg-gray-800 text-white text-xs rounded shadow-lg z-10">
                                  Measures how well the model explains the data. 1.0 = perfect, 0.0 = no better than guessing. Higher is better.
                                </div>
                              </div>
                            </div>
                            <div className="text-2xl font-bold text-blue-600">{model.r2_score.toFixed(3)}</div>
                          </div>
                          <div className="bg-white rounded-lg p-4 shadow-sm">
                            <div className="flex items-center gap-1 text-sm text-gray-600 mb-1">
                              <span>RMSE</span>
                              <div className="group relative">
                                <Info className="w-3 h-3 text-gray-400 cursor-help" />
                                <div className="hidden group-hover:block absolute bottom-full left-0 mb-2 w-64 p-2 bg-gray-800 text-white text-xs rounded shadow-lg z-10">
                                  Root Mean Square Error. Average prediction error in the same units as target. Lower is better.
                                </div>
                              </div>
                            </div>
                            <div className="text-2xl font-bold text-purple-600">{model.rmse.toFixed(3)}</div>
                          </div>
                          <div className="bg-white rounded-lg p-4 shadow-sm">
                            <div className="flex items-center gap-1 text-sm text-gray-600 mb-1">
                              <span>Confidence</span>
                              <div className="group relative">
                                <Info className="w-3 h-3 text-gray-400 cursor-help" />
                                <div className="hidden group-hover:block absolute bottom-full left-0 mb-2 w-64 p-2 bg-gray-800 text-white text-xs rounded shadow-lg z-10">
                                  Overall model reliability based on R² score. High (&gt;0.7), Medium (0.5-0.7), Low (&lt;0.5).
                                </div>
                              </div>
                            </div>
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
                    );
                  })}
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



      {/* Auto-Generated Charts Section */}
      {analysisResults.auto_charts && analysisResults.auto_charts.filter(chart => chart && chart.plotly_data).length > 0 && !collapsed.auto_charts && (
        <Card className="p-6">
          <div className="flex items-start justify-between mb-4">
            <div>
              <h3 className="text-lg font-semibold">📊 AI-Generated Analysis Charts</h3>
              <p className="text-sm text-gray-600 italic mt-1">Comprehensive visualization suite automatically generated based on your data</p>
            </div>
            <Button onClick={() => toggleSection('auto_charts')} variant="ghost" size="sm">
              <ChevronUp className="w-4 h-4" />
            </Button>
          </div>
          
          <div className="grid md:grid-cols-2 gap-6">
            {analysisResults.auto_charts
              .filter(chart => chart && chart.plotly_data)
              .map((chart, idx) => (
              <div key={idx} className="bg-white rounded-lg p-4 border border-gray-200 shadow-sm">
                <h4 className="font-semibold mb-2">{chart.title}</h4>
                {chart.description && (
                  <p className="text-sm text-gray-600 italic mb-3">{chart.description}</p>
                )}
                <div id={`auto-chart-${idx}`} style={{ width: '100%', height: '400px' }}></div>
              </div>
            ))}
          </div>
        </Card>
      )}

      {analysisResults.auto_charts && analysisResults.auto_charts.filter(chart => chart && chart.plotly_data).length > 0 && collapsed.auto_charts && (
        <Card className="p-4 cursor-pointer hover:bg-gray-50" onClick={() => toggleSection('auto_charts')}>
          <div className="flex items-center justify-between">
            <h3 className="text-lg font-semibold">📊 AI-Generated Analysis Charts ({analysisResults.auto_charts.filter(chart => chart && chart.plotly_data).length} charts)</h3>
            <ChevronDown className="w-5 h-5" />
          </div>
        </Card>
      )}

      {/* Chat Panel */}
      {showChat && !chatMinimized && (
        <div 
          className="fixed w-96 h-[calc(100vh-120px)] max-h-[600px] bg-white rounded-xl shadow-2xl border border-gray-200 flex flex-col z-50"
          style={{
            left: chatPosition.x !== null ? `${chatPosition.x}px` : 'auto',
            top: chatPosition.y !== null ? `${chatPosition.y}px` : '96px',
            right: chatPosition.x !== null ? 'auto' : '24px',
            cursor: isDragging ? 'grabbing' : 'default'
          }}
          onMouseDown={handleChatMouseDown}
        >
          <div className="chat-header p-4 border-b flex items-center justify-between bg-gradient-to-r from-blue-600 to-indigo-600 text-white rounded-t-xl cursor-grab active:cursor-grabbing">
            <h3 className="font-semibold">Analysis Assistant</h3>
            <div className="flex gap-2">
              {chatMessages.length > 0 && (
                <Button
                  onClick={() => {
                    if (confirm('Clear all chat messages?')) {
                      setChatMessages([]);
                      toast.success('Chat cleared');
                    }
                  }}
                  variant="ghost"
                  size="sm"
                  className="text-white hover:bg-white/20 text-xs"
                  title="Clear Chat"
                >
                  Clear
                </Button>
              )}
              <Button
                onClick={() => {
                  if (chatMessages.length > 0 && confirm('Start a new chat? Current messages will be cleared.')) {
                    setChatMessages([]);
                    toast.info('New chat started');
                  } else if (chatMessages.length === 0) {
                    toast.info('Already in a new chat');
                  }
                }}
                variant="ghost"
                size="sm"
                className="text-white hover:bg-white/20 text-xs"
                title="New Chat"
              >
                New
              </Button>
              <Button
                onClick={() => setChatMinimized(true)}
                variant="ghost"
                size="sm"
                className="text-white hover:bg-white/20"
                data-testid="minimize-chat-btn"
                title="Minimize"
              >
                <ChevronDown className="w-4 h-4" />
              </Button>
              <Button
                onClick={() => {
                  if (chatMessages.length > 0 && confirm('End chat and close? Messages will be saved with workspace.')) {
                    setShowChat(false);
                  } else {
                    setShowChat(false);
                  }
                }}
                variant="ghost"
                size="sm"
                className="text-white hover:bg-white/20"
                data-testid="close-chat-btn"
                title="End Chat"
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