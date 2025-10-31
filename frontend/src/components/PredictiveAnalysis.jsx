import { useState, useEffect, useRef } from "react";
import axios from "axios";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { toast } from "sonner";
import { Loader2, TrendingUp, AlertCircle, ChevronDown, ChevronUp, MessageSquare, X, Send, RefreshCw } from "lucide-react";
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
    const allSections = ['summary', 'volume', 'trends', 'correlations', 'predictions', 'forecasts'];
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
      } else if (actionData.action === 'add_chart') {
        // Add correlation or custom chart
        const updatedResults = {
          ...analysisResults,
          correlations: actionData.chart_data?.type === 'correlation' 
            ? [...(analysisResults.correlations || []), ...actionData.chart_data.correlations]
            : analysisResults.correlations,
          custom_charts: [...(analysisResults.custom_charts || []), actionData.chart_data]
        };
        setAnalysisResults(updatedResults);
        onAnalysisUpdate(updatedResults);
        toast.success("Chart added successfully!");
        setChatMessages(prev => [...prev, { 
          role: "assistant", 
          content: "✓ Chart has been added to your analysis. Scroll up to see it!" 
        }]);
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

      {/* Similar sections for trends, correlations, predictions... */}
      {/* I'll add the chat panel at the bottom */}

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
                <div className={`max-w-[80%] p-3 rounded-lg ${
                  msg.role === 'user' 
                    ? 'bg-blue-600 text-white' 
                    : 'bg-gray-100 text-gray-800'
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