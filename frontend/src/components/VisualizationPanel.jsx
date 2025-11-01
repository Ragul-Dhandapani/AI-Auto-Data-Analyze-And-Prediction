import { useState, useEffect, useRef } from "react";
import axios from "axios";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { toast } from "sonner";
import { Loader2, BarChart3, MessageSquare, X, Send, ChevronDown, AlertCircle } from "lucide-react";
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from "@/components/ui/collapsible";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Load Plotly script
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

const ChartComponent = ({ chart, index }) => {
  const chartId = `viz-plotly-chart-${index}`;
  const [error, setError] = useState(null);
  
  useEffect(() => {
    const renderChart = async () => {
      try {
        await loadPlotly();
        
        if (window.Plotly && chart.data) {
          const container = document.getElementById(chartId);
          if (container) {
            // Validate data structure
            if (!chart.data.data || !Array.isArray(chart.data.data) || chart.data.data.length === 0) {
              setError("No chart data available");
              return;
            }
            
            await window.Plotly.newPlot(
              chartId,
              chart.data.data,
              {
                ...chart.data.layout,
                autosize: true,
                height: 400,
                margin: { l: 60, r: 40, t: 60, b: 60 },  // Better margins
                paper_bgcolor: 'rgba(0,0,0,0)',
                plot_bgcolor: 'rgba(0,0,0,0)',
                font: { family: 'Inter, sans-serif' }
              },
              { 
                responsive: true, 
                displayModeBar: true,
                displaylogo: false,
                modeBarButtonsToRemove: ['lasso2d', 'select2d']
              }
            );
            setError(null);
          }
        }
      } catch (err) {
        console.error('Chart rendering error:', err);
        setError(err.message);
      }
    };
    
    renderChart();
    
    return () => {
      if (window.Plotly) {
        const container = document.getElementById(chartId);
        if (container) {
          window.Plotly.purge(chartId);
        }
      }
    };
  }, [chart, chartId]);
  
  if (error) {
    return (
      <Card className="p-6 bg-red-50 border-red-200" data-testid={`chart-${index}`}>
        <h4 className="text-lg font-semibold mb-2 text-red-800">{chart.title}</h4>
        <p className="text-sm text-red-600">Error: {error}</p>
      </Card>
    );
  }
  
  return (
    <Card className="p-6" data-testid={`chart-${index}`}>
      <h4 className="text-lg font-semibold mb-2">{chart.title}</h4>
      <p className="text-sm text-gray-600 mb-4 italic">{chart.description}</p>
      <div className="w-full bg-white rounded-lg p-2">
        <div id={chartId} className="w-full" style={{ minHeight: '400px', maxHeight: '450px' }} />
      </div>
    </Card>
  );
};

