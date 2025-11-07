import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Brain, Sparkles, Settings, CheckCircle2, Circle } from 'lucide-react';
import { toast } from 'sonner';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

/**
 * ModelSelector Component
 * Supports 3 selection modes:
 * - Auto: System selects best models
 * - AI Recommendations: Azure OpenAI recommends models
 * - Manual: User selects specific models
 */
const ModelSelector = ({ 
  problemType, 
  dataSummary, 
  onModelSelection,
  className = ""
}) => {
  const [selectionMode, setSelectionMode] = useState('auto'); // 'auto', 'ai', 'manual'
  const [availableModels, setAvailableModels] = useState([]);
  const [selectedModels, setSelectedModels] = useState([]);
  const [aiRecommendations, setAiRecommendations] = useState(null);
  const [loading, setLoading] = useState(false);
  const [loadingModels, setLoadingModels] = useState(false);

  // Load available models when component mounts or problem type changes
  useEffect(() => {
    // Always pre-load models for manual selection to improve UX
    if (problemType) {
      loadAvailableModels();
    }
  }, [problemType]);
  
  // Also load when switching to manual mode
  useEffect(() => {
    if (selectionMode === 'manual' && availableModels.length === 0 && problemType) {
      loadAvailableModels();
    }
  }, [selectionMode]);

  const loadAvailableModels = async () => {
    setLoadingModels(true);
    try {
      console.log(`Loading models for problem type: ${problemType}`);
      const response = await axios.get(`${API}/models/available`, {
        params: { problem_type: problemType }
      });
      console.log(`Loaded ${response.data.models.length} models:`, response.data.models);
      setAvailableModels(response.data.models);
    } catch (error) {
      console.error('Failed to load models:', error);
      toast.error('Failed to load available models');
    } finally {
      setLoadingModels(false);
    }
  };

  const getAIRecommendations = async () => {
    setLoading(true);
    try {
      const response = await axios.post(`${API}/models/recommend`, {
        problem_type: problemType,
        data_summary: dataSummary
      });
      
      setAiRecommendations(response.data);
      setSelectedModels(response.data.recommendations || []);
      toast.success('AI recommendations loaded');
    } catch (error) {
      console.error('Failed to get recommendations:', error);
      toast.error('Failed to get AI recommendations');
    } finally {
      setLoading(false);
    }
  };

  const toggleModel = (modelKey) => {
    setSelectedModels(prev => 
      prev.includes(modelKey)
        ? prev.filter(k => k !== modelKey)
        : [...prev, modelKey]
    );
  };

  const handleModeChange = (mode) => {
    setSelectionMode(mode);
    
    if (mode === 'auto') {
      setSelectedModels([]);
      setAiRecommendations(null);
      onModelSelection(null); // null means use all models
    } else if (mode === 'ai') {
      getAIRecommendations();
    } else if (mode === 'manual') {
      loadAvailableModels();
      setSelectedModels([]);
    }
  };

  const applySelection = () => {
    if (selectionMode === 'auto') {
      onModelSelection(null);
      toast.success('Using all available models');
    } else if (selectedModels.length === 0) {
      toast.error('Please select at least one model');
    } else {
      onModelSelection(selectedModels);
      toast.success(`${selectedModels.length} model(s) selected`);
    }
  };

  return (
    <Card className={`p-4 ${className}`}>
      <div className="space-y-4">
        {/* Selection Mode Buttons */}
        <div>
          <h3 className="text-sm font-semibold mb-3">Model Selection Method</h3>
          <div className="grid grid-cols-3 gap-2">
            <Button
              variant={selectionMode === 'auto' ? 'default' : 'outline'}
              size="sm"
              onClick={() => handleModeChange('auto')}
              className="flex items-center gap-2"
            >
              <Brain className="w-4 h-4" />
              <span>Auto-Select</span>
            </Button>
            
            <Button
              variant={selectionMode === 'ai' ? 'default' : 'outline'}
              size="sm"
              onClick={() => handleModeChange('ai')}
              className="flex items-center gap-2"
              disabled={loading}
            >
              <Sparkles className="w-4 h-4" />
              <span>AI Recommend</span>
            </Button>
            
            <Button
              variant={selectionMode === 'manual' ? 'default' : 'outline'}
              size="sm"
              onClick={() => handleModeChange('manual')}
              className="flex items-center gap-2"
            >
              <Settings className="w-4 h-4" />
              <span>Manual Select</span>
            </Button>
          </div>
        </div>

        {/* Mode-specific content */}
        {selectionMode === 'auto' && (
          <div className="bg-blue-50 p-3 rounded-lg">
            <p className="text-sm text-blue-800">
              <strong>Auto-Selection Active:</strong> The system will automatically select and train the best models for your data type.
              This includes all available models optimized for {problemType}.
            </p>
          </div>
        )}

        {selectionMode === 'ai' && (
          <div className="space-y-3">
            {loading ? (
              <div className="text-center py-4">
                <div className="animate-spin inline-block w-6 h-6 border-2 border-blue-600 border-t-transparent rounded-full"></div>
                <p className="text-sm text-gray-600 mt-2">Getting AI recommendations...</p>
              </div>
            ) : aiRecommendations ? (
              <div className="space-y-3">
                <div className="bg-purple-50 p-3 rounded-lg">
                  <div className="flex items-start gap-2">
                    <Sparkles className="w-5 h-5 text-purple-600 mt-0.5" />
                    <div className="flex-1">
                      <h4 className="font-semibold text-purple-900 mb-1">AI Recommendations</h4>
                      <p className="text-sm text-purple-800">{aiRecommendations.reasoning}</p>
                      <div className="mt-2 flex items-center gap-2">
                        <span className="text-xs font-medium text-purple-700">
                          Expected Performance:
                        </span>
                        <span className="px-2 py-0.5 bg-purple-200 text-purple-900 rounded text-xs font-semibold uppercase">
                          {aiRecommendations.expected_performance}
                        </span>
                      </div>
                    </div>
                  </div>
                </div>
                
                <div>
                  <p className="text-sm font-medium mb-2">Recommended Models ({selectedModels.length}):</p>
                  <div className="flex flex-wrap gap-2">
                    {selectedModels.map(modelKey => (
                      <span key={modelKey} className="px-3 py-1 bg-purple-100 text-purple-800 rounded-full text-sm font-medium">
                        {modelKey.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
                      </span>
                    ))}
                  </div>
                </div>
              </div>
            ) : null}
          </div>
        )}

        {selectionMode === 'manual' && availableModels.length > 0 && (
          <div className="space-y-3">
            <div>
              <div className="flex items-center justify-between mb-2">
                <p className="text-sm font-medium">
                  Available Models ({availableModels.length})
                </p>
                <span className="text-xs text-gray-500">
                  {selectedModels.length} selected
                </span>
              </div>
              
              <div className="max-h-64 overflow-y-auto border rounded-lg p-2 space-y-1">
                {availableModels.map(model => (
                  <div
                    key={model.key}
                    onClick={() => toggleModel(model.key)}
                    className={`flex items-start gap-3 p-2 rounded cursor-pointer transition-colors ${
                      selectedModels.includes(model.key)
                        ? 'bg-blue-50 border border-blue-200'
                        : 'hover:bg-gray-50'
                    }`}
                  >
                    {selectedModels.includes(model.key) ? (
                      <CheckCircle2 className="w-5 h-5 text-blue-600 mt-0.5 flex-shrink-0" />
                    ) : (
                      <Circle className="w-5 h-5 text-gray-400 mt-0.5 flex-shrink-0" />
                    )}
                    <div className="flex-1 min-w-0">
                      <p className="font-medium text-sm">{model.name}</p>
                      <p className="text-xs text-gray-600">{model.description}</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* Apply Button */}
        <div className="pt-2 border-t">
          <Button
            onClick={applySelection}
            className="w-full"
            disabled={selectionMode === 'manual' && selectedModels.length === 0}
          >
            {selectionMode === 'auto' 
              ? 'Use All Models' 
              : `Train with ${selectedModels.length || 0} Selected Model(s)`
            }
          </Button>
        </div>
      </div>
    </Card>
  );
};

export default ModelSelector;
