import { useState, useEffect } from 'react';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { toast } from 'sonner';
import { ThumbsUp, ThumbsDown, MessageSquare, Loader2, TrendingUp } from 'lucide-react';
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
    if (dataset && modelName) {
      loadStats();
    }
  }, [dataset, modelName]);

  const loadStats = async () => {
    try {
      const response = await axios.get(
        `${API}/feedback/stats/${dataset.id}/${encodeURIComponent(modelName)}`
      );
      setStats(response.data);
      setFeedbackList(response.data.feedback_data || []);
    } catch (error) {
      console.error('Failed to load feedback stats:', error);
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
      loadStats(); // Refresh stats
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
      await new Promise(resolve => setTimeout(resolve, 300));
      
      setProgress(30);
      setProgressMessage('Loading training dataset...');
      
      await new Promise(resolve => setTimeout(resolve, 300));
      
      setProgress(50);
      setProgressMessage('Retraining model with feedback...');
      
      const response = await axios.post(`${API}/feedback/retrain`, {
        dataset_id: dataset.id,
        model_name: modelName,
        target_column: 'target' // Adjust based on your data
      });

      setProgress(80);
      setProgressMessage('Evaluating new model...');
      
      await new Promise(resolve => setTimeout(resolve, 300));
      
      setProgress(100);
      setProgressMessage('Retraining complete!');

      toast.success(
        `Model retrained with ${response.data.feedback_samples} feedback samples!`
      );
      
      loadStats(); // Refresh stats
    } catch (error) {
      toast.error('Retraining failed: ' + (error.response?.data?.detail || error.message));
    } finally {
      setTimeout(() => {
        setRetraining(false);
        setProgress(0);
        setProgressMessage('');
      }, 500);
    }
  };

  if (!stats && !loading) {
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
      {/* Retraining Progress */}
      {retraining && (
        <Card className="p-6 bg-gradient-to-r from-green-50 to-blue-50">
          <div className="text-center">
            <Loader2 className="w-12 h-12 animate-spin mx-auto mb-4 text-green-600" />
            <h3 className="text-lg font-semibold mb-2">{progressMessage}</h3>
            <div className="w-full bg-gray-200 rounded-full h-3 mb-2">
              <div 
                className="bg-gradient-to-r from-green-600 to-blue-600 h-3 rounded-full transition-all duration-500"
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
              📊 Model Feedback & Performance
            </h3>

            {/* Stats Grid */}
            <div className="grid grid-cols-4 gap-4 mb-6">
              <div className="bg-blue-50 p-4 rounded">
                <div className="text-sm text-gray-600">Total Feedback</div>
                <div className="text-2xl font-bold text-blue-600">
                  {stats.feedback_count || 0}
                </div>
              </div>
              <div className="bg-green-50 p-4 rounded">
                <div className="text-sm text-gray-600">Correct</div>
                <div className="text-2xl font-bold text-green-600">
                  {stats.correct_predictions || 0}
                </div>
              </div>
              <div className="bg-red-50 p-4 rounded">
                <div className="text-sm text-gray-600">Incorrect</div>
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