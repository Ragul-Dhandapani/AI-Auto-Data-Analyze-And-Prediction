import { useState } from 'react';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Label } from '@/components/ui/label';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { toast } from 'sonner';
import { Loader2, Settings, Play } from 'lucide-react';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const HyperparameterTuning = ({ dataset, cachedResults, onComplete }) => {
  const [loading, setLoading] = useState(false);
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
    try {
      // Parse custom params
      const paramGrid = {};
      Object.entries(customParams).forEach(([key, value]) => {
        if (value.trim()) {
          const values = value.split(',').map(v => {
            const trimmed = v.trim();
            // Try to parse as number
            const num = parseFloat(trimmed);
            if (!isNaN(num)) return num;
            // Try to parse as None/null
            if (trimmed.toLowerCase() === 'none') return null;
            // Return as string
            return trimmed;
          });
          paramGrid[key] = values;
        }
      });

      const response = await axios.post(`${API}/analysis/hyperparameter-tuning`, {
        dataset_id: dataset.id,
        target_column: targetColumn,
        model_type: modelType,
        problem_type: problemType,
        search_type: searchType,
        param_grid: Object.keys(paramGrid).length > 0 ? paramGrid : null,
        n_iter: searchType === 'random' ? nIter : undefined
      });

      setResults(response.data);
      toast.success('Hyperparameter tuning complete!');
      if (onComplete) onComplete(response.data);
    } catch (error) {
      toast.error('Tuning failed: ' + (error.response?.data?.detail || error.message));
    } finally {
      setLoading(false);
    }
  };

  const numericColumns = dataset.columns?.filter(col => {
    const dtype = dataset.dtypes?.[col];
    return dtype && ['int64', 'float64', 'int32', 'float32'].includes(dtype);
  }) || [];

  return (
    <div className="space-y-6">
      <Card className="p-6">
        <h2 className="text-2xl font-bold mb-4 flex items-center gap-2">
          <Settings className="w-6 h-6" />
          Hyperparameter Tuning
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
              <option value="">-- Select Target --</option>
              {numericColumns.map(col => (
                <option key={col} value={col}>{col}</option>
              ))}
            </select>
          </div>

          {/* Model Type */}
          <div>
            <Label>Model Type</Label>
            <div className="grid grid-cols-3 gap-3 mt-2">
              <Card
                className={`p-3 cursor-pointer border-2 ${modelType === 'random_forest' ? 'border-green-500 bg-green-50' : 'border-gray-200'}`}
                onClick={() => setModelType('random_forest')}
              >
                <div className="font-semibold text-sm">🌳 Random Forest</div>
              </Card>
              <Card
                className={`p-3 cursor-pointer border-2 ${modelType === 'xgboost' ? 'border-blue-500 bg-blue-50' : 'border-gray-200'}`}
                onClick={() => setModelType('xgboost')}
              >
                <div className="font-semibold text-sm">⚡ XGBoost</div>
              </Card>
              <Card
                className={`p-3 cursor-pointer border-2 ${modelType === 'lightgbm' ? 'border-purple-500 bg-purple-50' : 'border-gray-200'}`}
                onClick={() => setModelType('lightgbm')}
              >
                <div className="font-semibold text-sm">💡 LightGBM</div>
              </Card>
            </div>
          </div>

          {/* Problem Type */}
          <div>
            <Label>Problem Type</Label>
            <div className="grid grid-cols-2 gap-3 mt-2">
              <Card
                className={`p-3 cursor-pointer border-2 ${problemType === 'regression' ? 'border-green-500 bg-green-50' : 'border-gray-200'}`}
                onClick={() => setProblemType('regression')}
              >
                <div className="font-semibold text-sm">📈 Regression</div>
              </Card>
              <Card
                className={`p-3 cursor-pointer border-2 ${problemType === 'classification' ? 'border-purple-500 bg-purple-50' : 'border-gray-200'}`}
                onClick={() => setProblemType('classification')}
              >
                <div className="font-semibold text-sm">🎯 Classification</div>
              </Card>
            </div>
          </div>

          {/* Search Type */}
          <div>
            <Label>Search Type</Label>
            <div className="grid grid-cols-2 gap-3 mt-2">
              <Card
                className={`p-3 cursor-pointer border-2 ${searchType === 'grid' ? 'border-blue-500 bg-blue-50' : 'border-gray-200'}`}
                onClick={() => setSearchType('grid')}
              >
                <div className="font-semibold text-sm">🧩 Grid Search</div>
                <div className="text-xs text-gray-600">Exhaustive search</div>
              </Card>
              <Card
                className={`p-3 cursor-pointer border-2 ${searchType === 'random' ? 'border-orange-500 bg-orange-50' : 'border-gray-200'}`}
                onClick={() => setSearchType('random')}
              >
                <div className="font-semibold text-sm">🎲 Random Search</div>
                <div className="text-xs text-gray-600">Faster, good enough</div>
              </Card>
            </div>
          </div>

          {/* Number of iterations for random search */}
          {searchType === 'random' && (
            <div>
              <Label>Number of Iterations</Label>
              <input
                type="number"
                className="w-full p-2 border rounded mt-1"
                value={nIter}
                onChange={(e) => setNIter(parseInt(e.target.value))}
                min={5}
                max={100}
              />
            </div>
          )}

          {/* Custom Parameters */}
          <div>
            <Label>Custom Parameters (optional)</Label>
            <div className="space-y-2 mt-2">
              <div>
                <label className="text-sm text-gray-600">n_estimators (comma-separated)</label>
                <input
                  type="text"
                  className="w-full p-2 border rounded"
                  value={customParams.n_estimators}
                  onChange={(e) => setCustomParams({...customParams, n_estimators: e.target.value})}
                  placeholder="50,100,200"
                />
              </div>
              <div>
                <label className="text-sm text-gray-600">max_depth (comma-separated)</label>
                <input
                  type="text"
                  className="w-full p-2 border rounded"
                  value={customParams.max_depth}
                  onChange={(e) => setCustomParams({...customParams, max_depth: e.target.value})}
                  placeholder="5,10,20,none"
                />
              </div>
              {modelType === 'xgboost' && (
                <div>
                  <label className="text-sm text-gray-600">learning_rate (comma-separated)</label>
                  <input
                    type="text"
                    className="w-full p-2 border rounded"
                    value={customParams.learning_rate}
                    onChange={(e) => setCustomParams({...customParams, learning_rate: e.target.value})}
                    placeholder="0.01,0.1,0.2"
                  />
                </div>
              )}
            </div>
          </div>

          {/* Run Button */}
          <Button
            onClick={runTuning}
            disabled={loading || !targetColumn}
            className="w-full"
          >
            {loading ? (
              <><Loader2 className="w-4 h-4 animate-spin mr-2" /> Tuning...</>
            ) : (
              <><Play className="w-4 h-4 mr-2" /> Start Tuning</>
            )}
          </Button>
        </div>
      </Card>

      {/* Results */}
      {results && results.success && (
        <Card className="p-6">
          <h3 className="text-xl font-bold mb-4">✅ Tuning Results</h3>
          
          <div className="space-y-4">
            {/* Best Score */}
            <div className="bg-green-50 p-4 rounded">
              <div className="text-sm text-gray-600">Best Score</div>
              <div className="text-3xl font-bold text-green-600">
                {results.best_score?.toFixed(4)}
              </div>
            </div>

            {/* Best Parameters */}
            <div>
              <h4 className="font-semibold mb-2">🏆 Best Parameters</h4>
              <div className="bg-gray-50 p-4 rounded">
                <pre className="text-sm">
                  {JSON.stringify(results.best_params, null, 2)}
                </pre>
              </div>
            </div>

            {/* CV Results Summary */}
            {results.cv_results && (
              <div>
                <h4 className="font-semibold mb-2">📉 Cross-Validation Results</h4>
                <div className="text-sm text-gray-600">
                  Tested {results.cv_results.params?.length || 0} parameter combinations
                </div>
              </div>
            )}
          </div>
        </Card>
      )}
    </div>
  );
};

export default HyperparameterTuning;
