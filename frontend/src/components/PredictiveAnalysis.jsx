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
  const [analysisResults, setAnalysisResults] = useState(null);
  const [hasAnalyzed, setHasAnalyzed] = useState(false);

  // Auto-run analysis only once on mount
  useEffect(() => {
    if (dataset && !hasAnalyzed) {
      runHolisticAnalysis();
    }
  }, [dataset, hasAnalyzed]);

  const runHolisticAnalysis = async () => {
    setLoading(true);
    toast.info("Running comprehensive dataset analysis...");
    
    try {
      const response = await axios.post(`${API}/analysis/holistic`, {
        dataset_id: dataset.id
      });

      setAnalysisResults(response.data);
      setHasAnalyzed(true);
      toast.success("Comprehensive analysis complete!");
    } catch (error) {
      toast.error("Analysis failed: " + (error.response?.data?.detail || error.message));
    } finally {
      setLoading(false);
    }
  };

  const refreshAnalysis = () => {
    setHasAnalyzed(false);
    setAnalysisResults(null);
    runHolisticAnalysis();
  };

  if (loading && !analysisResults) {
    return (
      <div className="flex items-center justify-center py-12" data-testid="predictive-analysis">
        <Loader2 className="w-8 h-8 animate-spin text-blue-600" />
        <span className="ml-3 text-lg">Analyzing entire dataset with AI/ML models...</span>
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

  return (
    <div className="space-y-6" data-testid="predictive-analysis">
      {/* Header with Refresh */}
      <Card className="p-6 bg-gradient-to-br from-indigo-50 to-purple-50 border-indigo-200">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h3 className="text-xl font-semibold flex items-center gap-2">
              <TrendingUp className="w-6 h-6 text-indigo-600" />
              Comprehensive Predictive Analytics
            </h3>
            <p className="text-sm text-gray-600 mt-2">
              AI-powered holistic analysis of your entire dataset with intelligent groupings and predictions
            </p>
          </div>
          <Button
            data-testid="refresh-analysis-btn"
            onClick={refreshAnalysis}
            disabled={loading}
            variant="outline"
          >
            {loading ? <Loader2 className="w-4 h-4 animate-spin mr-2" /> : <TrendingUp className="w-4 h-4 mr-2" />}
            Refresh Analysis
          </Button>
        </div>
      </Card>

      {/* Analysis Results */}
      {analysisResults.volume_analysis && (
        <Card className="p-6">
          <h3 className="text-lg font-semibold mb-4">📊 Volume Analysis</h3>
          <div className="space-y-4">
            {analysisResults.volume_analysis.by_dimensions?.map((item, idx) => (
              <div key={idx} className="p-4 bg-blue-50 rounded-lg border border-blue-200">
                <h4 className="font-semibold mb-2">{item.dimension}</h4>
                <p className="text-sm text-gray-700">{item.insights}</p>
                {item.chart && <div className="mt-3 h-64 bg-white rounded p-2" id={`chart-volume-${idx}`}></div>}
              </div>
            ))}
          </div>
        </Card>
      )}

      {/* Trend Analysis */}
      {analysisResults.trend_analysis && (
        <Card className="p-6">
          <h3 className="text-lg font-semibold mb-4">📈 Trend Analysis</h3>
          <div className="grid md:grid-cols-2 gap-4">
            {analysisResults.trend_analysis.trends?.map((trend, idx) => (
              <div key={idx} className="p-4 bg-green-50 rounded-lg border border-green-200">
                <h4 className="font-semibold mb-2">{trend.category}</h4>
                <p className="text-sm text-gray-700">{trend.insight}</p>
                <div className="mt-2 text-xs text-gray-600">
                  Trend: <span className="font-semibold">{trend.direction}</span>
                </div>
              </div>
            ))}
          </div>
        </Card>
      )}

      {/* Correlations */}
      {analysisResults.correlations && (
        <Card className="p-6">
          <h3 className="text-lg font-semibold mb-4">🔗 Key Correlations</h3>
          <div className="space-y-3">
            {analysisResults.correlations.map((corr, idx) => (
              <div key={idx} className="flex items-center gap-3 p-3 bg-purple-50 rounded-lg border border-purple-200">
                <div className="flex-1">
                  <p className="font-medium">{corr.feature1} ↔ {corr.feature2}</p>
                  <p className="text-sm text-gray-600">{corr.interpretation}</p>
                </div>
                <div className="text-right">
                  <div className="text-2xl font-bold text-purple-600">{corr.value.toFixed(2)}</div>
                  <div className="text-xs text-gray-500">{corr.strength}</div>
                </div>
              </div>
            ))}
          </div>
        </Card>
      )}

      {/* Predictions */}
      {analysisResults.predictions && (
        <Card className="p-6">
          <h3 className="text-lg font-semibold mb-4">🎯 Predictive Insights</h3>
          <div className="space-y-4">
            {analysisResults.predictions.map((pred, idx) => (
              <div key={idx} className="p-4 bg-orange-50 rounded-lg border border-orange-200">
                <h4 className="font-semibold mb-2">{pred.title}</h4>
                <p className="text-sm text-gray-700 mb-3">{pred.description}</p>
                <div className="grid grid-cols-3 gap-3">
                  <div className="text-center p-2 bg-white rounded">
                    <div className="text-xs text-gray-600">Model Accuracy</div>
                    <div className="text-lg font-bold text-green-600">{(pred.accuracy * 100).toFixed(1)}%</div>
                  </div>
                  <div className="text-center p-2 bg-white rounded">
                    <div className="text-xs text-gray-600">Confidence</div>
                    <div className="text-lg font-bold text-blue-600">{pred.confidence}</div>
                  </div>
                  <div className="text-center p-2 bg-white rounded">
                    <div className="text-xs text-gray-600">Risk Level</div>
                    <div className="text-lg font-bold text-orange-600">{pred.risk_level}</div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </Card>
      )}

      {/* AI Summary */}
      {analysisResults.ai_summary && (
        <Card className="p-6 bg-gradient-to-br from-purple-50 to-blue-50 border-purple-200">
          <h3 className="text-lg font-semibold mb-3 flex items-center gap-2">
            <AlertCircle className="w-5 h-5 text-purple-600" />
            AI-Generated Summary
          </h3>
          <div className="prose prose-sm max-w-none">
            <p className="whitespace-pre-wrap text-gray-700">{analysisResults.ai_summary}</p>
          </div>
        </Card>
      )}
    </div>
  );
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