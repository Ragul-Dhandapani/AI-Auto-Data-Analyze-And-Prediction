import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Loader2, X, TrendingUp, TrendingDown, Award, RefreshCw, Calendar, BarChart3 } from 'lucide-react';
import { toast } from 'sonner';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const TrainingMetadataDashboard = ({ onClose }) => {
  const [loading, setLoading] = useState(true);
  const [metadata, setMetadata] = useState([]);
  const [selectedDataset, setSelectedDataset] = useState(null);

  useEffect(() => {
    fetchMetadata();
  }, []);

  const fetchMetadata = async () => {
    setLoading(true);
    try {
      const response = await axios.get(`${API}/training-metadata`);
      setMetadata(response.data.metadata || []);
    } catch (error) {
      toast.error('Failed to fetch training metadata');
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
        <Card className="w-full max-w-6xl max-h-[90vh] p-8 m-4">
          <div className="flex items-center justify-center">
            <Loader2 className="w-8 h-8 animate-spin text-blue-600" />
            <span className="ml-3">Loading training metadata...</span>
          </div>
        </Card>
      </div>
    );
  }

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <Card className="w-full max-w-7xl max-h-[90vh] flex flex-col bg-white">
        {/* Header */}
        <div className="p-6 border-b flex items-center justify-between bg-gradient-to-r from-blue-600 to-indigo-600 text-white rounded-t-lg">
          <div className="flex items-center gap-3">
            <BarChart3 className="w-6 h-6" />
            <h2 className="text-2xl font-bold">Training Metadata Dashboard</h2>
          </div>
          <Button variant="ghost" size="sm" onClick={onClose} className="text-white hover:bg-white/20">
            <X className="w-5 h-5" />
          </Button>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto p-6">
          {metadata.length === 0 ? (
            <div className="text-center py-12 text-gray-500">
              <BarChart3 className="w-16 h-16 mx-auto mb-4 text-gray-400" />
              <p>No training data available yet.</p>
              <p className="text-sm mt-2">Run analysis on datasets to see training metadata.</p>
            </div>
          ) : (
            <div className="space-y-6">
              {metadata.map((dataset, idx) => (
                <Card key={idx} className="p-6 border-2 hover:border-blue-400 transition-colors">
                  {/* Dataset Header */}
                  <div className="flex items-start justify-between mb-4">
                    <div>
                      <h3 className="text-xl font-bold text-gray-800">{dataset.dataset_name}</h3>
                      <p className="text-sm text-gray-500">Dataset ID: {dataset.dataset_id}</p>
                    </div>
                    <div className="flex gap-2">
                      <div className="bg-blue-100 px-3 py-1 rounded-full">
                        <p className="text-xs font-semibold text-blue-700 flex items-center gap-1">
                          <RefreshCw className="w-3 h-3" />
                          {dataset.training_count} Training{dataset.training_count !== 1 ? 's' : ''}
                        </p>
                      </div>
                      {dataset.improvement_percentage !== null && (
                        <div className={`px-3 py-1 rounded-full ${dataset.improvement_percentage >= 0 ? 'bg-green-100' : 'bg-red-100'}`}>
                          <p className={`text-xs font-semibold flex items-center gap-1 ${dataset.improvement_percentage >= 0 ? 'text-green-700' : 'text-red-700'}`}>
                            {dataset.improvement_percentage >= 0 ? <TrendingUp className="w-3 h-3" /> : <TrendingDown className="w-3 h-3" />}
                            {Math.abs(dataset.improvement_percentage).toFixed(1)}% {dataset.improvement_percentage >= 0 ? 'Improvement' : 'Decline'}
                          </p>
                        </div>
                      )}
                    </div>
                  </div>

                  {/* Training Summary */}
                  <div className="grid md:grid-cols-3 gap-4 mb-4">
                    <div className="bg-gradient-to-br from-blue-50 to-blue-100 p-4 rounded-lg">
                      <p className="text-xs text-blue-600 font-semibold mb-1">Initial Score</p>
                      <p className="text-2xl font-bold text-blue-800">
                        {dataset.initial_score !== null ? `${(dataset.initial_score * 100).toFixed(1)}%` : 'N/A'}
                      </p>
                    </div>
                    <div className="bg-gradient-to-br from-green-50 to-green-100 p-4 rounded-lg">
                      <p className="text-xs text-green-600 font-semibold mb-1">Current Score</p>
                      <p className="text-2xl font-bold text-green-800">
                        {dataset.current_score !== null ? `${(dataset.current_score * 100).toFixed(1)}%` : 'N/A'}
                      </p>
                    </div>
                    <div className="bg-gradient-to-br from-purple-50 to-purple-100 p-4 rounded-lg">
                      <p className="text-xs text-purple-600 font-semibold mb-1 flex items-center gap-1">
                        <Award className="w-3 h-3" />
                        Best Model
                      </p>
                      <p className="text-lg font-bold text-purple-800">
                        {dataset.best_model_name || 'N/A'}
                      </p>
                    </div>
                  </div>

                  {/* Last Trained */}
                  {dataset.last_trained_at && (
                    <div className="flex items-center gap-2 text-sm text-gray-600 mb-4">
                      <Calendar className="w-4 h-4" />
                      Last trained: {new Date(dataset.last_trained_at).toLocaleString()}
                    </div>
                  )}

                  {/* Model Scores Table */}
                  {Object.keys(dataset.model_scores).length > 0 && (
                    <div className="mb-4">
                      <h4 className="font-semibold text-gray-700 mb-2">Model Performance</h4>
                      <div className="overflow-x-auto">
                        <table className="w-full text-sm">
                          <thead className="bg-gray-100">
                            <tr>
                              <th className="px-4 py-2 text-left font-semibold">Model</th>
                              <th className="px-4 py-2 text-center font-semibold">Initial Score</th>
                              <th className="px-4 py-2 text-center font-semibold">Current Score</th>
                              <th className="px-4 py-2 text-center font-semibold">Improvement</th>
                              <th className="px-4 py-2 text-center font-semibold">Confidence</th>
                            </tr>
                          </thead>
                          <tbody>
                            {Object.entries(dataset.model_scores).map(([modelName, scores]) => (
                              <tr key={modelName} className="border-b hover:bg-gray-50">
                                <td className="px-4 py-2 font-medium">{modelName}</td>
                                <td className="px-4 py-2 text-center">
                                  {scores.initial_score !== undefined 
                                    ? `${(scores.initial_score * 100).toFixed(1)}%` 
                                    : '-'}
                                </td>
                                <td className="px-4 py-2 text-center font-semibold">
                                  {(scores.current_score * 100).toFixed(1)}%
                                </td>
                                <td className="px-4 py-2 text-center">
                                  {scores.improvement_pct !== undefined ? (
                                    <span className={scores.improvement_pct >= 0 ? 'text-green-600 font-semibold' : 'text-red-600 font-semibold'}>
                                      {scores.improvement_pct >= 0 ? '+' : ''}{scores.improvement_pct.toFixed(1)}%
                                    </span>
                                  ) : (
                                    '-'
                                  )}
                                </td>
                                <td className="px-4 py-2 text-center">
                                  <span className={`px-2 py-1 rounded text-xs font-semibold ${
                                    scores.confidence === 'High' ? 'bg-green-100 text-green-700' :
                                    scores.confidence === 'Medium' ? 'bg-yellow-100 text-yellow-700' :
                                    'bg-red-100 text-red-700'
                                  }`}>
                                    {scores.confidence}
                                  </span>
                                </td>
                              </tr>
                            ))}
                          </tbody>
                        </table>
                      </div>
                    </div>
                  )}

                  {/* Workspaces */}
                  {dataset.workspaces.length > 0 && (
                    <div className="mb-4">
                      <h4 className="font-semibold text-gray-700 mb-2">Saved Workspaces ({dataset.workspaces.length})</h4>
                      <div className="grid md:grid-cols-2 gap-2">
                        {dataset.workspaces.map((workspace, wIdx) => (
                          <div key={wIdx} className="bg-blue-50 p-3 rounded border border-blue-200">
                            <p className="font-medium text-blue-800">{workspace.workspace_name}</p>
                            <p className="text-xs text-blue-600">
                              Saved: {new Date(workspace.saved_at).toLocaleString()}
                            </p>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Training History Accordion */}
                  {dataset.training_history.length > 0 && (
                    <details className="mt-4">
                      <summary className="cursor-pointer font-semibold text-gray-700 hover:text-blue-600 flex items-center gap-2">
                        <span>Training History ({dataset.training_history.length} sessions)</span>
                      </summary>
                      <div className="mt-3 space-y-2 max-h-64 overflow-y-auto">
                        {dataset.training_history.map((history, hIdx) => (
                          <div key={hIdx} className="bg-gray-50 p-3 rounded border">
                            <div className="flex items-center justify-between mb-2">
                              <span className="font-semibold text-sm">Training #{history.training_number}</span>
                              <span className="text-xs text-gray-500">
                                {new Date(history.trained_at).toLocaleString()}
                              </span>
                            </div>
                            <div className="flex items-center gap-4 text-sm">
                              <span className="text-gray-600">
                                Best: <span className="font-semibold">{history.best_model}</span>
                              </span>
                              <span className="text-gray-600">
                                Score: <span className="font-semibold text-blue-600">{(history.best_score * 100).toFixed(1)}%</span>
                              </span>
                            </div>
                          </div>
                        ))}
                      </div>
                    </details>
                  )}
                </Card>
              ))}
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="p-4 border-t bg-gray-50 flex justify-between items-center rounded-b-lg">
          <p className="text-sm text-gray-600">
            Total Datasets: {metadata.length} | Total Trainings: {metadata.reduce((sum, d) => sum + d.training_count, 0)}
          </p>
          <Button onClick={fetchMetadata} variant="outline" size="sm">
            <RefreshCw className="w-4 h-4 mr-2" />
            Refresh
          </Button>
        </div>
      </Card>
    </div>
  );
};

export default TrainingMetadataDashboard;
