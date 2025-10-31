import { useState } from "react";
import axios from "axios";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Label } from "@/components/ui/label";
import { toast } from "sonner";
import { Loader2, TrendingUp, AlertCircle } from "lucide-react";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const PredictiveAnalysis = ({ dataset }) => {
  const [loading, setLoading] = useState(false);
  const [targetColumn, setTargetColumn] = useState("");
  const [predictionResults, setPredictionResults] = useState(null);

  const runPrediction = async () => {
    if (!targetColumn) {
      toast.error("Please select a target column");
      return;
    }

    setLoading(true);
    try {
      const response = await axios.post(`${API}/analysis/run`, {
        dataset_id: dataset.id,
        analysis_type: "predict",
        options: { target_column: targetColumn }
      });

      if (response.data.error) {
        toast.error(response.data.error);
        setPredictionResults(null);
      } else {
        setPredictionResults(response.data);
        toast.success("Prediction completed successfully!");
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

  // Prepare chart data
  const maxDisplay = 30;
  const displayData = predictionResults?.predictions?.slice(0, maxDisplay) || [];
  const displayActuals = predictionResults?.actuals?.slice(0, maxDisplay) || [];

  return (
    <div className="space-y-6" data-testid="predictive-analysis">
      <Card className="p-6 bg-gradient-to-br from-indigo-50 to-purple-50 border-indigo-200">
        <h3 className="text-xl font-semibold mb-4 flex items-center gap-2">
          <TrendingUp className="w-6 h-6 text-indigo-600" />
          Predictive Analytics
        </h3>
        <p className="text-sm text-gray-600 mb-6">
          Select a numeric target column to predict using machine learning. The system will automatically
          select features and train a model.
        </p>

        <div className="space-y-4">
          <div>
            <Label>Target Column (What to Predict)</Label>
            <Select value={targetColumn} onValueChange={setTargetColumn}>
              <SelectTrigger data-testid="target-column-select">
                <SelectValue placeholder="Select numeric column" />
              </SelectTrigger>
              <SelectContent>
                {numericColumns.map((col) => (
                  <SelectItem key={col} value={col}>{col}</SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          <Button 
            data-testid="run-prediction-btn"
            onClick={runPrediction}
            disabled={loading || !targetColumn}
            className="w-full bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-700 hover:to-purple-700"
          >
            {loading ? (
              <><Loader2 className="w-4 h-4 animate-spin mr-2" /> Running Prediction...</>
            ) : (
              <><TrendingUp className="w-4 h-4 mr-2" /> Run Prediction</>
            )}
          </Button>
        </div>
      </Card>

      {predictionResults && (
        <>
          {/* Model Performance */}
          <Card className="p-6">
            <h3 className="text-lg font-semibold mb-4">Model Performance</h3>
            <div className="grid md:grid-cols-3 gap-4">
              <div className="p-4 bg-blue-50 rounded-lg border border-blue-200">
                <p className="text-sm text-gray-600 mb-1">Model Type</p>
                <p className="font-semibold">{predictionResults.model_type}</p>
              </div>
              <div className="p-4 bg-green-50 rounded-lg border border-green-200">
                <p className="text-sm text-gray-600 mb-1">Training Score (R²)</p>
                <p className="text-2xl font-bold text-green-600">
                  {(predictionResults.train_score * 100).toFixed(1)}%
                </p>
              </div>
              <div className="p-4 bg-purple-50 rounded-lg border border-purple-200">
                <p className="text-sm text-gray-600 mb-1">Test Score (R²)</p>
                <p className="text-2xl font-bold text-purple-600">
                  {(predictionResults.test_score * 100).toFixed(1)}%
                </p>
              </div>
            </div>

            {predictionResults.test_score < 0.5 && (
              <div className="mt-4 p-4 bg-yellow-50 border border-yellow-200 rounded-lg flex items-start gap-3">
                <AlertCircle className="w-5 h-5 text-yellow-600 mt-0.5" />
                <div className="text-sm text-yellow-800">
                  <p className="font-medium">Low Model Accuracy</p>
                  <p>The model's prediction accuracy is below 50%. Consider:
                    <ul className="list-disc ml-5 mt-1">
                      <li>Adding more relevant features</li>
                      <li>Collecting more data samples</li>
                      <li>Trying a different target column</li>
                    </ul>
                  </p>
                </div>
              </div>
            )}
          </Card>

          {/* Feature Importance */}
          <Card className="p-6">
            <h3 className="text-lg font-semibold mb-4">Feature Importance</h3>
            <p className="text-sm text-gray-600 mb-4">
              Features ranked by their impact on predictions:
            </p>
            <div className="space-y-3">
              {Object.entries(predictionResults.feature_importance)
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
          </Card>

          {/* Prediction vs Actual Chart */}
          <Card className="p-6">
            <h3 className="text-lg font-semibold mb-4">Predictions vs Actual Values</h3>
            <ResponsiveContainer width="100%" height={400}>
              <LineChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                <XAxis 
                  dataKey="index" 
                  stroke="#6b7280"
                  label={{ value: 'Sample Index', position: 'insideBottom', offset: -5 }}
                />
                <YAxis stroke="#6b7280" />
                <Tooltip 
                  contentStyle={{ 
                    backgroundColor: 'white', 
                    border: '1px solid #e5e7eb',
                    borderRadius: '8px'
                  }}
                />
                <Legend />
                <Line 
                  type="monotone" 
                  dataKey="Actual" 
                  stroke="#3b82f6" 
                  strokeWidth={2}
                  dot={{ fill: '#3b82f6', r: 4 }}
                />
                <Line 
                  type="monotone" 
                  dataKey="Predicted" 
                  stroke="#8b5cf6" 
                  strokeWidth={2}
                  dot={{ fill: '#8b5cf6', r: 4 }}
                />
              </LineChart>
            </ResponsiveContainer>
          </Card>
        </>
      )}
    </div>
  );
};

export default PredictiveAnalysis;