import { useState, useEffect } from "react";
import axios from "axios";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Label } from "@/components/ui/label";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { toast } from "sonner";
import { Loader2, TrendingUp, AlertCircle } from "lucide-react";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const PredictiveAnalysis = ({ dataset }) => {
  const [loading, setLoading] = useState(false);
  const [predictions, setPredictions] = useState({});
  const [activeTarget, setActiveTarget] = useState("");

  const models = [
    { key: "random_forest", name: "Random Forest", desc: "Ensemble method, highly accurate" },
    { key: "gradient_boosting", name: "Gradient Boosting", desc: "Powerful for complex patterns" },
    { key: "linear_regression", name: "Linear Regression", desc: "Fast, interpretable" },
    { key: "decision_tree", name: "Decision Tree", desc: "Visual, easy to understand" }
  ];

  // Auto-run analysis on mount
  useEffect(() => {
    const numericCols = dataset.columns.filter((col) => {
      const sample = dataset.data_preview[0]?.[col];
      return typeof sample === 'number' || !isNaN(Number(sample));
    });
    
    if (dataset && numericCols.length > 0) {
      runAutoAnalysis(numericCols);
    }
  }, [dataset]);

  const runAutoAnalysis = async (numericCols) => {
    setLoading(true);
    toast.info("Running automatic ML analysis on all numeric columns...");
    
    try {
      // Run predictions for each numeric column with best model
      for (const targetCol of numericCols) {
        // Run with Random Forest (best general-purpose model)
        const response = await axios.post(`${API}/analysis/run`, {
          dataset_id: dataset.id,
          analysis_type: "predict",
          options: { 
            target_column: targetCol,
            model_type: "random_forest"
          }
        });

        if (!response.data.error) {
          setPredictions(prev => ({
            ...prev,
            [targetCol]: {
              random_forest: response.data
            }
          }));
          
          if (!activeTarget) {
            setActiveTarget(targetCol);
          }
        }
      }
      toast.success(`Completed automated analysis for ${numericCols.length} columns!`);
    } catch (error) {
      toast.error("Auto-analysis failed: " + (error.response?.data?.detail || error.message));
    } finally {
      setLoading(false);
    }
  };

  const runModelForTarget = async (targetColumn, modelType) => {
    setLoading(true);
    try {
      const response = await axios.post(`${API}/analysis/run`, {
        dataset_id: dataset.id,
        analysis_type: "predict",
        options: { 
          target_column: targetColumn,
          model_type: modelType
        }
      });

      if (response.data.error) {
        toast.error(response.data.error);
      } else {
        setPredictions(prev => ({
          ...prev,
          [targetColumn]: {
            ...prev[targetColumn],
            [modelType]: response.data
          }
        }));
        toast.success(`${response.data.model_type} completed for ${targetColumn}!`);
      }
    } catch (error) {
      toast.error("Prediction failed: " + (error.response?.data?.detail || error.message));
    } finally {
      setLoading(false);
    }
  };

  // Numeric columns only
  const numericColumns = dataset.columns.filter((col) => {
    const sample = dataset.data_preview[0]?.[col];
    return typeof sample === 'number' || !isNaN(Number(sample));
  });

  if (loading && Object.keys(predictions).length === 0) {
    return (
      <div className="flex items-center justify-center py-12" data-testid="predictive-analysis">
        <Loader2 className="w-8 h-8 animate-spin text-blue-600" />
        <span className="ml-3 text-lg">Running automated ML analysis...</span>
      </div>
    );
  }

  return (
    <div className="space-y-6" data-testid="predictive-analysis">
      <Card className="p-6 bg-gradient-to-br from-indigo-50 to-purple-50 border-indigo-200">
        <h3 className="text-xl font-semibold mb-4 flex items-center gap-2">
          <TrendingUp className="w-6 h-6 text-indigo-600" />
          Automated Predictive Analytics
        </h3>
        <p className="text-sm text-gray-600 mb-4">
          AI automatically analyzed all {numericColumns.length} numeric columns and generated predictions. 
          Select a column below to view detailed results or run additional models for comparison.
        </p>

        {/* Column Selection */}
        {numericColumns.length > 0 && (
          <div className="space-y-4">
            <div>
              <Label>View Predictions For Column:</Label>
              <Select value={activeTarget} onValueChange={setActiveTarget}>
                <SelectTrigger data-testid="target-column-select">
                  <SelectValue placeholder="Select column" />
                </SelectTrigger>
                <SelectContent>
                  {numericColumns.map((col) => (
                    <SelectItem key={col} value={col}>
                      {col} {predictions[col] ? "✓" : ""}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            {/* Additional model buttons */}
            {activeTarget && (
              <div>
                <Label className="mb-2 block">Run Additional Models for {activeTarget}:</Label>
                <div className="grid md:grid-cols-4 gap-3">
                  {models.map((model) => (
                    <Button
                      key={model.key}
                      data-testid={`run-${model.key}-btn`}
                      onClick={() => runModelForTarget(activeTarget, model.key)}
                      disabled={loading}
                      variant={predictions[activeTarget]?.[model.key] ? "default" : "outline"}
                      className={predictions[activeTarget]?.[model.key] ? "bg-green-600 hover:bg-green-700" : ""}
                      size="sm"
                    >
                      {loading ? (
                        <Loader2 className="w-4 h-4 animate-spin mr-2" />
                      ) : predictions[activeTarget]?.[model.key] ? (
                        <span className="mr-2">✓</span>
                      ) : null}
                      {model.name}
                    </Button>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}
      </Card>

      {activeTarget && predictions[activeTarget] && (
        <>
          {/* Model Tabs for Selected Column */}
          <Card className="p-6">
            <h3 className="text-lg font-semibold mb-4">Results for: {activeTarget}</h3>
            <Tabs defaultValue={Object.keys(predictions[activeTarget])[0]}>
              <TabsList className="grid w-full grid-cols-4 mb-6">
                {models.map((model) => (
                  <TabsTrigger 
                    key={model.key} 
                    value={model.key}
                    disabled={!predictions[activeTarget]?.[model.key]}
                    data-testid={`tab-${model.key}`}
                  >
                    {model.name}
                  </TabsTrigger>
                ))}
              </TabsList>

              {models.map((model) => (
                <TabsContent key={model.key} value={model.key}>
                  {predictions[activeTarget]?.[model.key] && (
                    <ModelResults prediction={predictions[activeTarget][model.key]} maxDisplay={30} />
                  )}
                </TabsContent>
              ))}
            </Tabs>
          </Card>
        </>
      )}
    </div>
  );
};
};

// Separate component for model results
const ModelResults = ({ prediction, maxDisplay }) => {
  const displayData = prediction?.predictions?.slice(0, maxDisplay) || [];
  const displayActuals = prediction?.actuals?.slice(0, maxDisplay) || [];

  return (
    <div className="space-y-6">
      {/* Model Performance */}
      <div className="grid md:grid-cols-3 gap-4">
        <div className="p-4 bg-blue-50 rounded-lg border border-blue-200">
          <p className="text-sm text-gray-600 mb-1">Model Type</p>
          <p className="font-semibold">{prediction.model_type}</p>
        </div>
        <div className="p-4 bg-green-50 rounded-lg border border-green-200">
          <p className="text-sm text-gray-600 mb-1">Training Score (R²)</p>
          <p className="text-2xl font-bold text-green-600">
            {(prediction.train_score * 100).toFixed(1)}%
          </p>
        </div>
        <div className="p-4 bg-purple-50 rounded-lg border border-purple-200">
          <p className="text-sm text-gray-600 mb-1">Test Score (R²)</p>
          <p className="text-2xl font-bold text-purple-600">
            {(prediction.test_score * 100).toFixed(1)}%
          </p>
        </div>
      </div>

      {prediction.test_score < 0.5 && (
        <div className="p-4 bg-yellow-50 border border-yellow-200 rounded-lg flex items-start gap-3">
          <AlertCircle className="w-5 h-5 text-yellow-600 mt-0.5" />
          <div className="text-sm text-yellow-800">
            <p className="font-medium">Low Model Accuracy</p>
            <p>Consider: adding more features, collecting more data, or trying a different model.</p>
          </div>
        </div>
      )}

      {/* Feature Importance */}
      {Object.keys(prediction.feature_importance || {}).length > 0 && (
        <div>
          <h4 className="text-lg font-semibold mb-4">Feature Importance</h4>
          <div className="space-y-3">
            {Object.entries(prediction.feature_importance)
              .slice(0, 10)
              .map(([feature, importance], idx) => (
                <div key={idx} className="flex items-center gap-3">
                  <span className="text-sm font-medium w-40 truncate">{feature}</span>
                  <div className="flex-1 h-6 bg-gray-200 rounded-full overflow-hidden">
                    <div
                      className="h-full bg-gradient-to-r from-blue-500 to-indigo-500 transition-all"
                      style={{ width: `${importance * 100}%` }}
                    />
                  </div>
                  <span className="text-sm text-gray-600 w-16 text-right">
                    {(importance * 100).toFixed(1)}%
                  </span>
                </div>
              ))}
          </div>
        </div>
      )}

      {/* Prediction Chart */}
      <div>
        <h4 className="text-lg font-semibold mb-4">Predictions vs Actual Values (First {maxDisplay} samples)</h4>
        <div className="relative h-96 bg-gray-50 rounded-lg p-4">
          <svg viewBox="0 0 800 300" className="w-full h-full">
            {[0, 1, 2, 3, 4].map((i) => (
              <line
                key={`grid-${i}`}
                x1="50"
                y1={50 + i * 50}
                x2="750"
                y2={50 + i * 50}
                stroke="#e5e7eb"
                strokeWidth="1"
              />
            ))}
            
            {displayData.length > 0 && (() => {
              const minVal = Math.min(...displayActuals, ...displayData);
              const maxVal = Math.max(...displayActuals, ...displayData);
              const range = maxVal - minVal || 1;
              const xStep = 700 / (displayData.length - 1 || 1);
              
              const normalize = (val) => 250 - ((val - minVal) / range) * 200;
              
              return (
                <>
                  <polyline
                    points={displayActuals.map((val, idx) => 
                      `${50 + idx * xStep},${normalize(val)}`
                    ).join(' ')}
                    fill="none"
                    stroke="#3b82f6"
                    strokeWidth="2"
                  />
                  <polyline
                    points={displayData.map((val, idx) => 
                      `${50 + idx * xStep},${normalize(val)}`
                    ).join(' ')}
                    fill="none"
                    stroke="#8b5cf6"
                    strokeWidth="2"
                    strokeDasharray="5,5"
                  />
                  <g transform="translate(600, 20)">
                    <line x1="0" y1="0" x2="30" y2="0" stroke="#3b82f6" strokeWidth="2" />
                    <text x="35" y="5" fontSize="12" fill="#374151">Actual</text>
                  </g>
                  <g transform="translate(600, 40)">
                    <line x1="0" y1="0" x2="30" y2="0" stroke="#8b5cf6" strokeWidth="2" strokeDasharray="5,5" />
                    <text x="35" y="5" fontSize="12" fill="#374151">Predicted</text>
                  </g>
                </>
              );
            })()}
          </svg>
        </div>
      </div>
    </div>
  );
};

export default PredictiveAnalysis;