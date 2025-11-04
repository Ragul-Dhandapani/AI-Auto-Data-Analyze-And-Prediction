import { useState, useEffect } from 'react';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Label } from '@/components/ui/label';
import { toast } from 'sonner';
import { Loader2, Settings, Play, Zap } from 'lucide-react';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const HyperparameterTuning = ({ dataset, cachedResults, onComplete }) => {
  const [loading, setLoading] = useState(false);
  const [progress, setProgress] = useState(0);
  const [progressMessage, setProgressMessage] = useState('');
  const [targetColumn, setTargetColumn] = useState('');
  const [modelType, setModelType] = useState('random_forest');
  const [problemType, setProblemType] = useState('regression');
  const [searchType, setSearchType] = useState('grid');
  const [nIter, setNIter] = useState(20);
  const [results, setResults] = useState(cachedResults || null);
  
  // Custom parameter grid
  const [customParams, setCustomParams] = useState({
    n_estimators: '50,100,200',
    max_depth: '5,10,20',
    learning_rate: '0.01,0.1,0.2'
  });

  // Update results when cache changes
  useEffect(() => {
    if (cachedResults) {
      setResults(cachedResults);
    }
  }, [cachedResults]);

  const runTuning = async () => {
    if (!targetColumn) {
      toast.error('Please select a target column');
      return;
    }

    setLoading(true);
    setProgress(10);
    setProgressMessage('Initializing hyperparameter search...');
    
    try {
      setProgress(20);
      setProgressMessage('Preparing parameter grid...');
      
      // Parse custom params
      const paramGrid = {};
      Object.entries(customParams).forEach(([key, value]) => {
        if (value.trim()) {
          const values = value.split(',').map(v => {
            const trimmed = v.trim();
            const num = parseFloat(trimmed);
            if (!isNaN(num)) return num;
            if (trimmed.toLowerCase() === 'none') return null;
            return trimmed;
          });
          paramGrid[key] = values;
        }
      });

      await new Promise(resolve => setTimeout(resolve, 200));
      
      setProgress(40);
      setProgressMessage(`Running ${searchType} search with cross-validation...`);

      const response = await axios.post(`${API}/analysis/hyperparameter-tuning`, {
        dataset_id: dataset.id,
        target_column: targetColumn,
        model_type: modelType,
        problem_type: problemType,
        search_type: searchType,
        param_grid: Object.keys(paramGrid).length > 0 ? paramGrid : null,
        n_iter: searchType === 'random' ? nIter : undefined
      });

      setProgress(80);
      setProgressMessage('Evaluating best parameters...');
      
      await new Promise(resolve => setTimeout(resolve, 200));
      
      setProgress(100);
      setProgressMessage('Tuning complete!');

      setResults(response.data);
      toast.success('Hyperparameter tuning complete!');
      if (onComplete) onComplete(response.data);
    } catch (error) {
      toast.error('Tuning failed: ' + (error.response?.data?.detail || error.message));
    } finally {
      setTimeout(() => {
        setLoading(false);
        setProgress(0);
        setProgressMessage('');
      }, 300);
    }
  };

  const numericColumns = dataset.columns?.filter(col => {
    const dtype = dataset.dtypes?.[col];
    return dtype && ['int64', 'float64', 'int32', 'float32'].includes(dtype);
  }) || [];

  return (
    <div className="space-y-6">
      {/* Tab Description */}
      <Card className="p-4 bg-gradient-to-r from-indigo-50 to-purple-50 border-indigo-200">
        <div className="flex items-start gap-3">
          <div className="p-2 bg-indigo-500 rounded-lg">
            <Zap className="w-5 h-5 text-white" />
          </div>
          <div className="flex-1">
            <h3 className="font-semibold text-indigo-900 mb-2 flex items-center gap-2">
              🎯 Hyperparameter Tuning - Optimize Your ML Models
            </h3>
            <div className="space-y-2">
              <p className="text-sm text-indigo-700">
                <strong>🔧 What it does:</strong> Automatically finds the best configuration for your ML models by intelligently testing different parameter combinations using cross-validation.
              </p>
              <p className="text-sm text-indigo-700">
                <strong>✅ How it helps:</strong> The tuned hyperparameters are <span className="font-semibold underline">automatically applied</span> to improve your Predictive Analysis models, potentially boosting accuracy by 10-30%.
              </p>
              <p className="text-sm text-indigo-600 mt-2">
                <strong>💡 Benefits:</strong> Maximum accuracy, optimal settings discovery, reduced overfitting, better generalization, time-saving automation.
              </p>
              <p className="text-xs text-indigo-500 italic mt-2">
                Note: After tuning, re-run Predictive Analysis to see the improvements with optimized parameters.
              </p>
            </div>
          </div>
        </div>
      </Card>

      {/* Loading Progress */}
      {loading && (
        <Card className="p-6 bg-gradient-to-r from-indigo-50 to-purple-50">
          <div className="text-center">
            <Loader2 className="w-12 h-12 animate-spin mx-auto mb-4 text-indigo-600" />
            <h3 className="text-lg font-semibold mb-2">{progressMessage}</h3>
            <div className="w-full bg-gray-200 rounded-full h-3 mb-2">
              <div 
                className="bg-gradient-to-r from-indigo-600 to-purple-600 h-3 rounded-full transition-all duration-300"
                style={{ width: `${progress}%` }}
              ></div>
            </div>
            <p className="text-sm text-gray-600">{progress}% Complete</p>
          </div>
        </Card>
      )}

      {!loading && (
        <Card className="p-6">
          <h2 className="text-2xl font-bold mb-4 flex items-center gap-2">
            <Settings className="w-6 h-6" />
            Hyperparameter Configuration
          </h2>

          <div className="space-y-4">
            {/* Target Column */}
            <div>
              <Label>Target Column</Label>
              <select
                className="w-full p-2 border rounded mt-1"
                value={targetColumn}
                onChange={(e) => setTargetColumn(e.target.value)}
              >
                <option value="">-- Select Target Column --</option>
                {numericColumns.map(col => (
                  <option key={col} value={col}>{col}</option>
                ))}
              </select>
            </div>

            {/* Model Type Selection */}
            <div>
              <Label>Model Type</Label>
              <div className="grid grid-cols-3 gap-3 mt-2">
                {['random_forest', 'xgboost', 'lightgbm'].map(model => (
                  <button
                    key={model}
                    className={`p-3 rounded border-2 transition-all ${
                      modelType === model
                        ? 'border-indigo-600 bg-indigo-50'
                        : 'border-gray-300 hover:border-indigo-300'
                    }`}
                    onClick={() => setModelType(model)}
                  >
                    <div className="font-semibold capitalize">{model.replace('_', ' ')}</div>
                  </button>
                ))}
              </div>
            </div>

            {/* Problem Type */}
            <div>
              <Label>Problem Type</Label>
              <select
                className="w-full p-2 border rounded mt-1"
                value={problemType}
                onChange={(e) => setProblemType(e.target.value)}
              >
                <option value="regression">Regression</option>
                <option value="classification">Classification</option>
              </select>
            </div>

            {/* Search Type */}
            <div>
              <Label>Search Strategy</Label>
              <div className="grid grid-cols-2 gap-3 mt-2">
                <button
                  className={`p-3 rounded border-2 transition-all ${
                    searchType === 'grid'
                      ? 'border-indigo-600 bg-indigo-50'
                      : 'border-gray-300 hover:border-indigo-300'
                  }`}
                  onClick={() => setSearchType('grid')}
                >
                  <div className="font-semibold">Grid Search</div>
                  <div className="text-xs text-gray-600 mt-1">Exhaustive search</div>
                </button>
                <button
                  className={`p-3 rounded border-2 transition-all ${
                    searchType === 'random'
                      ? 'border-indigo-600 bg-indigo-50'
                      : 'border-gray-300 hover:border-indigo-300'
                  }`}
                  onClick={() => setSearchType('random')}
                >
                  <div className="font-semibold">Random Search</div>
                  <div className="text-xs text-gray-600 mt-1">Faster, good results</div>
                </button>
              </div>
            </div>

            {/* N Iterations (for random search) */}
            {searchType === 'random' && (
              <div>
                <Label>Number of Iterations</Label>
                <input
                  type="number"
                  className="w-full p-2 border rounded mt-1"
                  value={nIter}
                  onChange={(e) => setNIter(parseInt(e.target.value))}
                  min="5"
                  max="100"
                />
              </div>
            )}

            {/* Custom Parameters */}
            <div className="border rounded p-4 bg-gray-50">
              <Label className="mb-3 block">Custom Parameters (comma-separated)</Label>
              <div className="space-y-2">
                <div>
                  <label className="text-sm text-gray-600">n_estimators</label>
                  <input
                    type="text"
                    className="w-full p-2 border rounded mt-1"
                    value={customParams.n_estimators}
                    onChange={(e) => setCustomParams({...customParams, n_estimators: e.target.value})}
                    placeholder="e.g., 50,100,200"
                  />
                </div>
                <div>
                  <label className="text-sm text-gray-600">max_depth</label>
                  <input
                    type="text"
                    className="w-full p-2 border rounded mt-1"
                    value={customParams.max_depth}
                    onChange={(e) => setCustomParams({...customParams, max_depth: e.target.value})}
                    placeholder="e.g., 5,10,20"
                  />
                </div>
                <div>
                  <label className="text-sm text-gray-600">learning_rate</label>
                  <input
                    type="text"
                    className="w-full p-2 border rounded mt-1"
                    value={customParams.learning_rate}
                    onChange={(e) => setCustomParams({...customParams, learning_rate: e.target.value})}
                    placeholder="e.g., 0.01,0.1,0.2"
                  />
                </div>
              </div>
            </div>

            <Button onClick={runTuning} className="w-full" disabled={!targetColumn}>
              <Play className="w-4 h-4 mr-2" />
              Start Tuning
            </Button>
          </div>
        </Card>
      )}

      {/* Results */}
      {results && !loading && (
        <Card className="p-6">
          <h3 className="text-xl font-bold mb-4">Tuning Results</h3>
          
          <div className="bg-gradient-to-r from-green-50 to-blue-50 p-6 rounded-lg mb-4">
            <div className="text-center">
              <div className="text-sm text-gray-600 mb-2">Best Score</div>
              <div className="text-4xl font-bold text-green-600">
                {(results.best_score * 100).toFixed(2)}%
              </div>
            </div>
          </div>

          <div className="bg-gray-50 p-4 rounded mb-4">
            <h4 className="font-semibold mb-2">Best Parameters:</h4>
            <pre className="text-sm bg-white p-3 rounded overflow-x-auto">
              {JSON.stringify(results.best_params, null, 2)}
            </pre>
          </div>

          {results.cv_results && (
            <div className="bg-gray-50 p-4 rounded">
              <h4 className="font-semibold mb-2">Cross-Validation Summary:</h4>
              <div className="text-sm space-y-1">
                <div>Total combinations tested: <strong>{results.cv_results.n_splits || 'N/A'}</strong></div>
                <div>Best CV score: <strong>{(results.best_score * 100).toFixed(2)}%</strong></div>
              </div>
            </div>
          )}
        </Card>
      )}
    </div>
  );
};

export default HyperparameterTuning;