import { useState, useEffect, useRef } from "react";
import axios from "axios";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";
import { toast } from "sonner";
import { TrendingUp, Activity, BarChart3, Target, Zap, LineChart, AlertCircle, CheckCircle, Info, Brain, ChevronDown, ChevronUp, Code, Download, Eye } from "lucide-react";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Dynamic Plotly import for SSR compatibility
let plotlyPromise = null;
const loadPlotly = () => {
  if (plotlyPromise) {
    return plotlyPromise;
  }
  
  if (typeof window === 'undefined') {
    return Promise.reject(new Error('Plotly requires browser environment'));
  }

  if (window.Plotly) {
    return Promise.resolve(window.Plotly);
  }

  plotlyPromise = new Promise((resolve) => {
    const script = document.createElement('script');
    script.src = 'https://cdn.plot.ly/plotly-2.26.0.min.js';
    script.onload = () => resolve(window.Plotly);
    document.head.appendChild(script);
  });
};

const PredictiveAnalysis = ({ dataset, analysisCache, onAnalysisUpdate, variableSelection }) => {
  // CRITICAL: Initialize ref BEFORE state to ensure it's ready for merge operations
  const previousResultsRef = useRef(null);  // CRITICAL: Persist previous results across state updates
  
  // Load analysis results from localStorage on mount (for page refresh persistence)
  // PRODUCTION FIX: Only use parent cache, no localStorage (supports unlimited data size)
  const getInitialAnalysisResults = () => {
    // PRODUCTION: Only use cache from parent (supports unlimited size via IndexedDB)
    if (analysisCache) {
      console.log('✅ Restored analysis results from parent cache');
      
      // CRITICAL FIX: Immediately update ref when loading from cache
      previousResultsRef.current = analysisCache;
      console.log('✅ Immediately set previousResultsRef from cache with', 
                  analysisCache?.ml_models?.length || 0, 'models');
      
      return analysisCache;
    }
    
    return null;
  };

  const [analysisResults, setAnalysisResults] = useState(getInitialAnalysisResults);
  const [loading, setLoading] = useState(false);
  const [progress, setProgress] = useState(0);
  const [analysisTime, setAnalysisTime] = useState(null);
  const [expandedRow, setExpandedRow] = useState(null);
  const [selectedModels, setSelectedModels] = useState([]);
  const [selectionFeedback, setSelectionFeedback] = useState(null);
  const [showModelSelection, setShowModelSelection] = useState(false);
  const [collapsed, setCollapsed] = useState({
    model_comparison: false,
    feature_importance: false,
    predictions: false,
    preprocessing: false,
    auto_charts: false, // NEW: Collapsible auto-generated charts
    custom_charts: false
  });
  const [showCode, setShowCode] = useState({});
  
  const progressIntervalRef = useRef(null);
  const hasRunAnalysisRef = useRef(false);

  // Save analysis results to parent cache (IndexedDB) instead of localStorage
  useEffect(() => {
    if (analysisResults && onAnalysisUpdate) {
      console.log('💾 Passing analysis results to parent for caching...');
      onAnalysisUpdate(analysisResults);
      
      // CRITICAL: Also update the ref when results change
      previousResultsRef.current = analysisResults;
      console.log('✅ Updated previousResultsRef with', analysisResults?.ml_models?.length || 0, 'models');
    }
  }, [analysisResults, onAnalysisUpdate]);

  // CRITICAL FIX: Watch analysisCache changes (when workspace is loaded)
  useEffect(() => {
    if (analysisCache && analysisCache.ml_models && analysisCache.ml_models.length > 0) {
      // Update ref immediately
      previousResultsRef.current = analysisCache;
      console.log('✅ Updated previousResultsRef from analysisCache prop change with', 
                  analysisCache.ml_models.length, 'models');
      
      // Also update state to ensure UI shows loaded data
      if (!analysisResults || analysisResults !== analysisCache) {
        setAnalysisResults(analysisCache);
        console.log('✅ Updated analysisResults state from analysisCache');
      }
    }
  }, [analysisCache]); // Only watch analysisCache changes
  
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
      // Check if it has target and features (either format)
      return (
        (selection.target_variable && selection.selected_features?.length > 0) ||
        (selection.target && selection.features?.length > 0)
      );
    };
    
    // Only auto-run if:
    // 1. We haven't run yet (hasRunAnalysisRef is false)
    // 2. Not currently loading
    // 3. Either we have valid variable selection OR we're skipping selection
    const shouldAutoRun = (
      !hasRunAnalysisRef.current && 
      !loading && 
      (!variableSelection || hasValidSelection(variableSelection))
    );
    
    console.log('Should auto-run?', shouldAutoRun, '- Has valid selection?', hasValidSelection(variableSelection));
    
    if (shouldAutoRun) {
      console.log('Auto-running analysis based on variable selection...');
      hasRunAnalysisRef.current = true; // Mark as run
      runHolisticAnalysis();
    } else if (analysisCache && !hasRunAnalysisRef.current) {
      // If we have cached data and haven't run yet, mark as run to prevent loops
      console.log('Using cached analysis results, marking as run');
      hasRunAnalysisRef.current = true;
    }
  }, [variableSelection]); // Re-run when variableSelection changes

  // Render custom charts when available OR when collapsed state changes
  useEffect(() => {
    if (analysisResults?.custom_charts && analysisResults.custom_charts.length > 0 && !collapsed.custom_charts) {
      loadPlotly().then((Plotly) => {
        analysisResults.custom_charts.forEach((chart, idx) => {
          const chartDiv = document.getElementById(`custom-chart-${idx}`);
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
            
            Plotly.newPlot(`custom-chart-${idx}`, plotlyData.data, enhancedLayout, {
              responsive: true,
              displayModeBar: true,
              displaylogo: false,
              modeBarButtonsToRemove: ['lasso2d', 'select2d']
            }).then(() => {
              // Force resize to container
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
          // Handle both formats: transformed (target_variable/selected_features) and original (target/features)
          target_variable: variableSelection.target_variable || variableSelection.target,
          selected_features: variableSelection.selected_features || variableSelection.features,
          mode: variableSelection.mode,
          ai_suggestions: variableSelection.ai_suggestions || variableSelection.aiSuggestions
        };
        
        // CRITICAL NEW: Add user expectation to payload
        if (variableSelection.user_expectation) {
          payload.user_selection.user_expectation = variableSelection.user_expectation;
          console.log('✅ Including user expectation in payload:', variableSelection.user_expectation);
        }
        
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
      
      // Merge if we have previous results to preserve
      if (previousResults && previousResults.ml_models && previousResults.ml_models.length > 0) {
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
      
      setAnalysisResults(updatedResults);

      toast.success(`Analysis complete in ${timeTaken}s!`);

    } catch (error) {
      console.error("Analysis error:", error);
      toast.error("Analysis failed: " + (error.response?.data?.detail || error.message));
      setProgress(0);
    } finally {
      setLoading(false);
      if (progressIntervalRef.current) {
        clearInterval(progressIntervalRef.current);
      }
    }
  };

  const handleRunAdditionalModels = () => {
    setShowModelSelection(true);
  };

  const handleModelSelectionComplete = (models) => {
    setSelectedModels(models);
    setShowModelSelection(false);
    // Trigger analysis with selected models
    setTimeout(() => runHolisticAnalysis(), 100);
  };

  const toggleSection = (section) => {
    setCollapsed(prev => ({ ...prev, [section]: !prev[section] }));
  };

  const toggleCode = (chartIndex) => {
    setShowCode(prev => ({ ...prev, [chartIndex]: !prev[chartIndex] }));
  };

  const downloadChart = async (chartIndex, chartData) => {
    try {
      await loadPlotly();
      const chartId = `custom-chart-${chartIndex}`;
      const element = document.getElementById(chartId);
      if (element && window.Plotly) {
        window.Plotly.downloadImage(element, {
          format: 'png',
          width: 1200,
          height: 800,
          filename: `chart-${chartIndex + 1}`
        });
      }
    } catch (error) {
      console.error('Download failed:', error);
      toast.error('Failed to download chart');
    }
  };

  const renderPredictionExamples = () => {
    if (!analysisResults?.prediction_examples || analysisResults.prediction_examples.length === 0) {
      return null;
    }

    return (
      <Card className="mt-6 border-l-4 border-l-green-500">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Eye className="w-5 h-5 text-green-600" />
            Real Prediction Examples
          </CardTitle>
          <CardDescription>
            See how the model performs on actual data points from your test set
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {analysisResults.prediction_examples.map((example, idx) => (
              <div key={idx} className="p-4 bg-gradient-to-r from-green-50 to-blue-50 rounded-lg border border-green-200">
                <div className="grid md:grid-cols-2 gap-4 mb-3">
                  <div>
                    <p className="text-sm font-semibold text-gray-700 mb-2">Input Features:</p>
                    <div className="space-y-1">
                      {Object.entries(example.features || {}).map(([key, value]) => (
                        <div key={key} className="flex justify-between text-sm">
                          <span className="text-gray-600">{key}:</span>
                          <span className="font-medium">{typeof value === 'number' ? value.toFixed(2) : value}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                  <div>
                    <p className="text-sm font-semibold text-gray-700 mb-2">Prediction vs Actual:</p>
                    <div className="space-y-2">
                      <div className="flex justify-between text-sm">
                        <span className="text-gray-600">Actual Value:</span>
                        <span className="font-bold text-green-700">{example.actual_value?.toFixed(2) || 'N/A'}</span>
                      </div>
                      <div className="flex justify-between text-sm">
                        <span className="text-gray-600">Predicted Value:</span>
                        <span className="font-bold text-blue-700">{example.predicted_value?.toFixed(2) || 'N/A'}</span>
                      </div>
                      {example.error && (
                        <div className="flex justify-between text-sm">
                          <span className="text-gray-600">Error:</span>
                          <span className={`font-medium ${Math.abs(example.error) < 0.1 ? 'text-green-600' : 'text-orange-600'}`}>
                            {example.error > 0 ? '+' : ''}{(example.error * 100).toFixed(1)}%
                          </span>
                        </div>
                      )}
                    </div>
                  </div>
                </div>
                {example.interpretation && (
                  <div className="mt-3 p-3 bg-white rounded border border-gray-200">
                    <p className="text-sm text-gray-700">
                      <span className="font-semibold">💬 Plain English: </span>
                      {example.interpretation}
                    </p>
                  </div>
                )}
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    );
  };

  const renderPreprocessingReport = () => {
    if (!analysisResults?.preprocessing_report) {
      return null;
    }

    const report = analysisResults.preprocessing_report;

    return (
      <Card className="mt-6 border-l-4 border-l-purple-500">
        <CardHeader className="cursor-pointer" onClick={() => toggleSection('preprocessing')}>
          <div className="flex justify-between items-center">
            <CardTitle className="flex items-center gap-2">
              <Zap className="w-5 h-5 text-purple-600" />
              Automated Data Preprocessing Report
            </CardTitle>
            {collapsed.preprocessing ? <ChevronDown className="w-5 h-5" /> : <ChevronUp className="w-5 h-5" />}
          </div>
          <CardDescription>
            All data cleaning and preparation steps applied automatically
          </CardDescription>
        </CardHeader>
        {!collapsed.preprocessing && (
          <CardContent>
            <div className="space-y-4">
              {report.missing_values_handled > 0 && (
                <div className="p-3 bg-blue-50 rounded-lg">
                  <p className="text-sm font-semibold text-blue-900">✓ Missing Values Handled</p>
                  <p className="text-sm text-blue-700">Filled {report.missing_values_handled} missing values using mean/median/mode imputation</p>
                </div>
              )}
              {report.numeric_scaled && (
                <div className="p-3 bg-green-50 rounded-lg">
                  <p className="text-sm font-semibold text-green-900">✓ Numeric Features Scaled</p>
                  <p className="text-sm text-green-700">Normalized {report.numeric_columns?.length || 0} numeric columns to [0, 1] range</p>
                </div>
              )}
              {report.categorical_encoded && (
                <div className="p-3 bg-purple-50 rounded-lg">
                  <p className="text-sm font-semibold text-purple-900">✓ Categorical Features Encoded</p>
                  <p className="text-sm text-purple-700">One-hot encoded {report.categorical_columns?.length || 0} categorical columns</p>
                </div>
              )}
              {report.outliers_handled > 0 && (
                <div className="p-3 bg-orange-50 rounded-lg">
                  <p className="text-sm font-semibold text-orange-900">⚠ Outliers Detected</p>
                  <p className="text-sm text-orange-700">Found {report.outliers_handled} outliers (kept for analysis as they may contain insights)</p>
                </div>
              )}
            </div>
          </CardContent>
        )}
      </Card>
    );
  };

  if (!dataset) {
    return (
      <div className="p-8 text-center text-gray-500">
        <BarChart3 className="w-16 h-16 mx-auto mb-4 text-gray-400" />
        <p>No dataset selected. Please upload or select a dataset to begin analysis.</p>
      </div>
    );
  }

  return (
    <div className="space-y-6 p-6">
      {/* Analysis Control Panel */}
      <Card className="border-t-4 border-t-blue-500">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Target className="w-6 h-6 text-blue-600" />
            Predictive Analysis
          </CardTitle>
          <CardDescription>
            Training 35+ ML models for comprehensive predictions and insights
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex gap-3">
            <Button 
              onClick={runHolisticAnalysis} 
              disabled={loading}
              className="flex-1"
            >
              {loading ? (
                <>
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2" />
                  Analyzing... {progress}%
                </>
              ) : (
                <>
                  <Activity className="w-4 h-4 mr-2" />
                  Run Analysis
                </>
              )}
            </Button>
            
            {analysisResults && (
              <Button 
                onClick={handleRunAdditionalModels}
                variant="outline"
                disabled={loading}
              >
                <Brain className="w-4 h-4 mr-2" />
                Train Additional Models
              </Button>
            )}
          </div>

          {loading && (
            <div className="mt-4">
              <Progress value={progress} className="w-full" />
              <p className="text-sm text-gray-600 mt-2 text-center">
                {progress < 30 && "Analyzing dataset..."}
                {progress >= 30 && progress < 60 && "Training machine learning models..."}
                {progress >= 60 && progress < 90 && "Evaluating model performance..."}
                {progress >= 90 && "Finalizing results..."}
              </p>
            </div>
          )}

          {analysisTime && (
            <div className="mt-3 text-sm text-gray-600 text-center">
              ⏱️ Analysis completed in {analysisTime} seconds
            </div>
          )}
        </CardContent>
      </Card>

      {/* Selection Feedback (AI Validation) */}
      {selectionFeedback && (
        <Card className="border-l-4 border-l-blue-500">
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-blue-700">
              {selectionFeedback.status === 'approved' ? (
                <CheckCircle className="w-5 h-5" />
              ) : (
                <Info className="w-5 h-5" />
              )}
              AI Variable Selection Feedback
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              <p className="text-sm font-semibold">Status: <span className={selectionFeedback.status === 'approved' ? 'text-green-600' : 'text-orange-600'}>{selectionFeedback.status}</span></p>
              <p className="text-sm text-gray-700">{selectionFeedback.message}</p>
              
              {selectionFeedback.suggestions && selectionFeedback.suggestions.length > 0 && (
                <div className="mt-3">
                  <p className="text-sm font-semibold mb-2">💡 Suggestions:</p>
                  <ul className="list-disc list-inside space-y-1">
                    {selectionFeedback.suggestions.map((suggestion, idx) => (
                      <li key={idx} className="text-sm text-gray-600">{suggestion}</li>
                    ))}
                  </ul>
                </div>
              )}
              
              {selectionFeedback.warnings && selectionFeedback.warnings.length > 0 && (
                <div className="mt-3 p-3 bg-orange-50 rounded-lg">
                  <p className="text-sm font-semibold text-orange-800 mb-2">⚠️ Warnings:</p>
                  <ul className="list-disc list-inside space-y-1">
                    {selectionFeedback.warnings.map((warning, idx) => (
                      <li key={idx} className="text-sm text-orange-700">{warning}</li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Model Selection Modal */}
      {showModelSelection && (
        <ModelSelectionPanel
          onClose={() => setShowModelSelection(false)}
          onConfirm={handleModelSelectionComplete}
          problemType={analysisResults?.problem_type || 'auto'}
        />
      )}

      {/* Results Section - Only show if analysis completed */}
      {analysisResults && (
        <div className="space-y-6">
          {/* Preprocessing Report */}
          {renderPreprocessingReport()}

          {/* Real Prediction Examples */}
          {renderPredictionExamples()}

          {/* ML Model Comparison Table */}
          {analysisResults.ml_models && analysisResults.ml_models.length > 0 && (
            <Card className="border-l-4 border-l-green-500">
              <CardHeader className="cursor-pointer" onClick={() => toggleSection('model_comparison')}>
                <div className="flex justify-between items-center">
                  <CardTitle className="flex items-center gap-2">
                    <TrendingUp className="w-5 h-5 text-green-600" />
                    ML Model Data Comparison ({analysisResults.ml_models.length} models)
                  </CardTitle>
                  {collapsed.model_comparison ? <ChevronDown className="w-5 h-5" /> : <ChevronUp className="w-5 h-5" />}
                </div>
                <CardDescription>
                  Performance comparison across {analysisResults.ml_models.length} trained models
                </CardDescription>
              </CardHeader>
              {!collapsed.model_comparison && (
                <CardContent>
                  <div className="overflow-x-auto">
                    <table className="w-full text-sm">
                      <thead className="bg-gray-50">
                        <tr>
                          <th className="px-4 py-3 text-left font-semibold text-gray-700">Rank</th>
                          <th className="px-4 py-3 text-left font-semibold text-gray-700">Model</th>
                          <th className="px-4 py-3 text-left font-semibold text-gray-700">Score</th>
                          <th className="px-4 py-3 text-left font-semibold text-gray-700">Type</th>
                          <th className="px-4 py-3 text-left font-semibold text-gray-700">Complexity</th>
                        </tr>
                      </thead>
                      <tbody>
                        {analysisResults.ml_models.map((model, idx) => {
                          const isExpanded = expandedRow === idx;
                          const mainMetric = model.r2_score !== undefined ? model.r2_score : model.accuracy;
                          const metricName = model.r2_score !== undefined ? 'R² Score' : 'Accuracy';
                          
                          return (
                            <tr 
                              key={idx} 
                              className={`border-t hover:bg-gray-50 cursor-pointer ${
                                idx === 0 ? 'bg-green-50 font-semibold' : ''
                              }`}
                              onClick={() => setExpandedRow(isExpanded ? null : idx)}
                            >
                              <td className="px-4 py-3">
                                {idx === 0 && <span className="text-yellow-500">👑</span>} #{idx + 1}
                              </td>
                              <td className="px-4 py-3">{model.model_name}</td>
                              <td className="px-4 py-3">
                                <span className={`px-2 py-1 rounded text-xs ${
                                  mainMetric >= 0.8 ? 'bg-green-100 text-green-800' :
                                  mainMetric >= 0.6 ? 'bg-yellow-100 text-yellow-800' :
                                  'bg-red-100 text-red-800'
                                }`}>
                                  {(mainMetric * 100).toFixed(1)}%
                                </span>
                              </td>
                              <td className="px-4 py-3 text-gray-600">{model.model_type || 'ML'}</td>
                              <td className="px-4 py-3">
                                <span className={`text-xs px-2 py-1 rounded ${
                                  model.complexity === 'low' ? 'bg-blue-100 text-blue-700' :
                                  model.complexity === 'medium' ? 'bg-purple-100 text-purple-700' :
                                  'bg-red-100 text-red-700'
                                }`}>
                                  {model.complexity || 'N/A'}
                                </span>
                              </td>
                            </tr>
                          );
                        })}
                      </tbody>
                    </table>
                  </div>
                </CardContent>
              )}
            </Card>
          )}

          {/* Feature Importance */}
          {analysisResults.feature_importance && analysisResults.feature_importance.length > 0 && (
            <Card className="border-l-4 border-l-purple-500">
              <CardHeader className="cursor-pointer" onClick={() => toggleSection('feature_importance')}>
                <div className="flex justify-between items-center">
                  <CardTitle className="flex items-center gap-2">
                    <BarChart3 className="w-5 h-5 text-purple-600" />
                    Feature Importance
                  </CardTitle>
                  {collapsed.feature_importance ? <ChevronDown className="w-5 h-5" /> : <ChevronUp className="w-5 h-5" />}
                </div>
                <CardDescription>
                  Which features contribute most to predictions
                </CardDescription>
              </CardHeader>
              {!collapsed.feature_importance && (
                <CardContent>
                  <div className="space-y-3">
                    {analysisResults.feature_importance.map((feature, idx) => (
                      <div key={idx} className="flex items-center gap-3">
                        <div className="w-32 text-sm font-medium text-gray-700 truncate" title={feature.feature}>
                          {feature.feature}
                        </div>
                        <div className="flex-1">
                          <div className="h-6 bg-gray-100 rounded-full overflow-hidden">
                            <div 
                              className="h-full bg-gradient-to-r from-purple-500 to-blue-500 flex items-center justify-end px-2"
                              style={{ width: `${(feature.importance * 100).toFixed(1)}%` }}
                            >
                              <span className="text-xs font-semibold text-white">
                                {(feature.importance * 100).toFixed(1)}%
                              </span>
                            </div>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </CardContent>
              )}
            </Card>
          )}

          {/* AI Insights */}
          {analysisResults.insights && (
            <Card className="border-l-4 border-l-orange-500">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Zap className="w-5 h-5 text-orange-600" />
                  AI-Powered Insights
                </CardTitle>
                <CardDescription>
                  Key findings and recommendations from Azure OpenAI
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="prose prose-sm max-w-none">
                  <div className="whitespace-pre-wrap text-gray-700">{analysisResults.insights}</div>
                </div>
              </CardContent>
            </Card>
          )}

          {/* Custom Charts from Chat */}
          {analysisResults.custom_charts && analysisResults.custom_charts.length > 0 && (
            <Card className="border-l-4 border-l-indigo-500">
              <CardHeader className="cursor-pointer" onClick={() => toggleSection('custom_charts')}>
                <div className="flex justify-between items-center">
                  <CardTitle className="flex items-center gap-2">
                    <LineChart className="w-5 h-5 text-indigo-600" />
                    Chat-Generated Charts ({analysisResults.custom_charts.length})
                  </CardTitle>
                  {collapsed.custom_charts ? <ChevronDown className="w-5 h-5" /> : <ChevronUp className="w-5 h-5" />}
                </div>
                <CardDescription>
                  Custom visualizations created through AI chat
                </CardDescription>
              </CardHeader>
              {!collapsed.custom_charts && (
                <CardContent>
                  <div className="space-y-6">
                    {analysisResults.custom_charts.map((chart, idx) => (
                      <div key={idx} className="border rounded-lg p-4 bg-gray-50">
                        <div className="flex justify-between items-start mb-3">
                          <div>
                            <h4 className="font-semibold text-gray-800">{chart.title || `Chart ${idx + 1}`}</h4>
                            {chart.description && (
                              <p className="text-sm text-gray-600 mt-1">{chart.description}</p>
                            )}
                          </div>
                          <div className="flex gap-2">
                            <Button
                              variant="ghost"
                              size="sm"
                              onClick={() => downloadChart(idx, chart)}
                            >
                              <Download className="w-4 h-4" />
                            </Button>
                            <Button
                              variant="ghost"
                              size="sm"
                              onClick={() => toggleCode(idx)}
                            >
                              <Code className="w-4 h-4" />
                            </Button>
                          </div>
                        </div>
                        <div id={`custom-chart-${idx}`} className="w-full" style={{ height: '400px' }} />
                        {showCode[idx] && chart.code && (
                          <div className="mt-3 p-3 bg-gray-900 rounded-lg overflow-x-auto">
                            <pre className="text-xs text-green-400">
                              <code>{chart.code}</code>
                            </pre>
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                </CardContent>
              )}
            </Card>
          )}
        </div>
      )}

      {!analysisResults && !loading && (
        <Card className="border-dashed border-2">
          <CardContent className="py-12 text-center">
            <BarChart3 className="w-16 h-16 mx-auto mb-4 text-gray-400" />
            <p className="text-gray-600 mb-4">Click "Run Analysis" to start training ML models</p>
            <p className="text-sm text-gray-500">35+ models will be trained and evaluated automatically</p>
          </CardContent>
        </Card>
      )}
    </div>
  );
};

export default PredictiveAnalysis;