const VisualizationPanel = ({ dataset, chartsCache, onChartsUpdate }) => {
  const [loading, setLoading] = useState(false);
  const [charts, setCharts] = useState(chartsCache?.charts || []);
  const [skippedCharts, setSkippedCharts] = useState(chartsCache?.skipped || []);
  const [hasGenerated, setHasGenerated] = useState(!!chartsCache);
  const [progress, setProgress] = useState(0);  // Progress tracking
  const [showChat, setShowChat] = useState(false);
  const [chatMessages, setChatMessages] = useState(chartsCache?.chatMessages || []);
  const [chatInput, setChatInput] = useState("");
  const [chatLoading, setChatLoading] = useState(false);
  const [customCharts, setCustomCharts] = useState(chartsCache?.customCharts || []);
  const [showSkipped, setShowSkipped] = useState(false);
  const [customChartsOpen, setCustomChartsOpen] = useState(true);
  const [generatedChartsOpen, setGeneratedChartsOpen] = useState(true);
  const chatEndRef = useRef(null);
  const progressIntervalRef = useRef(null);

  // Update cache when data changes
  useEffect(() => {
    if (onChartsUpdate && (charts.length > 0 || customCharts.length > 0)) {
      onChartsUpdate({
        charts,
        skipped: skippedCharts,
        chatMessages,
        customCharts
      });
    }
  }, [charts, skippedCharts, chatMessages, customCharts]);

  // Restore from cache when dataset changes
  useEffect(() => {
    if (chartsCache) {
      setCharts(chartsCache.charts || []);
      setSkippedCharts(chartsCache.skipped || []);
      setChatMessages(chartsCache.chatMessages || []);
      setCustomCharts(chartsCache.customCharts || []);
      setHasGenerated(true);
    }
  }, [dataset?.id]);

  const generateCharts = async () => {
    setLoading(true);
    setProgress(0);
    
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
      const response = await axios.post(`${API}/analysis/run`, {
        dataset_id: dataset.id,
        analysis_type: "visualize"
      });
      
      // Complete progress
      setProgress(100);
      
      setCharts(response.data.charts || []);
      setSkippedCharts(response.data.skipped || []);
      setHasGenerated(true);
      if (response.data.charts?.length > 0) {
        toast.success(`Generated ${response.data.charts.length} visualizations!`);
      }
      if (response.data.skipped?.length > 0) {
        toast.info(`${response.data.skipped.length} charts skipped due to data issues`);
      }
    } catch (error) {
      toast.error("Chart generation failed: " + (error.response?.data?.detail || error.message));
    } finally {
      if (progressIntervalRef.current) {
        clearInterval(progressIntervalRef.current);
      }
      setLoading(false);
      setTimeout(() => setProgress(0), 1000); // Reset progress after 1s
    }
  };

  // Cleanup progress interval on unmount
  useEffect(() => {
    return () => {
      if (progressIntervalRef.current) {
        clearInterval(progressIntervalRef.current);
      }
    };
  }, []);

  // Auto-generate charts only once on mount
  const hasRunGenerationRef = useRef(false);
  
  useEffect(() => {
    if (dataset && !hasGenerated && !hasRunGenerationRef.current && !loading) {
      hasRunGenerationRef.current = true;
      generateCharts();
    }
  }, [dataset, hasGenerated]);

  // Reset generation ref when dataset changes
  useEffect(() => {
    hasRunGenerationRef.current = !!chartsCache;
  }, [dataset?.id]);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [chatMessages]);

  // Render custom charts from chat when expanded
  useEffect(() => {
    if (customCharts.length > 0 && customChartsOpen) {
      // Small delay to ensure DOM is ready
      setTimeout(() => {
        loadPlotly().then((Plotly) => {
          customCharts.forEach((chart, idx) => {
            const chartDiv = document.getElementById(`viz-custom-chart-${idx}`);
            if (chartDiv && chart.plotly_data) {
              Plotly.newPlot(`viz-custom-chart-${idx}`, chart.plotly_data.data, chart.plotly_data.layout, {
                responsive: true,
                displayModeBar: true,
                modeBarButtonsToRemove: ['lasso2d', 'select2d']
              });
            }
          });
        });
      }, 100);
    }
  }, [customCharts, customChartsOpen]);

  const refreshCharts = () => {
    setHasGenerated(false);
    setCharts([]);
    setSkippedCharts([]);
    generateCharts();
  };

  const handleChatSend = async () => {
    if (!chatInput.trim()) return;

    const userMsg = { role: 'user', content: chatInput };
    setChatMessages(prev => [...prev, userMsg]);
    setChatInput("");
    setChatLoading(true);

    try {
      const response = await axios.post(`${API}/analysis/chat-action`, {
        dataset_id: dataset.id,
        message: chatInput,
        conversation_history: chatMessages
      });

      const assistantMsg = { role: 'assistant', content: response.data.message || response.data.response };
      setChatMessages(prev => [...prev, assistantMsg]);

      // Handle chart additions
      if (response.data.action === 'add_chart' && response.data.chart_data) {
        setCustomCharts(prev => [...prev, response.data.chart_data]);
        toast.success("Chart added!");
      }

      // Handle chart removal
      if (response.data.action === 'remove_section') {
        if (response.data.section_to_remove === 'custom_chart' && customCharts.length > 0) {
          setCustomCharts(prev => prev.slice(0, -1));
          toast.success("Chart removed!");
        }
      }
    } catch (error) {
      const errorMsg = error.response?.data?.detail || error.message;
      setChatMessages(prev => [...prev, { role: 'assistant', content: `Error: ${errorMsg}` }]);
      toast.error("Chat failed");
    } finally {
      setChatLoading(false);
    }
  };

  // Filter charts to only show those with valid data
  const validCharts = charts.filter(chart => 
    chart && 
    chart.data
  );

  const validCustomCharts = customCharts.filter(chart =>
    chart && 
    chart.plotly_data
  );

  if (loading && validCharts.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center py-12 space-y-6" data-testid="visualization-panel">
        <Loader2 className="w-8 h-8 animate-spin text-blue-600" />
        <span className="text-lg">Generating comprehensive visualizations...</span>
        
        {/* Progress Bar */}
        <div className="w-full max-w-md">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm text-gray-600">Generation Progress</span>
            <span className="text-sm font-semibold text-blue-600">{Math.min(Math.round(progress), 100)}%</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-3 overflow-hidden">
            <div 
              className="bg-gradient-to-r from-blue-500 to-blue-600 h-3 rounded-full transition-all duration-500 ease-out"
              style={{ width: `${Math.min(progress, 100)}%` }}
            />
          </div>
          <p className="text-xs text-gray-500 mt-2 text-center">
            {progress < 30 ? "Loading data and analyzing..." : 
             progress < 60 ? "Detecting patterns and relationships..." :
             progress < 85 ? "Generating intelligent charts..." :
             progress >= 90 ? "Finalizing visualizations..." :
             "Creating visual insights..."}
          </p>
        </div>
      </div>
    );
  }

  if (validCharts.length === 0 && !loading) {
    return (
      <div className="flex items-center justify-center py-12" data-testid="visualization-panel">
        <p className="text-gray-600">No visualizations available. Please select a dataset.</p>
      </div>
    );
  }

  return (
    <div className="space-y-6" data-testid="visualization-panel">
      <Card className="p-6 bg-gradient-to-br from-blue-50 to-cyan-50 border-blue-200">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-xl font-semibold flex items-center gap-2">
              <BarChart3 className="w-6 h-6 text-blue-600" />
              Data Visualization & Insights
            </h3>
            <p className="text-sm text-gray-600 mt-2">
              Comprehensive charts automatically generated based on your data characteristics. 
              {validCharts.length > 0 && ` Showing ${validCharts.length} visualizations.`}
              {skippedCharts.length > 0 && ` (${skippedCharts.length} skipped)`}
            </p>
          </div>
          <div className="flex gap-2">
            <Button 
              onClick={() => setShowChat(!showChat)}
              variant="outline"
              size="sm"
            >
              <MessageSquare className="w-4 h-4 mr-2" />
              {showChat ? 'Hide' : 'Chat'}
            </Button>
            {validCharts.length > 0 && (
              <Button 
                data-testid="refresh-charts-btn"
                onClick={refreshCharts}
                disabled={loading}
                variant="outline"
                size="sm"
              >
                {loading ? (
                  <><Loader2 className="w-4 h-4 animate-spin mr-2" /> Refreshing...</>
                ) : (
                  <><BarChart3 className="w-4 h-4 mr-2" /> Refresh</>
                )}
              </Button>
            )}
          </div>
        </div>
      </Card>

      {/* Skipped Charts Section */}
      {skippedCharts.length > 0 && (
        <Collapsible open={showSkipped} onOpenChange={setShowSkipped}>
          <Card className="p-4 bg-amber-50 border-amber-200">
            <CollapsibleTrigger className="w-full">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <AlertCircle className="w-5 h-5 text-amber-600" />
                  <span className="font-semibold text-amber-800">
                    {skippedCharts.length} Charts Skipped
                  </span>
                </div>
                <ChevronDown className={`w-4 h-4 transition-transform ${showSkipped ? 'rotate-180' : ''}`} />
              </div>
            </CollapsibleTrigger>
            <CollapsibleContent className="mt-3">
              <ul className="space-y-1 text-sm text-amber-800">
                {skippedCharts.map((reason, idx) => (
                  <li key={idx} className="flex items-start gap-2">
                    <span className="text-amber-600">•</span>
                    <span>{reason}</span>
                  </li>
                ))}
              </ul>
            </CollapsibleContent>
          </Card>
        </Collapsible>
      )}

      {/* Custom Charts from Chat - Collapsible */}
      {validCustomCharts.length > 0 && (
        <Collapsible defaultOpen={true}>
          <Card className="p-6">
            <CollapsibleTrigger className="w-full">
              <div className="flex items-center justify-between cursor-pointer hover:opacity-80">
                <h3 className="text-lg font-semibold">📈 Custom Charts (from Chat) ({validCustomCharts.length})</h3>
                <ChevronDown className="w-5 h-5" />
              </div>
            </CollapsibleTrigger>
            <CollapsibleContent className="mt-4">
              <div className="grid md:grid-cols-2 gap-6">
                {validCustomCharts.map((chart, idx) => (
                  <div key={idx} className="bg-white rounded-lg p-4 border border-gray-200">
                    <h4 className="font-semibold mb-2">{chart.title}</h4>
                    {chart.description && (
                      <p className="text-sm text-gray-600 italic mb-3">{chart.description}</p>
                    )}
                    <div id={`viz-custom-chart-${idx}`} className="w-full" style={{ minHeight: '400px', maxHeight: '500px' }}></div>
                  </div>
                ))}
              </div>
            </CollapsibleContent>
          </Card>
        </Collapsible>
      )}

      {/* Generated Visualizations - Collapsible */}
      {validCharts.length > 0 && (
        <Collapsible defaultOpen={true}>
          <Card className="p-6">
            <CollapsibleTrigger className="w-full">
              <div className="flex items-center justify-between cursor-pointer hover:opacity-80">
                <h3 className="text-lg font-semibold">📊 Generated Visualizations ({validCharts.length})</h3>
                <ChevronDown className="w-5 h-5" />
              </div>
            </CollapsibleTrigger>
            <CollapsibleContent className="mt-4">
              <div className="grid md:grid-cols-2 gap-6">
                {validCharts.map((chart, idx) => (
                  <ChartComponent key={`${dataset.id}-${idx}`} chart={chart} index={idx} />
                ))}
              </div>
            </CollapsibleContent>
          </Card>
        </Collapsible>
      )}

      {/* Chat Panel */}
      {showChat && (
        <div className="fixed right-6 bottom-6 w-96 h-[600px] bg-white rounded-xl shadow-2xl border border-gray-200 flex flex-col z-50">
          <div className="p-4 border-b flex items-center justify-between bg-gradient-to-r from-blue-600 to-indigo-600 text-white rounded-t-xl">
            <h3 className="font-semibold">Visualization Assistant</h3>
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
                >
                  Clear
                </Button>
              )}
              <Button
                onClick={() => setShowChat(false)}
                variant="ghost"
                size="sm"
                className="text-white hover:bg-white/20"
              >
                <X className="w-4 h-4" />
              </Button>
            </div>
          </div>
          
          <div className="flex-1 overflow-y-auto p-4 space-y-3">
            {chatMessages.length === 0 && (
              <div className="text-center text-gray-500 mt-8">
                <MessageSquare className="w-12 h-12 mx-auto mb-3 text-gray-400" />
                <p className="text-sm">Ask me to create custom charts!</p>
                <ul className="text-xs mt-2 space-y-1">
                  <li>• "Create a scatter plot"</li>
                  <li>• "Show me a pie chart"</li>
                  <li>• "Generate a bar chart"</li>
                </ul>
              </div>
            )}
            {chatMessages.map((msg, idx) => (
              <div key={idx} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                <div className={`max-w-[80%] ${
                  msg.role === 'user' 
                    ? 'bg-blue-600 text-white p-3 rounded-lg' 
                    : 'bg-gray-100 text-gray-800 p-3 rounded-lg'
                }`}>
                  <p className="text-sm whitespace-pre-wrap">{msg.content}</p>
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
                onKeyPress={(e) => e.key === 'Enter' && handleChatSend()}
                placeholder="Ask for custom charts..."
                disabled={chatLoading}
                className="flex-1"
              />
              <Button onClick={handleChatSend} disabled={chatLoading || !chatInput.trim()}>
                <Send className="w-4 h-4" />
              </Button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default VisualizationPanel;
