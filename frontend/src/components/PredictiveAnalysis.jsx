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
export default PredictiveAnalysis;