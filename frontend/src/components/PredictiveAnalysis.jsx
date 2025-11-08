import { useState, useEffect, useRef } from "react";
import axios from "axios";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { toast } from "sonner";
import { Loader2, TrendingUp, AlertCircle, ChevronDown, ChevronUp, MessageSquare, X, Send, RefreshCw, Info, Download, FileText } from "lucide-react";
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from "@/components/ui/collapsible";
import { Input } from "@/components/ui/input";
import jsPDF from 'jspdf';
import html2canvas from 'html2canvas';
import ModelSelector from '@/components/ModelSelector';

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

const PredictiveAnalysis = ({ dataset, analysisCache, onAnalysisUpdate, variableSelection }) => {
  // Load analysis results from localStorage on mount (for page refresh persistence)
  // PRODUCTION FIX: Only use parent cache, no localStorage (supports unlimited data size)
  const getInitialAnalysisResults = () => {
    // Only restore from parent-provided cache (DashboardPage state management)
    // This cache is stored in:
    // 1. Backend database (unlimited size via workspace save)
    // 2. Parent component state (current session only)
    if (analysisCache) {
      console.log('✅ Restored analysis results from parent cache');
      return analysisCache;
    }
    
    // No localStorage fallback - localStorage cannot handle 2GB datasets
    // All persistence happens through backend workspace save/load
    return null;
  };
  
  const [loading, setLoading] = useState(false);
  const [analysisResults, setAnalysisResults] = useState(getInitialAnalysisResults());
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
  const [selectionFeedback, setSelectionFeedback] = useState(null); // User selection validation feedback
  const [selectedModels, setSelectedModels] = useState(null); // NEW: Selected ML models
  const [showModelSelector, setShowModelSelector] = useState(false); // NEW: Show model selector
  const [restoredFromCache, setRestoredFromCache] = useState(false); // Track if results restored from localStorage
  const chatEndRef = useRef(null);
  const progressIntervalRef = useRef(null);
  const hasRunAnalysisRef = useRef(false);  // Track if analysis has been triggered
  const previousResultsRef = useRef(null);  // CRITICAL: Persist previous results across state updates
  
  // PRODUCTION FIX: No localStorage for large datasets (2GB+ support)
  // Save analysis results to ref only (in-memory) - localStorage cannot handle large data
  useEffect(() => {
    if (analysisResults && dataset?.id) {
      // CRITICAL: Save to ref for merge operations (always succeeds, no size limit)
      previousResultsRef.current = analysisResults;
      console.log('✅ Analysis results saved to memory (ref)');
      
      // DO NOT USE LOCALSTORAGE - it has 5-10MB limit and will fail with large datasets
      // All persistence is handled through:
      // 1. Backend workspace save (unlimited size via Oracle/MongoDB)
      // 2. Parent component cache (passed via props)
      // 3. In-memory ref (this component only)
    }
  }, [analysisResults, dataset?.id]);
  
  // Debug: Log the variableSelection prop value whenever it changes
  useEffect(() => {
    console.log('PredictiveAnalysis received variableSelection prop:', variableSelection);
  }, [variableSelection]);

  // Use cached data if available, re-run when variableSelection changes
  useEffect(() => {
    console.log('useEffect triggered - analysisCache:', !!analysisCache, 'hasRunAnalysisRef:', hasRunAnalysisRef.current, 'loading:', loading, 'variableSelection:', variableSelection);
    
    // Helper to check if variableSelection has actual data (not just mode)
    const hasValidSelection = (selection) => {
      if (!selection) return false;
      if (selection.mode === 'skip') return true; // Skip is valid
      // Check for single target format
      if (selection.target_variable && selection.selected_features) return true;
      // Check for multi-target format
      if (selection.target_variables && Array.isArray(selection.target_variables) && selection.target_variables.length > 0) return true;
      return false;
    };
    
    // CRITICAL FIX: Always restore from cache if available
    if (analysisCache) {
      console.log('Restoring from cache - analysisCache has data');
      setAnalysisResults(analysisCache);
      hasRunAnalysisRef.current = true;
      return; // Don't re-run analysis if we have cache
    }
    
    // Only run analysis if no cache exists
    if (dataset && !hasRunAnalysisRef.current && !loading) {
      // Check if we have valid variable selection or should wait
      if (!hasValidSelection(variableSelection) && variableSelection && variableSelection.mode) {
        // We have partial selection (mode only) - wait for full data
        console.log('Waiting for complete variableSelection data...');
        return;
      }
      
      console.log('Running initial analysis with variableSelection:', variableSelection);
      hasRunAnalysisRef.current = true;
      runHolisticAnalysis();
    }
  }, [dataset?.id, analysisCache]); // FIXED: Only depend on dataset ID and cache, not full dataset object

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
            
            // Force layout to respect container
            const enhancedLayout = {
              ...plotlyData.layout,
              autosize: true,
              width: null,
              height: null,
              margin: { l: 50, r: 30, t: 50, b: 50 },
              modebar: { orientation: 'v' }
            };
            
            Plotly.newPlot(`custom-chart-${idx}`, plotlyData.data, enhancedLayout, {
              responsive: true,
              displayModeBar: true,
              displaylogo: false,
              modeBarButtonsToRemove: ['lasso2d', 'select2d', 'pan2d', 'zoom2d']
            }).then(() => {
              const container = document.getElementById(`custom-chart-${idx}`);
              if (container) {
                Plotly.Plots.resize(container);
              }
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
            
            // Force layout to respect container
            const enhancedLayout = {
              ...plotlyData.layout,
              autosize: true,
              width: null,  // Let Plotly calculate based on container
              height: null, // Let Plotly calculate based on container
              margin: { l: 50, r: 30, t: 50, b: 50 },
              modebar: { orientation: 'v' }
            };
            
            Plotly.newPlot(`auto-chart-${idx}`, plotlyData.data, enhancedLayout, {
              responsive: true,
              displayModeBar: true,
              displaylogo: false,
              modeBarButtonsToRemove: ['lasso2d', 'select2d', 'pan2d', 'zoom2d']
            }).then(() => {
              // Force resize to container
              const container = document.getElementById(`auto-chart-${idx}`);
              if (container) {
                Plotly.Plots.resize(container);
              }
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
    // CRITICAL: Preserve existing results from BOTH state AND ref (for reliability)
    const previousResults = analysisResults || previousResultsRef.current || null;
    console.log('🔄 Starting analysis - Previous models:', previousResults?.ml_models?.length || 0, 
                'Source:', analysisResults ? 'state' : previousResultsRef.current ? 'ref' : 'none');
    
    // Prevent multiple simultaneous runs
    if (loading) {
      console.log('Analysis already in progress, skipping duplicate run');
      return;
    }
    
    setLoading(true);
    setProgress(0);
    setSelectionFeedback(null); // Reset feedback
    const startTime = Date.now();
    
    // Show different toast based on variable selection
    if (variableSelection && variableSelection.mode !== 'skip') {
      // Handle both single and multi-target formats
      if (variableSelection.target_variables && Array.isArray(variableSelection.target_variables)) {
        // Multi-target format
        toast.info(`Running analysis with ${variableSelection.target_variables.length} target(s)...`);
      } else if (variableSelection.target_variable) {
        // Single target format
        const featureCount = variableSelection.selected_features?.length || 0;
        toast.info(`Running analysis: Target=${variableSelection.target_variable}, Features=${featureCount}...`);
      } else {
        toast.info("Running comprehensive AI/ML analysis...");
      }
    } else {
      toast.info("Running comprehensive AI/ML analysis...");
    }
    
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
      // Prepare request payload with variable selection
      const payload = {
        dataset_id: dataset.id
      };
      
      // Add workspace_name from localStorage for linking training to workspace
      const currentWorkspaceName = localStorage.getItem('current_workspace_name') || 'default';
      payload.workspace_name = currentWorkspaceName;
      console.log('Training with workspace:', currentWorkspaceName);
      
      // Add variable selection and problem_type if provided
      if (variableSelection && variableSelection.mode !== 'skip') {
        payload.user_selection = {
          target_variable: variableSelection.target,
          selected_features: variableSelection.features,
          mode: variableSelection.mode,
          ai_suggestions: variableSelection.aiSuggestions
        };
        
        // Add problem_type if specified
        if (variableSelection.problem_type) {
          payload.problem_type = variableSelection.problem_type;
        }
        
        // Add time_column if specified (for time series)
        if (variableSelection.time_column) {
          payload.time_column = variableSelection.time_column;
        }
        
        console.log('Sending user_selection to backend:', JSON.stringify(payload.user_selection, null, 2));
        console.log('Problem type:', payload.problem_type);
      }
      
      // NEW: Add selected models if any
      if (selectedModels && selectedModels.length > 0) {
        payload.selected_models = selectedModels;
        console.log('Using selected models:', selectedModels);
      }
      
      const response = await axios.post(`${API}/analysis/holistic`, payload);

      const endTime = Date.now();
      const timeTaken = ((endTime - startTime) / 1000).toFixed(1); // in seconds
      setAnalysisTime(timeTaken);

      // Complete progress
      setProgress(100);
      
      // Check if backend returned selection feedback
      if (response.data.selection_feedback) {
        setSelectionFeedback(response.data.selection_feedback);
      }
      
      // CRITICAL FIX #8: Merge new models with existing models instead of replacing
      const updatedResults = { ...response.data };
      
      console.log('🔍 Model merging check:', {
        selectedModels: selectedModels,
        hasPreviousResults: !!previousResults,
        previousModelsCount: previousResults?.ml_models?.length || 0,
        newModelsCount: response.data?.ml_models?.length || 0,
        analysisResultsCount: analysisResults?.ml_models?.length || 0,
        refCount: previousResultsRef.current?.ml_models?.length || 0
      });
      
      // Merge if we have previous results to preserve (from selected model training)
      if (selectedModels && previousResults && previousResults.ml_models && previousResults.ml_models.length > 0) {
        const existingModels = previousResults.ml_models || [];
        const newModels = response.data.ml_models || [];
        
        console.log('🔀 Merging models:', {
          existingModelNames: existingModels.map(m => m.model_name),
          newModelNames: newModels.map(m => m.model_name)
        });
        
        // Create a map of existing models by model_name to avoid duplicates
        const modelMap = new Map();
        existingModels.forEach(model => {
          modelMap.set(model.model_name, model);
        });
        
        // Add or update with new models
        newModels.forEach(model => {
          modelMap.set(model.model_name, model);
        });
        
        // Convert back to array and sort by performance
        updatedResults.ml_models = Array.from(modelMap.values()).sort((a, b) => {
          const metricA = a.r2_score || a.accuracy || 0;
          const metricB = b.r2_score || b.accuracy || 0;
          return metricB - metricA;
        });
        
        console.log(`✅ Merged models: ${existingModels.length} existing + ${newModels.length} new = ${updatedResults.ml_models.length} total`);
        console.log('✅ Final merged model names:', updatedResults.ml_models.map(m => m.model_name));
      } else {
        console.log('No existing models to merge, using new results only');
      }
      
      // CRITICAL: Update both state AND ref immediately for next merge
      setAnalysisResults(updatedResults);
      previousResultsRef.current = updatedResults;
      console.log('✅ Updated state and ref with merged results');
      
      // CRITICAL: Always notify parent to cache results immediately
      if (onAnalysisUpdate) {
        console.log('Caching analysis results to parent');
        onAnalysisUpdate(updatedResults);
      } else {
        console.warn('onAnalysisUpdate callback not provided - results will not be cached!');
      }
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

  const refreshAnalysis = async () => {
    console.log('Refresh button clicked - resetting analysis');
    
    // Clear localStorage cache for this dataset
    if (dataset?.id) {
      try {
        localStorage.removeItem(`analysis_${dataset.id}`);
        console.log('🗑️ Cleared localStorage cache');
      } catch (e) {
        console.warn('Failed to clear localStorage:', e);
      }
    }
    
    setAnalysisResults(null);
    onAnalysisUpdate(null);
    // Reset the ref to allow fresh run
    hasRunAnalysisRef.current = false;
    await runHolisticAnalysis();
    // Mark as run after completion
    hasRunAnalysisRef.current = true;
  };

  const toggleSection = (section) => {
    setCollapsed(prev => ({ ...prev, [section]: !prev[section] }));
  };

  const expandAll = () => {
    setCollapsed({});
  };

  const collapseAll = () => {
    const allSections = ['summary', 'volume', 'ai_insights', 'explainability', 'recommendations', 'correlations', 'custom_charts', 'ml_models', 'auto_charts'];
    const newCollapsed = {};
    allSections.forEach(s => newCollapsed[s] = true);
    setCollapsed(newCollapsed);
  };

  const downloadPDF = async () => {
    try {
      toast.info("Opening print dialog... You can save as PDF from there.");
      
      // Use browser's native print which is much more stable
      setTimeout(() => {
        window.print();
      }, 500);
      
    } catch (error) {
      console.error("Print Error:", error);
      toast.error("Failed to open print dialog");
    }
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
        has_correlations: !!(analysisResults.correlations && analysisResults.correlations.correlations),
        has_ml_models: !!analysisResults.ml_models,
        has_custom_charts: !!analysisResults.custom_charts,
        custom_charts_count: analysisResults.custom_charts?.length || 0,
        volume_analysis: analysisResults.volume_analysis,
        predictions: analysisResults.predictions
      } : null;

      // Use enhanced chat endpoint for comprehensive features
      const response = await axios.post(`${API}/enhanced-chat/message`, {
        dataset_id: dataset.id,
        message: userMsg,
        conversation_history: chatMessages.slice(-5).map(m => ({ role: m.role, content: m.content })),
        // Note: enhanced endpoint loads analysis_results internally if available
      });

      // Handle enhanced chat response
      const assistantMsg = { 
        role: "assistant", 
        content: response.data.response 
      };
      
      // Check if action requires confirmation
      if (response.data.action === 'chart' && response.data.requires_confirmation) {
        // Chart creation with confirmation
        assistantMsg.pendingAction = true;
        assistantMsg.actionData = response.data;
        setPendingAction(response.data);
      } else if (response.data.action === 'chart') {
        // Direct chart addition (no confirmation needed)
        // This would be handled in visualization panel
        assistantMsg.content = response.data.response;
      }
      
      setChatMessages(prev => [...prev, assistantMsg]);
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
            correlations: {
              correlations: actionData.chart_data.correlations || [],
              matrix: actionData.chart_data.matrix || null
            },
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
            onClick={downloadPDF}
            disabled={loading}
            variant="outline"
            className="bg-blue-50 hover:bg-blue-100 border-blue-200"
          >
            <Download className="w-4 h-4 mr-2" />
            Print/Save PDF
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

      {/* Model Selector - ALWAYS VISIBLE */}
      <div className="mb-6 border-2 border-blue-300 rounded-lg p-4 bg-blue-50">
        <h3 className="text-lg font-semibold mb-3 flex items-center gap-2">
          <TrendingUp className="w-5 h-5 text-blue-600" />
          Select ML Models (35+ Available)
        </h3>
        
        {showModelSelector ? (
          <ModelSelector
            problemType={
              // Use variableSelection if available, otherwise fall back to analysisResults
              variableSelection?.problemType || 
              (analysisResults?.problem_type === 'auto' 
                ? 'classification' 
                : (analysisResults?.problem_type || 'classification'))
            }
            dataSummary={{
              row_count: dataset?.row_count || 0,
              feature_count: Object.keys(dataset?.data_preview?.[0] || {}).length,
              missing_percentage: 0
            }}
            onModelSelection={(models) => {
              setSelectedModels(models);
              setShowModelSelector(false);
              if (models) {
                toast.success(models.length > 0 ? `${models.length} models selected` : 'All models selected');
              }
            }}
            className="mb-2"
          />
        ) : (
          <div>
            <p className="text-sm text-gray-600 mb-3">
              Choose from 35+ ML models across 5 categories: Classification (11), Regression (13), Clustering (5), Dimensionality (3), Anomaly (3)
            </p>
            <Button
              onClick={() => setShowModelSelector(true)}
              variant="default"
              size="lg"
              className="w-full bg-blue-600 hover:bg-blue-700"
              disabled={loading}
            >
              {selectedModels && selectedModels.length > 0 
                ? `✅ ${selectedModels.length} Models Selected - Click to Change`
                : '🚀 Select ML Models (Default: Auto-Select All)'}
            </Button>
            {selectedModels && selectedModels.length > 0 && (
              <>
                <p className="text-xs text-blue-600 mt-2 font-medium">
                  Selected: {selectedModels.join(', ')}
                </p>
                <Button
                  onClick={() => {
                    console.log('🔄 Running analysis with selected models');
                    runHolisticAnalysis();
                  }}
                  variant="outline"
                  className="w-full mt-3 border-green-500 text-green-600 hover:bg-green-50"
                  disabled={loading}
                >
                  <RefreshCw className="w-4 h-4 mr-2" />
                  {loading ? 'Training...' : '🔄 Train Selected Models & Merge with Existing'}
                </Button>
              </>
            )}
          </div>
        )}
      </div>

      {/* Cache Restoration Indicator */}
      {restoredFromCache && analysisResults && (
        <div className="mb-4 p-4 bg-blue-50 border border-blue-200 rounded-lg flex items-center gap-3">
          <div className="flex-shrink-0">
            <svg className="w-5 h-5 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
          <div className="flex-1">
            <p className="text-sm font-medium text-blue-900">
              Analysis Results Restored
            </p>
            <p className="text-xs text-blue-700 mt-1">
              Your previous analysis results have been restored after page refresh. Click "Refresh" to run a new analysis.
            </p>
          </div>
          <button 
            onClick={() => setRestoredFromCache(false)}
            className="text-blue-400 hover:text-blue-600"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
      )}

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
        <Card id="training-metadata-section" className="p-4 bg-gradient-to-r from-green-50 to-teal-50 border-green-200">
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

      {/* Variable Selection Feedback */}
      {selectionFeedback && (
        <Card id="selection-feedback-section" className={`p-4 border-2 ${
          selectionFeedback.status === 'used' 
            ? 'bg-blue-50 border-blue-300' 
            : 'bg-amber-50 border-amber-300'
        }`}>
          <div className="flex items-start gap-3">
            <div className={`w-10 h-10 rounded-full flex items-center justify-center ${
              selectionFeedback.status === 'used' 
                ? 'bg-blue-100' 
                : 'bg-amber-100'
            }`}>
              <Info className={`w-5 h-5 ${
                selectionFeedback.status === 'used' 
                  ? 'text-blue-600' 
                  : 'text-amber-600'
              }`} />
            </div>
            <div className="flex-1">
              <h4 className="font-semibold text-gray-800 mb-1">
                {selectionFeedback.status === 'used' 
                  ? '✅ Your Variable Selection Used' 
                  : '⚠️ Variable Selection Modified'}
              </h4>
              <p className="text-sm text-gray-700 whitespace-pre-wrap">
                {selectionFeedback.message}
              </p>
              {selectionFeedback.used_target && (
                <div className="mt-2 text-xs bg-white p-2 rounded border">
                  <span className="font-semibold">Target:</span> {selectionFeedback.used_target}
                  {selectionFeedback.used_features && selectionFeedback.used_features.length > 0 && (
                    <>
                      <br />
                      <span className="font-semibold">Features ({selectionFeedback.used_features.length}):</span> {selectionFeedback.used_features.join(', ')}
                    </>
                  )}
                </div>
              )}
            </div>
          </div>
        </Card>
      )}

      {/* Rest of sections with collapse... */}
      {/* Volume Analysis */}
      {analysisResults.volume_analysis && analysisResults.volume_analysis.by_dimensions && analysisResults.volume_analysis.by_dimensions.length > 0 && !collapsed.volume && (
        <Card id="volume-analysis-section" className="p-6">
          <div className="flex items-start justify-between mb-4">
            <div>
              <h3 className="text-lg font-semibold">📊 Volume Analysis</h3>
              <p className="text-sm text-gray-600 italic mt-1">Comprehensive data distribution and pattern analysis</p>
              {analysisResults.volume_analysis.summary && (
                <div className="mt-2 flex gap-4 text-xs text-gray-600">
                  <span>📈 Total: {analysisResults.volume_analysis.total_records.toLocaleString()} rows</span>
                  <span>📋 Columns: {analysisResults.volume_analysis.summary.total_columns}</span>
                  <span>💾 Memory: {analysisResults.volume_analysis.summary.memory_usage_mb} MB</span>
                </div>
              )}
            </div>
            <Button onClick={() => toggleSection('volume')} variant="ghost" size="sm">
              <ChevronUp className="w-4 h-4" />
            </Button>
          </div>
          
          {/* Categorical Volume Analysis - Two-Column Grid Layout */}
          <div className="mb-6">
            <h4 className="font-semibold text-gray-800 mb-4">Categorical Distribution</h4>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {analysisResults.volume_analysis.by_dimensions.map((item, idx) => (
                <div key={idx} className="p-4 bg-gradient-to-r from-blue-50 to-indigo-50 rounded-lg border border-blue-200">
                  <div className="flex items-start justify-between mb-2">
                    <h5 className="font-semibold text-gray-900 truncate flex-1">{String(item.dimension)}</h5>
                    <span className="text-xs bg-blue-600 text-white px-2 py-1 rounded ml-2 whitespace-nowrap">
                      {item.total_unique} unique
                    </span>
                  </div>
                  <p className="text-sm text-gray-700 mb-3 line-clamp-2">{String(item.insights)}</p>
                  
                  {/* Top values breakdown */}
                  {item.breakdown && Object.keys(item.breakdown).length > 0 && (
                    <div className="space-y-2">
                      <p className="text-xs font-semibold text-gray-600 mb-2">Top Values:</p>
                      {Object.entries(item.breakdown).slice(0, 4).map(([key, value], i) => {
                        const percentage = ((value / analysisResults.volume_analysis.total_records) * 100).toFixed(1);
                        return (
                          <div key={i} className="flex items-center gap-2">
                            <span className="text-xs text-gray-700 w-24 truncate" title={key}>{key}</span>
                            <div className="flex-1 h-4 bg-gray-200 rounded-full overflow-hidden">
                              <div 
                                className="h-full bg-gradient-to-r from-blue-400 to-indigo-500"
                                style={{ width: `${percentage}%` }}
                              ></div>
                            </div>
                            <span className="text-xs text-gray-600 w-16 text-right">{percentage}%</span>
                          </div>
                        );
                      })}
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
          
          {/* Numeric Volume Analysis - Horizontal Cards Layout */}
          {analysisResults.volume_analysis.numeric_summary && analysisResults.volume_analysis.numeric_summary.length > 0 && (
            <div className="space-y-4">
              <h4 className="font-semibold text-gray-800">Numeric Distribution</h4>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {analysisResults.volume_analysis.numeric_summary.map((item, idx) => (
                  <div key={idx} className="p-4 bg-gradient-to-r from-green-50 to-teal-50 rounded-lg border border-green-200">
                    <h5 className="font-semibold text-gray-900 mb-2">{String(item.dimension)}</h5>
                    <p className="text-sm text-gray-700 mb-3">{String(item.insights)}</p>
                    <div className="grid grid-cols-3 gap-2 text-xs">
                      <div className="bg-white p-2 rounded border border-green-200">
                        <span className="text-gray-600">Min:</span>
                        <span className="font-semibold text-gray-900 ml-1">{item.min}</span>
                      </div>
                      <div className="bg-white p-2 rounded border border-green-200">
                        <span className="text-gray-600">Mean:</span>
                        <span className="font-semibold text-gray-900 ml-1">{item.mean}</span>
                      </div>
                      <div className="bg-white p-2 rounded border border-green-200">
                        <span className="text-gray-600">Max:</span>
                        <span className="font-semibold text-gray-900 ml-1">{item.max}</span>
                      </div>
                      <div className="bg-white p-2 rounded border border-green-200">
                        <span className="text-gray-600">Median:</span>
                        <span className="font-semibold text-gray-900 ml-1">{item.median}</span>
                      </div>
                      <div className="bg-white p-2 rounded border border-green-200">
                        <span className="text-gray-600">Std Dev:</span>
                        <span className="font-semibold text-gray-900 ml-1">{item.std}</span>
                      </div>
                      <div className="bg-white p-2 rounded border border-green-200">
                        <span className="text-gray-600">Range:</span>
                        <span className="font-semibold text-gray-900 ml-1">{item.range}</span>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
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

      {/* PHASE 3: AI-Powered Insights */}
      {analysisResults.ai_insights && analysisResults.ai_insights.length > 0 && !collapsed.ai_insights && (
        <Card id="ai-insights-section" className="p-6 bg-gradient-to-br from-purple-50 to-indigo-50 border-2 border-purple-200">
          <div className="flex items-start justify-between mb-4">
            <div>
              <h3 className="text-lg font-semibold flex items-center gap-2">
                🤖 AI-Powered Insights
              </h3>
              <p className="text-sm text-gray-600 italic mt-1">Intelligent analysis powered by AI</p>
            </div>
            <Button onClick={() => toggleSection('ai_insights')} variant="ghost" size="sm">
              <ChevronUp className="w-4 h-4" />
            </Button>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {analysisResults.ai_insights.map((insight, idx) => (
              <div key={idx} className={`p-4 rounded-lg border-2 ${
                insight.severity === 'critical' ? 'bg-red-50 border-red-300' :
                insight.severity === 'warning' ? 'bg-amber-50 border-amber-300' :
                'bg-blue-50 border-blue-300'
              }`}>
                <div className="flex items-start gap-3">
                  <div className={`w-10 h-10 rounded-full flex items-center justify-center flex-shrink-0 ${
                    insight.severity === 'critical' ? 'bg-red-100' :
                    insight.severity === 'warning' ? 'bg-amber-100' :
                    'bg-blue-100'
                  }`}>
                    <span className="text-xl">
                      {insight.type === 'anomaly' ? '⚠️' :
                       insight.type === 'trend' ? '📈' :
                       insight.type === 'correlation' ? '🔗' :
                       insight.type === 'business' ? '💼' : '📊'}
                    </span>
                  </div>
                  <div className="flex-1 min-w-0">
                    <h4 className="font-semibold text-gray-900 truncate" title={insight.title}>{insight.title}</h4>
                    <p className="text-sm text-gray-700 mt-1 line-clamp-3">{insight.description}</p>
                    {insight.recommendation && (
                      <div className="mt-2 p-2 bg-white rounded border border-gray-200">
                        <p className="text-xs text-gray-600 line-clamp-2">
                          <span className="font-semibold">💡 Tip:</span> {insight.recommendation}
                        </p>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </Card>
      )}

      {analysisResults.ai_insights && analysisResults.ai_insights.length > 0 && collapsed.ai_insights && (
        <Card className="p-4 cursor-pointer hover:bg-gray-50" onClick={() => toggleSection('ai_insights')}>
          <div className="flex items-center justify-between">
            <h3 className="text-lg font-semibold">🤖 AI-Powered Insights ({analysisResults.ai_insights.length} insights)</h3>
            <ChevronDown className="w-5 h-5" />
          </div>
        </Card>
      )}

      {/* PHASE 3: Model Explainability */}
      {analysisResults.explainability && analysisResults.explainability.available && !collapsed.explainability && (
        <Card id="explainability-section" className="p-6 bg-gradient-to-br from-green-50 to-teal-50 border-2 border-green-200">
          <div className="flex items-start justify-between mb-4">
            <div>
              <h3 className="text-lg font-semibold flex items-center gap-2">
                🔍 Model Explainability
              </h3>
              <p className="text-sm text-gray-600 italic mt-1">Understand how your model makes predictions</p>
            </div>
            <Button onClick={() => toggleSection('explainability')} variant="ghost" size="sm">
              <ChevronUp className="w-4 h-4" />
            </Button>
          </div>
          <div className="space-y-4">
            <div className="p-4 bg-white rounded-lg border border-green-200">
              <h4 className="font-semibold text-green-900 mb-2">
                Model: {analysisResults.explainability.model_name}
              </h4>
              <p className="text-sm text-gray-700 mb-3">
                Target: <span className="font-medium">{analysisResults.explainability.target_variable}</span>
              </p>
              <p className="text-sm text-gray-700">{analysisResults.explainability.explanation_text}</p>
              {analysisResults.explainability.note && (
                <p className="text-xs text-gray-500 mt-2 italic">{analysisResults.explainability.note}</p>
              )}
            </div>
            {analysisResults.explainability.feature_importance && 
             Object.keys(analysisResults.explainability.feature_importance).length > 0 && (
              <div className="p-4 bg-white rounded-lg border border-green-200">
                <h4 className="font-semibold text-green-900 mb-3">Feature Importance Scores</h4>
                <div className="space-y-2">
                  {Object.entries(analysisResults.explainability.feature_importance)
                    .slice(0, 5)
                    .map(([feature, importance], idx) => (
                      <div key={idx} className="flex items-center gap-2">
                        <span className="text-sm text-gray-700 w-32 truncate" title={feature}>{feature}</span>
                        <div className="flex-1 h-6 bg-gray-200 rounded-full overflow-hidden">
                          <div 
                            className="h-full bg-gradient-to-r from-green-400 to-green-600"
                            style={{ width: `${importance * 100}%` }}
                          ></div>
                        </div>
                        <span className="text-xs text-gray-600 w-12 text-right">{(importance * 100).toFixed(1)}%</span>
                      </div>
                    ))}
                </div>
              </div>
            )}
          </div>
        </Card>
      )}

      {analysisResults.explainability && analysisResults.explainability.available && collapsed.explainability && (
        <Card className="p-4 cursor-pointer hover:bg-gray-50" onClick={() => toggleSection('explainability')}>
          <div className="flex items-center justify-between">
            <h3 className="text-lg font-semibold">🔍 Model Explainability</h3>
            <ChevronDown className="w-5 h-5" />
          </div>
        </Card>
      )}

      {/* PHASE 3: Business Recommendations */}
      {analysisResults.business_recommendations && analysisResults.business_recommendations.length > 0 && !collapsed.recommendations && (
        <Card id="recommendations-section" className="p-6 bg-gradient-to-br from-orange-50 to-yellow-50 border-2 border-orange-200">
          <div className="flex items-start justify-between mb-4">
            <div>
              <h3 className="text-lg font-semibold flex items-center gap-2">
                💼 Business Recommendations
              </h3>
              <p className="text-sm text-gray-600 italic mt-1">AI-generated strategic recommendations</p>
              <p className="text-xs text-orange-700 mt-2 bg-white px-3 py-2 rounded border border-orange-200">
                💡 <strong>How to use:</strong> These are strategic recommendations for your team to implement. 
                Review each recommendation, assess the effort vs. impact, and work with your technical team to apply the suggested improvements.
              </p>
            </div>
            <Button onClick={() => toggleSection('recommendations')} variant="ghost" size="sm">
              <ChevronUp className="w-4 h-4" />
            </Button>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {analysisResults.business_recommendations.map((rec, idx) => (
              <div key={idx} className={`p-4 rounded-lg border-2 ${
                rec.priority === 'high' ? 'bg-red-50 border-red-300' :
                rec.priority === 'medium' ? 'bg-yellow-50 border-yellow-300' :
                'bg-green-50 border-green-300'
              }`}>
                <div className="flex items-start gap-3 mb-3">
                  <div className={`px-2 py-1 rounded text-xs font-semibold ${
                    rec.priority === 'high' ? 'bg-red-600 text-white' :
                    rec.priority === 'medium' ? 'bg-yellow-600 text-white' :
                    'bg-green-600 text-white'
                  }`}>
                    {rec.priority?.toUpperCase()}
                  </div>
                  <h4 className="font-semibold text-gray-900 flex-1">{rec.title}</h4>
                </div>
                <p className="text-sm text-gray-700 mb-2">{rec.description}</p>
                {rec.expected_impact && (
                  <div className="flex items-start gap-2 text-xs mb-1">
                    <span className="font-semibold text-gray-600">📊 Impact:</span>
                    <span className="text-gray-700">{rec.expected_impact}</span>
                  </div>
                )}
                {rec.implementation_effort && (
                  <div className="flex items-center gap-2 text-xs">
                    <span className="font-semibold text-gray-600">⚙️ Effort:</span>
                    <span className={`px-2 py-0.5 rounded ${
                      rec.implementation_effort === 'high' ? 'bg-red-100 text-red-700' :
                      rec.implementation_effort === 'medium' ? 'bg-yellow-100 text-yellow-700' :
                      'bg-green-100 text-green-700'
                    }`}>
                      {rec.implementation_effort}
                    </span>
                  </div>
                )}
              </div>
            ))}
          </div>
        </Card>
      )}

      {analysisResults.business_recommendations && analysisResults.business_recommendations.length > 0 && collapsed.recommendations && (
        <Card className="p-4 cursor-pointer hover:bg-gray-50" onClick={() => toggleSection('recommendations')}>
          <div className="flex items-center justify-between">
            <h3 className="text-lg font-semibold">💼 Business Recommendations ({analysisResults.business_recommendations.length} recommendations)</h3>
            <ChevronDown className="w-5 h-5" />
          </div>
        </Card>
      )}

      {/* Correlations */}
      {analysisResults.correlations && 
       analysisResults.correlations.correlations && 
       analysisResults.correlations.correlations.length > 0 && 
       !collapsed.correlations && (
        <Card id="correlations-section" className="p-6">
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
            {analysisResults.correlations.correlations.map((corr, idx) => (
              <div key={idx} className="flex items-center gap-3 p-3 bg-purple-50 rounded-lg border border-purple-200">
                <div className="flex-1">
                  <p className="font-medium">{String(corr.feature1)} ↔ {String(corr.feature2)}</p>
                  <p className="text-sm text-gray-600">{String(corr.interpretation || corr.direction)}</p>
                </div>
                <div className="text-right">
                  <div className="text-2xl font-bold text-purple-600">{Number(corr.value || corr.correlation).toFixed(2)}</div>
                  <div className="text-xs text-gray-500">{String(corr.strength)}</div>
                </div>
              </div>
            ))}
          </div>
        </Card>
      )}

      {analysisResults.correlations && 
       analysisResults.correlations.correlations && 
       analysisResults.correlations.correlations.length > 0 && 
       collapsed.correlations && (
        <Card className="p-4 cursor-pointer hover:bg-gray-50" onClick={() => toggleSection('correlations')}>
          <div className="flex items-center justify-between">
            <h3 className="text-lg font-semibold">🔗 Key Correlations ({analysisResults.correlations.correlations.length} found)</h3>
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
                <h4 className="font-semibold mb-2 text-sm">{chart.title}</h4>
                {chart.description && (
                  <p className="text-xs text-gray-600 italic mb-3 line-clamp-2">{chart.description}</p>
                )}
                <div 
                  id={`custom-chart-${idx}`} 
                  className="w-full"
                  style={{ 
                    height: '450px',
                    maxWidth: '100%',
                    overflow: 'hidden'
                  }}
                ></div>
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
      {analysisResults.ml_models && analysisResults.ml_models.length > 0 && (
        <Card id="ml-models-section" className="p-6">
          <div className="flex items-start justify-between mb-4">
            <div>
              <h3 className="text-lg font-semibold">🤖 ML Model Comparison</h3>
              <p className="text-sm text-gray-600 italic mt-1">
                Compare performance of different machine learning models 
                {analysisResults.problem_type && (
                  <span className="ml-2 px-2 py-1 bg-blue-100 text-blue-800 rounded text-xs font-semibold">
                    {analysisResults.problem_type === 'classification' ? 'Classification' : 'Regression'}
                  </span>
                )}
              </p>
            </div>
            <Button onClick={() => toggleSection('ml_models')} variant="ghost" size="sm">
              <ChevronUp className="w-4 h-4" />
            </Button>
          </div>
          
          {/* DEBUG INFO - Remove after testing */}
          {console.log('ML Models Debug:', {
            problem_type: analysisResults.problem_type,
            ml_models_count: analysisResults.ml_models?.length,
            unique_targets: [...new Set(analysisResults.ml_models.map(m => m.target_column))],
            first_model: analysisResults.ml_models[0]
          })}
          
          {/* Model Comparison Table - Show when multiple targets exist */}
          {(() => {
            const uniqueTargets = [...new Set(analysisResults.ml_models.map(m => m.target_column))];
            
            if (uniqueTargets.length > 1) {
              return (
                <div className="mb-6 p-4 bg-gradient-to-br from-green-50 to-emerald-50 rounded-lg border border-green-200">
                  <h4 className="font-semibold text-green-900 mb-3 flex items-center gap-2">
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                    </svg>
                    All Models Comparison ({uniqueTargets.length} Target Variables)
                  </h4>
                  <p className="text-sm text-green-700 mb-4">
                    Found {analysisResults.correlations?.correlations?.length || 0} key correlations. Compare all trained models below:
                  </p>
                  
                  <div className="overflow-x-auto bg-white rounded-lg border border-green-300">
                    <table className="w-full text-sm">
                      <thead className="bg-green-100">
                        <tr>
                          <th className="text-left p-3 font-semibold text-green-900">Rank</th>
                          <th className="text-left p-3 font-semibold text-green-900">Model</th>
                          <th className="text-left p-3 font-semibold text-green-900">Target Variable</th>
                          {analysisResults.problem_type === 'classification' ? (
                            <>
                              <th className="text-right p-3 font-semibold text-green-900">Accuracy</th>
                              <th className="text-right p-3 font-semibold text-green-900">F1-Score</th>
                              <th className="text-right p-3 font-semibold text-green-900">Precision</th>
                            </>
                          ) : (
                            <>
                              <th className="text-right p-3 font-semibold text-green-900">R² Score</th>
                              <th className="text-right p-3 font-semibold text-green-900">RMSE</th>
                            </>
                          )}
                          <th className="text-center p-3 font-semibold text-green-900">Confidence</th>
                          <th className="text-right p-3 font-semibold text-green-900">Train Samples</th>
                        </tr>
                      </thead>
                      <tbody>
                        {[...analysisResults.ml_models]
                          .sort((a, b) => {
                            if (analysisResults.problem_type === 'classification') {
                              return (b.accuracy || 0) - (a.accuracy || 0);
                            } else {
                              return (b.r2_score || 0) - (a.r2_score || 0);
                            }
                          })
                          .map((model, idx) => (
                            <tr key={idx} className={`border-t ${idx === 0 ? 'bg-yellow-50' : 'hover:bg-gray-50'}`}>
                              <td className="p-3">
                                {idx === 0 ? (
                                  <span className="inline-flex items-center gap-1 px-2 py-1 bg-yellow-400 text-yellow-900 rounded-full text-xs font-bold">
                                    🏆 #{idx + 1}
                                  </span>
                                ) : (
                                  <span className="text-gray-600 font-semibold">#{idx + 1}</span>
                                )}
                              </td>
                              <td className="p-3 font-medium text-gray-900">{model.model_name}</td>
                              <td className="p-3 text-gray-700">
                                <span className="px-2 py-1 bg-blue-100 text-blue-800 rounded text-xs font-medium">
                                  {model.target_column}
                                </span>
                              </td>
                              {analysisResults.problem_type === 'classification' ? (
                                <>
                                  <td className="p-3 text-right">
                                    <span className={`font-bold ${
                                      (model.accuracy || 0) >= 0.85 ? 'text-green-600' : 
                                      (model.accuracy || 0) >= 0.70 ? 'text-yellow-600' : 'text-red-600'
                                    }`}>
                                      {((model.accuracy || 0) * 100).toFixed(1)}%
                                    </span>
                                  </td>
                                  <td className="p-3 text-right text-gray-700">{((model.f1_score || 0) * 100).toFixed(1)}%</td>
                                  <td className="p-3 text-right text-gray-700">{((model.precision || 0) * 100).toFixed(1)}%</td>
                                </>
                              ) : (
                                <>
                                  <td className="p-3 text-right">
                                    <span className={`font-bold ${
                                      (model.r2_score || 0) >= 0.7 ? 'text-green-600' : 
                                      (model.r2_score || 0) >= 0.5 ? 'text-yellow-600' : 'text-red-600'
                                    }`}>
                                      {(model.r2_score || 0).toFixed(3)}
                                    </span>
                                  </td>
                                  <td className="p-3 text-right text-gray-700">{(model.rmse || 0).toFixed(3)}</td>
                                </>
                              )}
                              <td className="p-3 text-center">
                                <span className={`px-2 py-1 rounded-full text-xs font-semibold ${
                                  model.confidence === 'High' ? 'bg-green-100 text-green-800' : 
                                  model.confidence === 'Medium' ? 'bg-yellow-100 text-yellow-800' : 
                                  model.confidence === 'Low' ? 'bg-red-100 text-red-800' : 'bg-gray-100 text-gray-600'
                                }`}>
                                  {model.confidence || 'N/A'}
                                </span>
                              </td>
                              <td className="p-3 text-right text-gray-600">{model.n_train_samples}</td>
                            </tr>
                          ))}
                      </tbody>
                    </table>
                  </div>
                  
                  <div className="mt-3 text-xs text-green-700">
                    {analysisResults.problem_type === 'classification' ? (
                      <>💡 <strong>Tip:</strong> The model with the highest accuracy (closest to 100%) and F1-score typically performs best for classification. 
                      Top-ranked model is highlighted with 🏆.</>
                    ) : (
                      <>💡 <strong>Tip:</strong> The model with the highest R² score (closest to 1.0) and lowest RMSE typically performs best. 
                      Top-ranked model is highlighted with 🏆.</>
                    )}
                  </div>
                </div>
              );
            }
            return null;
          })()}
          
          {/* Single Target Comparison Table - Show for all single target scenarios */}
          {(() => {
            const uniqueTargets = [...new Set(analysisResults.ml_models.map(m => m.target_column))];
            
            if (uniqueTargets.length === 1) {
              // Single target - show simple comparison table
              const sortedModels = [...analysisResults.ml_models].sort((a, b) => {
                if (analysisResults.problem_type === 'classification') {
                  return (b.accuracy || 0) - (a.accuracy || 0);
                } else {
                  return (b.r2_score || 0) - (a.r2_score || 0);
                }
              });
              
              return (
                <div className="mb-6 p-4 bg-gradient-to-br from-blue-50 to-indigo-50 rounded-lg border border-blue-200">
                  <h4 className="font-semibold text-blue-900 mb-3 flex items-center gap-2">
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                    </svg>
                    Model Performance Comparison ({sortedModels.length} Models Trained)
                  </h4>
                  <p className="text-sm text-blue-700 mb-4">
                    Comparing {analysisResults.problem_type === 'classification' ? 'Classification' : 'Regression'} models for target: <strong>{uniqueTargets[0]}</strong>
                  </p>
                  
                  <div className="overflow-x-auto bg-white rounded-lg border border-blue-300">
                    <table className="w-full text-sm">
                      <thead className="bg-blue-100">
                        <tr>
                          <th className="p-3 text-left font-semibold">Rank</th>
                          <th className="p-3 text-left font-semibold">Model</th>
                          {analysisResults.problem_type === 'classification' ? (
                            <>
                              <th className="p-3 text-right font-semibold">Accuracy</th>
                              <th className="p-3 text-right font-semibold">Precision</th>
                              <th className="p-3 text-right font-semibold">Recall</th>
                              <th className="p-3 text-right font-semibold">F1-Score</th>
                            </>
                          ) : (
                            <>
                              <th className="p-3 text-right font-semibold">R² Score</th>
                              <th className="p-3 text-right font-semibold">RMSE</th>
                              <th className="p-3 text-right font-semibold">MAE</th>
                            </>
                          )}
                          <th className="p-3 text-right font-semibold">Training Time</th>
                        </tr>
                      </thead>
                      <tbody>
                        {sortedModels.map((model, idx) => {
                          const isTopModel = idx === 0;
                          return (
                            <tr key={idx} className={`border-b hover:bg-blue-50 ${isTopModel ? 'bg-yellow-50' : ''}`}>
                              <td className="p-3 text-center">
                                {isTopModel ? '🏆' : `${idx + 1}`}
                              </td>
                              <td className="p-3 font-medium">
                                {model.model_name}
                                {isTopModel && <span className="ml-2 text-xs bg-yellow-200 text-yellow-800 px-2 py-1 rounded">Best</span>}
                              </td>
                              {analysisResults.problem_type === 'classification' ? (
                                <>
                                  <td className="p-3 text-right font-semibold text-blue-700">
                                    {(model.accuracy * 100).toFixed(2)}%
                                  </td>
                                  <td className="p-3 text-right text-gray-600">
                                    {model.precision ? (model.precision * 100).toFixed(2) + '%' : 'N/A'}
                                  </td>
                                  <td className="p-3 text-right text-gray-600">
                                    {model.recall ? (model.recall * 100).toFixed(2) + '%' : 'N/A'}
                                  </td>
                                  <td className="p-3 text-right text-gray-600">
                                    {model.f1_score ? (model.f1_score * 100).toFixed(2) + '%' : 'N/A'}
                                  </td>
                                </>
                              ) : (
                                <>
                                  <td className="p-3 text-right font-semibold text-blue-700">
                                    {model.r2_score?.toFixed(4) || 'N/A'}
                                  </td>
                                  <td className="p-3 text-right text-gray-600">
                                    {model.rmse?.toFixed(4) || 'N/A'}
                                  </td>
                                  <td className="p-3 text-right text-gray-600">
                                    {model.mae?.toFixed(4) || 'N/A'}
                                  </td>
                                </>
                              )}
                              <td className="p-3 text-right text-gray-600">
                                {model.training_time ? `${model.training_time.toFixed(2)}s` : 'N/A'}
                              </td>
                            </tr>
                          );
                        })}
                      </tbody>
                    </table>
                  </div>
                  
                  <div className="mt-3 text-xs text-blue-700">
                    {analysisResults.problem_type === 'classification' ? (
                      <>💡 <strong>Quick Guide:</strong> Higher accuracy means better overall predictions. F1-score balances precision and recall. 
                      The 🏆 model performed best on your data.</>
                    ) : (
                      <>💡 <strong>Quick Guide:</strong> R² closer to 1.0 is better (explains variance). Lower RMSE/MAE means fewer errors. 
                      The 🏆 model performed best on your data.</>
                    )}
                  </div>
                </div>
              );
            }
            return null;
          })()}
          
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
                  <TabsList className="flex flex-wrap gap-2 mb-4 h-auto bg-transparent p-0">
                    {models.map((model) => {
                      const modelDescriptions = {
                        "Linear Regression": "Simple model that assumes a linear relationship between features and target. Best for: Basic trends, interpretable results, linear patterns.",
                        "Random Forest": "Ensemble of decision trees that reduces overfitting. Best for: Complex patterns, handling non-linear relationships, robust predictions.",
                        "Decision Tree": "Tree-like model making decisions based on feature values. Best for: Interpretable results, categorical data, quick training.",
                        "XGBoost": "Advanced gradient boosting algorithm, highly accurate. Best for: Competition-level accuracy, complex datasets, handling missing values.",
                        "LSTM Neural Network": "Deep learning model that captures sequential patterns. Best for: Time-series data, long-term dependencies, complex sequences.",
                        "LightGBM": "Fast gradient boosting framework using tree-based learning. Best for: Large datasets, fast training, memory efficiency."
                      };
                      
                      return (
                        <TabsTrigger 
                          key={model.model_name} 
                          value={model.model_name} 
                          className="relative px-4 py-2 text-sm whitespace-nowrap bg-white border border-gray-200 rounded-md hover:bg-gray-50 data-[state=active]:bg-blue-50 data-[state=active]:border-blue-500"
                        >
                          <div className="flex items-center gap-1">
                            <span>{model.model_name}</span>
                            <div className="group relative inline-block">
                              <Info className="w-3 h-3 text-gray-400 cursor-help" />
                              <div className="invisible group-hover:visible absolute bottom-full left-1/2 transform -translate-x-1/2 mb-2 w-80 max-w-md p-4 bg-gray-900 text-white text-xs rounded-lg shadow-2xl z-[100] whitespace-normal break-words">
                                <div className="font-bold text-sm mb-2 text-blue-300">{model.model_name}</div>
                                <p className="leading-relaxed">{modelDescriptions[model.model_name] || "Advanced ML model for predictive analysis."}</p>
                                {/* Tooltip arrow */}
                                <div className="absolute top-full left-1/2 transform -translate-x-1/2 -mt-1">
                                  <div className="border-8 border-transparent border-t-gray-900"></div>
                                </div>
                              </div>
                            </div>
                          </div>
                        </TabsTrigger>
                      );
                    })}
                  </TabsList>
                  
                  {models.map((model) => {
                    return (
                    <TabsContent key={model.model_name} value={model.model_name}>
                      <div className="bg-gradient-to-br from-blue-50 to-indigo-50 rounded-lg p-6 border border-blue-200">
                        <div className="grid md:grid-cols-3 gap-4 mb-4">
                          {analysisResults.problem_type === 'classification' ? (
                            <>
                              <div className="bg-white rounded-lg p-4 shadow-sm">
                                <div className="flex items-center gap-1 text-sm text-gray-600 mb-1">
                                  <span>Accuracy</span>
                                  <div className="group relative">
                                    <Info className="w-3 h-3 text-gray-400 cursor-help" />
                                    <div className="hidden group-hover:block absolute bottom-full left-0 mb-2 w-64 p-2 bg-gray-800 text-white text-xs rounded shadow-lg z-10">
                                      Percentage of correct predictions. 100% = perfect, 0% = all wrong. Higher is better.
                                    </div>
                                  </div>
                                </div>
                                <div className="text-2xl font-bold text-blue-600">{((model.accuracy || 0) * 100).toFixed(1)}%</div>
                              </div>
                              <div className="bg-white rounded-lg p-4 shadow-sm">
                                <div className="flex items-center gap-1 text-sm text-gray-600 mb-1">
                                  <span>F1-Score</span>
                                  <div className="group relative">
                                    <Info className="w-3 h-3 text-gray-400 cursor-help" />
                                    <div className="hidden group-hover:block absolute bottom-full left-0 mb-2 w-64 p-2 bg-gray-800 text-white text-xs rounded shadow-lg z-10">
                                      Harmonic mean of precision and recall. Balances false positives and false negatives. Higher is better.
                                    </div>
                                  </div>
                                </div>
                                <div className="text-2xl font-bold text-purple-600">{((model.f1_score || 0) * 100).toFixed(1)}%</div>
                              </div>
                            </>
                          ) : (
                            <>
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
                                <div className="text-2xl font-bold text-blue-600">{(model.r2_score || 0).toFixed(3)}</div>
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
                                <div className="text-2xl font-bold text-purple-600">{(model.rmse || 0).toFixed(3)}</div>
                              </div>
                            </>
                          )}
                          <div className="bg-white rounded-lg p-4 shadow-sm">
                            <div className="flex items-center gap-1 text-sm text-gray-600 mb-1">
                              <span>Confidence</span>
                              <div className="group relative">
                                <Info className="w-3 h-3 text-gray-400 cursor-help" />
                                <div className="hidden group-hover:block absolute bottom-full left-0 mb-2 w-64 p-2 bg-gray-800 text-white text-xs rounded shadow-lg z-10">
                                  {analysisResults.problem_type === 'classification' ? 
                                    'Overall model reliability based on accuracy. High (>0.85), Medium (0.70-0.85), Low (<0.70).' :
                                    'Overall model reliability based on R² score. High (>0.7), Medium (0.5-0.7), Low (<0.5).'}
                                </div>
                              </div>
                            </div>
                            <div className={`text-2xl font-bold ${
                              model.confidence === 'High' ? 'text-green-600' : 
                              model.confidence === 'Medium' ? 'text-yellow-600' : 
                              model.confidence === 'Low' ? 'text-red-600' : 'text-gray-400'
                            }`}>{model.confidence || 'N/A'}</div>
                          </div>
                        </div>
                        
                        {model.feature_importance && Object.keys(model.feature_importance).length > 0 && (
                          <div className="mt-4">
                            <h5 className="font-semibold mb-2">Feature Importance</h5>
                            <div className="space-y-2">
                              {Object.entries(model.feature_importance).slice(0, 10).map(([feature, importance]) => {
                                // Truncate long feature names intelligently
                                const displayName = feature.length > 25 ? feature.substring(0, 22) + '...' : feature;
                                
                                return (
                                  <div key={feature} className="flex items-center gap-2">
                                    <span 
                                      className="text-sm min-w-[180px] max-w-[180px] truncate" 
                                      title={feature}
                                      style={{fontSize: '12px'}}
                                    >
                                      {displayName}
                                    </span>
                                    <div className="flex-1 bg-gray-200 rounded-full h-2">
                                      <div 
                                        className="bg-blue-600 rounded-full h-2" 
                                        style={{width: `${importance * 100}%`}}
                                      ></div>
                                    </div>
                                    <span className="text-sm text-gray-600 w-16 text-right">{(importance * 100).toFixed(1)}%</span>
                                  </div>
                                );
                              })}
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
        <Card id="auto-charts-section" className="p-6">
          <div className="flex items-start justify-between mb-4">
            <div>
              <div>
                <div className="flex items-center gap-2">
                  <h3 className="text-lg font-semibold">📊 AI-Generated Analysis Charts</h3>
                  <div className="relative group">
                    <AlertCircle className="w-4 h-4 text-blue-500 cursor-help" />
                    <div className="absolute left-0 top-6 hidden group-hover:block w-80 bg-gray-900 text-white text-xs p-3 rounded-lg shadow-lg z-10">
                      <p className="font-semibold mb-1">📊 Prediction-Specific Charts</p>
                      <p className="mb-2">These charts analyze predicted values and model performance. They are different from the Visualization tab charts, which show raw data patterns.</p>
                      <p className="text-gray-300">💡 Use Visualization tab for data exploration and this section for prediction insights.</p>
                    </div>
                  </div>
                </div>
                <p className="text-sm text-gray-600 italic mt-1">Comprehensive visualization suite automatically generated based on your data</p>
              </div>
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
                <h4 className="font-semibold mb-2 text-sm">{chart.title}</h4>
                {chart.description && (
                  <p className="text-xs text-gray-600 italic mb-3 line-clamp-2">{chart.description}</p>
                )}
                <div 
                  id={`auto-chart-${idx}`} 
                  className="w-full"
                  style={{ 
                    height: '350px',
                    maxWidth: '100%',
                    overflow: 'hidden'
                  }}
                ></div>
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

      {/* Skipped Charts Explanation */}
      {analysisResults.skipped_charts && analysisResults.skipped_charts.length > 0 && (
        <Card className="p-6 bg-amber-50 border border-amber-200">
          <div className="flex items-start gap-3">
            <div className="w-10 h-10 bg-amber-100 rounded-full flex items-center justify-center flex-shrink-0">
              <svg className="w-5 h-5 text-amber-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <div className="flex-1">
              <h3 className="text-lg font-semibold text-amber-900 mb-2">Why Some Charts Weren't Generated</h3>
              <p className="text-sm text-amber-700 mb-4">
                Due to data characteristics or insufficient values, the following chart types couldn't be created:
              </p>
              <div className="space-y-2">
                {(() => {
                  // Group by category
                  const grouped = analysisResults.skipped_charts.reduce((acc, item) => {
                    if (!acc[item.category]) acc[item.category] = [];
                    acc[item.category].push(item.reason);
                    return acc;
                  }, {});
                  
                  return Object.entries(grouped).map(([category, reasons], idx) => (
                    <div key={idx} className="bg-white p-3 rounded border border-amber-200">
                      <p className="font-medium text-amber-900 text-sm mb-1">📊 {category}</p>
                      <ul className="text-xs text-amber-700 space-y-1 ml-4">
                        {reasons.slice(0, 3).map((reason, ridx) => (
                          <li key={ridx} className="list-disc">{reason}</li>
                        ))}
                        {reasons.length > 3 && (
                          <li className="text-amber-600 italic">... and {reasons.length - 3} more</li>
                        )}
                      </ul>
                    </div>
                  ));
                })()}
              </div>
            </div>
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