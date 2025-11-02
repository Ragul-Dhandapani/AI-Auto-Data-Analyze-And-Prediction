import { useState } from 'react';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from '@/components/ui/collapsible';
import { 
  BookOpen, Home, Database, Target, BarChart3, TrendingUp, 
  Settings, Lightbulb, MessageSquare, ThumbsUp, Link2, 
  ChevronDown, ChevronRight, AlertCircle, Info, CheckCircle,
  TrendingDown, Activity
} from 'lucide-react';
import { useNavigate } from 'react-router-dom';

const DocumentationPage = () => {
  const navigate = useNavigate();
  const [expandedSections, setExpandedSections] = useState({});

  const toggleSection = (section) => {
    setExpandedSections(prev => ({
      ...prev,
      [section]: !prev[section]
    }));
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50">
      {/* Header */}
      <div className="bg-white border-b shadow-sm sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <BookOpen className="w-8 h-8 text-blue-600" />
            <div>
              <h1 className="text-2xl font-bold text-gray-900">PROMISE AI Documentation</h1>
              <p className="text-sm text-gray-600">Enterprise Machine Learning Platform</p>
            </div>
          </div>
          <Button onClick={() => navigate('/')} variant="outline">
            <Home className="w-4 h-4 mr-2" />
            Back to Home
          </Button>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-6 py-8">
        <Tabs defaultValue="overview" className="w-full">
          <TabsList className="grid w-full grid-cols-7 mb-6">
            <TabsTrigger value="overview">Overview</TabsTrigger>
            <TabsTrigger value="architecture">Architecture</TabsTrigger>
            <TabsTrigger value="features">Features</TabsTrigger>
            <TabsTrigger value="metrics">Metrics Guide</TabsTrigger>
            <TabsTrigger value="insights">AI Insights</TabsTrigger>
            <TabsTrigger value="workflows">Workflows</TabsTrigger>
            <TabsTrigger value="faq">FAQ</TabsTrigger>
          </TabsList>

          {/* OVERVIEW TAB */}
          <TabsContent value="overview">
            <div className="space-y-6">
              <Card className="p-6">
                <h2 className="text-2xl font-bold mb-4">Welcome to PROMISE AI</h2>
                <p className="text-gray-700 mb-4">
                  PROMISE AI is an enterprise-grade machine learning platform that automates the entire ML workflow from data ingestion to model deployment and monitoring.
                </p>
                
                <div className="grid md:grid-cols-3 gap-4 mt-6">
                  <div className="bg-blue-50 p-4 rounded-lg">
                    <BarChart3 className="w-8 h-8 text-blue-600 mb-2" />
                    <h3 className="font-semibold mb-2">Predictive Analytics</h3>
                    <p className="text-sm text-gray-600">Automated ML with 6+ algorithms for regression and classification</p>
                  </div>
                  <div className="bg-purple-50 p-4 rounded-lg">
                    <TrendingUp className="w-8 h-8 text-purple-600 mb-2" />
                    <h3 className="font-semibold mb-2">Time Series</h3>
                    <p className="text-sm text-gray-600">Forecasting with Prophet, LSTM, and anomaly detection</p>
                  </div>
                  <div className="bg-green-50 p-4 rounded-lg">
                    <Lightbulb className="w-8 h-8 text-green-600 mb-2" />
                    <h3 className="font-semibold mb-2">AI Insights</h3>
                    <p className="text-sm text-gray-600">Business recommendations powered by large language models</p>
                  </div>
                </div>
              </Card>

              <Card className="p-6">
                <h2 className="text-xl font-bold mb-4">Key Capabilities</h2>
                <div className="space-y-3">
                  <div className="flex items-start gap-3">
                    <CheckCircle className="w-5 h-5 text-green-600 mt-1" />
                    <div>
                      <strong>Multiple Problem Types:</strong> Regression, Classification (Binary & Multi-class), Time Series Forecasting
                    </div>
                  </div>
                  <div className="flex items-start gap-3">
                    <CheckCircle className="w-5 h-5 text-green-600 mt-1" />
                    <div>
                      <strong>Data Source Flexibility:</strong> CSV upload, PostgreSQL, MySQL, SQL Server, Oracle, MongoDB (with Kerberos)
                    </div>
                  </div>
                  <div className="flex items-start gap-3">
                    <CheckCircle className="w-5 h-5 text-green-600 mt-1" />
                    <div>
                      <strong>Advanced Features:</strong> Hyperparameter tuning, NLP/text processing, multi-target prediction, relational joins
                    </div>
                  </div>
                  <div className="flex items-start gap-3">
                    <CheckCircle className="w-5 h-5 text-green-600 mt-1" />
                    <div>
                      <strong>Active Learning:</strong> Feedback loop for continuous model improvement
                    </div>
                  </div>
                  <div className="flex items-start gap-3">
                    <CheckCircle className="w-5 h-5 text-green-600 mt-1" />
                    <div>
                      <strong>Model Explainability:</strong> SHAP and LIME for interpretable AI
                    </div>
                  </div>
                </div>
              </Card>
            </div>
          </TabsContent>

          {/* FEATURES TAB */}
          <TabsContent value="features">
            <div className="space-y-4">
              
              {/* Data Upload & Connection */}
              <Card className="p-6">
                <Collapsible open={expandedSections['data-upload']} onOpenChange={() => toggleSection('data-upload')}>
                  <CollapsibleTrigger className="flex items-center justify-between w-full">
                    <div className="flex items-center gap-3">
                      <Database className="w-6 h-6 text-blue-600" />
                      <h3 className="text-xl font-bold">1. Data Upload & Database Connection</h3>
                    </div>
                    {expandedSections['data-upload'] ? <ChevronDown /> : <ChevronRight />}
                  </CollapsibleTrigger>
                  <CollapsibleContent className="mt-4 space-y-3">
                    <p className="text-gray-700">Connect to various data sources or upload files directly.</p>
                    
                    <div className="bg-gray-50 p-4 rounded">
                      <h4 className="font-semibold mb-2">Supported Data Sources:</h4>
                      <ul className="list-disc list-inside space-y-1 text-sm">
                        <li><strong>CSV Upload:</strong> Direct file upload (max 100MB recommended)</li>
                        <li><strong>PostgreSQL:</strong> Connection with optional Kerberos authentication</li>
                        <li><strong>MySQL:</strong> Standard or Kerberos-enabled connections</li>
                        <li><strong>SQL Server:</strong> Windows or SQL authentication</li>
                        <li><strong>Oracle:</strong> Enterprise database support</li>
                        <li><strong>MongoDB:</strong> Document database with authentication</li>
                      </ul>
                    </div>

                    <div className="bg-blue-50 p-4 rounded border-l-4 border-blue-600">
                      <div className="flex items-start gap-2">
                        <Info className="w-5 h-5 text-blue-600 mt-0.5" />
                        <div>
                          <strong className="text-blue-900">Kerberos Authentication:</strong>
                          <p className="text-sm text-blue-800 mt-1">
                            For enterprise databases, enable Kerberos authentication for secure, ticket-based access. 
                            Provide KDC address, realm, and keytab file when prompted.
                          </p>
                        </div>
                      </div>
                    </div>
                  </CollapsibleContent>
                </Collapsible>
              </Card>

              {/* Variable Selection */}
              <Card className="p-6">
                <Collapsible open={expandedSections['variable-selection']} onOpenChange={() => toggleSection('variable-selection')}>
                  <CollapsibleTrigger className="flex items-center justify-between w-full">
                    <div className="flex items-center gap-3">
                      <Target className="w-6 h-6 text-purple-600" />
                      <h3 className="text-xl font-bold">2. Variable Selection & Problem Types</h3>
                    </div>
                    {expandedSections['variable-selection'] ? <ChevronDown /> : <ChevronRight />}
                  </CollapsibleTrigger>
                  <CollapsibleContent className="mt-4 space-y-3">
                    <p className="text-gray-700">Configure your analysis by selecting variables and problem type.</p>
                    
                    <div className="bg-gray-50 p-4 rounded">
                      <h4 className="font-semibold mb-2">Selection Modes:</h4>
                      <ul className="space-y-2">
                        <li>
                          <strong className="text-blue-600">Manual:</strong> You select target variable(s) and features
                        </li>
                        <li>
                          <strong className="text-green-600">AI-Suggested:</strong> AI recommends optimal target and features
                        </li>
                        <li>
                          <strong className="text-purple-600">Hybrid:</strong> AI suggests, you refine the selection
                        </li>
                        <li>
                          <strong className="text-gray-600">Skip:</strong> Auto-detection handles everything
                        </li>
                      </ul>
                    </div>

                    <div className="bg-gray-50 p-4 rounded">
                      <h4 className="font-semibold mb-2">Problem Types:</h4>
                      <div className="grid md:grid-cols-2 gap-3 mt-2">
                        <div className="bg-white p-3 rounded border">
                          <div className="font-semibold text-green-600">📈 Regression</div>
                          <p className="text-sm text-gray-600 mt-1">Predict continuous numeric values (e.g., sales, temperature, price)</p>
                          <p className="text-xs text-gray-500 mt-2">Metrics: R², RMSE, MAE</p>
                        </div>
                        <div className="bg-white p-3 rounded border">
                          <div className="font-semibold text-purple-600">🏷️ Classification</div>
                          <p className="text-sm text-gray-600 mt-1">Predict categories (e.g., yes/no, fraud/legitimate, A/B/C)</p>
                          <p className="text-xs text-gray-500 mt-2">Metrics: Accuracy, F1, Precision, Recall</p>
                        </div>
                        <div className="bg-white p-3 rounded border">
                          <div className="font-semibold text-orange-600">⏰ Time Series</div>
                          <p className="text-sm text-gray-600 mt-1">Forecast future values based on temporal patterns</p>
                          <p className="text-xs text-gray-500 mt-2">Metrics: MAPE, RMSE, Trends</p>
                        </div>
                        <div className="bg-white p-3 rounded border">
                          <div className="font-semibold text-blue-600">🔍 Auto-Detect</div>
                          <p className="text-sm text-gray-600 mt-1">Let AI determine the best problem type automatically</p>
                          <p className="text-xs text-gray-500 mt-2">Based on data characteristics</p>
                        </div>
                      </div>
                    </div>
                  </CollapsibleContent>
                </Collapsible>
              </Card>

              {/* Predictive Analysis */}
              <Card className="p-6">
                <Collapsible open={expandedSections['predictive']} onOpenChange={() => toggleSection('predictive')}>
                  <CollapsibleTrigger className="flex items-center justify-between w-full">
                    <div className="flex items-center gap-3">
                      <BarChart3 className="w-6 h-6 text-green-600" />
                      <h3 className="text-xl font-bold">3. Predictive Analysis</h3>
                    </div>
                    {expandedSections['predictive'] ? <ChevronDown /> : <ChevronRight />}
                  </CollapsibleTrigger>
                  <CollapsibleContent className="mt-4 space-y-3">
                    <p className="text-gray-700">Automated machine learning with multiple algorithms.</p>
                    
                    <div className="bg-gray-50 p-4 rounded">
                      <h4 className="font-semibold mb-2">Available Models:</h4>
                      <div className="grid md:grid-cols-2 gap-2 text-sm">
                        <div>• Linear/Logistic Regression</div>
                        <div>• Random Forest</div>
                        <div>• XGBoost</div>
                        <div>• Decision Tree</div>
                        <div>• LightGBM</div>
                        <div>• LSTM Neural Network</div>
                      </div>
                    </div>

                    <div className="bg-yellow-50 p-4 rounded border-l-4 border-yellow-600">
                      <div className="flex items-start gap-2">
                        <AlertCircle className="w-5 h-5 text-yellow-600 mt-0.5" />
                        <div>
                          <strong className="text-yellow-900">Model Comparison:</strong>
                          <p className="text-sm text-yellow-800 mt-1">
                            All models are trained and ranked automatically. The top-performing model is highlighted with 🏆. 
                            Models are sorted by accuracy (classification) or R² score (regression).
                          </p>
                        </div>
                      </div>
                    </div>
                  </CollapsibleContent>
                </Collapsible>
              </Card>

              {/* Time Series */}
              <Card className="p-6">
                <Collapsible open={expandedSections['timeseries']} onOpenChange={() => toggleSection('timeseries')}>
                  <CollapsibleTrigger className="flex items-center justify-between w-full">
                    <div className="flex items-center gap-3">
                      <TrendingUp className="w-6 h-6 text-orange-600" />
                      <h3 className="text-xl font-bold">4. Time Series Forecasting</h3>
                    </div>
                    {expandedSections['timeseries'] ? <ChevronDown /> : <ChevronRight />}
                  </CollapsibleTrigger>
                  <CollapsibleContent className="mt-4 space-y-3">
                    <p className="text-gray-700">Forecast future values and detect anomalies in temporal data.</p>
                    
                    <div className="bg-gray-50 p-4 rounded">
                      <h4 className="font-semibold mb-2">Forecasting Methods:</h4>
                      <ul className="space-y-2">
                        <li>
                          <strong className="text-blue-600">Prophet:</strong> Facebook's forecasting tool with trend decomposition
                        </li>
                        <li>
                          <strong className="text-purple-600">LSTM:</strong> Deep learning for complex temporal patterns
                        </li>
                        <li>
                          <strong className="text-green-600">Both:</strong> Compare both methods for best results
                        </li>
                      </ul>
                    </div>

                    <div className="bg-gray-50 p-4 rounded">
                      <h4 className="font-semibold mb-2">Anomaly Detection:</h4>
                      <p className="text-sm text-gray-600">
                        Automatically identifies unusual patterns using Isolation Forest and Local Outlier Factor (LOF) algorithms.
                        Shows anomaly count, percentage, and highlighted points on charts.
                      </p>
                    </div>
                  </CollapsibleContent>
                </Collapsible>
              </Card>

              {/* Hyperparameter Tuning */}
              <Card className="p-6">
                <Collapsible open={expandedSections['tuning']} onOpenChange={() => toggleSection('tuning')}>
                  <CollapsibleTrigger className="flex items-center justify-between w-full">
                    <div className="flex items-center gap-3">
                      <Settings className="w-6 h-6 text-indigo-600" />
                      <h3 className="text-xl font-bold">5. Hyperparameter Tuning</h3>
                    </div>
                    {expandedSections['tuning'] ? <ChevronDown /> : <ChevronRight />}
                  </CollapsibleTrigger>
                  <CollapsibleContent className="mt-4 space-y-3">
                    <p className="text-gray-700">Optimize model performance through systematic parameter search.</p>
                    
                    <div className="grid md:grid-cols-2 gap-3">
                      <div className="bg-blue-50 p-4 rounded">
                        <h4 className="font-semibold text-blue-900 mb-2">🧩 Grid Search</h4>
                        <p className="text-sm text-blue-800">
                          Exhaustive search through specified parameter combinations. 
                          More thorough but slower.
                        </p>
                      </div>
                      <div className="bg-orange-50 p-4 rounded">
                        <h4 className="font-semibold text-orange-900 mb-2">🎲 Random Search</h4>
                        <p className="text-sm text-orange-800">
                          Random sampling of parameter space. 
                          Faster with good results.
                        </p>
                      </div>
                    </div>

                    <div className="bg-gray-50 p-4 rounded">
                      <h4 className="font-semibold mb-2">Common Parameters:</h4>
                      <ul className="list-disc list-inside text-sm space-y-1">
                        <li><strong>n_estimators:</strong> Number of trees/iterations</li>
                        <li><strong>max_depth:</strong> Maximum tree depth</li>
                        <li><strong>learning_rate:</strong> Step size for gradient descent</li>
                        <li><strong>min_samples_split:</strong> Minimum samples to split node</li>
                      </ul>
                    </div>
                  </CollapsibleContent>
                </Collapsible>
              </Card>

              {/* Feedback & Active Learning */}
              <Card className="p-6">
                <Collapsible open={expandedSections['feedback']} onOpenChange={() => toggleSection('feedback')}>
                  <CollapsibleTrigger className="flex items-center justify-between w-full">
                    <div className="flex items-center gap-3">
                      <ThumbsUp className="w-6 h-6 text-green-600" />
                      <h3 className="text-xl font-bold">6. Feedback Loop & Active Learning</h3>
                    </div>
                    {expandedSections['feedback'] ? <ChevronDown /> : <ChevronRight />}
                  </CollapsibleTrigger>
                  <CollapsibleContent className="mt-4 space-y-3">
                    <p className="text-gray-700">Improve models continuously based on real-world performance.</p>
                    
                    <div className="bg-gray-50 p-4 rounded">
                      <h4 className="font-semibold mb-2">How It Works:</h4>
                      <ol className="list-decimal list-inside space-y-2 text-sm">
                        <li>Model makes predictions on new data</li>
                        <li>You mark predictions as correct/incorrect or provide actual outcome</li>
                        <li>System tracks accuracy and identifies areas for improvement</li>
                        <li>Retrain model with feedback data for better performance</li>
                      </ol>
                    </div>

                    <div className="bg-green-50 p-4 rounded border-l-4 border-green-600">
                      <div className="flex items-start gap-2">
                        <Info className="w-5 h-5 text-green-600 mt-0.5" />
                        <div>
                          <strong className="text-green-900">Active Learning:</strong>
                          <p className="text-sm text-green-800 mt-1">
                            The system identifies uncertain predictions (low confidence) and prioritizes them for your review, 
                            maximizing learning efficiency.
                          </p>
                        </div>
                      </div>
                    </div>
                  </CollapsibleContent>
                </Collapsible>
              </Card>

              {/* Chat Assistant */}
              <Card className="p-6">
                <Collapsible open={expandedSections['chat']} onOpenChange={() => toggleSection('chat')}>
                  <CollapsibleTrigger className="flex items-center justify-between w-full">
                    <div className="flex items-center gap-3">
                      <MessageSquare className="w-6 h-6 text-blue-600" />
                      <h3 className="text-xl font-bold">7. AI Chat Assistant</h3>
                    </div>
                    {expandedSections['chat'] ? <ChevronDown /> : <ChevronRight />}
                  </CollapsibleTrigger>
                  <CollapsibleContent className="mt-4 space-y-3">
                    <p className="text-gray-700">Interactive chat powered by AI to help with analysis interpretation.</p>
                    
                    <div className="bg-gray-50 p-4 rounded">
                      <h4 className="font-semibold mb-2">What You Can Ask:</h4>
                      <ul className="list-disc list-inside space-y-1 text-sm">
                        <li>Explain model results and metrics</li>
                        <li>Why is a certain model performing better?</li>
                        <li>What do these correlations mean?</li>
                        <li>Generate custom charts</li>
                        <li>Add or remove analysis sections</li>
                        <li>Business recommendations based on data</li>
                      </ul>
                    </div>

                    <div className="bg-blue-50 p-4 rounded">
                      <h4 className="font-semibold text-blue-900 mb-2">Example Prompts:</h4>
                      <div className="space-y-2 text-sm">
                        <div className="bg-white p-2 rounded border">
                          "Show me a scatter plot of price vs sales"
                        </div>
                        <div className="bg-white p-2 rounded border">
                          "Why is Random Forest performing better than XGBoost?"
                        </div>
                        <div className="bg-white p-2 rounded border">
                          "What business actions should I take based on these insights?"
                        </div>
                      </div>
                    </div>
                  </CollapsibleContent>
                </Collapsible>
              </Card>
            </div>
          </TabsContent>

          {/* METRICS GUIDE TAB */}
          <TabsContent value="metrics">
            <div className="space-y-4">
              
              {/* Regression Metrics */}
              <Card className="p-6">
                <h2 className="text-xl font-bold mb-4 flex items-center gap-2">
                  <Activity className="w-6 h-6 text-green-600" />
                  Regression Metrics
                </h2>
                
                <div className="space-y-4">
                  <div className="bg-green-50 p-4 rounded border-l-4 border-green-600">
                    <h3 className="font-semibold text-lg mb-2">R² Score (Coefficient of Determination)</h3>
                    <p className="text-sm text-gray-700 mb-2">
                      Measures how well the model explains the variance in the data.
                    </p>
                    <div className="bg-white p-3 rounded mt-2">
                      <div className="grid grid-cols-3 gap-2 text-sm">
                        <div>
                          <strong className="text-green-600">1.0 (Perfect):</strong>
                          <p className="text-xs text-gray-600">Model explains all variance</p>
                        </div>
                        <div>
                          <strong className="text-yellow-600">0.7-0.9 (Good):</strong>
                          <p className="text-xs text-gray-600">Strong predictive power</p>
                        </div>
                        <div>
                          <strong className="text-red-600">&lt;0.5 (Poor):</strong>
                          <p className="text-xs text-gray-600">Weak predictions</p>
                        </div>
                      </div>
                    </div>
                  </div>

                  <div className="bg-purple-50 p-4 rounded border-l-4 border-purple-600">
                    <h3 className="font-semibold text-lg mb-2">RMSE (Root Mean Square Error)</h3>
                    <p className="text-sm text-gray-700 mb-2">
                      Average prediction error in the same units as your target variable.
                    </p>
                    <div className="bg-white p-3 rounded mt-2 text-sm">
                      <strong>Interpretation:</strong> Lower is better. If predicting house prices, RMSE of $50,000 means 
                      predictions are off by $50K on average.
                    </div>
                  </div>

                  <div className="bg-blue-50 p-4 rounded border-l-4 border-blue-600">
                    <h3 className="font-semibold text-lg mb-2">MAE (Mean Absolute Error)</h3>
                    <p className="text-sm text-gray-700 mb-2">
                      Average absolute difference between predictions and actuals.
                    </p>
                    <div className="bg-white p-3 rounded mt-2 text-sm">
                      <strong>Interpretation:</strong> More interpretable than RMSE. Less sensitive to outliers.
                    </div>
                  </div>
                </div>
              </Card>

              {/* Classification Metrics */}
              <Card className="p-6">
                <h2 className="text-xl font-bold mb-4 flex items-center gap-2">
                  <Target className="w-6 h-6 text-purple-600" />
                  Classification Metrics
                </h2>
                
                <div className="space-y-4">
                  <div className="bg-purple-50 p-4 rounded border-l-4 border-purple-600">
                    <h3 className="font-semibold text-lg mb-2">Accuracy</h3>
                    <p className="text-sm text-gray-700 mb-2">
                      Percentage of correct predictions out of total predictions.
                    </p>
                    <div className="bg-white p-3 rounded mt-2">
                      <div className="grid grid-cols-3 gap-2 text-sm">
                        <div>
                          <strong className="text-green-600">85%+ (Excellent):</strong>
                          <p className="text-xs text-gray-600">High confidence</p>
                        </div>
                        <div>
                          <strong className="text-yellow-600">70-85% (Good):</strong>
                          <p className="text-xs text-gray-600">Moderate confidence</p>
                        </div>
                        <div>
                          <strong className="text-red-600">&lt;70% (Poor):</strong>
                          <p className="text-xs text-gray-600">Low confidence</p>
                        </div>
                      </div>
                    </div>
                    <div className="bg-yellow-50 p-2 rounded mt-2 text-xs">
                      ⚠️ <strong>Caution:</strong> Can be misleading with imbalanced datasets. Use F1-Score instead.
                    </div>
                  </div>

                  <div className="bg-blue-50 p-4 rounded border-l-4 border-blue-600">
                    <h3 className="font-semibold text-lg mb-2">Precision</h3>
                    <p className="text-sm text-gray-700 mb-2">
                      Of all positive predictions, how many were actually correct?
                    </p>
                    <div className="bg-white p-3 rounded mt-2 text-sm">
                      <strong>Use Case:</strong> When false positives are costly (e.g., spam detection, fraud alerts)
                    </div>
                  </div>

                  <div className="bg-green-50 p-4 rounded border-l-4 border-green-600">
                    <h3 className="font-semibold text-lg mb-2">Recall (Sensitivity)</h3>
                    <p className="text-sm text-gray-700 mb-2">
                      Of all actual positives, how many did we correctly identify?
                    </p>
                    <div className="bg-white p-3 rounded mt-2 text-sm">
                      <strong>Use Case:</strong> When false negatives are costly (e.g., disease detection, fraud prevention)
                    </div>
                  </div>

                  <div className="bg-orange-50 p-4 rounded border-l-4 border-orange-600">
                    <h3 className="font-semibold text-lg mb-2">F1-Score</h3>
                    <p className="text-sm text-gray-700 mb-2">
                      Harmonic mean of Precision and Recall. Balanced metric.
                    </p>
                    <div className="bg-white p-3 rounded mt-2 text-sm">
                      <strong>Interpretation:</strong> Best metric for imbalanced datasets. Range: 0-1, higher is better.
                    </div>
                  </div>

                  <div className="bg-indigo-50 p-4 rounded border-l-4 border-indigo-600">
                    <h3 className="font-semibold text-lg mb-2">ROC-AUC</h3>
                    <p className="text-sm text-gray-700 mb-2">
                      Area Under the Receiver Operating Characteristic curve.
                    </p>
                    <div className="bg-white p-3 rounded mt-2">
                      <div className="grid grid-cols-3 gap-2 text-sm">
                        <div>
                          <strong className="text-green-600">0.9-1.0:</strong>
                          <p className="text-xs text-gray-600">Excellent</p>
                        </div>
                        <div>
                          <strong className="text-yellow-600">0.7-0.9:</strong>
                          <p className="text-xs text-gray-600">Good</p>
                        </div>
                        <div>
                          <strong className="text-red-600">&lt;0.7:</strong>
                          <p className="text-xs text-gray-600">Poor</p>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </Card>

              {/* Time Series Metrics */}
              <Card className="p-6">
                <h2 className="text-xl font-bold mb-4 flex items-center gap-2">
                  <TrendingUp className="w-6 h-6 text-orange-600" />
                  Time Series Metrics
                </h2>
                
                <div className="space-y-4">
                  <div className="bg-orange-50 p-4 rounded border-l-4 border-orange-600">
                    <h3 className="font-semibold text-lg mb-2">MAPE (Mean Absolute Percentage Error)</h3>
                    <p className="text-sm text-gray-700 mb-2">
                      Average percentage error of forecasts. Easy to interpret.
                    </p>
                    <div className="bg-white p-3 rounded mt-2 text-sm">
                      <strong>Example:</strong> MAPE of 5% means forecasts are off by 5% on average.
                    </div>
                  </div>

                  <div className="bg-blue-50 p-4 rounded border-l-4 border-blue-600">
                    <h3 className="font-semibold text-lg mb-2">Trend Components</h3>
                    <p className="text-sm text-gray-700 mb-2">
                      Prophet decomposes time series into:
                    </p>
                    <ul className="list-disc list-inside text-sm bg-white p-3 rounded mt-2">
                      <li><strong>Trend:</strong> Long-term increase or decrease</li>
                      <li><strong>Seasonality:</strong> Repeating patterns (weekly, yearly)</li>
                      <li><strong>Holidays:</strong> Special event effects</li>
                    </ul>
                  </div>
                </div>
              </Card>
            </div>
          </TabsContent>

          {/* AI INSIGHTS TAB */}
          <TabsContent value="insights">
            <div className="space-y-4">
              
              <Card className="p-6">
                <h2 className="text-xl font-bold mb-4 flex items-center gap-2">
                  <Lightbulb className="w-6 h-6 text-yellow-600" />
                  AI-Powered Insights & Recommendations
                </h2>
                
                <p className="text-gray-700 mb-4">
                  PROMISE AI uses large language models to generate actionable business insights from your data and model results.
                </p>

                {/* Insight Severity Levels */}
                <div className="bg-gray-50 p-4 rounded mb-4">
                  <h3 className="font-semibold mb-3">Insight Severity Levels:</h3>
                  <div className="space-y-2">
                    <div className="flex items-center gap-3 bg-red-50 p-3 rounded border-l-4 border-red-600">
                      <AlertCircle className="w-5 h-5 text-red-600" />
                      <div>
                        <strong className="text-red-900">Critical:</strong>
                        <p className="text-sm text-red-800">Immediate action required. May indicate data quality issues or model failures.</p>
                      </div>
                    </div>
                    <div className="flex items-center gap-3 bg-yellow-50 p-3 rounded border-l-4 border-yellow-600">
                      <AlertCircle className="w-5 h-5 text-yellow-600" />
                      <div>
                        <strong className="text-yellow-900">Warning:</strong>
                        <p className="text-sm text-yellow-800">Attention needed. Potential issues that could affect results.</p>
                      </div>
                    </div>
                    <div className="flex items-center gap-3 bg-blue-50 p-3 rounded border-l-4 border-blue-600">
                      <Info className="w-5 h-5 text-blue-600" />
                      <div>
                        <strong className="text-blue-900">Info:</strong>
                        <p className="text-sm text-blue-800">Informational insights. Interesting patterns or observations.</p>
                      </div>
                    </div>
                  </div>
                </div>

                {/* Insight Types */}
                <div className="bg-gray-50 p-4 rounded mb-4">
                  <h3 className="font-semibold mb-3">Insight Categories:</h3>
                  <div className="grid md:grid-cols-2 gap-3">
                    <div className="bg-white p-3 rounded border">
                      <strong className="text-purple-600">🔍 Anomaly</strong>
                      <p className="text-sm text-gray-600 mt-1">Unusual patterns or outliers detected in data</p>
                    </div>
                    <div className="bg-white p-3 rounded border">
                      <strong className="text-green-600">📈 Trend</strong>
                      <p className="text-sm text-gray-600 mt-1">Directional movements over time</p>
                    </div>
                    <div className="bg-white p-3 rounded border">
                      <strong className="text-blue-600">🔗 Correlation</strong>
                      <p className="text-sm text-gray-600 mt-1">Relationships between variables</p>
                    </div>
                    <div className="bg-white p-3 rounded border">
                      <strong className="text-orange-600">💼 Business</strong>
                      <p className="text-sm text-gray-600 mt-1">Strategic recommendations and actions</p>
                    </div>
                  </div>
                </div>

                {/* Business Recommendations */}
                <div className="bg-gradient-to-br from-purple-50 to-blue-50 p-4 rounded border-l-4 border-purple-600">
                  <h3 className="font-semibold mb-3 text-purple-900">📊 Business Recommendations</h3>
                  <p className="text-sm text-gray-700 mb-3">
                    AI-generated strategic recommendations based on your analysis results, categorized by priority:
                  </p>
                  <div className="space-y-2">
                    <div className="bg-white p-3 rounded border-l-4 border-red-500">
                      <strong className="text-red-600">🔴 High Priority:</strong>
                      <p className="text-sm text-gray-600">Critical actions that need immediate attention</p>
                      <p className="text-xs text-gray-500 mt-1">Expected Impact: High | Effort: Varies</p>
                    </div>
                    <div className="bg-white p-3 rounded border-l-4 border-yellow-500">
                      <strong className="text-yellow-600">🟡 Medium Priority:</strong>
                      <p className="text-sm text-gray-600">Important but can be scheduled</p>
                      <p className="text-xs text-gray-500 mt-1">Expected Impact: Medium | Effort: Varies</p>
                    </div>
                    <div className="bg-white p-3 rounded border-l-4 border-green-500">
                      <strong className="text-green-600">🟢 Low Priority:</strong>
                      <p className="text-sm text-gray-600">Nice to have improvements</p>
                      <p className="text-xs text-gray-500 mt-1">Expected Impact: Low-Medium | Effort: Low</p>
                    </div>
                  </div>
                </div>

                {/* Chart Explanations */}
                <div className="bg-gray-50 p-4 rounded">
                  <h3 className="font-semibold mb-3">📉 Chart Insights:</h3>
                  <p className="text-sm text-gray-700 mb-2">
                    When charts are empty or show unexpected patterns, AI explains why:
                  </p>
                  <ul className="list-disc list-inside text-sm space-y-1">
                    <li>Insufficient correlations found (threshold: 0.3)</li>
                    <li>Data type incompatibility</li>
                    <li>Missing or insufficient data points</li>
                    <li>Recommendations for data collection or preprocessing</li>
                  </ul>
                </div>
              </Card>
            </div>
          </TabsContent>

          {/* WORKFLOWS TAB */}
          <TabsContent value="workflows">
            <div className="space-y-4">
              
              <Card className="p-6">
                <h2 className="text-xl font-bold mb-4">Common Workflows</h2>
                
                {/* Workflow 1 */}
                <div className="bg-gradient-to-r from-blue-50 to-purple-50 p-6 rounded-lg mb-6">
                  <h3 className="font-semibold text-lg mb-3">📈 Workflow 1: Regression Analysis</h3>
                  <div className="space-y-3">
                    <div className="flex items-start gap-3">
                      <div className="bg-blue-600 text-white rounded-full w-6 h-6 flex items-center justify-center text-sm font-bold flex-shrink-0">1</div>
                      <div>
                        <strong>Upload Data:</strong> CSV or connect to database
                      </div>
                    </div>
                    <div className="flex items-start gap-3">
                      <div className="bg-blue-600 text-white rounded-full w-6 h-6 flex items-center justify-center text-sm font-bold flex-shrink-0">2</div>
                      <div>
                        <strong>Select Variables:</strong> Choose Manual/AI/Hybrid mode, select problem type "Regression"
                      </div>
                    </div>
                    <div className="flex items-start gap-3">
                      <div className="bg-blue-600 text-white rounded-full w-6 h-6 flex items-center justify-center text-sm font-bold flex-shrink-0">3</div>
                      <div>
                        <strong>Run Analysis:</strong> System trains 6 models automatically
                      </div>
                    </div>
                    <div className="flex items-start gap-3">
                      <div className="bg-blue-600 text-white rounded-full w-6 h-6 flex items-center justify-center text-sm font-bold flex-shrink-0">4</div>
                      <div>
                        <strong>Review Results:</strong> Check R² scores, feature importance, AI insights
                      </div>
                    </div>
                    <div className="flex items-start gap-3">
                      <div className="bg-blue-600 text-white rounded-full w-6 h-6 flex items-center justify-center text-sm font-bold flex-shrink-0">5</div>
                      <div>
                        <strong>Optimize (Optional):</strong> Use Hyperparameter Tuning tab to improve best model
                      </div>
                    </div>
                  </div>
                </div>

                {/* Workflow 2 */}
                <div className="bg-gradient-to-r from-orange-50 to-red-50 p-6 rounded-lg mb-6">
                  <h3 className="font-semibold text-lg mb-3">⏰ Workflow 2: Time Series Forecasting</h3>
                  <div className="space-y-3">
                    <div className="flex items-start gap-3">
                      <div className="bg-orange-600 text-white rounded-full w-6 h-6 flex items-center justify-center text-sm font-bold flex-shrink-0">1</div>
                      <div>
                        <strong>Upload Temporal Data:</strong> Dataset with datetime column
                      </div>
                    </div>
                    <div className="flex items-start gap-3">
                      <div className="bg-orange-600 text-white rounded-full w-6 h-6 flex items-center justify-center text-sm font-bold flex-shrink-0">2</div>
                      <div>
                        <strong>Navigate to Time Series Tab:</strong> Click "Time Series" in analysis tabs
                      </div>
                    </div>
                    <div className="flex items-start gap-3">
                      <div className="bg-orange-600 text-white rounded-full w-6 h-6 flex items-center justify-center text-sm font-bold flex-shrink-0">3</div>
                      <div>
                        <strong>Detect Datetime:</strong> Click "Detect Datetime Columns" button
                      </div>
                    </div>
                    <div className="flex items-start gap-3">
                      <div className="bg-orange-600 text-white rounded-full w-6 h-6 flex items-center justify-center text-sm font-bold flex-shrink-0">4</div>
                      <div>
                        <strong>Configure:</strong> Select time column, target, forecast method (Prophet/LSTM/Both)
                      </div>
                    </div>
                    <div className="flex items-start gap-3">
                      <div className="bg-orange-600 text-white rounded-full w-6 h-6 flex items-center justify-center text-sm font-bold flex-shrink-0">5</div>
                      <div>
                        <strong>Forecast:</strong> Set forecast periods and run analysis
                      </div>
                    </div>
                    <div className="flex items-start gap-3">
                      <div className="bg-orange-600 text-white rounded-full w-6 h-6 flex items-center justify-center text-sm font-bold flex-shrink-0">6</div>
                      <div>
                        <strong>Review:</strong> Check MAPE/RMSE, trends, confidence intervals, anomalies
                      </div>
                    </div>
                  </div>
                </div>

                {/* Workflow 3 */}
                <div className="bg-gradient-to-r from-green-50 to-teal-50 p-6 rounded-lg">
                  <h3 className="font-semibold text-lg mb-3">🔄 Workflow 3: Active Learning Loop</h3>
                  <div className="space-y-3">
                    <div className="flex items-start gap-3">
                      <div className="bg-green-600 text-white rounded-full w-6 h-6 flex items-center justify-center text-sm font-bold flex-shrink-0">1</div>
                      <div>
                        <strong>Train Initial Model:</strong> Complete predictive analysis
                      </div>
                    </div>
                    <div className="flex items-start gap-3">
                      <div className="bg-green-600 text-white rounded-full w-6 h-6 flex items-center justify-center text-sm font-bold flex-shrink-0">2</div>
                      <div>
                        <strong>Make Predictions:</strong> Use model on new data in production
                      </div>
                    </div>
                    <div className="flex items-start gap-3">
                      <div className="bg-green-600 text-white rounded-full w-6 h-6 flex items-center justify-center text-sm font-bold flex-shrink-0">3</div>
                      <div>
                        <strong>Collect Feedback:</strong> Mark predictions as correct/incorrect, provide actual outcomes
                      </div>
                    </div>
                    <div className="flex items-start gap-3">
                      <div className="bg-green-600 text-white rounded-full w-6 h-6 flex items-center justify-center text-sm font-bold flex-shrink-0">4</div>
                      <div>
                        <strong>Monitor Stats:</strong> Navigate to "Feedback & Learning" tab, view accuracy metrics
                      </div>
                    </div>
                    <div className="flex items-start gap-3">
                      <div className="bg-green-600 text-white rounded-full w-6 h-6 flex items-center justify-center text-sm font-bold flex-shrink-0">5</div>
                      <div>
                        <strong>Retrain:</strong> Click "Retrain Model with Feedback" when enough data collected
                      </div>
                    </div>
                    <div className="flex items-start gap-3">
                      <div className="bg-green-600 text-white rounded-full w-6 h-6 flex items-center justify-center text-sm font-bold flex-shrink-0">6</div>
                      <div>
                        <strong>Deploy Updated Model:</strong> Use improved model for better predictions
                      </div>
                    </div>
                  </div>
                </div>
              </Card>
            </div>
          </TabsContent>

          {/* FAQ TAB */}
          <TabsContent value="faq">
            <div className="space-y-4">
              
              <Card className="p-6">
                <h2 className="text-2xl font-bold mb-6">Frequently Asked Questions</h2>
                
                <div className="space-y-4">
                  {/* FAQ Item */}
                  <div className="border-b pb-4">
                    <h3 className="font-semibold text-lg mb-2">Q: How do I know which model to use?</h3>
                    <p className="text-gray-700 text-sm">
                      <strong>A:</strong> PROMISE AI automatically trains multiple models and ranks them by performance. 
                      The top-performing model is highlighted with 🏆. Generally, ensemble methods (Random Forest, XGBoost, LightGBM) 
                      perform well on most datasets. LSTM works best for large datasets with complex patterns.
                    </p>
                  </div>

                  <div className="border-b pb-4">
                    <h3 className="font-semibold text-lg mb-2">Q: What does "confidence" mean in model results?</h3>
                    <p className="text-gray-700 text-sm">
                      <strong>A:</strong> Confidence indicates model reliability:
                      <ul className="list-disc list-inside mt-2 ml-4">
                        <li><strong>Regression:</strong> High (R²&gt;0.7), Medium (0.5-0.7), Low (&lt;0.5)</li>
                        <li><strong>Classification:</strong> High (Accuracy&gt;85%), Medium (70-85%), Low (&lt;70%)</li>
                      </ul>
                    </p>
                  </div>

                  <div className="border-b pb-4">
                    <h3 className="font-semibold text-lg mb-2">Q: Why are some charts empty?</h3>
                    <p className="text-gray-700 text-sm">
                      <strong>A:</strong> Charts may be empty due to:
                      <ul className="list-disc list-inside mt-2 ml-4">
                        <li>No correlations above threshold (0.3)</li>
                        <li>Insufficient data points</li>
                        <li>Data type incompatibility</li>
                      </ul>
                      Check the AI Insights section for specific explanations and recommendations.
                    </p>
                  </div>

                  <div className="border-b pb-4">
                    <h3 className="font-semibold text-lg mb-2">Q: How accurate is the AI auto-detection?</h3>
                    <p className="text-gray-700 text-sm">
                      <strong>A:</strong> The AI auto-detection is highly accurate for standard datasets. It analyzes:
                      <ul className="list-disc list-inside mt-2 ml-4">
                        <li>Data types and distributions</li>
                        <li>Correlations and feature importance</li>
                        <li>Missing value patterns</li>
                        <li>Cardinality and uniqueness</li>
                      </ul>
                      For best results, use Manual or Hybrid mode if you have domain expertise.
                    </p>
                  </div>

                  <div className="border-b pb-4">
                    <h3 className="font-semibold text-lg mb-2">Q: Can I use PROMISE AI for real-time predictions?</h3>
                    <p className="text-gray-700 text-sm">
                      <strong>A:</strong> PROMISE AI is designed for batch analysis and model training. For production deployment, 
                      export trained models and deploy them in your infrastructure. The feedback loop allows you to improve 
                      models based on real-world performance.
                    </p>
                  </div>

                  <div className="border-b pb-4">
                    <h3 className="font-semibold text-lg mb-2">Q: What's the maximum dataset size?</h3>
                    <p className="text-gray-700 text-sm">
                      <strong>A:</strong> For CSV uploads, we recommend up to 100MB. For larger datasets, use database connections. 
                      The system automatically samples large datasets (intelligently stratified) to ensure analysis completes 
                      in reasonable time while maintaining representativeness.
                    </p>
                  </div>

                  <div className="border-b pb-4">
                    <h3 className="font-semibold text-lg mb-2">Q: How does hyperparameter tuning improve results?</h3>
                    <p className="text-gray-700 text-sm">
                      <strong>A:</strong> Hyperparameter tuning systematically searches for optimal model parameters. 
                      It can improve model performance by 5-20% typically. Use Grid Search for thorough optimization 
                      or Random Search for faster results. Most beneficial for Random Forest, XGBoost, and LightGBM models.
                    </p>
                  </div>

                  <div className="border-b pb-4">
                    <h3 className="font-semibold text-lg mb-2">Q: What data sources are supported?</h3>
                    <p className="text-gray-700 text-sm">
                      <strong>A:</strong> PROMISE AI supports:
                      <ul className="list-disc list-inside mt-2 ml-4">
                        <li>CSV file upload</li>
                        <li>PostgreSQL (with Kerberos)</li>
                        <li>MySQL (with Kerberos)</li>
                        <li>SQL Server</li>
                        <li>Oracle</li>
                        <li>MongoDB</li>
                      </ul>
                      All with optional Kerberos authentication for enterprise security.
                    </p>
                  </div>

                  <div className="pb-4">
                    <h3 className="font-semibold text-lg mb-2">Q: How do I interpret business recommendations?</h3>
                    <p className="text-gray-700 text-sm">
                      <strong>A:</strong> Business recommendations are AI-generated strategic actions based on your analysis. 
                      They're categorized by priority (High/Medium/Low) and include expected impact and implementation effort. 
                      Treat them as starting points for discussion - validate with domain expertise before implementation.
                    </p>
                  </div>
                </div>
              </Card>

              {/* Contact/Support Section */}
              <Card className="p-6 bg-gradient-to-br from-blue-50 to-purple-50">
                <h2 className="text-xl font-bold mb-4">Need More Help?</h2>
                <p className="text-gray-700 mb-4">
                  For additional support, feature requests, or bug reports:
                </p>
                <div className="space-y-2 text-sm">
                  <div className="flex items-center gap-2">
                    <MessageSquare className="w-4 h-4 text-blue-600" />
                    <span>Use the AI Chat Assistant in the analysis page</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <BookOpen className="w-4 h-4 text-purple-600" />
                    <span>Check the AI Insights section for context-specific help</span>
                  </div>
                </div>
              </Card>
            </div>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
};

export default DocumentationPage;
