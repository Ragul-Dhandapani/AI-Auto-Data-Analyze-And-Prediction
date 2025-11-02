import { useState, useEffect } from 'react';
import axios from 'axios';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Label } from '@/components/ui/label';
import { toast } from 'sonner';
import { Loader2, Calendar, TrendingUp, AlertTriangle } from 'lucide-react';
import Plot from 'react-plotly.js';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const TimeSeriesAnalysis = ({ dataset, cachedResults, onComplete }) => {
  const [loading, setLoading] = useState(false);
  const [progress, setProgress] = useState(0);
  const [progressMessage, setProgressMessage] = useState('');
  const [timeColumn, setTimeColumn] = useState('');
  const [targetColumn, setTargetColumn] = useState('');
  const [forecastPeriods, setForecastPeriods] = useState(30);
  const [forecastMethod, setForecastMethod] = useState('prophet');
  const [results, setResults] = useState(cachedResults || null);
  const [datetimeColumns, setDatetimeColumns] = useState([]);

  // Update results when cache changes
  useEffect(() => {
    if (cachedResults) {
      setResults(cachedResults);
    }
  }, [cachedResults]);

  const detectDatetimeColumns = async () => {
    try {
      const response = await axios.get(`${API}/datetime-columns/${dataset.id}`);
      setDatetimeColumns(response.data.datetime_columns || []);
      if (response.data.datetime_columns?.length > 0) {
        setTimeColumn(response.data.datetime_columns[0]);
      }
      toast.success(`Found ${response.data.datetime_columns?.length || 0} datetime columns`);
    } catch (error) {
      toast.error('Failed to detect datetime columns');
    }
  };

  const runTimeSeriesAnalysis = async () => {
    if (!timeColumn || !targetColumn) {
      toast.error('Please select both time and target columns');
      return;
    }

    setLoading(true);
    setProgress(10);
    setProgressMessage('Loading time series data...');
    
    try {
      setProgress(30);
      setProgressMessage('Preparing temporal features...');
      
      await new Promise(resolve => setTimeout(resolve, 500));
      
      setProgress(50);
      setProgressMessage(`Running ${forecastMethod} forecasting...`);
      
      const response = await axios.post(`${API}/analysis/time-series`, {
        dataset_id: dataset.id,
        time_column: timeColumn,
        target_column: targetColumn,
        forecast_periods: forecastPeriods,
        forecast_method: forecastMethod
      });

      setProgress(80);
      setProgressMessage('Detecting anomalies...');
      
      await new Promise(resolve => setTimeout(resolve, 300));
      
      setProgress(100);
      setProgressMessage('Analysis complete!');
      
      setResults(response.data);
      if (onComplete) onComplete(response.data);
      toast.success('Time series analysis complete!');
    } catch (error) {
      toast.error('Analysis failed: ' + (error.response?.data?.detail || error.message));
    } finally {
      setTimeout(() => {
        setLoading(false);
        setProgress(0);
        setProgressMessage('');
      }, 500);
    }
  };

  const numericColumns = dataset.columns?.filter(col => {
    const dtype = dataset.dtypes?.[col];
    return dtype && ['int64', 'float64', 'int32', 'float32'].includes(dtype);
  }) || [];

  return (
    <div className="space-y-6">
      {/* Loading Progress */}
      {loading && (
        <Card className="p-6 bg-gradient-to-r from-blue-50 to-purple-50">
          <div className="text-center">
            <Loader2 className="w-12 h-12 animate-spin mx-auto mb-4 text-blue-600" />
            <h3 className="text-lg font-semibold mb-2">{progressMessage}</h3>
            <div className="w-full bg-gray-200 rounded-full h-3 mb-2">
              <div 
                className="bg-gradient-to-r from-blue-600 to-purple-600 h-3 rounded-full transition-all duration-500"
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
            <Calendar className="w-6 h-6" />
            Time Series Forecasting & Anomaly Detection
          </h2>

          <div className="space-y-4">
          {/* Detect Datetime Columns */}
          <Button onClick={detectDatetimeColumns} variant="outline">
            🔍 Detect Datetime Columns
          </Button>

          {/* Time Column Selection */}
          <div>
            <Label>Time/Date Column</Label>
            <select
              className="w-full p-2 border rounded mt-1"
              value={timeColumn}
              onChange={(e) => setTimeColumn(e.target.value)}
            >
              <option value="">-- Select Time Column --</option>
              {datetimeColumns.map(col => (
                <option key={col} value={col}>{col}</option>
              ))}
              {dataset.columns?.map(col => (
                <option key={col} value={col}>{col}</option>
              ))}
            </select>
          </div>

          {/* Target Column Selection */}
          <div>
            <Label>Target Column (to forecast)</Label>
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

          {/* Forecast Method */}
          <div>
            <Label>Forecast Method</Label>
            <div className="grid grid-cols-3 gap-3 mt-2">
              <Card
                className={`p-3 cursor-pointer border-2 ${forecastMethod === 'prophet' ? 'border-blue-500 bg-blue-50' : 'border-gray-200'}`}
                onClick={() => setForecastMethod('prophet')}
              >
                <div className="font-semibold">📈 Prophet</div>
                <div className="text-xs text-gray-600">Facebook's forecasting</div>
              </Card>
              <Card
                className={`p-3 cursor-pointer border-2 ${forecastMethod === 'lstm' ? 'border-purple-500 bg-purple-50' : 'border-gray-200'}`}
                onClick={() => setForecastMethod('lstm')}
              >
                <div className="font-semibold">🧠 LSTM</div>
                <div className="text-xs text-gray-600">Deep learning</div>
              </Card>
              <Card
                className={`p-3 cursor-pointer border-2 ${forecastMethod === 'both' ? 'border-green-500 bg-green-50' : 'border-gray-200'}`}
                onClick={() => setForecastMethod('both')}
              >
                <div className="font-semibold">🔄 Both</div>
                <div className="text-xs text-gray-600">Compare methods</div>
              </Card>
            </div>
          </div>

          {/* Forecast Periods */}
          <div>
            <Label>Forecast Periods</Label>
            <input
              type="number"
              className="w-full p-2 border rounded mt-1"
              value={forecastPeriods}
              onChange={(e) => setForecastPeriods(parseInt(e.target.value))}
              min={1}
              max={365}
            />
            <p className="text-xs text-gray-600 mt-1">Number of future time periods to forecast</p>
          </div>

          {/* Run Analysis Button */}
          <Button
            onClick={runTimeSeriesAnalysis}
            disabled={loading || !timeColumn || !targetColumn}
            className="w-full"
          >
            {loading ? (
              <><Loader2 className="w-4 h-4 animate-spin mr-2" /> Analyzing...</>
            ) : (
              <><TrendingUp className="w-4 h-4 mr-2" /> Run Time Series Analysis</>
            )}
          </Button>
        </div>
      </Card>
      )}

      {/* Results Display */}
      {results && (
        <div className="space-y-6">
          {/* Prophet Results */}
          {results.prophet_forecast && results.prophet_forecast.success && (
            <Card className="p-6">
              <h3 className="text-xl font-bold mb-4 flex items-center gap-2">
                📈 Prophet Forecast Results
              </h3>
              
              {/* Metrics */}
              <div className="grid grid-cols-2 gap-4 mb-6">
                <div className="bg-blue-50 p-4 rounded">
                  <div className="text-sm text-gray-600">MAPE</div>
                  <div className="text-2xl font-bold text-blue-600">
                    {results.prophet_forecast.metrics?.mape?.toFixed(2)}%
                  </div>
                </div>
                <div className="bg-purple-50 p-4 rounded">
                  <div className="text-sm text-gray-600">RMSE</div>
                  <div className="text-2xl font-bold text-purple-600">
                    {results.prophet_forecast.metrics?.rmse?.toFixed(2)}
                  </div>
                </div>
              </div>

              {/* Forecast Chart */}
              {results.prophet_forecast.forecast_data && (
                <Plot
                  data={[
                    {
                      x: results.prophet_forecast.historical_data.dates,
                      y: results.prophet_forecast.historical_data.values,
                      type: 'scatter',
                      mode: 'lines',
                      name: 'Historical',
                      line: { color: 'blue' }
                    },
                    {
                      x: results.prophet_forecast.forecast_data.dates,
                      y: results.prophet_forecast.forecast_data.values,
                      type: 'scatter',
                      mode: 'lines',
                      name: 'Forecast',
                      line: { color: 'red', dash: 'dash' }
                    },
                    {
                      x: results.prophet_forecast.forecast_data.dates,
                      y: results.prophet_forecast.forecast_data.upper_bound,
                      type: 'scatter',
                      mode: 'lines',
                      name: 'Upper Bound',
                      line: { color: 'rgba(255,0,0,0.2)', width: 0 },
                      fill: 'tonexty',
                      fillcolor: 'rgba(255,0,0,0.1)'
                    },
                    {
                      x: results.prophet_forecast.forecast_data.dates,
                      y: results.prophet_forecast.forecast_data.lower_bound,
                      type: 'scatter',
                      mode: 'lines',
                      name: 'Lower Bound',
                      line: { color: 'rgba(255,0,0,0.2)' }
                    }
                  ]}
                  layout={{
                    title: `${targetColumn} Forecast`,
                    xaxis: { title: 'Date' },
                    yaxis: { title: targetColumn },
                    height: 400
                  }}
                  config={{ responsive: true }}
                  style={{ width: '100%' }}
                />
              )}
            </Card>
          )}

          {/* LSTM Results */}
          {results.lstm_forecast && results.lstm_forecast.success && (
            <Card className="p-6">
              <h3 className="text-xl font-bold mb-4 flex items-center gap-2">
                🧠 LSTM Forecast Results
              </h3>
              
              {/* Metrics */}
              <div className="grid grid-cols-2 gap-4 mb-6">
                <div className="bg-purple-50 p-4 rounded">
                  <div className="text-sm text-gray-600">MAPE</div>
                  <div className="text-2xl font-bold text-purple-600">
                    {results.lstm_forecast.metrics?.mape?.toFixed(2)}%
                  </div>
                </div>
                <div className="bg-blue-50 p-4 rounded">
                  <div className="text-sm text-gray-600">RMSE</div>
                  <div className="text-2xl font-bold text-blue-600">
                    {results.lstm_forecast.metrics?.rmse?.toFixed(2)}
                  </div>
                </div>
              </div>

              {/* Forecast Chart */}
              {results.lstm_forecast.forecast_data && (
                <Plot
                  data={[
                    {
                      x: results.lstm_forecast.historical_data.dates,
                      y: results.lstm_forecast.historical_data.values,
                      type: 'scatter',
                      mode: 'lines',
                      name: 'Historical',
                      line: { color: 'blue' }
                    },
                    {
                      x: results.lstm_forecast.forecast_data.dates,
                      y: results.lstm_forecast.forecast_data.values,
                      type: 'scatter',
                      mode: 'lines',
                      name: 'LSTM Forecast',
                      line: { color: 'purple', dash: 'dash' }
                    }
                  ]}
                  layout={{
                    title: `${targetColumn} LSTM Forecast`,
                    xaxis: { title: 'Date' },
                    yaxis: { title: targetColumn },
                    height: 400
                  }}
                  config={{ responsive: true }}
                  style={{ width: '100%' }}
                />
              )}
            </Card>
          )}

          {/* Anomaly Detection */}
          {results.anomaly_detection && results.anomaly_detection.success && (
            <Card className="p-6">
              <h3 className="text-xl font-bold mb-4 flex items-center gap-2">
                <AlertTriangle className="w-6 h-6 text-orange-600" />
                Anomaly Detection
              </h3>
              
              <div className="grid grid-cols-3 gap-4 mb-6">
                <div className="bg-orange-50 p-4 rounded">
                  <div className="text-sm text-gray-600">Anomalies Found</div>
                  <div className="text-2xl font-bold text-orange-600">
                    {results.anomaly_detection.anomaly_count}
                  </div>
                </div>
                <div className="bg-gray-50 p-4 rounded">
                  <div className="text-sm text-gray-600">Total Points</div>
                  <div className="text-2xl font-bold text-gray-600">
                    {results.anomaly_detection.total_points}
                  </div>
                </div>
                <div className="bg-red-50 p-4 rounded">
                  <div className="text-sm text-gray-600">Anomaly %</div>
                  <div className="text-2xl font-bold text-red-600">
                    {results.anomaly_detection.anomaly_percentage?.toFixed(2)}%
                  </div>
                </div>
              </div>

              <div className="text-sm text-gray-600">
                <strong>Method:</strong> {results.anomaly_detection.method}
              </div>
            </Card>
          )}
        </div>
      )}
    </div>
  );
};

export default TimeSeriesAnalysis;
