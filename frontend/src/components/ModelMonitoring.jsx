import { useState, useEffect } from "react";
import axios from "axios";
import { Card } from "@/components/ui/card";
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from "recharts";
import { TrendingUp, Award, Activity, Calendar } from "lucide-react";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const ModelMonitoring = ({ workspaceId }) => {
  const [trends, setTrends] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (workspaceId) {
      loadPerformanceTrends();
    }
  }, [workspaceId]);

  const loadPerformanceTrends = async () => {
    setLoading(true);
    try {
      const response = await axios.get(`${API}/workspace/${workspaceId}/performance-trends`);
      setTrends(response.data);
    } catch (error) {
      console.error("Failed to load performance trends:", error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div className="text-center py-8">Loading performance trends...</div>;
  }

  if (!trends || trends.total_training_runs === 0) {
    return (
      <Card className="p-8 text-center">
        <Activity className="w-12 h-12 mx-auto mb-4 text-gray-400" />
        <h4 className="font-semibold text-gray-700 mb-2">No Training History Yet</h4>
        <p className="text-sm text-gray-600">
          Train models in this workspace to see performance trends over time
        </p>
      </Card>
    );
  }

  const { model_trends, best_model_recommendation, total_training_runs } = trends;

  // Prepare chart data
  const chartData = {};
  Object.entries(model_trends).forEach(([modelType, runs]) => {
    runs.forEach((run) => {
      const date = new Date(run.timestamp).toLocaleDateString();
      if (!chartData[date]) {
        chartData[date] = { date };
      }
      const score = run.metrics.r2_score || run.metrics.accuracy || 0;
      chartData[date][modelType] = score;
    });
  });

  const chartDataArray = Object.values(chartData);

  const colors = [
    "#3b82f6", "#ef4444", "#10b981", "#f59e0b", "#8b5cf6",
    "#ec4899", "#14b8a6", "#f97316", "#6366f1", "#84cc16"
  ];

  return (
    <div className="space-y-6">
      {/* Header Stats */}
      <div className="grid md:grid-cols-3 gap-4">
        <Card className="p-4 bg-gradient-to-br from-blue-50 to-blue-100">
          <div className="flex items-center gap-3">
            <Calendar className="w-8 h-8 text-blue-600" />
            <div>
              <p className="text-sm text-gray-600">Total Trainings</p>
              <p className="text-2xl font-bold text-gray-900">{total_training_runs}</p>
            </div>
          </div>
        </Card>

        <Card className="p-4 bg-gradient-to-br from-green-50 to-green-100">
          <div className="flex items-center gap-3">
            <Activity className="w-8 h-8 text-green-600" />
            <div>
              <p className="text-sm text-gray-600">Models Tested</p>
              <p className="text-2xl font-bold text-gray-900">{Object.keys(model_trends).length}</p>
            </div>
          </div>
        </Card>

        {best_model_recommendation && (
          <Card className="p-4 bg-gradient-to-br from-purple-50 to-purple-100">
            <div className="flex items-center gap-3">
              <Award className="w-8 h-8 text-purple-600" />
              <div>
                <p className="text-sm text-gray-600">Best Model</p>
                <p className="text-lg font-bold text-gray-900">{best_model_recommendation.model_type}</p>
                <p className="text-xs text-gray-600">
                  Avg Score: {best_model_recommendation.avg_score.toFixed(4)}
                </p>
              </div>
            </div>
          </Card>
        )}
      </div>

      {/* Performance Trends Chart */}
      <Card className="p-6">
        <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
          <TrendingUp className="w-5 h-5 text-blue-600" />
          Performance Trends Over Time
        </h3>

        <ResponsiveContainer width="100%" height={400}>
          <LineChart data={chartDataArray}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="date" />
            <YAxis domain={[0, 1]} />
            <Tooltip />
            <Legend />
            {Object.keys(model_trends).map((modelType, idx) => (
              <Line
                key={modelType}
                type="monotone"
                dataKey={modelType}
                stroke={colors[idx % colors.length]}
                strokeWidth={2}
                dot={{ r: 4 }}
                activeDot={{ r: 6 }}
              />
            ))}
          </LineChart>
        </ResponsiveContainer>

        <p className="text-xs text-gray-500 mt-4 text-center">
          Higher scores indicate better model performance. Track trends to identify the most consistent models.
        </p>
      </Card>

      {/* Model Performance Details */}
      <Card className="p-6">
        <h3 className="text-lg font-semibold mb-4">Model Performance Details</h3>
        <div className="space-y-4">
          {Object.entries(model_trends).map(([modelType, runs]) => {
            const avgScore = (runs.reduce((sum, r) => sum + (r.metrics.r2_score || r.metrics.accuracy || 0), 0) / runs.length).toFixed(4);
            const minScore = Math.min(...runs.map(r => r.metrics.r2_score || r.metrics.accuracy || 0)).toFixed(4);
            const maxScore = Math.max(...runs.map(r => r.metrics.r2_score || r.metrics.accuracy || 0)).toFixed(4);

            return (
              <div key={modelType} className="border-l-4 border-blue-500 pl-4 py-2">
                <h4 className="font-semibold text-gray-900">{modelType}</h4>
                <div className="grid grid-cols-3 gap-4 mt-2 text-sm">
                  <div>
                    <p className="text-gray-600">Avg Score</p>
                    <p className="font-semibold">{avgScore}</p>
                  </div>
                  <div>
                    <p className="text-gray-600">Best</p>
                    <p className="font-semibold text-green-600">{maxScore}</p>
                  </div>
                  <div>
                    <p className="text-gray-600">Worst</p>
                    <p className="font-semibold text-red-600">{minScore}</p>
                  </div>
                </div>
                <p className="text-xs text-gray-500 mt-1">{runs.length} training runs</p>
              </div>
            );
          })}
        </div>
      </Card>
    </div>
  );
};

export default ModelMonitoring;
