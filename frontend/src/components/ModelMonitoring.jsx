import { useState, useEffect } from 'react';
import axios from 'axios';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Loader2, Activity, TrendingUp, Clock, CheckCircle, AlertTriangle, Download, Filter } from 'lucide-react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, BarChart, Bar } from 'recharts';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;

const ModelMonitoring = ({ workspaceId, datasetId }) => {
  const [trainingHistory, setTrainingHistory] = useState([]);
  const [filteredHistory, setFilteredHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedMetric, setSelectedMetric] = useState('r2_score');
  const [selectedModelFilter, setSelectedModelFilter] = useState('all');
  const [dateRangeFilter, setDateRangeFilter] = useState('all'); // all, week, month
  const [comparisonMode, setComparisonMode] = useState(false);

  useEffect(() => {
    loadTrainingHistory();
  }, [workspaceId, datasetId]);

  useEffect(() => {
    applyFilters();
  }, [trainingHistory, selectedModelFilter, dateRangeFilter]);

  const loadTrainingHistory = async () => {
    try {
      setLoading(true);
      let response;
      
      if (datasetId) {
        response = await axios.get(`${BACKEND_URL}/api/training-metadata/${datasetId}`);
      } else if (workspaceId) {
        response = await axios.get(`${BACKEND_URL}/api/workspace/${workspaceId}/training-history`);
      }
      
      const trainings = response?.data?.trainings || [];
      setTrainingHistory(trainings);
      setFilteredHistory(trainings);
    } catch (error) {
      console.error('Failed to load training history:', error);
    } finally {
      setLoading(false);
    }
  };

  const applyFilters = () => {
    let filtered = [...trainingHistory];

    // Filter by model type
    if (selectedModelFilter !== 'all') {
      filtered = filtered.filter(t => t.model_type === selectedModelFilter);
    }

    // Filter by date range
    if (dateRangeFilter !== 'all') {
      const now = new Date();
      const cutoffDate = new Date();
      
      if (dateRangeFilter === 'week') {
        cutoffDate.setDate(now.getDate() - 7);
      } else if (dateRangeFilter === 'month') {
        cutoffDate.setMonth(now.getMonth() - 1);
      }
      
      filtered = filtered.filter(t => new Date(t.created_at) >= cutoffDate);
    }

    setFilteredHistory(filtered);
  };

  const getUniqueModels = () => {
    const models = new Set(trainingHistory.map(t => t.model_type));
    return Array.from(models);
  };

  const exportTrainingHistory = () => {
    const csvContent = [
      ['Model Type', 'Score', 'Duration (s)', 'Problem Type', 'Date', 'RMSE', 'MAE'].join(','),
      ...filteredHistory.map(t => [
        t.model_type,
        t.metrics?.r2_score || t.metrics?.accuracy || 0,
        t.training_duration || 0,
        t.problem_type || 'N/A',
        new Date(t.created_at).toLocaleString(),
        t.metrics?.rmse || 'N/A',
        t.metrics?.mae || 'N/A'
      ].join(','))
    ].join('\n');

    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `training_history_${new Date().toISOString().split('T')[0]}.csv`;
    a.click();
    window.URL.revokeObjectURL(url);
  };

  const prepareChartData = () => {
    return filteredHistory
      .slice().reverse()
      .map((training, idx) => ({
        name: `Run ${idx + 1}`,
        timestamp: new Date(training.created_at).toLocaleDateString(),
        r2_score: training.metrics?.r2_score || training.metrics?.accuracy || 0,
        rmse: training.metrics?.rmse || 0,
        mae: training.metrics?.mae || 0,
        training_duration: training.training_duration || 0,
        model: training.model_type
      }));
  };

  const prepareComparisonData = () => {
    const modelStats = {};
    
    filteredHistory.forEach(training => {
      const modelType = training.model_type;
      const score = training.metrics?.r2_score || training.metrics?.accuracy || 0;
      
      if (!modelStats[modelType]) {
        modelStats[modelType] = {
          scores: [],
          durations: []
        };
      }
      
      modelStats[modelType].scores.push(score);
      modelStats[modelType].durations.push(training.training_duration || 0);
    });

    return Object.keys(modelStats).map(modelType => ({
      model: modelType,
      avgScore: (modelStats[modelType].scores.reduce((a, b) => a + b, 0) / modelStats[modelType].scores.length).toFixed(4),
      avgDuration: (modelStats[modelType].durations.reduce((a, b) => a + b, 0) / modelStats[modelType].durations.length).toFixed(2),
      runs: modelStats[modelType].scores.length
    }));
  };

  const getModelTypeColor = (modelType) => {
    const colors = {
      'RandomForest': '#10b981',
      'XGBoost': '#3b82f6',
      'LinearRegression': '#8b5cf6',
      'GradientBoosting': '#f59e0b',
      'Default': '#6b7280'
    };
    return colors[modelType] || colors.Default;
  };

  const calculateStats = () => {
    if (filteredHistory.length === 0) return null;

    const scores = filteredHistory.map(t => t.metrics?.r2_score || t.metrics?.accuracy || 0);
    const durations = filteredHistory.map(t => t.training_duration || 0);
    
    return {
      avgScore: (scores.reduce((a, b) => a + b, 0) / scores.length).toFixed(4),
      bestScore: Math.max(...scores).toFixed(4),
      totalRuns: filteredHistory.length,
      avgDuration: (durations.reduce((a, b) => a + b, 0) / durations.length).toFixed(2),
      trend: scores[scores.length - 1] > scores[0] ? 'improving' : 'declining'
    };
  };

  const stats = calculateStats();
  const chartData = prepareChartData();
  const comparisonData = prepareComparisonData();
  const uniqueModels = getUniqueModels();

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Loader2 className="w-8 h-8 animate-spin text-blue-600" />
      </div>
    );
  }

  if (trainingHistory.length === 0) {
    return (
      <Card className="p-12 text-center">
        <Activity className="w-16 h-16 mx-auto text-gray-400 mb-4" />
        <h3 className="text-lg font-semibold text-gray-700 mb-2">No Training History</h3>
        <p className="text-gray-500">Run your first analysis to start tracking model performance</p>
      </Card>
    );
  }

  return (
    <div className="space-y-6">
      {/* Filters and Actions */}
      <Card className="p-4">
        <div className="flex flex-wrap items-center gap-4 justify-between">
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-2">
              <Filter className="w-4 h-4 text-gray-600" />
              <span className="text-sm font-medium">Filters:</span>
            </div>
            
            <Select value={selectedModelFilter} onValueChange={setSelectedModelFilter}>
              <SelectTrigger className="w-[180px]">
                <SelectValue placeholder="All Models" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Models</SelectItem>
                {uniqueModels.map(model => (
                  <SelectItem key={model} value={model}>{model}</SelectItem>
                ))}
              </SelectContent>
            </Select>

            <Select value={dateRangeFilter} onValueChange={setDateRangeFilter}>
              <SelectTrigger className="w-[180px]">
                <SelectValue placeholder="All Time" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Time</SelectItem>
                <SelectItem value="week">Last 7 Days</SelectItem>
                <SelectItem value="month">Last 30 Days</SelectItem>
              </SelectContent>
            </Select>
          </div>

          <div className="flex items-center gap-2">
            <Button
              variant={comparisonMode ? 'default' : 'outline'}
              onClick={() => setComparisonMode(!comparisonMode)}
              size="sm"
            >
              {comparisonMode ? 'Timeline View' : 'Comparison View'}
            </Button>
            <Button
              variant="outline"
              onClick={exportTrainingHistory}
              size="sm"
            >
              <Download className="w-4 h-4 mr-2" />
              Export CSV
            </Button>
          </div>
        </div>
      </Card>

      {/* Stats Overview */}
      {stats && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <Card className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Average Score</p>
                <p className="text-2xl font-bold">{stats.avgScore}</p>
              </div>
              <TrendingUp className="w-8 h-8 text-blue-600" />
            </div>
          </Card>
          
          <Card className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Best Score</p>
                <p className="text-2xl font-bold">{stats.bestScore}</p>
              </div>
              <CheckCircle className="w-8 h-8 text-green-600" />
            </div>
          </Card>
          
          <Card className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Total Runs</p>
                <p className="text-2xl font-bold">{stats.totalRuns}</p>
              </div>
              <Activity className="w-8 h-8 text-purple-600" />
            </div>
          </Card>
          
          <Card className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Avg Duration</p>
                <p className="text-2xl font-bold">{stats.avgDuration}s</p>
              </div>
              <Clock className="w-8 h-8 text-orange-600" />
            </div>
          </Card>
        </div>
      )}

      {/* Performance Chart */}
      <Card className="p-6">
        <div className="flex justify-between items-center mb-4">
          <h3 className="text-lg font-semibold">
            {comparisonMode ? 'Model Comparison' : 'Performance Trend'}
          </h3>
          {!comparisonMode && stats && (
            <div className="flex items-center gap-2">
              <span className={`px-3 py-1 rounded-full text-sm font-semibold ${
                stats.trend === 'improving' ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'
              }`}>
                {stats.trend === 'improving' ? '↗ Improving' : '↘ Declining'}
              </span>
            </div>
          )}
        </div>
        
        <ResponsiveContainer width="100%" height={300}>
          {comparisonMode ? (
            <BarChart data={comparisonData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="model" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Bar dataKey="avgScore" fill="#3b82f6" name="Avg Score" />
            </BarChart>
          ) : (
            <LineChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Line type="monotone" dataKey="r2_score" stroke="#3b82f6" name="R² Score" strokeWidth={2} />
            </LineChart>
          )}
        </ResponsiveContainer>
      </Card>

      {/* Model Comparison Table (Comparison Mode) */}
      {comparisonMode && (
        <Card className="p-6">
          <h3 className="text-lg font-semibold mb-4">Model Performance Comparison</h3>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b">
                  <th className="text-left py-2 px-4">Model</th>
                  <th className="text-left py-2 px-4">Avg Score</th>
                  <th className="text-left py-2 px-4">Avg Duration</th>
                  <th className="text-left py-2 px-4">Total Runs</th>
                  <th className="text-left py-2 px-4">Efficiency</th>
                </tr>
              </thead>
              <tbody>
                {comparisonData.map((model, idx) => {
                  const efficiency = (parseFloat(model.avgScore) / parseFloat(model.avgDuration)).toFixed(4);
                  return (
                    <tr key={idx} className="border-b hover:bg-gray-50">
                      <td className="py-3 px-4">
                        <span
                          className="px-2 py-1 rounded text-sm font-medium"
                          style={{ 
                            backgroundColor: `${getModelTypeColor(model.model)}20`, 
                            color: getModelTypeColor(model.model) 
                          }}
                        >
                          {model.model}
                        </span>
                      </td>
                      <td className="py-3 px-4 font-semibold">{model.avgScore}</td>
                      <td className="py-3 px-4">{model.avgDuration}s</td>
                      <td className="py-3 px-4">{model.runs}</td>
                      <td className="py-3 px-4">
                        <span className="px-2 py-1 bg-blue-100 text-blue-700 rounded text-sm font-medium">
                          {efficiency}
                        </span>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </Card>
      )}

      {/* Recent Training Runs */}
      <Card className="p-6">
        <h3 className="text-lg font-semibold mb-4">Recent Training Runs</h3>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b">
                <th className="text-left py-2 px-4">Model</th>
                <th className="text-left py-2 px-4">Score</th>
                <th className="text-left py-2 px-4">Duration</th>
                <th className="text-left py-2 px-4">Date</th>
                <th className="text-left py-2 px-4">Status</th>
              </tr>
            </thead>
            <tbody>
              {filteredHistory.slice(0, 10).map((training, idx) => (
                <tr key={idx} className="border-b hover:bg-gray-50">
                  <td className="py-3 px-4">
                    <span
                      className="px-2 py-1 rounded text-sm font-medium"
                      style={{ backgroundColor: `${getModelTypeColor(training.model_type)}20`, color: getModelTypeColor(training.model_type) }}
                    >
                      {training.model_type}
                    </span>
                  </td>
                  <td className="py-3 px-4 font-semibold">
                    {(training.metrics?.r2_score || training.metrics?.accuracy || 0).toFixed(4)}
                  </td>
                  <td className="py-3 px-4">{(training.training_duration || 0).toFixed(2)}s</td>
                  <td className="py-3 px-4">{new Date(training.created_at).toLocaleString()}</td>
                  <td className="py-3 px-4">
                    <span className="px-2 py-1 bg-green-100 text-green-700 rounded text-sm font-medium">
                      ✓ Complete
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Card>
    </div>
  );
};

export default ModelMonitoring;
