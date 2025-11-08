import { useState, useEffect } from 'react';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { toast } from 'sonner';
import { ThumbsUp, ThumbsDown, MessageSquare, Loader2, TrendingUp, Target } from 'lucide-react';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const FeedbackPanel = ({ dataset, modelName }) => {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(false);
  const [retraining, setRetraining] = useState(false);
  const [progress, setProgress] = useState(0);
  const [progressMessage, setProgressMessage] = useState('');
  const [feedbackList, setFeedbackList] = useState([]);

  useEffect(() => {
    if (dataset) {
      loadTrainingHistory();
    }
  }, [dataset]);

  const loadTrainingHistory = async () => {
    setLoading(true);
    try {
      // Load training metadata (training history) for this dataset
      const response = await axios.get(`${API}/training/metadata?dataset_id=${dataset.id}`);
      const trainingRuns = response.data.metadata || [];
      
      setFeedbackList(trainingRuns);
      
      // Calculate stats from training runs
      const totalRuns = trainingRuns.length;
      const avgAccuracy = totalRuns > 0 
        ? trainingRuns.reduce((sum, run) => sum + (run.metrics?.accuracy || run.metrics?.r2_score || 0), 0) / totalRuns
        : 0;
      
      setStats({
        feedback_count: totalRuns,
        correct_predictions: trainingRuns.filter(r => (r.metrics?.accuracy || r.metrics?.r2_score || 0) > 0.7).length,
        incorrect_predictions: trainingRuns.filter(r => (r.metrics?.accuracy || r.metrics?.r2_score || 0) <= 0.7).length,
        accuracy: avgAccuracy
      });
    } catch (error) {
      console.error('Failed to load training history:', error);
      setStats({
        feedback_count: 0,
        correct_predictions: 0,
        incorrect_predictions: 0,
        accuracy: null
      });
      setFeedbackList([]);
    } finally {
      setLoading(false);
    }
  };

  const submitFeedback = async (predictionId, isCorrect, actualOutcome = null) => {
    setLoading(true);
    try {
      await axios.post(`${API}/feedback/submit`, {
        prediction_id: predictionId,
        is_correct: isCorrect,
        actual_outcome: actualOutcome
      });
      
      toast.success('Feedback submitted!');
      loadStats();
    } catch (error) {
      toast.error('Failed to submit feedback: ' + (error.response?.data?.detail || error.message));
    } finally {
      setLoading(false);
    }
  };

  const retrainModel = async () => {
    if (!stats || stats.feedback_count === 0) {
      toast.error('No feedback data available for retraining');
      return;
    }

    setRetraining(true);
    setProgress(10);
    setProgressMessage('Preparing feedback data...');
    
    try {
      await new Promise(resolve => setTimeout(resolve, 200));
      
      setProgress(30);
      setProgressMessage('Loading training dataset...');
      
      await new Promise(resolve => setTimeout(resolve, 200));
      
      setProgress(50);
      setProgressMessage('Retraining model with feedback...');
      
      const response = await axios.post(`${API}/feedback/retrain`, {
        dataset_id: dataset.id,
        model_name: modelName,
        target_column: 'target'
      });

      setProgress(80);
      setProgressMessage('Evaluating new model...');
      
      await new Promise(resolve => setTimeout(resolve, 200));
      
      setProgress(100);
      setProgressMessage('Retraining complete!');

      toast.success(
        `Model retrained with ${response.data.feedback_samples} feedback samples!`
      );
      
      loadStats();
    } catch (error) {
      toast.error('Retraining failed: ' + (error.response?.data?.detail || error.message));
    } finally {
      setTimeout(() => {
        setRetraining(false);
        setProgress(0);
        setProgressMessage('');
      }, 300);
    }
  };

  if (!stats && !loading && !retraining) {
    return (
      <Card className="p-6">
        <div className="text-center text-gray-500">
          <Loader2 className="w-8 h-8 animate-spin mx-auto mb-2" />
          Loading feedback data...
        </div>
      </Card>
    );
  }

  return (
    <div className="space-y-6">
      {/* Tab Description */}
      <Card className="p-4 bg-gradient-to-r from-green-50 to-blue-50 border-green-200">
        <div className="flex items-start gap-3">
          <div className="p-2 bg-green-500 rounded-lg">
            <Target className="w-5 h-5 text-white" />
          </div>
          <div className="flex-1">
            <h3 className="font-semibold text-green-900 mb-1">Feedback & Learning (Active Learning)</h3>
            <p className="text-sm text-green-700">
              <strong>What it does:</strong> Collects user feedback on predictions and retrains models to improve accuracy over time.
            </p>
            <p className="text-sm text-green-600 mt-1">
              <strong>Advantages:</strong> Continuous model improvement, learn from real-world outcomes, adapt to changing patterns, increase accuracy through human-in-the-loop learning.
            </p>
          </div>
        </div>
      </Card>

      {/* Retraining Progress */}
      {retraining && (
        <Card className="p-6 bg-gradient-to-r from-green-50 to-blue-50">
          <div className="text-center">
            <Loader2 className="w-12 h-12 animate-spin mx-auto mb-4 text-green-600" />
            <h3 className="text-lg font-semibold mb-2">{progressMessage}</h3>
            <div className="w-full bg-gray-200 rounded-full h-3 mb-2">
              <div 
                className="bg-gradient-to-r from-green-600 to-blue-600 h-3 rounded-full transition-all duration-300"
                style={{ width: `${progress}%` }}
              ></div>
            </div>
            <p className="text-sm text-gray-600">{progress}% Complete</p>
          </div>
        </Card>
      )}

      {!retraining && stats && (
        <>
          <Card className="p-6">
            <h3 className="text-xl font-bold mb-4 flex items-center gap-2">
              📊 Training History & Model Performance
            </h3>

            {/* Stats Grid */}
            <div className="grid grid-cols-4 gap-4 mb-6">
              <div className="bg-blue-50 p-4 rounded">
                <div className="text-sm text-gray-600">Training Runs</div>
                <div className="text-2xl font-bold text-blue-600">
                  {stats.feedback_count || 0}
                </div>
              </div>
              <div className="bg-green-50 p-4 rounded">
                <div className="text-sm text-gray-600">High Performance</div>
                <div className="text-2xl font-bold text-green-600">
                  {stats.correct_predictions || 0}
                </div>
              </div>
              <div className="bg-red-50 p-4 rounded">
                <div className="text-sm text-gray-600">Low Performance</div>
                <div className="text-2xl font-bold text-red-600">
                  {stats.incorrect_predictions || 0}
                </div>
              </div>
              <div className="bg-purple-50 p-4 rounded">
                <div className="text-sm text-gray-600">Accuracy</div>
                <div className="text-2xl font-bold text-purple-600">
                  {stats.accuracy ? `${(stats.accuracy * 100).toFixed(1)}%` : 'N/A'}
                </div>
              </div>
            </div>

            <Button 
              onClick={retrainModel} 
              disabled={!stats || stats.feedback_count === 0 || retraining}
              className="w-full"
            >
              {retraining ? (
                <>
                  <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                  Retraining...
                </>
              ) : (
                <>
                  <TrendingUp className="w-4 h-4 mr-2" />
                  Retrain Model with Feedback
                </>
              )}
            </Button>
          </Card>

          {/* Recent Feedback List */}
          {feedbackList && feedbackList.length > 0 && (
            <Card className="p-6">
              <h3 className="text-lg font-bold mb-4">Recent Feedback</h3>
              <div className="space-y-3">
                {feedbackList.slice(0, 10).map((feedback, idx) => (
                  <div key={idx} className="flex items-center gap-3 p-3 bg-gray-50 rounded">
                    {feedback.is_correct ? (
                      <ThumbsUp className="w-5 h-5 text-green-600" />
                    ) : (
                      <ThumbsDown className="w-5 h-5 text-red-600" />
                    )}
                    <div className="flex-1">
                      <div className="text-sm font-medium">
                        Prediction: {feedback.prediction} → Actual: {feedback.actual_outcome || 'N/A'}
                      </div>
                      {feedback.comment && (
                        <div className="text-xs text-gray-600 mt-1">{feedback.comment}</div>
                      )}
                    </div>
                    <div className="text-xs text-gray-500">
                      {new Date(feedback.timestamp).toLocaleDateString()}
                    </div>
                  </div>
                ))}
              </div>
            </Card>
          )}

          {(!feedbackList || feedbackList.length === 0) && (
            <Card className="p-6">
              <div className="text-center text-gray-500 py-8">
                <MessageSquare className="w-12 h-12 mx-auto mb-3 text-gray-400" />
                <p>No feedback submitted yet</p>
                <p className="text-sm mt-2">Submit feedback on predictions to enable model retraining</p>
              </div>
            </Card>
          )}
        </>
      )}
    </div>
  );
};

export default FeedbackPanel;