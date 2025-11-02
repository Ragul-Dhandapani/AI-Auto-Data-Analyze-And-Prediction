import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Card } from "@/components/ui/card";
import PredictiveAnalysis from './PredictiveAnalysis';
import TimeSeriesAnalysis from './TimeSeriesAnalysis';
import HyperparameterTuning from './HyperparameterTuning';
import FeedbackPanel from './FeedbackPanel';
import { BarChart3, TrendingUp, Settings, MessageSquare, Database } from 'lucide-react';

const AnalysisTabs = ({ dataset, analysisCache, onAnalysisUpdate, variableSelection }) => {
  const [tabResults, setTabResults] = useState({
    predictive: analysisCache || null,
    timeseries: null,
    hyperparameters: null,
    feedback: null
  });

  // Persist results across tab switches
  const handleTimeSeriesComplete = (results) => {
    setTabResults(prev => ({ ...prev, timeseries: results }));
  };

  const handleHyperparameterComplete = (results) => {
    setTabResults(prev => ({ ...prev, hyperparameters: results }));
  };

  return (
    <div className="w-full">
      <Tabs defaultValue="predictive" className="w-full">
        <TabsList className="grid w-full grid-cols-4 mb-6">
          <TabsTrigger value="predictive" className="flex items-center gap-2">
            <BarChart3 className="w-4 h-4" />
            Predictive Analysis & Forecasting
          </TabsTrigger>
          <TabsTrigger value="timeseries" className="flex items-center gap-2">
            <TrendingUp className="w-4 h-4" />
            Time Series
          </TabsTrigger>
          <TabsTrigger value="hyperparameters" className="flex items-center gap-2">
            <Settings className="w-4 h-4" />
            Tune Models
          </TabsTrigger>
          <TabsTrigger value="feedback" className="flex items-center gap-2">
            <MessageSquare className="w-4 h-4" />
            Feedback & Learning
          </TabsTrigger>
        </TabsList>

        <TabsContent value="predictive">
          <PredictiveAnalysis
            dataset={dataset}
            analysisCache={analysisCache}
            onAnalysisUpdate={onAnalysisUpdate}
            variableSelection={variableSelection}
          />
        </TabsContent>

        <TabsContent value="timeseries">
          <TimeSeriesAnalysis 
            dataset={dataset} 
            cachedResults={tabResults.timeseries}
            onComplete={handleTimeSeriesComplete}
          />
        </TabsContent>

        <TabsContent value="hyperparameters">
          <HyperparameterTuning 
            dataset={dataset}
            cachedResults={tabResults.hyperparameters}
            onComplete={handleHyperparameterComplete}
          />
        </TabsContent>

        <TabsContent value="feedback">
          <Card className="p-6">
            <div className="space-y-6">
              <div className="text-center">
                <h2 className="text-2xl font-bold mb-2">Active Learning & Model Improvement</h2>
                <p className="text-gray-600">
                  Track model performance and retrain based on user feedback
                </p>
              </div>
              
              {analysisCache?.ml_models && analysisCache.ml_models.length > 0 ? (
                <FeedbackPanel
                  dataset={dataset}
                  modelName={analysisCache.ml_models[0].model_name}
                />
              ) : (
                <div className="text-center text-gray-500 py-12">
                  <MessageSquare className="w-16 h-16 mx-auto mb-4 text-gray-400" />
                  <p>Run predictive analysis first to enable feedback tracking</p>
                </div>
              )}
            </div>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default AnalysisTabs;
