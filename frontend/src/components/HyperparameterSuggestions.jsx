import { useState, useEffect } from 'react';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Lightbulb, CheckCircle, Info, TrendingUp } from 'lucide-react';
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from '@/components/ui/tooltip';

const HyperparameterSuggestions = ({ suggestions, onApply }) => {
  if (!suggestions || Object.keys(suggestions).length === 0) {
    return (
      <Card className="p-6 text-center">
        <Lightbulb className="w-12 h-12 mx-auto text-gray-400 mb-3" />
        <p className="text-gray-600">No hyperparameter suggestions available</p>
        <p className="text-sm text-gray-500 mt-2">Run an analysis with AutoML enabled to get AI-powered tuning recommendations</p>
      </Card>
    );
  }

  const modelSuggestions = Object.entries(suggestions).map(([modelName, params]) => ({
    modelName,
    params
  }));

  const [expandedModels, setExpandedModels] = useState([]);

  const toggleModel = (modelName) => {
    setExpandedModels(prev =>
      prev.includes(modelName)
        ? prev.filter(m => m !== modelName)
        : [...prev, modelName]
    );
  };

  const formatModelName = (name) => {
    return name.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
  };

  const getParameterExplanation = (paramName) => {
    const explanations = {
      'n_estimators': 'Number of trees in the forest. More trees = better accuracy but slower training',
      'max_depth': 'Maximum depth of trees. Controls model complexity and overfitting',
      'min_samples_split': 'Minimum samples required to split a node. Higher = more generalization',
      'min_samples_leaf': 'Minimum samples in a leaf node. Controls tree granularity',
      'max_features': 'Number of features to consider for best split',
      'learning_rate': 'Step size for gradient descent. Lower = more precise but slower',
      'subsample': 'Fraction of samples used for training each tree',
      'alpha': 'Regularization strength. Higher = more regularization',
      'C': 'Inverse of regularization strength. Lower = more regularization',
      'gamma': 'Kernel coefficient. Affects decision boundary complexity',
      'n_neighbors': 'Number of neighbors to consider for classification'
    };
    return explanations[paramName] || 'Hyperparameter for model tuning';
  };

  return (
    <div className="space-y-4">
      <div className="flex items-center gap-2 mb-4">
        <Lightbulb className="w-5 h-5 text-yellow-500" />
        <h3 className="text-lg font-semibold">AI-Powered Hyperparameter Suggestions</h3>
      </div>

      <Card className="p-4 bg-blue-50 border-blue-200">
        <div className="flex items-start gap-3">
          <Info className="w-5 h-5 text-blue-600 mt-0.5" />
          <div>
            <p className="text-sm font-medium text-blue-900">About These Suggestions</p>
            <p className="text-sm text-blue-700 mt-1">
              Our AI has analyzed your dataset characteristics and problem type to recommend optimal parameter ranges.
              These suggestions are based on proven best practices and dataset-specific patterns.
            </p>
            <p className="text-sm text-blue-700 mt-2">
              <strong>Why different models have different parameter counts:</strong> Simpler models like Linear Regression 
              have fewer hyperparameters (mainly regularization), while complex models like XGBoost have many parameters 
              to control tree growth, learning rate, and sampling strategies.
            </p>
          </div>
        </div>
      </Card>

      <div className="space-y-3">
        {modelSuggestions.map(({ modelName, params }) => {
          const isExpanded = expandedModels.includes(modelName);
          const paramEntries = Object.entries(params);
          
          return (
            <Card key={modelName} className="overflow-hidden">
              <div
                className="p-4 cursor-pointer hover:bg-gray-50 flex items-center justify-between"
                onClick={() => toggleModel(modelName)}
              >
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 bg-purple-100 rounded-full flex items-center justify-center">
                    <TrendingUp className="w-5 h-5 text-purple-600" />
                  </div>
                  <div>
                    <h4 className="font-semibold">{formatModelName(modelName)}</h4>
                    <p className="text-sm text-gray-600">{paramEntries.length} parameters suggested</p>
                  </div>
                </div>
                <Button variant="ghost" size="sm">
                  {isExpanded ? '▲' : '▼'}
                </Button>
              </div>

              {isExpanded && (
                <div className="border-t bg-gray-50 p-4">
                  <div className="space-y-3">
                    {paramEntries.map(([paramName, value]) => (
                      <div key={paramName} className="bg-white p-3 rounded border">
                        <div className="flex items-start justify-between mb-2">
                          <div className="flex items-center gap-2">
                            <span className="font-medium text-gray-900">{paramName}</span>
                            <TooltipProvider>
                              <Tooltip>
                                <TooltipTrigger>
                                  <Info className="w-4 h-4 text-gray-400" />
                                </TooltipTrigger>
                                <TooltipContent>
                                  <p className="max-w-xs">{getParameterExplanation(paramName)}</p>
                                </TooltipContent>
                              </Tooltip>
                            </TooltipProvider>
                          </div>
                          <span className="px-2 py-1 bg-green-100 text-green-700 rounded text-sm font-medium">
                            Recommended
                          </span>
                        </div>
                        <div className="text-sm text-gray-700">
                          <span className="font-semibold">Suggested Value: </span>
                          {typeof value === 'object' && value !== null ? (
                            <span className="text-blue-600">
                              Range: {value.min} - {value.max} (optimal: {value.optimal || value.default})
                            </span>
                          ) : (
                            <span className="text-blue-600">{String(value)}</span>
                          )}
                        </div>
                        <p className="text-xs text-gray-500 mt-1">
                          {getParameterExplanation(paramName)}
                        </p>
                      </div>
                    ))}
                  </div>

                  {onApply && (
                    <div className="mt-4 pt-4 border-t">
                      <Button
                        onClick={() => onApply(modelName, params)}
                        className="w-full bg-purple-600 hover:bg-purple-700"
                      >
                        <CheckCircle className="w-4 h-4 mr-2" />
                        Apply These Parameters
                      </Button>
                    </div>
                  )}
                </div>
              )}
            </Card>
          );
        })}
      </div>

      <Card className="p-4 bg-green-50 border-green-200">
        <div className="flex items-start gap-3">
          <CheckCircle className="w-5 h-5 text-green-600 mt-0.5" />
          <div>
            <p className="text-sm font-medium text-green-900">Next Steps</p>
            <ul className="text-sm text-green-700 mt-1 space-y-1 list-disc list-inside">
              <li>Review each suggestion and understand the parameter impact</li>
              <li>Apply parameters to re-run training with optimized settings</li>
              <li>Compare results with baseline to measure improvement</li>
            </ul>
          </div>
        </div>
      </Card>
    </div>
  );
};

export default HyperparameterSuggestions;
