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
  const [problemType, setProblemType] = useState("auto"); // "auto", "regression", "classification", "time_series", "clustering", "dimensionality", "anomaly"
  const [timeColumn, setTimeColumn] = useState(""); // For time series
  const [userExpectation, setUserExpectation] = useState(""); // NEW: User's prediction expectation/context

  useEffect(() => {
    // Auto-select first numeric column as potential target
    if (dataset && dataset.dtypes) {
      const numericCols = Object.keys(dataset.dtypes).filter(
        col => ['int64', 'float64', 'int32', 'float32'].includes(dataset.dtypes[col])
      );
      if (numericCols.length > 0 && !targetVariables[0].target) {
        setTargetVariables([{ target: numericCols[0], features: [] }]);
      }
      
      // Auto-populate user expectation if dataset has stored expectation
      if (dataset.last_user_expectation && !userExpectation) {
        setUserExpectation(dataset.last_user_expectation);
        console.log('📝 Auto-populated user expectation from dataset:', dataset.last_user_expectation);
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
    
    console.log('targetVariables:', targetVariables);
    console.log('validTargets:', validTargets);
    
    if (validTargets.length === 0) {
      toast.error("Please select at least one target with features");
      return;
    }

    // Check if time series requires time column
    if (problemType === "time_series" && !timeColumn) {
      toast.error("Please select a time/date column for time series analysis");
      return;
    }

    // Check if multiple targets
    if (validTargets.length === 1) {
      // Single target - backward compatible format
      const selection = {
        target: validTargets[0].target,
        features: validTargets[0].features,
        mode: mode,
        problem_type: problemType,
        time_column: problemType === "time_series" ? timeColumn : undefined,
        aiSuggestions: aiSuggestions,
        user_expectation: userExpectation || null  // NEW: User's prediction context
      };
      console.log('Confirming single target selection:', selection);
      onConfirm(selection);
    } else {
      // Multiple targets - new format
      const selection = {
        targets: validTargets,
        mode: mode,
        problem_type: problemType,
        is_multi_target: true,
        user_expectation: userExpectation || null  // NEW: User's prediction context
      };
      console.log('Confirming multi-target selection:', selection);
      onConfirm(selection);
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
  
  // Filter columns based on problem type
  let targetColumns = [];
  if (problemType === "regression" || problemType === "auto") {
    // Numeric columns for regression
    targetColumns = availableColumns.filter(col => {
      const dtype = dataset.dtypes?.[col];
      return dtype && ['int64', 'float64', 'int32', 'float32'].includes(dtype);
    });
  } else if (problemType === "classification") {
    // All columns for classification (categorical + numeric with few unique values)
    targetColumns = availableColumns;
  } else if (problemType === "time_series") {
    // Numeric columns for time series
    targetColumns = availableColumns.filter(col => {
      const dtype = dataset.dtypes?.[col];
      return dtype && ['int64', 'float64', 'int32', 'float32'].includes(dtype);
    });
  }
  
  const numericColumns = targetColumns;

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

        {/* NEW: User Expectation / Context Input with Domain Guidance */}
        <div className="mb-6 p-4 bg-gradient-to-r from-indigo-50 to-purple-50 rounded-lg border-2 border-indigo-200">
          <Label className="text-lg font-semibold mb-2 block flex items-center gap-2">
            <Info className="w-5 h-5 text-indigo-600" />
            💭 What are you trying to predict? (Recommended)
          </Label>
          <p className="text-sm text-gray-600 mb-3">
            <strong>Format:</strong> Domain: Your prediction goal
          </p>
          
          {/* Example Prompts Section */}
          <div className="mb-3 p-3 bg-white rounded-lg border border-indigo-200">
            <p className="text-xs font-semibold text-indigo-800 mb-2">📋 Example Prompts (Click to use):</p>
            <div className="space-y-1">
              {[
                "Food: Predict the price and revenue for 2026",
                "IT - Investment Banking: Predict the trade latency of E2E for the client/product wise",
                "E-commerce: Predict customer churn to improve retention strategies",
                "Healthcare: Predict patient readmission rates for resource planning",
                "Finance: Predict stock price volatility for risk management",
                "Payments: Detect fraudulent transactions to minimize losses",
                "Logistics: Predict delivery delays for capacity optimization"
              ].map((example, idx) => (
                <button
                  key={idx}
                  onClick={() => setUserExpectation(example)}
                  className="text-xs text-left w-full p-2 hover:bg-indigo-50 rounded transition-colors text-gray-700"
                >
                  • {example}
                </button>
              ))}
            </div>
          </div>
          
          <textarea
            value={userExpectation}
            onChange={(e) => setUserExpectation(e.target.value)}
            placeholder="Domain: Your prediction goal (e.g., 'IT: Predict system latency for performance optimization')"
            className="w-full p-3 border-2 border-indigo-300 rounded-lg focus:border-indigo-500 focus:ring-2 focus:ring-indigo-200 transition-all resize-none"
            rows={3}
          />
          <p className="text-xs text-indigo-700 mt-2 mb-3">
            💡 <strong>Tip:</strong> Start with your domain (IT, Finance, Healthcare, etc.) followed by your specific prediction goal. 
            This helps AI generate domain-specific insights with appropriate terminology.
          </p>
          
          {/* Smart Selection Button */}
          {userExpectation && userExpectation.length > 10 && (
            <Button
              onClick={async () => {
                setLoading(true);
                try {
                  const response = await axios.post(`${API}/analysis/suggest-from-expectation`, {
                    dataset_id: dataset.id,
                    user_expectation: userExpectation
                  });
                  
                  if (response.data.success) {
                    const suggestions = response.data.suggestions;
                    
                    // Auto-populate target and features
                    if (suggestions.suggested_target) {
                      updateTargetVariable(activeTargetIndex, 'target', suggestions.suggested_target);
                    }
                    if (suggestions.suggested_features && suggestions.suggested_features.length > 0) {
                      updateTargetVariable(activeTargetIndex, 'features', suggestions.suggested_features);
                    }
                    if (suggestions.problem_type) {
                      setProblemType(suggestions.problem_type);
                    }
                    
                    // Store suggestions for display
                    setAiSuggestions({
                      ...suggestions,
                      from_expectation: true
                    });
                    
                    toast.success(`🧠 AI suggested: ${suggestions.suggested_target} with ${suggestions.suggested_features?.length || 0} features`);
                  }
                } catch (error) {
                  console.error("Smart selection error:", error);
                  toast.error("Failed to get AI suggestions: " + (error.response?.data?.detail || error.message));
                } finally {
                  setLoading(false);
                }
              }}
              disabled={loading}
              variant="outline"
              className="w-full bg-white border-indigo-400 hover:bg-indigo-50 text-indigo-700"
            >
              {loading ? (
                <>
                  <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                  Getting AI Suggestions...
                </>
              ) : (
                <>
                  <Sparkles className="w-4 h-4 mr-2" />
                  🧠 Get AI Suggestions (Smart Selection)
                </>
              )}
            </Button>
          )}
          
          {/* Show AI suggestions explanation if available */}
          {aiSuggestions?.from_expectation && (
            <div className="mt-3 p-3 bg-white rounded-lg border border-indigo-300">
              <p className="text-xs font-semibold text-indigo-800 mb-1">
                ✨ AI Suggestions ({aiSuggestions.confidence} confidence)
              </p>
              <p className="text-xs text-gray-700">{aiSuggestions.explanation}</p>
            </div>
          )}
        </div>

        {/* Problem Type Selection - ALL 7 CATEGORIES */}
        <div className="mb-6">
          <Label className="text-lg font-semibold mb-3 block">
            🎯 Problem Type (7 Categories Available)
          </Label>
          <div className="grid md:grid-cols-4 gap-3 mb-3">
            <Card
              className={`p-3 cursor-pointer border-2 transition-all ${
                problemType === "auto" ? "border-blue-500 bg-blue-50" : "border-gray-200"
              }`}
              onClick={() => setProblemType("auto")}
            >
              <h3 className="font-semibold text-sm">🔍 Auto-Detect</h3>
              <p className="text-xs text-gray-600 mt-1">Let AI decide</p>
            </Card>
            
            <Card
              className={`p-3 cursor-pointer border-2 transition-all ${
                problemType === "regression" ? "border-green-500 bg-green-50" : "border-gray-200"
              }`}
              onClick={() => setProblemType("regression")}
            >
              <h3 className="font-semibold text-sm">📈 Regression</h3>
              <p className="text-xs text-gray-600 mt-1">Predict numbers (13 models)</p>
            </Card>
            
            <Card
              className={`p-3 cursor-pointer border-2 transition-all ${
                problemType === "classification" ? "border-purple-500 bg-purple-50" : "border-gray-200"
              }`}
              onClick={() => setProblemType("classification")}
            >
              <h3 className="font-semibold text-sm">🏷️ Classification</h3>
              <p className="text-xs text-gray-600 mt-1">Predict categories (11 models)</p>
            </Card>
            
            <Card
              className={`p-3 cursor-pointer border-2 transition-all ${
                problemType === "time_series" ? "border-orange-500 bg-orange-50" : "border-gray-200"
              }`}
              onClick={() => setProblemType("time_series")}
            >
              <h3 className="font-semibold text-sm">⏰ Time Series</h3>
              <p className="text-xs text-gray-600 mt-1">Forecast trends</p>
            </Card>
          </div>
          
          {/* Row 2: New Problem Types */}
          <div className="grid md:grid-cols-3 gap-3">
            <Card
              className={`p-3 cursor-pointer border-2 transition-all ${
                problemType === "clustering" ? "border-pink-500 bg-pink-50" : "border-gray-200"
              }`}
              onClick={() => setProblemType("clustering")}
            >
              <h3 className="font-semibold text-sm">🔗 Clustering</h3>
              <p className="text-xs text-gray-600 mt-1">Group similar data (5 models)</p>
            </Card>
            
            <Card
              className={`p-3 cursor-pointer border-2 transition-all ${
                problemType === "dimensionality" ? "border-indigo-500 bg-indigo-50" : "border-gray-200"
              }`}
              onClick={() => setProblemType("dimensionality")}
            >
              <h3 className="font-semibold text-sm">📊 Dimensionality</h3>
              <p className="text-xs text-gray-600 mt-1">Reduce dimensions (3 models)</p>
            </Card>
            
            <Card
              className={`p-3 cursor-pointer border-2 transition-all ${
                problemType === "anomaly" ? "border-red-500 bg-red-50" : "border-gray-200"
              }`}
              onClick={() => setProblemType("anomaly")}
            >
              <h3 className="font-semibold text-sm">🚨 Anomaly Detection</h3>
              <p className="text-xs text-gray-600 mt-1">Find outliers (3 models)</p>
            </Card>
          </div>
        </div>

        {/* Time Column Selection (only for time series) */}
        {problemType === "time_series" && (
          <div className="mb-6">
            <Label className="text-lg font-semibold mb-2 block">
              📅 Select Time/Date Column
            </Label>
            <select
              className="w-full p-2 border rounded"
              value={timeColumn}
              onChange={(e) => setTimeColumn(e.target.value)}
            >
              <option value="">-- Select Time Column --</option>
              {availableColumns.map(col => (
                <option key={col} value={col}>{col}</option>
              ))}
            </select>
            <p className="text-sm text-gray-600 mt-1">
              Select the column containing dates or timestamps
            </p>
          </div>
        )}

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
            disabled={targetVariables.every(tv => !tv.target || tv.features.length === 0)}
          >
            <Check className="w-4 h-4 mr-2" />
            Confirm Selection ({targetVariables.filter(tv => tv.target && tv.features.length > 0).length} target{targetVariables.filter(tv => tv.target && tv.features.length > 0).length !== 1 ? 's' : ''})
          </Button>
        </div>
      </Card>
    </div>
  );
};

export default VariableSelectionModal;
