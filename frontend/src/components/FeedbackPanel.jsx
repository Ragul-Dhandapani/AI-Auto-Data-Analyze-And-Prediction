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
    try {
      const response = await axios.post(`${API}/feedback/retrain`, {
        dataset_id: dataset.id,
        model_name: modelName,
        target_column: 'target' // Adjust based on your data
      });

      toast.success(
        `Model retrained with ${response.data.feedback_samples} feedback samples!`
      );
      
    } catch (error) {
      toast.error('Retraining failed: ' + (error.response?.data?.detail || error.message));
    } finally {
      setRetraining(false);
    }
  };

  if (!stats) {
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
      <Card className="p-6">
        <h3 className="text-xl font-bold mb-4 flex items-center gap-2">
          📊 Model Feedback & Performance
        </h3>

        {/* Stats Grid */}
        <div className="grid grid-cols-4 gap-4 mb-6">
          <div className="bg-blue-50 p-4 rounded">
            <div className="text-sm text-gray-600">Total Feedback</div>
            <div className="text-2xl font-bold text-blue-600">
              {stats.feedback_count}
            </div>
          </div>
          
          <div className="bg-green-50 p-4 rounded">
            <div className="text-sm text-gray-600">Correct</div>
            <div className="text-2xl font-bold text-green-600">
              {stats.correct_predictions}
            </div>
          </div>
          
          <div className="bg-red-50 p-4 rounded">
            <div className="text-sm text-gray-600">Incorrect</div>
            <div className="text-2xl font-bold text-red-600">
              {stats.incorrect_predictions}
            </div>
          </div>
          
          <div className="bg-purple-50 p-4 rounded">
            <div className="text-sm text-gray-600">Accuracy</div>
            <div className="text-2xl font-bold text-purple-600">
              {stats.accuracy ? (stats.accuracy * 100).toFixed(1) : 'N/A'}%
            </div>
          </div>
        </div>

        {/* Retrain Button */}
        {stats.feedback_count > 0 && (
          <Button
            onClick={retrainModel}
            disabled={retraining}
            className="w-full"
          >
            {retraining ? (
              <><Loader2 className="w-4 h-4 animate-spin mr-2" /> Retraining...</>
            ) : (
              <><TrendingUp className="w-4 h-4 mr-2" /> Retrain Model with Feedback</>
            )}
          </Button>
        )}

        {stats.feedback_count === 0 && (
          <div className="text-center text-gray-500 py-8">
            <MessageSquare className="w-12 h-12 mx-auto mb-2 text-gray-400" />
            <p>No feedback yet. Start making predictions and submit feedback!</p>
          </div>
        )}
      </Card>

      {/* Feedback List */}
      {feedbackList.length > 0 && (
        <Card className="p-6">
          <h4 className="font-semibold mb-4">📝 Recent Feedback</h4>
          <div className="space-y-3">
            {feedbackList.slice(0, 10).map((item, idx) => (
              <div key={idx} className="border-b pb-3">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    {item.is_correct ? (
                      <ThumbsUp className="w-4 h-4 text-green-600" />
                    ) : (
                      <ThumbsDown className="w-4 h-4 text-red-600" />
                    )}
                    <span className="text-sm font-medium">
                      Prediction: {item.prediction}
                    </span>
                  </div>
                  {item.actual_outcome && (
                    <span className="text-sm text-gray-600">
                      Actual: {item.actual_outcome}
                    </span>
                  )}
                </div>
                {item.feedback?.user_comment && (
                  <p className="text-xs text-gray-500 mt-1">
                    {item.feedback.user_comment}
                  </p>
                )}
              </div>
            ))}
          </div>
        </Card>
      )}
    </div>
  );
};

export default FeedbackPanel;
