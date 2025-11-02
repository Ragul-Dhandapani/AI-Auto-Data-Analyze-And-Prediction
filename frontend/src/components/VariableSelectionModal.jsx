import { useState, useEffect } from "react";
import axios from "axios";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Label } from "@/components/ui/label";
import { toast } from "sonner";
import { X, Brain, Hand, Sparkles, Loader2, Check, Info } from "lucide-react";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const VariableSelectionModal = ({ dataset, onClose, onConfirm }) => {
  const [mode, setMode] = useState("manual"); // "manual", "ai", "hybrid"
  const [loading, setLoading] = useState(false);
  const [targetVariables, setTargetVariables] = useState([{ target: "", features: [] }]); // Support multiple targets
  const [aiSuggestions, setAiSuggestions] = useState(null);
  const [showExplanations, setShowExplanations] = useState(false);
  const [activeTargetIndex, setActiveTargetIndex] = useState(0);

  useEffect(() => {
    // Auto-select first numeric column as potential target
    if (dataset && dataset.dtypes) {
      const numericCols = Object.keys(dataset.dtypes).filter(
        col => ['int64', 'float64', 'int32', 'float32'].includes(dataset.dtypes[col])
      );
      if (numericCols.length > 0 && !targetVariables[0].target) {
        setTargetVariables([{ target: numericCols[0], features: [] }]);
      }
    }
  }, [dataset]);

  const addTargetVariable = () => {
    setTargetVariables([...targetVariables, { target: "", features: [] }]);
    setActiveTargetIndex(targetVariables.length);
  };

  const removeTargetVariable = (index) => {
    if (targetVariables.length > 1) {
      const updated = targetVariables.filter((_, i) => i !== index);
      setTargetVariables(updated);
      if (activeTargetIndex >= updated.length) {
        setActiveTargetIndex(updated.length - 1);
      }
    }
  };

  const updateTargetVariable = (index, field, value) => {
    const updated = [...targetVariables];
    updated[index] = { ...updated[index], [field]: value };
    setTargetVariables(updated);
  };

  const fetchAISuggestions = async () => {
    const currentTarget = targetVariables[activeTargetIndex].target;
    if (!currentTarget) {
      toast.error("Please select a target variable first");
      return;
    }

    setLoading(true);
    try {
      const response = await axios.post(`${API}/datasource/suggest-features`, {
        dataset_id: dataset.id,
        target_column: currentTarget,
        top_n: 10
      });

      setAiSuggestions(response.data);
      
      // Auto-select suggested features in hybrid mode
      if (mode === "hybrid" || mode === "ai") {
        const suggestedFeatureNames = response.data.suggested_features.map(f => f.feature);
        updateTargetVariable(activeTargetIndex, 'features', suggestedFeatureNames);
      }

      toast.success(`AI suggested ${response.data.suggested_features.length} features`);
    } catch (error) {
      console.error("Error fetching AI suggestions:", error);
      toast.error("Failed to get AI suggestions: " + (error.response?.data?.detail || error.message));
    } finally {
      setLoading(false);
    }
  };

  const handleFeatureToggle = (feature) => {
    const currentFeatures = targetVariables[activeTargetIndex].features;
    const updated = currentFeatures.includes(feature)
      ? currentFeatures.filter(f => f !== feature)
      : [...currentFeatures, feature];
    updateTargetVariable(activeTargetIndex, 'features', updated);
  };

  const handleConfirm = () => {
    // Validate all targets
    const validTargets = targetVariables.filter(tv => tv.target && tv.features.length > 0);
    
    if (validTargets.length === 0) {
      toast.error("Please select at least one target with features");
      return;
    }

    // Check if multiple targets
    if (validTargets.length === 1) {
      // Single target - backward compatible format
      onConfirm({
        target: validTargets[0].target,
        features: validTargets[0].features,
        mode: mode,
        aiSuggestions: aiSuggestions
      });
    } else {
      // Multiple targets - new format
      onConfirm({
        targets: validTargets,
        mode: mode,
        is_multi_target: true
      });
    }
  };

  const handleSkip = () => {
    // User wants to proceed without variable selection
    onConfirm({
      target: null,
      features: [],
      mode: "skip"
    });
  };

  if (!dataset) return null;

  const availableColumns = dataset.columns || [];
  const numericColumns = availableColumns.filter(col => {
    const dtype = dataset.dtypes?.[col];
    return dtype && ['int64', 'float64', 'int32', 'float32'].includes(dtype);
  });

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <Card className="w-full max-w-4xl max-h-[90vh] overflow-y-auto p-6">
        <div className="flex justify-between items-start mb-6">
          <div>
            <h2 className="text-2xl font-bold">🎯 Select Target Variables & Features</h2>
            <p className="text-gray-600 mt-1">
              Choose how you'd like to select variables for prediction and analysis
            </p>
          </div>
          <Button variant="ghost" size="icon" onClick={onClose}>
            <X className="w-5 h-5" />
          </Button>
        </div>

        {/* Mode Selection */}
        <div className="grid md:grid-cols-3 gap-4 mb-6">
          <Card
            className={`p-4 cursor-pointer border-2 transition-all ${
              mode === "manual" ? "border-blue-500 bg-blue-50" : "border-gray-200"
            }`}
            onClick={() => setMode("manual")}
          >
            <Hand className="w-8 h-8 text-blue-600 mb-2" />
            <h3 className="font-semibold mb-1">✅ Manual Selection</h3>
            <p className="text-sm text-gray-600">
              Choose target and features yourself with checkboxes
            </p>
          </Card>

          <Card
            className={`p-4 cursor-pointer border-2 transition-all ${
              mode === "ai" ? "border-purple-500 bg-purple-50" : "border-gray-200"
            }`}
            onClick={() => setMode("ai")}
          >
            <Brain className="w-8 h-8 text-purple-600 mb-2" />
            <h3 className="font-semibold mb-1">🤖 AI-Suggested</h3>
            <p className="text-sm text-gray-600">
              Let AI analyze and suggest best features automatically
            </p>
          </Card>

          <Card
            className={`p-4 cursor-pointer border-2 transition-all ${
              mode === "hybrid" ? "border-green-500 bg-green-50" : "border-gray-200"
            }`}
            onClick={() => setMode("hybrid")}
          >
            <Sparkles className="w-8 h-8 text-green-600 mb-2" />
            <h3 className="font-semibold mb-1">🔄 Hybrid</h3>
            <p className="text-sm text-gray-600">
              AI suggests, you review and adjust the selection
            </p>
          </Card>
        </div>

        {/* Target Variables Selection - Support Multiple */}
        <div className="mb-6">
          <div className="flex justify-between items-center mb-2">
            <Label className="text-lg font-semibold">
              1️⃣ Select Target Variables (What to Predict)
            </Label>
            <Button
              onClick={addTargetVariable}
              variant="outline"
              size="sm"
              className="text-xs"
            >
              + Add Another Target
            </Button>
          </div>
          
          {/* Target Tabs */}
          <div className="flex gap-2 mb-3 overflow-x-auto">
            {targetVariables.map((tv, idx) => (
              <div key={idx} className="flex items-center gap-1">
                <Button
                  onClick={() => setActiveTargetIndex(idx)}
                  variant={activeTargetIndex === idx ? "default" : "outline"}
                  size="sm"
                  className="whitespace-nowrap"
                >
                  Target {idx + 1} {tv.target && `(${tv.target})`}
                </Button>
                {targetVariables.length > 1 && (
                  <Button
                    onClick={() => removeTargetVariable(idx)}
                    variant="ghost"
                    size="icon"
                    className="h-8 w-8"
                  >
                    <X className="w-4 h-4" />
                  </Button>
                )}
              </div>
            ))}
          </div>
          
          {/* Active Target Selection */}
          <select
            className="w-full p-2 border rounded"
            value={targetVariables[activeTargetIndex].target}
            onChange={(e) => updateTargetVariable(activeTargetIndex, 'target', e.target.value)}
          >
            <option value="">-- Select Target Variable {activeTargetIndex + 1} --</option>
            {numericColumns.map(col => (
              <option key={col} value={col}>{col}</option>
            ))}
          </select>
          {numericColumns.length === 0 && (
            <p className="text-sm text-amber-600 mt-1">
              ⚠️ No numeric columns found for prediction target
            </p>
          )}
        </div>

        {/* AI Suggestion Button */}
        {(mode === "ai" || mode === "hybrid") && targetVariables[activeTargetIndex].target && (
          <div className="mb-6">
            <Button
              onClick={fetchAISuggestions}
              disabled={loading}
              className="w-full"
            >
              {loading ? (
                <><Loader2 className="w-4 h-4 animate-spin mr-2" /> Analyzing Features...</>
              ) : (
                <><Brain className="w-4 h-4 mr-2" /> Get AI Feature Suggestions</>
              )}
            </Button>
          </div>
        )}

        {/* Feature Selection */}
        <div className="mb-6">
          <div className="flex justify-between items-center mb-2">
            <Label className="text-lg font-semibold">
              2️⃣ Select Features for Target {activeTargetIndex + 1} (Predictors)
            </Label>
            {aiSuggestions && (
              <Button
                variant="outline"
                size="sm"
                onClick={() => setShowExplanations(!showExplanations)}
              >
                <Info className="w-4 h-4 mr-1" />
                {showExplanations ? "Hide" : "Show"} Explanations
              </Button>
            )}
          </div>

          <div className="max-h-96 overflow-y-auto border rounded p-4">
            {availableColumns
              .filter(col => col !== targetVariables[activeTargetIndex].target)
              .map(col => {
                const suggestion = aiSuggestions?.suggested_features?.find(s => s.feature === col);
                const isSelected = targetVariables[activeTargetIndex].features.includes(col);

                return (
                  <div key={col} className="mb-3">
                    <div className="flex items-start space-x-2">
                      <input
                        type="checkbox"
                        id={`feature-${col}`}
                        checked={isSelected}
                        onChange={() => handleFeatureToggle(col)}
                        className="mt-1"
                        disabled={mode === "ai" && loading}
                      />
                      <div className="flex-1">
                        <Label htmlFor={`feature-${col}`} className="cursor-pointer">
                          <span className="font-medium">{col}</span>
                          {suggestion && (
                            <span className="ml-2 text-xs bg-purple-100 text-purple-700 px-2 py-1 rounded">
                              AI Score: {(suggestion.combined_score * 100).toFixed(1)}%
                            </span>
                          )}
                        </Label>
                        
                        {showExplanations && suggestion && (
                          <p className="text-sm text-gray-600 mt-1 pl-6">
                            💡 {suggestion.explanation}
                          </p>
                        )}
                      </div>
                    </div>
                  </div>
                );
              })}
          </div>

          <p className="text-sm text-gray-600 mt-2">
            Selected: {targetVariables[activeTargetIndex].features.length} feature(s) for Target {activeTargetIndex + 1}
          </p>
        </div>

        {/* Action Buttons */}
        <div className="flex gap-3">
          <Button
            onClick={handleSkip}
            variant="outline"
            className="flex-1"
          >
            Skip (Use All Columns)
          </Button>
          <Button
            onClick={handleConfirm}
            className="flex-1"
            disabled={!targetVariable || selectedFeatures.length === 0}
          >
            <Check className="w-4 h-4 mr-2" />
            Confirm Selection
          </Button>
        </div>
      </Card>
    </div>
  );
};

export default VariableSelectionModal;
