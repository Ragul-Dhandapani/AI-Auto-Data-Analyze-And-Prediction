import { useState } from 'react';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from '@/components/ui/collapsible';
import { 
  BookOpen, Home, Database, Target, BarChart3, TrendingUp, 
  Settings, Lightbulb, MessageSquare, ThumbsUp, Link2, 
  ChevronDown, ChevronRight, AlertCircle, Info, CheckCircle,
  TrendingDown, Activity, Sparkles
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
          <TabsList className="grid w-full grid-cols-9 mb-6">
            <TabsTrigger value="overview">Overview</TabsTrigger>
            <TabsTrigger value="architecture">Architecture</TabsTrigger>
            <TabsTrigger value="features">Features</TabsTrigger>
            <TabsTrigger value="visualizations">Visualizations</TabsTrigger>
            <TabsTrigger value="metrics">Metrics Guide</TabsTrigger>
            <TabsTrigger value="insights">AI Insights</TabsTrigger>
            <TabsTrigger value="workflows">Workflows</TabsTrigger>
            <TabsTrigger value="mcp">MCP Server</TabsTrigger>
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
                    <p className="text-sm text-gray-600">Automated ML with 35+ models including XGBoost, Random Forest, LightGBM, CatBoost for regression and classification</p>
                  </div>
                  <div className="bg-purple-50 p-4 rounded-lg">
                    <TrendingUp className="w-8 h-8 text-purple-600 mb-2" />
                    <h3 className="font-semibold mb-2">Time Series</h3>
                    <p className="text-sm text-gray-600">Forecasting with Prophet, LSTM, and anomaly detection using Isolation Forest</p>
                  </div>
                  <div className="bg-green-50 p-4 rounded-lg">
                    <Lightbulb className="w-8 h-8 text-green-600 mb-2" />
                    <h3 className="font-semibold mb-2">AI Insights (Azure OpenAI)</h3>
                    <p className="text-sm text-gray-600">Business recommendations and insights powered by Azure OpenAI GPT-4o</p>
                  </div>
                </div>
              </Card>

              <Card className="p-6">
                <h2 className="text-xl font-bold mb-4">Key Capabilities</h2>
                <div className="space-y-3">
                  <div className="flex items-start gap-3">
                    <CheckCircle className="w-5 h-5 text-green-600 mt-1" />
                    <div>
                      <strong>35+ ML Models:</strong> Regression (XGBoost, LightGBM, Random Forest, CatBoost, etc.), Classification (SVC, Gradient Boosting, AdaBoost, etc.)
                    </div>
                  </div>
                  <div className="flex items-start gap-3">
                    <CheckCircle className="w-5 h-5 text-green-600 mt-1" />
                    <div>
                      <strong>Problem Types:</strong> Regression, Classification (Binary & Multi-class), Time Series, Clustering, Dimensionality Reduction, Anomaly Detection
                    </div>
                  </div>
                  <div className="flex items-start gap-3">
                    <CheckCircle className="w-5 h-5 text-green-600 mt-1" />
                    <div>
                      <strong>Dual Database Support:</strong> Oracle RDS 19c (default) with MongoDB alternative - seamless switching with compact toggle
                    </div>
                  </div>
                  <div className="flex items-start gap-3">
                    <CheckCircle className="w-5 h-5 text-green-600 mt-1" />
                    <div>
                      <strong>Azure OpenAI Integration:</strong> GPT-4o powered insights, chat-based analysis, and natural language chart generation
                    </div>
                  </div>
                  <div className="flex items-start gap-3">
                    <CheckCircle className="w-5 h-5 text-green-600 mt-1" />
                    <div>
                      <strong>Enhanced UI/UX:</strong> Always-visible Model Selector, localStorage persistence, Training Metadata dashboard, improved visualizations
                    </div>
                  </div>
                  <div className="flex items-start gap-3">
                    <CheckCircle className="w-5 h-5 text-green-600 mt-1" />
                    <div>
                      <strong>Data Sources:</strong> CSV upload, PostgreSQL, MySQL, SQL Server, Oracle (with Kerberos authentication support)
                    </div>
                  </div>
                </div>
              </Card>
            </div>
          </TabsContent>

          {/* ARCHITECTURE TAB */}
          <TabsContent value="architecture">
            <div className="space-y-6">
              
              {/* Tech Stack */}
              <Card className="p-6">
                <h2 className="text-2xl font-bold mb-4">Technology Stack</h2>
                
                <div className="grid md:grid-cols-2 gap-6">
                  {/* Frontend */}
                  <div className="bg-gradient-to-br from-blue-50 to-indigo-50 p-6 rounded-lg">
                    <h3 className="text-xl font-bold mb-4 text-blue-900">🎨 Frontend</h3>
                    <div className="space-y-3">
                      <div className="bg-white p-3 rounded">
                        <strong className="text-blue-600">React 18</strong>
                        <p className="text-sm text-gray-600">Modern UI framework with hooks</p>
                      </div>
                      <div className="bg-white p-3 rounded">
                        <strong className="text-blue-600">Vite</strong>
                        <p className="text-sm text-gray-600">Lightning-fast build tool</p>
                      </div>
                      <div className="bg-white p-3 rounded">
                        <strong className="text-blue-600">Shadcn/UI</strong>
                        <p className="text-sm text-gray-600">Beautiful component library</p>
                      </div>
                      <div className="bg-white p-3 rounded">
                        <strong className="text-blue-600">TailwindCSS</strong>
                        <p className="text-sm text-gray-600">Utility-first CSS framework</p>
                      </div>
                      <div className="bg-white p-3 rounded">
                        <strong className="text-blue-600">Plotly.js</strong>
                        <p className="text-sm text-gray-600">Interactive data visualization</p>
                      </div>
                      <div className="bg-white p-3 rounded">
                        <strong className="text-blue-600">React Router</strong>
                        <p className="text-sm text-gray-600">Client-side routing</p>
                      </div>
                      <div className="bg-white p-3 rounded">
                        <strong className="text-blue-600">Axios</strong>
                        <p className="text-sm text-gray-600">HTTP client for API calls</p>
                      </div>
                    </div>
                  </div>

                  {/* Backend */}
                  <div className="bg-gradient-to-br from-green-50 to-teal-50 p-6 rounded-lg">
                    <h3 className="text-xl font-bold mb-4 text-green-900">⚙️ Backend</h3>
                    <div className="space-y-3">
                      <div className="bg-white p-3 rounded">
                        <strong className="text-green-600">FastAPI 0.115.5 (Python 3.11+)</strong>
                        <p className="text-sm text-gray-600">High-performance async API framework with Pydantic validation</p>
                      </div>
                      <div className="bg-white p-3 rounded">
                        <strong className="text-green-600">Oracle RDS 19c (Default)</strong>
                        <p className="text-sm text-gray-600">Enterprise relational database with BLOB storage & connection pooling</p>
                      </div>
                      <div className="bg-white p-3 rounded">
                        <strong className="text-green-600">MongoDB (Alternative)</strong>
                        <p className="text-sm text-gray-600">NoSQL document database with GridFS for file storage</p>
                      </div>
                      <div className="bg-white p-3 rounded">
                        <strong className="text-green-600">35+ ML Models</strong>
                        <p className="text-sm text-gray-600">Scikit-learn, XGBoost, LightGBM, CatBoost, Prophet, TensorFlow/Keras (LSTM)</p>
                      </div>
                      <div className="bg-white p-3 rounded">
                        <strong className="text-green-600">Azure OpenAI (GPT-4o)</strong>
                        <p className="text-sm text-gray-600">AI insights, chat, model recommendations, chart generation</p>
                      </div>
                      <div className="bg-white p-3 rounded">
                        <strong className="text-green-600">Model Explainability</strong>
                        <p className="text-sm text-gray-600">SHAP & LIME for interpretable AI predictions</p>
                      </div>
                      <div className="bg-white p-3 rounded">
                        <strong className="text-green-600">cx_Oracle 8.3.0</strong>
                        <p className="text-sm text-gray-600">Oracle database driver with instant client 19.23</p>
                      </div>
                    </div>
                  </div>
                </div>

                {/* ML Models & Database Connectors */}
                <div className="mt-6 grid md:grid-cols-2 gap-6">
                  {/* ML Models */}
                  <div className="bg-indigo-50 p-6 rounded-lg">
                    <h3 className="text-xl font-bold mb-4 text-indigo-900">🤖 35+ ML Models</h3>
                    <div className="space-y-2">
                      <div className="bg-white p-3 rounded">
                        <strong className="text-indigo-600 text-sm">Regression (18+)</strong>
                        <p className="text-xs text-gray-600 mt-1">Linear, Ridge, Lasso, ElasticNet, SVR, XGBoost, LightGBM, CatBoost, Random Forest, Gradient Boosting, AdaBoost, Extra Trees, KNN, Bagging, HistGradient, Huber, RANSAC</p>
                      </div>
                      <div className="bg-white p-3 rounded">
                        <strong className="text-indigo-600 text-sm">Classification (17+)</strong>
                        <p className="text-xs text-gray-600 mt-1">Logistic, SVC, XGBoost, LightGBM, CatBoost, Random Forest, Gradient Boosting, Decision Tree, AdaBoost, Extra Trees, KNN, Naive Bayes (3 types), Bagging, HistGradient, Perceptron</p>
                      </div>
                      <div className="bg-white p-3 rounded">
                        <strong className="text-indigo-600 text-sm">Advanced</strong>
                        <p className="text-xs text-gray-600 mt-1">Prophet, LSTM (TensorFlow/Keras), Isolation Forest, LOF, Clustering, Dimensionality Reduction</p>
                      </div>
                    </div>
                  </div>

                  {/* Database Connectors */}
                  <div className="bg-purple-50 p-6 rounded-lg">
                    <h3 className="text-xl font-bold mb-4 text-purple-900">🔌 Data Source Connectors</h3>
                    <div className="grid grid-cols-2 gap-3">
                      <div className="bg-white p-3 rounded text-center">
                        <strong className="text-purple-600">CSV Upload</strong>
                        <p className="text-xs text-gray-600 mt-1">Direct file upload</p>
                      </div>
                      <div className="bg-white p-3 rounded text-center">
                        <strong className="text-purple-600">PostgreSQL</strong>
                        <p className="text-xs text-gray-600 mt-1">psycopg2</p>
                      </div>
                      <div className="bg-white p-3 rounded text-center">
                        <strong className="text-purple-600">MySQL</strong>
                        <p className="text-xs text-gray-600 mt-1">pymysql</p>
                      </div>
                      <div className="bg-white p-3 rounded text-center">
                        <strong className="text-purple-600">SQL Server</strong>
                        <p className="text-xs text-gray-600 mt-1">pyodbc</p>
                      </div>
                      <div className="bg-white p-3 rounded text-center">
                        <strong className="text-purple-600">Oracle (External)</strong>
                        <p className="text-xs text-gray-600 mt-1">cx_Oracle</p>
                      </div>
                      <div className="bg-white p-3 rounded text-center">
                        <strong className="text-purple-600">MongoDB (External)</strong>
                        <p className="text-xs text-gray-600 mt-1">pymongo</p>
                      </div>
                    </div>
                    <div className="mt-3 bg-white p-3 rounded text-center">
                      <strong className="text-purple-600">🔐 Kerberos Auth</strong>
                      <p className="text-xs text-gray-600 mt-1">GSSAPI authentication for enterprise databases</p>
                    </div>
                  </div>
                </div>
              </Card>

              {/* Architecture Diagram */}
              <Card className="p-6">
                <h2 className="text-2xl font-bold mb-4">System Architecture</h2>
                
                <div className="bg-gray-50 p-6 rounded-lg">
                  <div className="space-y-6">
                    {/* Client Layer */}
                    <div className="text-center">
                      <div className="inline-block bg-blue-600 text-white px-6 py-3 rounded-lg font-semibold">
                        👤 User Browser
                      </div>
                      <div className="flex justify-center my-2">
                        <div className="w-0.5 h-8 bg-gray-400"></div>
                      </div>
                    </div>

                    {/* Frontend Layer */}
                    <div className="bg-blue-100 p-4 rounded-lg">
                      <h4 className="font-bold text-blue-900 mb-3 text-center">Frontend Layer (React)</h4>
                      <div className="grid md:grid-cols-4 gap-2">
                        <div className="bg-white p-2 rounded text-center text-sm">
                          <strong>HomePage</strong>
                          <p className="text-xs text-gray-600">Landing</p>
                        </div>
                        <div className="bg-white p-2 rounded text-center text-sm">
                          <strong>Dashboard</strong>
                          <p className="text-xs text-gray-600">Data Upload</p>
                        </div>
                        <div className="bg-white p-2 rounded text-center text-sm">
                          <strong>Analysis Tabs</strong>
                          <p className="text-xs text-gray-600">5 Analysis Types</p>
                        </div>
                        <div className="bg-white p-2 rounded text-center text-sm">
                          <strong>Training Metadata</strong>
                          <p className="text-xs text-gray-600">Model History</p>
                        </div>
                      </div>
                      <div className="flex justify-center my-2">
                        <div className="w-0.5 h-8 bg-gray-400"></div>
                      </div>
                      <div className="text-center text-sm text-gray-600">
                        HTTP/REST API (Port 3000 → Backend 8001)
                      </div>
                    </div>

                    <div className="flex justify-center">
                      <div className="w-0.5 h-8 bg-gray-400"></div>
                    </div>

                    {/* Backend Layer */}
                    <div className="bg-green-100 p-4 rounded-lg">
                      <h4 className="font-bold text-green-900 mb-3 text-center">Backend Layer (FastAPI)</h4>
                      <div className="grid md:grid-cols-3 gap-3 mb-3">
                        <div className="bg-white p-3 rounded">
                          <strong className="text-sm">Routes</strong>
                          <div className="text-xs space-y-1 mt-1">
                            <div>• /api/datasource</div>
                            <div>• /api/analysis</div>
                            <div>• /api/training</div>
                            <div>• /api/feedback</div>
                          </div>
                        </div>
                        <div className="bg-white p-3 rounded">
                          <strong className="text-sm">Services</strong>
                          <div className="text-xs space-y-1 mt-1">
                            <div>• ml_service_enhanced (35+ models)</div>
                            <div>• azure_openai_service</div>
                            <div>• chat_service</div>
                            <div>• time_series_service</div>
                            <div>• hyperparameter_service</div>
                            <div>• analytics_tracking_service</div>
                          </div>
                        </div>
                        <div className="bg-white p-3 rounded">
                          <strong className="text-sm">AI/ML Features</strong>
                          <div className="text-xs space-y-1 mt-1">
                            <div>• 35+ Model Training</div>
                            <div>• NaN Handling</div>
                            <div>• Training Time Tracking</div>
                            <div>• Azure OpenAI Insights</div>
                            <div>• Model Explainability (SHAP)</div>
                            <div>• Training Metadata Recording</div>
                          </div>
                        </div>
                      </div>
                    </div>

                    <div className="flex justify-center">
                      <div className="w-0.5 h-8 bg-gray-400"></div>
                    </div>

                    {/* Data Layer */}
                    <div className="bg-purple-100 p-4 rounded-lg">
                      <h4 className="font-bold text-purple-900 mb-3 text-center">Data Layer</h4>
                      <div className="grid md:grid-cols-2 gap-3">
                        <div className="bg-white p-3 rounded">
                          <strong className="text-sm">Oracle RDS 19c (Default)</strong>
                          <div className="text-xs space-y-1 mt-1">
                            <div>✓ Datasets metadata</div>
                            <div>✓ Training metadata tracking</div>
                            <div>✓ BLOB storage for large files</div>
                            <div>✓ Connection pooling (2-10)</div>
                          </div>
                        </div>
                        <div className="bg-white p-3 rounded">
                          <strong className="text-sm">MongoDB (Alternative)</strong>
                          <div className="text-xs space-y-1 mt-1">
                            <div>✓ Document-based storage</div>
                            <div>✓ GridFS for files</div>
                            <div>✓ Flexible schema</div>
                            <div>✓ Seamless switching</div>
                          </div>
                        </div>
                      </div>
                    </div>

                    {/* Data Flow */}
                    <div className="bg-yellow-50 p-4 rounded-lg border-2 border-yellow-400">
                      <h4 className="font-bold text-yellow-900 mb-2">📊 Complete ML Workflow</h4>
                      <div className="text-sm space-y-1">
                        <div><strong>1.</strong> User uploads CSV or connects to external database (PostgreSQL, MySQL, Oracle, etc.)</div>
                        <div><strong>2.</strong> Data stored in Oracle RDS 19c (default) or MongoDB with metadata tracking</div>
                        <div><strong>3.</strong> Variable Selection Modal appears - Manual/AI-Suggested/Hybrid/Skip modes</div>
                        <div><strong>4.</strong> Model Selector (always visible) - Select specific models or use "AI Recommend"</div>
                        <div><strong>5.</strong> Backend trains selected models (35+ available) with NaN handling & training time tracking</div>
                        <div><strong>6.</strong> Results ranked by performance (🏆 best model) - stored in localStorage for persistence</div>
                        <div><strong>7.</strong> Azure OpenAI generates insights, business recommendations, and chart suggestions</div>
                        <div><strong>8.</strong> Training metadata saved to database - view in Training Metadata dashboard</div>
                        <div><strong>9.</strong> User can chat with AI, generate visualizations, or provide feedback</div>
                      </div>
                    </div>
                  </div>
                </div>

                {/* External Services */}
                <div className="mt-6 bg-gradient-to-r from-blue-50 to-indigo-50 p-6 rounded-lg border-2 border-blue-300">
                  <h4 className="font-bold text-blue-900 mb-3">☁️ External Services Integration</h4>
                  <div className="bg-white p-4 rounded-lg">
                    <div className="flex items-start gap-3">
                      <div className="bg-blue-100 p-3 rounded">
                        <strong className="text-blue-700">Azure OpenAI (GPT-4o)</strong>
                      </div>
                      <div className="flex-1">
                        <p className="text-sm text-gray-700 mb-2">
                          <strong>Endpoint:</strong> User-provided Azure resource
                        </p>
                        <p className="text-sm text-gray-700 mb-2">
                          <strong>API Version:</strong> 2024-12-01-preview
                        </p>
                        <p className="text-sm text-gray-700">
                          <strong>Features:</strong> AI insights generation, model recommendations, natural language chart generation, 
                          chat-based analysis, business recommendations
                        </p>
                      </div>
                    </div>
                  </div>
                </div>

                {/* Key Features */}
                <div className="mt-6 grid md:grid-cols-3 gap-4">
                  <div className="bg-blue-50 p-4 rounded border-l-4 border-blue-600">
                    <strong className="text-blue-900">🔒 Security</strong>
                    <p className="text-sm text-gray-700 mt-2">
                      Kerberos authentication, parameterized queries (SQL injection protection), API key encryption, CORS configuration
                    </p>
                  </div>
                  <div className="bg-green-50 p-4 rounded border-l-4 border-green-600">
                    <strong className="text-green-900">⚡ Performance</strong>
                    <p className="text-sm text-gray-700 mt-2">
                      Async FastAPI, Oracle connection pooling (2-10), localStorage caching, intelligent data sampling, NaN handling
                    </p>
                  </div>
                  <div className="bg-purple-50 p-4 rounded border-l-4 border-purple-600">
                    <strong className="text-purple-900">🔄 Scalability</strong>
                    <p className="text-sm text-gray-700 mt-2">
                      Kubernetes deployment, horizontal pod autoscaling, load balancing, CDN for static assets, supervisor process management
                    </p>
                  </div>
                </div>
              </Card>

              {/* Deployment */}
              <Card className="p-6">
                <h2 className="text-2xl font-bold mb-4">Deployment Architecture</h2>
                
                <div className="bg-gradient-to-r from-gray-50 to-gray-100 p-6 rounded-lg mb-4">
                  <div className="grid md:grid-cols-3 gap-4">
                    <div className="bg-white p-4 rounded shadow">
                      <h4 className="font-semibold text-blue-600 mb-2">Development</h4>
                      <ul className="text-sm space-y-1">
                        <li>✓ Hot reload (Vite + FastAPI)</li>
                        <li>✓ Local Oracle/MongoDB</li>
                        <li>✓ Debug mode enabled</li>
                        <li>✓ Source maps</li>
                        <li>✓ Supervisor for services</li>
                      </ul>
                    </div>
                    <div className="bg-white p-4 rounded shadow">
                      <h4 className="font-semibold text-green-600 mb-2">Staging</h4>
                      <ul className="text-sm space-y-1">
                        <li>✓ Docker containers</li>
                        <li>✓ Oracle RDS 19c</li>
                        <li>✓ HTTPS enabled</li>
                        <li>✓ Azure OpenAI integration</li>
                        <li>✓ Performance monitoring</li>
                      </ul>
                    </div>
                    <div className="bg-white p-4 rounded shadow">
                      <h4 className="font-semibold text-purple-600 mb-2">Production (Current)</h4>
                      <ul className="text-sm space-y-1">
                        <li>✓ Kubernetes cluster</li>
                        <li>✓ Oracle RDS 19c (2-10 pool)</li>
                        <li>✓ Horizontal pod autoscaling</li>
                        <li>✓ Ingress load balancer</li>
                        <li>✓ Supervisor process mgmt</li>
                      </ul>
                    </div>
                  </div>
                </div>

                {/* Current Production Setup */}
                <div className="bg-blue-50 p-4 rounded-lg border-l-4 border-blue-600">
                  <h4 className="font-semibold text-blue-900 mb-2">🚀 Current Production Configuration</h4>
                  <div className="text-sm text-gray-700 space-y-1">
                    <div><strong>Backend:</strong> FastAPI on port 8001 (managed by supervisor) → Ingress routes /api/* requests</div>
                    <div><strong>Frontend:</strong> React (Vite) on port 3000 → Ingress routes all other requests</div>
                    <div><strong>Database:</strong> Oracle RDS 19c (AWS) with connection pooling, switchable to MongoDB</div>
                    <div><strong>AI Services:</strong> Azure OpenAI GPT-4o (user-provided endpoint)</div>
                    <div><strong>Process Management:</strong> supervisorctl manages frontend & backend services</div>
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
                      <h4 className="font-semibold mb-2">Problem Types (7 Types Supported):</h4>
                      <div className="grid md:grid-cols-3 gap-3 mt-2">
                        <div className="bg-white p-3 rounded border">
                          <div className="font-semibold text-green-600">📈 Regression</div>
                          <p className="text-sm text-gray-600 mt-1">Predict continuous values</p>
                          <p className="text-xs text-gray-500 mt-2">18+ models available</p>
                        </div>
                        <div className="bg-white p-3 rounded border">
                          <div className="font-semibold text-purple-600">🏷️ Classification</div>
                          <p className="text-sm text-gray-600 mt-1">Predict categories</p>
                          <p className="text-xs text-gray-500 mt-2">17+ models available</p>
                        </div>
                        <div className="bg-white p-3 rounded border">
                          <div className="font-semibold text-orange-600">⏰ Time Series</div>
                          <p className="text-sm text-gray-600 mt-1">Forecast temporal patterns</p>
                          <p className="text-xs text-gray-500 mt-2">Prophet & LSTM</p>
                        </div>
                        <div className="bg-white p-3 rounded border">
                          <div className="font-semibold text-indigo-600">🎯 Clustering</div>
                          <p className="text-sm text-gray-600 mt-1">Group similar data points</p>
                          <p className="text-xs text-gray-500 mt-2">K-Means, DBSCAN</p>
                        </div>
                        <div className="bg-white p-3 rounded border">
                          <div className="font-semibold text-pink-600">📐 Dimensionality Reduction</div>
                          <p className="text-sm text-gray-600 mt-1">Reduce feature space</p>
                          <p className="text-xs text-gray-500 mt-2">PCA, t-SNE</p>
                        </div>
                        <div className="bg-white p-3 rounded border">
                          <div className="font-semibold text-red-600">🚨 Anomaly Detection</div>
                          <p className="text-sm text-gray-600 mt-1">Find outliers</p>
                          <p className="text-xs text-gray-500 mt-2">Isolation Forest, LOF</p>
                        </div>
                        <div className="bg-white p-3 rounded border">
                          <div className="font-semibold text-blue-600">🔍 Auto-Detect</div>
                          <p className="text-sm text-gray-600 mt-1">AI determines best type</p>
                          <p className="text-xs text-gray-500 mt-2">Azure OpenAI powered</p>
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
                      <h4 className="font-semibold mb-2">35+ Available Models:</h4>
                      <div className="grid md:grid-cols-3 gap-2 text-sm">
                        <div>
                          <strong className="text-blue-600">Regression:</strong>
                          <div className="text-xs mt-1">Linear, Ridge, Lasso, ElasticNet, SVR, XGBoost, LightGBM, CatBoost, Random Forest, Gradient Boosting, AdaBoost, Extra Trees, KNN, Bagging, HistGradient, Huber, RANSAC</div>
                        </div>
                        <div>
                          <strong className="text-purple-600">Classification:</strong>
                          <div className="text-xs mt-1">Logistic, SVC, XGBoost, LightGBM, CatBoost, Random Forest, Gradient Boosting, Decision Tree, AdaBoost, Extra Trees, KNN, Naive Bayes (Gaussian/Multinomial/Bernoulli), Bagging, HistGradient, Perceptron</div>
                        </div>
                        <div>
                          <strong className="text-green-600">Advanced:</strong>
                          <div className="text-xs mt-1">Neural Networks, Ensemble Methods, AutoML capabilities, Deep Learning integration</div>
                        </div>
                      </div>
                    </div>

                    <div className="bg-blue-50 p-4 rounded border-l-4 border-blue-600">
                      <div className="flex items-start gap-2">
                        <Info className="w-5 h-5 text-blue-600 mt-0.5" />
                        <div>
                          <strong className="text-blue-900">Model Selection:</strong>
                          <p className="text-sm text-blue-800 mt-1">
                            The Model Selector is always visible - no more hunting for it! Select specific models manually or use "AI Recommend" 
                            to let Azure OpenAI suggest the best models for your dataset. The selector loads models immediately based on your problem type.
                          </p>
                        </div>
                      </div>
                    </div>

                    <div className="bg-yellow-50 p-4 rounded border-l-4 border-yellow-600">
                      <div className="flex items-start gap-2">
                        <AlertCircle className="w-5 h-5 text-yellow-600 mt-0.5" />
                        <div>
                          <strong className="text-yellow-900">Model Comparison & Results:</strong>
                          <p className="text-sm text-yellow-800 mt-1">
                            All selected models are trained and compared side-by-side. The best model is highlighted with 🏆. 
                            Results persist in localStorage (survives page refresh) and include training time for each model. 
                            Click "New Analysis" to clear cached results and start fresh.
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

                    <div className="bg-blue-50 p-4 rounded border-l-4 border-blue-600 mb-3">
                      <div className="flex items-start gap-2">
                        <Sparkles className="w-5 h-5 text-blue-600 mt-0.5" />
                        <div>
                          <strong className="text-blue-900">Azure OpenAI Integration:</strong>
                          <p className="text-sm text-blue-800 mt-1">
                            AI recommends optimal hyperparameter ranges based on your dataset characteristics (size, features, problem type). 
                            Get AI explanations of why certain parameters work best for YOUR specific data.
                          </p>
                        </div>
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

              {/* Azure OpenAI Integration */}
              <Card className="p-6 bg-gradient-to-br from-blue-50 to-indigo-50 border-2 border-blue-300">
                <Collapsible open={expandedSections['azure-openai']} onOpenChange={() => toggleSection('azure-openai')}>
                  <CollapsibleTrigger className="flex items-center justify-between w-full">
                    <div className="flex items-center gap-3">
                      <Sparkles className="w-6 h-6 text-blue-600" />
                      <h3 className="text-xl font-bold text-blue-900">🚀 Complete Azure OpenAI Integration (GPT-4o)</h3>
                    </div>
                    {expandedSections['azure-openai'] ? <ChevronDown /> : <ChevronRight />}
                  </CollapsibleTrigger>
                  <CollapsibleContent className="mt-4 space-y-4">
                    <div className="bg-white p-4 rounded-lg border-2 border-blue-200">
                      <h4 className="font-bold text-blue-900 mb-3">🎯 Azure OpenAI Powers EVERY Feature:</h4>
                      
                      <div className="space-y-3 text-sm">
                        <div className="bg-gradient-to-r from-purple-50 to-pink-50 p-3 rounded-lg border-l-4 border-purple-500">
                          <strong className="text-purple-900">1. Model Selection & Recommendations</strong>
                          <p className="text-gray-700 mt-1">AI analyzes your dataset and recommends the best ML models from 35+ options. Click "AI Recommend" in Model Selector.</p>
                        </div>
                        
                        <div className="bg-gradient-to-r from-green-50 to-teal-50 p-3 rounded-lg border-l-4 border-green-500">
                          <strong className="text-green-900">2. Variable Selection Intelligence</strong>
                          <p className="text-gray-700 mt-1">AI suggests optimal target variables and important features by analyzing column names, data types, and relationships.</p>
                        </div>
                        
                        <div className="bg-gradient-to-r from-orange-50 to-red-50 p-3 rounded-lg border-l-4 border-orange-500">
                          <strong className="text-orange-900">3. Hyperparameter Tuning Guidance</strong>
                          <p className="text-gray-700 mt-1">AI recommends optimal hyperparameter ranges based on dataset size and complexity. Explains why certain parameters work best.</p>
                        </div>
                        
                        <div className="bg-gradient-to-r from-blue-50 to-cyan-50 p-3 rounded-lg border-l-4 border-blue-500">
                          <strong className="text-blue-900">4. ML Insights & Performance Analysis</strong>
                          <p className="text-gray-700 mt-1">AI generates business insights from ML results. Explains why models succeed/fail and provides actionable recommendations.</p>
                        </div>
                        
                        <div className="bg-gradient-to-r from-yellow-50 to-amber-50 p-3 rounded-lg border-l-4 border-yellow-500">
                          <strong className="text-yellow-900">5. Model Explainability (SHAP/LIME)</strong>
                          <p className="text-gray-700 mt-1">AI converts technical SHAP/LIME results into plain-language business explanations. Understand feature impacts without ML expertise.</p>
                        </div>
                        
                        <div className="bg-gradient-to-r from-indigo-50 to-purple-50 p-3 rounded-lg border-l-4 border-indigo-500">
                          <strong className="text-indigo-900">6. Time Series Forecasting Insights</strong>
                          <p className="text-gray-700 mt-1">AI explains forecast trends, interprets anomalies with business context, and recommends forecast strategies.</p>
                        </div>
                        
                        <div className="bg-gradient-to-r from-pink-50 to-rose-50 p-3 rounded-lg border-l-4 border-pink-500">
                          <strong className="text-pink-900">7. Natural Language Chart Generation</strong>
                          <p className="text-gray-700 mt-1">Create visualizations by simply asking: "Show me a scatter plot of price vs sales" or "Generate a correlation heatmap"</p>
                        </div>
                        
                        <div className="bg-gradient-to-r from-cyan-50 to-sky-50 p-3 rounded-lg border-l-4 border-cyan-500">
                          <strong className="text-cyan-900">8. Interactive Chat Assistant</strong>
                          <p className="text-gray-700 mt-1">Ask questions about your data, models, and results. Get instant AI-powered answers and business recommendations.</p>
                        </div>
                      </div>

                      <div className="mt-4 bg-green-50 p-4 rounded-lg border-2 border-green-400">
                        <div className="flex items-start gap-2">
                          <CheckCircle className="w-6 h-6 text-green-600 mt-0.5" />
                          <div>
                            <strong className="text-green-900 text-base">100% Azure OpenAI Powered Platform!</strong>
                            <p className="text-sm text-green-800 mt-1">
                              Unlike traditional ML platforms, PROMISE AI uses Azure OpenAI GPT-4o at EVERY step - from data analysis 
                              to model training to results interpretation. Get AI-powered insights throughout your entire workflow.
                            </p>
                          </div>
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
                      <h3 className="text-xl font-bold">7. AI Chat Assistant (Azure OpenAI)</h3>
                    </div>
                    {expandedSections['chat'] ? <ChevronDown /> : <ChevronRight />}
                  </CollapsibleTrigger>
                  <CollapsibleContent className="mt-4 space-y-3">
                    <p className="text-gray-700">Interactive chat powered by Azure OpenAI GPT-4o to help with analysis interpretation and data exploration.</p>
                    
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

              {/* Training Metadata */}
              <Card className="p-6">
                <Collapsible open={expandedSections['training-metadata']} onOpenChange={() => toggleSection('training-metadata')}>
                  <CollapsibleTrigger className="flex items-center justify-between w-full">
                    <div className="flex items-center gap-3">
                      <Activity className="w-6 h-6 text-indigo-600" />
                      <h3 className="text-xl font-bold">8. Training Metadata & Model History</h3>
                    </div>
                    {expandedSections['training-metadata'] ? <ChevronDown /> : <ChevronRight />}
                  </CollapsibleTrigger>
                  <CollapsibleContent className="mt-4 space-y-3">
                    <p className="text-gray-700">Track and compare all your model training sessions and experiments.</p>
                    
                    <div className="bg-green-50 p-4 rounded border-l-4 border-green-600">
                      <div className="flex items-start gap-2">
                        <CheckCircle className="w-5 h-5 text-green-600 mt-0.5" />
                        <div>
                          <h4 className="font-semibold text-green-900">Training Metadata - Now Fully Implemented!</h4>
                          <p className="text-sm text-green-800 mt-1">
                            Every ML training session is automatically tracked and saved to the database (Oracle/MongoDB). 
                            Access via Dashboard → Training Metadata tab to view complete training history with metrics, timestamps, 
                            and model details. Datasets show training_count and last_trained_at for easy tracking.
                          </p>
                        </div>
                      </div>
                    </div>

                    <div className="bg-indigo-50 p-4 rounded border-l-4 border-indigo-600">
                      <h4 className="font-semibold text-indigo-900 mb-2">📊 What Gets Tracked?</h4>
                      <div className="grid md:grid-cols-2 gap-3 mt-2">
                        <div className="bg-white p-3 rounded">
                          <strong className="text-sm text-indigo-600">Model Performance</strong>
                          <ul className="text-xs space-y-1 mt-1">
                            <li>✓ R² / Accuracy scores</li>
                            <li>✓ RMSE / F1-Score</li>
                            <li>✓ Feature importance</li>
                            <li>✓ Confidence levels</li>
                          </ul>
                        </div>
                        <div className="bg-white p-3 rounded">
                          <strong className="text-sm text-indigo-600">Training Context</strong>
                          <ul className="text-xs space-y-1 mt-1">
                            <li>✓ Dataset used</li>
                            <li>✓ Target variable</li>
                            <li>✓ Features selected</li>
                            <li>✓ Problem type</li>
                          </ul>
                        </div>
                        <div className="bg-white p-3 rounded">
                          <strong className="text-sm text-indigo-600">Timestamps</strong>
                          <ul className="text-xs space-y-1 mt-1">
                            <li>✓ Training date & time</li>
                            <li>✓ Duration</li>
                            <li>✓ Last updated</li>
                            <li>✓ Training count</li>
                          </ul>
                        </div>
                        <div className="bg-white p-3 rounded">
                          <strong className="text-sm text-indigo-600">Model Details</strong>
                          <ul className="text-xs space-y-1 mt-1">
                            <li>✓ Algorithm used</li>
                            <li>✓ Hyperparameters</li>
                            <li>✓ Train/test split</li>
                            <li>✓ Sample sizes</li>
                          </ul>
                        </div>
                      </div>
                    </div>

                    <div className="bg-gray-50 p-4 rounded">
                      <h4 className="font-semibold mb-2">How to Access Training Metadata:</h4>
                      <ol className="list-decimal list-inside space-y-2 text-sm">
                        <li>Navigate to <strong>Dashboard</strong></li>
                        <li>Click on <strong>Training Metadata</strong> tab</li>
                        <li>View all historical training sessions in chronological order</li>
                        <li>Click on any session to see detailed metrics</li>
                        <li>Compare performance across different experiments</li>
                      </ol>
                    </div>

                    <div className="bg-green-50 p-4 rounded">
                      <h4 className="font-semibold text-green-900 mb-2">💡 Use Cases:</h4>
                      <ul className="space-y-2 text-sm">
                        <li>
                          <strong className="text-green-700">Model Comparison:</strong> Compare different model runs to find the best performer
                        </li>
                        <li>
                          <strong className="text-green-700">Experiment Tracking:</strong> Track how model performance changes with different features or datasets
                        </li>
                        <li>
                          <strong className="text-green-700">Reproducibility:</strong> Recreate successful models using saved metadata
                        </li>
                        <li>
                          <strong className="text-green-700">Audit Trail:</strong> Maintain compliance records of all ML experiments
                        </li>
                        <li>
                          <strong className="text-green-700">Team Collaboration:</strong> Share training results and insights with team members
                        </li>
                      </ul>
                    </div>

                    <div className="bg-yellow-50 p-4 rounded border-l-4 border-yellow-600">
                      <div className="flex items-start gap-2">
                        <Info className="w-5 h-5 text-yellow-600 mt-0.5" />
                        <div>
                          <strong className="text-yellow-900">Performance Tracking:</strong>
                          <p className="text-sm text-yellow-800 mt-1">
                            The Training Metadata dashboard shows training count and last trained date for each dataset. 
                            This helps you monitor how often models are retrained and identify stale models that may need updating.
                          </p>
                        </div>
                      </div>
                    </div>

                    <div className="bg-gray-50 p-4 rounded">
                      <h4 className="font-semibold mb-2">Metadata Dashboard Features:</h4>
                      <div className="grid md:grid-cols-2 gap-3 mt-2 text-sm">
                        <div>
                          <strong className="text-indigo-600">📋 Table View</strong>
                          <p className="text-gray-600">All training sessions in sortable table format</p>
                        </div>
                        <div>
                          <strong className="text-indigo-600">🔍 Search & Filter</strong>
                          <p className="text-gray-600">Find specific experiments quickly</p>
                        </div>
                        <div>
                          <strong className="text-indigo-600">📊 Performance Charts</strong>
                          <p className="text-gray-600">Visualize model performance trends</p>
                        </div>
                        <div>
                          <strong className="text-indigo-600">📥 Export</strong>
                          <p className="text-gray-600">Download metadata for reporting</p>
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

          {/* VISUALIZATIONS TAB */}
          <TabsContent value="visualizations">
            <div className="space-y-6">
              <Card className="p-6">
                <h2 className="text-3xl font-bold mb-4 bg-gradient-to-r from-purple-600 to-pink-600 bg-clip-text text-transparent">
                  📊 Intelligent Visualization System
                </h2>
                <p className="text-lg text-gray-700 mb-4">
                  PROMISE AI features a world-class AI-powered visualization engine that analyzes your data and automatically
                  generates the most suitable charts across 8 categories with 28+ chart types.
                </p>
                
                <div className="bg-gradient-to-r from-purple-50 to-pink-50 p-4 rounded-lg mb-6">
                  <h3 className="font-bold text-purple-900 mb-2">🧠 Key Features</h3>
                  <ul className="space-y-1 text-sm text-gray-700">
                    <li>✅ <strong>Deep Data Profiling</strong> - Statistical analysis, pattern detection, outlier identification</li>
                    <li>✅ <strong>Smart Chart Recommendation</strong> - AI determines which charts fit your data</li>
                    <li>✅ <strong>28+ Chart Types</strong> - Across 8 comprehensive categories</li>
                    <li>✅ <strong>Azure OpenAI Insights</strong> - 5 key findings about your data</li>
                    <li>✅ <strong>Clear Labels & Descriptions</strong> - Every chart explains what it shows and why</li>
                    <li>✅ <strong>Graceful Failure Handling</strong> - Shows why charts can't be generated</li>
                  </ul>
                </div>
              </Card>

              {/* Category 1: Distribution */}
              <Card className="p-6 bg-gradient-to-br from-blue-50 to-cyan-50">
                <h3 className="text-2xl font-bold mb-4 text-blue-900">1️⃣ Distribution Analysis (6 Chart Types)</h3>
                <p className="text-gray-700 mb-4">Understand how your data values are spread and distributed.</p>
                
                <div className="grid md:grid-cols-2 gap-4">
                  <div className="bg-white p-4 rounded-lg shadow-sm">
                    <h4 className="font-bold text-blue-700">📊 Histogram</h4>
                    <p className="text-sm text-gray-600 mt-2">Shows frequency distribution of numeric values. Includes mean, median, std dev.</p>
                    <p className="text-xs text-gray-500 mt-1"><strong>When shown:</strong> For all numeric columns (top 5)</p>
                  </div>
                  
                  <div className="bg-white p-4 rounded-lg shadow-sm">
                    <h4 className="font-bold text-blue-700">📦 Box Plot</h4>
                    <p className="text-sm text-gray-600 mt-2">Detects outliers and shows value ranges. Displays middle 50% of data with whiskers.</p>
                    <p className="text-xs text-gray-500 mt-1"><strong>When shown:</strong> Up to 6 numeric columns</p>
                  </div>
                  
                  <div className="bg-white p-4 rounded-lg shadow-sm">
                    <h4 className="font-bold text-blue-700">🎻 Violin Plot</h4>
                    <p className="text-sm text-gray-600 mt-2">Combines box plot with density curve (KDE). Shows distribution shape.</p>
                    <p className="text-xs text-gray-500 mt-1"><strong>When shown:</strong> Top 3 numeric columns</p>
                  </div>
                  
                  <div className="bg-white p-4 rounded-lg shadow-sm">
                    <h4 className="font-bold text-blue-700">🌊 Density Plot (KDE)</h4>
                    <p className="text-sm text-gray-600 mt-2">Smooth distribution curve showing probability density.</p>
                    <p className="text-xs text-gray-500 mt-1"><strong>When shown:</strong> Top 3 numeric columns</p>
                  </div>
                  
                  <div className="bg-white p-4 rounded-lg shadow-sm">
                    <h4 className="font-bold text-blue-700">🥧 Pie Chart</h4>
                    <p className="text-sm text-gray-600 mt-2">Shows proportions across categories. Includes percentages and top category.</p>
                    <p className="text-xs text-gray-500 mt-1"><strong>When shown:</strong> Categorical columns with ≤10 unique values</p>
                  </div>
                  
                  <div className="bg-white p-4 rounded-lg shadow-sm">
                    <h4 className="font-bold text-blue-700">📈 ECDF Plot</h4>
                    <p className="text-sm text-gray-600 mt-2">Empirical Cumulative Distribution Function.</p>
                    <p className="text-xs text-gray-500 mt-1"><strong>When shown:</strong> Based on data suitability</p>
                  </div>
                </div>
              </Card>

              {/* Category 2: Relationships */}
              <Card className="p-6 bg-gradient-to-br from-green-50 to-teal-50">
                <h3 className="text-2xl font-bold mb-4 text-green-900">2️⃣ Relationship Analysis (5 Chart Types)</h3>
                <p className="text-gray-700 mb-4">Discover correlations and relationships between variables.</p>
                
                <div className="grid md:grid-cols-2 gap-4">
                  <div className="bg-white p-4 rounded-lg shadow-sm">
                    <h4 className="font-bold text-green-700">🔗 Scatter Plot</h4>
                    <p className="text-sm text-gray-600 mt-2">Shows relationship between two numeric variables. Includes trend line and correlation strength.</p>
                    <p className="text-xs text-gray-500 mt-1"><strong>When shown:</strong> Top 3 correlated pairs</p>
                  </div>
                  
                  <div className="bg-white p-4 rounded-lg shadow-sm">
                    <h4 className="font-bold text-green-700">🔥 Correlation Heatmap</h4>
                    <p className="text-sm text-gray-600 mt-2">Matrix showing correlation between all numeric variables. Hover shows variable names and strength.</p>
                    <p className="text-xs text-gray-500 mt-1"><strong>When shown:</strong> ≥2 numeric columns</p>
                  </div>
                  
                  <div className="bg-white p-4 rounded-lg shadow-sm">
                    <h4 className="font-bold text-green-700">🫧 Bubble Chart</h4>
                    <p className="text-sm text-gray-600 mt-2">3D relationship visualization with size encoding third variable.</p>
                    <p className="text-xs text-gray-500 mt-1"><strong>When shown:</strong> ≥3 numeric columns</p>
                  </div>
                  
                  <div className="bg-white p-4 rounded-lg shadow-sm">
                    <h4 className="font-bold text-green-700">🔲 Pair Plot</h4>
                    <p className="text-sm text-gray-600 mt-2">All variable pair combinations in a matrix.</p>
                    <p className="text-xs text-gray-500 mt-1"><strong>When shown:</strong> 2-5 numeric columns (readability)</p>
                  </div>
                  
                  <div className="bg-white p-4 rounded-lg shadow-sm">
                    <h4 className="font-bold text-green-700">🔷 Hexbin Plot</h4>
                    <p className="text-sm text-gray-600 mt-2">Density of points for large datasets.</p>
                    <p className="text-xs text-gray-500 mt-1"><strong>When shown:</strong> High-density data</p>
                  </div>
                </div>
              </Card>

              {/* Category 3-8: Compact View */}
              <Card className="p-6 bg-gradient-to-br from-purple-50 to-indigo-50">
                <h3 className="text-2xl font-bold mb-4 text-purple-900">3️⃣ Categorical Data Analysis (4 Chart Types)</h3>
                <div className="space-y-2 text-sm">
                  <p>📊 <strong>Bar Chart</strong> - Frequency distribution, top category with percentage</p>
                  <p>📚 <strong>Stacked Bar</strong> - Distribution across subgroups (2 categorical columns)</p>
                  <p>📈 <strong>Grouped Bar</strong> - Average numeric values by category</p>
                  <p>🔢 <strong>Count Plot</strong> - Value frequencies per category</p>
                </div>
              </Card>

              <Card className="p-6 bg-gradient-to-br from-amber-50 to-yellow-50">
                <h3 className="text-2xl font-bold mb-4 text-amber-900">4️⃣ Time Series Analysis (5 Chart Types)</h3>
                <div className="space-y-2 text-sm">
                  <p>📈 <strong>Line Plot</strong> - Value over time with trend analysis (increasing/decreasing/stable)</p>
                  <p>🌊 <strong>Rolling Average</strong> - Smoothed trends (7-period moving average)</p>
                  <p>📅 <strong>Seasonality Plot</strong> - Monthly/weekly patterns</p>
                  <p>⏱️ <strong>Lag Plot</strong> - Autocorrelation check</p>
                  <p>🗓️ <strong>Calendar Heatmap</strong> - Daily/weekly intensity</p>
                </div>
                <p className="text-xs text-gray-600 mt-3"><strong>Requirement:</strong> Dataset must have datetime column</p>
              </Card>

              <Card className="p-6 bg-gradient-to-br from-red-50 to-pink-50">
                <h3 className="text-2xl font-bold mb-4 text-red-900">5️⃣ Data Quality & Profiling (4 Chart Types)</h3>
                <div className="space-y-2 text-sm">
                  <p>🔍 <strong>Missing Value Heatmap</strong> - Visualize null patterns (sample of 500 rows)</p>
                  <p>📊 <strong>Missing % Bar Chart</strong> - Percentage of nulls per column</p>
                  <p>🎨 <strong>Data Type Distribution</strong> - Breakdown of numeric/categorical/datetime columns</p>
                  <p>🔄 <strong>Duplicate Rows Analysis</strong> - Count and percentage of duplicates</p>
                </div>
              </Card>

              <Card className="p-6 bg-gradient-to-br from-indigo-50 to-blue-50">
                <h3 className="text-2xl font-bold mb-4 text-indigo-900">6️⃣ Dimensionality & Clustering (4 Chart Types)</h3>
                <div className="space-y-2 text-sm">
                  <p>🎯 <strong>PCA Scatter</strong> - 2D projection of high-dimensional data with variance explained</p>
                  <p>🔮 <strong>K-Means Clustering</strong> - Identifies 3-5 natural clusters</p>
                  <p>🌳 <strong>Dendrogram</strong> - Hierarchical clustering tree (max 100 samples)</p>
                  <p>📐 <strong>Silhouette Plot</strong> - Cluster quality validation</p>
                </div>
                <p className="text-xs text-gray-600 mt-3"><strong>Requirement:</strong> ≥2 numeric columns, ≥10 data points</p>
              </Card>

              <Card className="p-6 bg-gradient-to-br from-teal-50 to-cyan-50">
                <h3 className="text-2xl font-bold mb-4 text-teal-900">7️⃣ Dashboard Components (2 Types)</h3>
                <div className="space-y-2 text-sm">
                  <p>📋 <strong>KPI Cards</strong> - Dataset summary (rows, columns, missing, duplicates)</p>
                  <p>🕸️ <strong>Radar Chart</strong> - Multi-dimensional feature comparison (≥3 numeric columns)</p>
                </div>
              </Card>

              <Card className="p-6 bg-gradient-to-br from-orange-50 to-red-50">
                <h3 className="text-2xl font-bold mb-4 text-orange-900">8️⃣ Custom / AI-Generated Charts</h3>
                <p className="text-gray-700 mb-3">Chat with AI assistant to generate custom visualizations:</p>
                <div className="space-y-2 text-sm">
                  <p>💬 "Show me a scatter plot of price vs sales"</p>
                  <p>💬 "Generate a correlation heatmap"</p>
                  <p>💬 "Create a bar chart comparing regions"</p>
                </div>
              </Card>

              {/* AI Insights */}
              <Card className="p-6 bg-gradient-to-r from-purple-100 to-pink-100">
                <h3 className="text-2xl font-bold mb-4 text-purple-900">🤖 AI Insights (Azure OpenAI)</h3>
                <p className="text-gray-700 mb-3">Every visualization run includes 5 key insights about your data:</p>
                <div className="bg-white p-4 rounded-lg">
                  <p className="text-sm"><strong>Example Insights:</strong></p>
                  <ul className="text-sm text-gray-700 space-y-1 mt-2 list-disc list-inside">
                    <li>Dataset contains 10,000 rows with 12 columns</li>
                    <li>Strong correlation between cpu_usage and memory_usage (0.82)</li>
                    <li>42 outliers detected in latency_ms variable</li>
                    <li>Data quality: 98.5% complete with minimal missing values</li>
                    <li>Recommendation: Consider feature engineering for date columns</li>
                  </ul>
                </div>
              </Card>

              {/* What Changed */}
              <Card className="p-6 bg-gradient-to-r from-yellow-50 to-orange-50 border-2 border-yellow-400">
                <h3 className="text-2xl font-bold mb-4 text-yellow-900">🔔 Recent Updates</h3>
                <div className="space-y-3">
                  <div className="bg-white p-4 rounded-lg">
                    <h4 className="font-bold text-green-700 mb-2">✅ Removed from Predictions Tab</h4>
                    <p className="text-sm text-gray-700">
                      Auto-generated charts are NO LONGER shown in the Predictive Analysis tab. 
                      The Predictions tab now focuses exclusively on ML models, feature importance, and model metrics.
                    </p>
                  </div>
                  
                  <div className="bg-white p-4 rounded-lg">
                    <h4 className="font-bold text-blue-700 mb-2">✅ Enhanced Visualizations Tab</h4>
                    <p className="text-sm text-gray-700">
                      All 28+ charts are now exclusively in the Visualizations tab with:
                    </p>
                    <ul className="text-xs text-gray-600 mt-2 space-y-1 list-disc list-inside">
                      <li>Categorized display (8 categories)</li>
                      <li>Clear axis labels with variable names</li>
                      <li>1-2 line descriptions explaining what each chart shows</li>
                      <li>Hover tooltips with detailed information</li>
                      <li>Skipped charts with explanations</li>
                    </ul>
                  </div>
                </div>
              </Card>
            </div>
          </TabsContent>

          {/* MCP SERVER TAB */}
          <TabsContent value="mcp">
            <div className="space-y-6">
              <Card className="p-6">
                <h2 className="text-3xl font-bold mb-4 bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                  🔌 MCP Server (Model Context Protocol)
                </h2>
                <p className="text-lg text-gray-700 mb-4">
                  The PROMISE AI MCP Server enables programmatic access to all platform features through a standardized protocol.
                  Perfect for automation, integration, and building AI agents.
                </p>
                
                <div className="bg-gradient-to-r from-blue-50 to-purple-50 p-4 rounded-lg mb-4">
                  <h3 className="font-bold text-blue-900 mb-2">📍 Location</h3>
                  <p className="text-sm text-gray-700 font-mono">/app/mcp_server/promise_ai_mcp.py</p>
                </div>
              </Card>

              {/* 12 MCP Tools */}
              <Card className="p-6 bg-gradient-to-br from-blue-50 to-cyan-50">
                <h3 className="text-2xl font-bold mb-4 text-blue-900">🛠️ 12 Available Tools</h3>
                
                <div className="space-y-4">
                  {/* Tool 1 */}
                  <div className="bg-white p-4 rounded-lg shadow-sm">
                    <h4 className="font-bold text-blue-700">1. upload_dataset</h4>
                    <p className="text-sm text-gray-600 mt-2">Upload CSV or Excel files to the platform.</p>
                    <div className="bg-gray-50 p-2 rounded mt-2 text-xs font-mono">
                      <strong>Input:</strong> file_path: string<br/>
                      <strong>Returns:</strong> dataset_id, row_count, column_count, column_list
                    </div>
                  </div>

                  {/* Tool 2 */}
                  <div className="bg-white p-4 rounded-lg shadow-sm">
                    <h4 className="font-bold text-blue-700">2. profile_data</h4>
                    <p className="text-sm text-gray-600 mt-2">Generate comprehensive data profile with statistics, missing values, outliers.</p>
                    <div className="bg-gray-50 p-2 rounded mt-2 text-xs font-mono">
                      <strong>Input:</strong> dataset_id: string<br/>
                      <strong>Returns:</strong> Full data profile with statistics
                    </div>
                  </div>

                  {/* Tool 3 */}
                  <div className="bg-white p-4 rounded-lg shadow-sm">
                    <h4 className="font-bold text-blue-700">3. train_models</h4>
                    <p className="text-sm text-gray-600 mt-2">Train 35+ ML models with auto problem type detection.</p>
                    <div className="bg-gray-50 p-2 rounded mt-2 text-xs font-mono">
                      <strong>Input:</strong> dataset_id, target_variable, feature_variables, problem_type, models<br/>
                      <strong>Returns:</strong> Trained models with metrics, feature importance, best model
                    </div>
                  </div>

                  {/* Tool 4 */}
                  <div className="bg-white p-4 rounded-lg shadow-sm">
                    <h4 className="font-bold text-blue-700">4. generate_visualizations</h4>
                    <p className="text-sm text-gray-600 mt-2">Generate 28+ intelligent visualizations across 8 categories.</p>
                    <div className="bg-gray-50 p-2 rounded mt-2 text-xs font-mono">
                      <strong>Input:</strong> dataset_id: string<br/>
                      <strong>Returns:</strong> Charts array, AI insights, skipped charts with reasons
                    </div>
                  </div>

                  {/* Tool 5 */}
                  <div className="bg-white p-4 rounded-lg shadow-sm">
                    <h4 className="font-bold text-blue-700">5. get_training_metadata</h4>
                    <p className="text-sm text-gray-600 mt-2">Retrieve historical training results and model performance.</p>
                    <div className="bg-gray-50 p-2 rounded mt-2 text-xs font-mono">
                      <strong>Input:</strong> dataset_id (optional), workspace_name (optional)<br/>
                      <strong>Returns:</strong> Training history with metrics
                    </div>
                  </div>

                  {/* Tool 6 */}
                  <div className="bg-white p-4 rounded-lg shadow-sm">
                    <h4 className="font-bold text-blue-700">6. save_workspace</h4>
                    <p className="text-sm text-gray-600 mt-2">Save complete workspace state (models, charts, configurations).</p>
                    <div className="bg-gray-50 p-2 rounded mt-2 text-xs font-mono">
                      <strong>Input:</strong> workspace_name, dataset_id, state: object<br/>
                      <strong>Returns:</strong> Success confirmation
                    </div>
                  </div>

                  {/* Tool 7 */}
                  <div className="bg-white p-4 rounded-lg shadow-sm">
                    <h4 className="font-bold text-blue-700">7. load_workspace</h4>
                    <p className="text-sm text-gray-600 mt-2">Load previously saved workspace with all cached results.</p>
                    <div className="bg-gray-50 p-2 rounded mt-2 text-xs font-mono">
                      <strong>Input:</strong> workspace_name, dataset_id<br/>
                      <strong>Returns:</strong> Complete workspace state
                    </div>
                  </div>

                  {/* Tool 8 */}
                  <div className="bg-white p-4 rounded-lg shadow-sm">
                    <h4 className="font-bold text-blue-700">8. chat_assistant</h4>
                    <p className="text-sm text-gray-600 mt-2">Interact with AI chat assistant (Azure OpenAI GPT-4o) with context-aware responses.</p>
                    <div className="bg-gray-50 p-2 rounded mt-2 text-xs font-mono">
                      <strong>Input:</strong> message, dataset_id, conversation_history<br/>
                      <strong>Returns:</strong> AI response, action type, suggestions
                    </div>
                  </div>

                  {/* Tool 9 */}
                  <div className="bg-white p-4 rounded-lg shadow-sm">
                    <h4 className="font-bold text-blue-700">9. list_datasets</h4>
                    <p className="text-sm text-gray-600 mt-2">List all uploaded datasets with metadata.</p>
                    <div className="bg-gray-50 p-2 rounded mt-2 text-xs font-mono">
                      <strong>Input:</strong> limit: integer (default 50)<br/>
                      <strong>Returns:</strong> Array of datasets with id, name, rows, columns
                    </div>
                  </div>

                  {/* Tool 10 */}
                  <div className="bg-white p-4 rounded-lg shadow-sm">
                    <h4 className="font-bold text-blue-700">10. switch_database</h4>
                    <p className="text-sm text-gray-600 mt-2">Switch between MongoDB and Oracle databases.</p>
                    <div className="bg-gray-50 p-2 rounded mt-2 text-xs font-mono">
                      <strong>Input:</strong> db_type: "mongodb" | "oracle"<br/>
                      <strong>Returns:</strong> Switch confirmation (requires backend restart)
                    </div>
                  </div>

                  {/* Tool 11 */}
                  <div className="bg-white p-4 rounded-lg shadow-sm">
                    <h4 className="font-bold text-blue-700">11. hyperparameter_tuning</h4>
                    <p className="text-sm text-gray-600 mt-2">Optimize model hyperparameters using Grid Search CV.</p>
                    <div className="bg-gray-50 p-2 rounded mt-2 text-xs font-mono">
                      <strong>Input:</strong> dataset_id, model_name, target_variable, feature_variables<br/>
                      <strong>Returns:</strong> Best hyperparameters and improved metrics
                    </div>
                  </div>

                  {/* Tool 12 */}
                  <div className="bg-white p-4 rounded-lg shadow-sm">
                    <h4 className="font-bold text-blue-700">12. delete_dataset</h4>
                    <p className="text-sm text-gray-600 mt-2">Delete dataset and all associated data (⚠️ irreversible).</p>
                    <div className="bg-gray-50 p-2 rounded mt-2 text-xs font-mono">
                      <strong>Input:</strong> dataset_id: string<br/>
                      <strong>Returns:</strong> Deletion confirmation
                    </div>
                  </div>
                </div>
              </Card>

              {/* Installation */}
              <Card className="p-6 bg-gradient-to-br from-green-50 to-teal-50">
                <h3 className="text-2xl font-bold mb-4 text-green-900">⚙️ Installation & Setup</h3>
                
                <div className="space-y-4">
                  <div>
                    <h4 className="font-bold text-green-700 mb-2">1. Install MCP Package</h4>
                    <div className="bg-gray-900 text-green-400 p-3 rounded font-mono text-sm">
                      pip install mcp aiohttp aiofiles
                    </div>
                  </div>

                  <div>
                    <h4 className="font-bold text-green-700 mb-2">2. Configure Backend URL</h4>
                    <p className="text-sm text-gray-700 mb-2">Edit <code className="bg-gray-100 px-2 py-1 rounded">/app/mcp_server/promise_ai_mcp.py</code></p>
                    <div className="bg-gray-900 text-green-400 p-3 rounded font-mono text-sm">
                      self.backend_url = "http://localhost:8001/api"  # Development<br/>
                      # or<br/>
                      self.backend_url = "https://api.yourdomain.com/api"  # Production
                    </div>
                  </div>

                  <div>
                    <h4 className="font-bold text-green-700 mb-2">3. Run MCP Server</h4>
                    <div className="bg-gray-900 text-green-400 p-3 rounded font-mono text-sm">
                      cd /app/mcp_server<br/>
                      python promise_ai_mcp.py
                    </div>
                  </div>
                </div>
              </Card>

              {/* Usage Examples */}
              <Card className="p-6 bg-gradient-to-br from-purple-50 to-pink-50">
                <h3 className="text-2xl font-bold mb-4 text-purple-900">💡 Usage Examples</h3>
                
                <div className="space-y-4">
                  <div>
                    <h4 className="font-bold text-purple-700 mb-2">Example 1: Complete Analysis Workflow</h4>
                    <div className="bg-gray-900 text-purple-400 p-3 rounded font-mono text-xs overflow-x-auto">
{`# 1. Upload dataset
result = await upload_dataset(file_path="data.csv")
dataset_id = result['dataset_id']

# 2. Profile data
profile = await profile_data(dataset_id=dataset_id)

# 3. Train models
models = await train_models(
    dataset_id=dataset_id,
    target_variable="price",
    feature_variables=["size", "location", "bedrooms"],
    problem_type="auto"
)

# 4. Generate visualizations
viz = await generate_visualizations(dataset_id=dataset_id)

# 5. Save workspace
await save_workspace(
    workspace_name="price_analysis_nov2025",
    dataset_id=dataset_id,
    state={...}
)`}
                    </div>
                  </div>

                  <div>
                    <h4 className="font-bold text-purple-700 mb-2">Example 2: Chat Assistant</h4>
                    <div className="bg-gray-900 text-purple-400 p-3 rounded font-mono text-xs overflow-x-auto">
{`response = await chat_assistant(
    message="Show me outliers in the data",
    dataset_id=dataset_id,
    conversation_history=[]
)

print(response['response'])  # AI explanation
if response['action'] == 'chart':
    display(response['data']['chart'])  # Generated chart`}
                    </div>
                  </div>
                </div>
              </Card>

              {/* Features */}
              <Card className="p-6 bg-gradient-to-r from-indigo-50 to-blue-50">
                <h3 className="text-2xl font-bold mb-4 text-indigo-900">✨ Key Features</h3>
                <div className="grid md:grid-cols-2 gap-4">
                  <div className="bg-white p-4 rounded-lg">
                    <h4 className="font-bold text-indigo-700">🔄 Asynchronous Operations</h4>
                    <p className="text-sm text-gray-600 mt-2">All tools use async/await for non-blocking execution.</p>
                  </div>
                  
                  <div className="bg-white p-4 rounded-lg">
                    <h4 className="font-bold text-indigo-700">🎯 Type-Safe</h4>
                    <p className="text-sm text-gray-600 mt-2">Pydantic schemas for input validation.</p>
                  </div>
                  
                  <div className="bg-white p-4 rounded-lg">
                    <h4 className="font-bold text-indigo-700">🚀 High Performance</h4>
                    <p className="text-sm text-gray-600 mt-2">Direct API communication with minimal overhead.</p>
                  </div>
                  
                  <div className="bg-white p-4 rounded-lg">
                    <h4 className="font-bold text-indigo-700">🔐 Secure</h4>
                    <p className="text-sm text-gray-600 mt-2">Uses same authentication as web interface.</p>
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
                
                <div className="space-y-3">
                  {/* General FAQs */}
                  <div className="border-b pb-3">
                    <h3 className="font-bold text-lg text-blue-600 mb-3">📌 General Questions</h3>
                  </div>

                  <Collapsible open={expandedSections['faq-1']} onOpenChange={() => toggleSection('faq-1')}>
                    <CollapsibleTrigger className="flex items-center justify-between w-full p-3 hover:bg-gray-50 rounded">
                      <h3 className="font-semibold text-left">Q: What is PROMISE AI and what can it do?</h3>
                      {expandedSections['faq-1'] ? <ChevronDown className="w-5 h-5" /> : <ChevronRight className="w-5 h-5" />}
                    </CollapsibleTrigger>
                    <CollapsibleContent className="px-3 py-2">
                      <p className="text-gray-700 text-sm">
                        <strong>A:</strong> PROMISE AI is an enterprise-grade machine learning platform with dual-database support (Oracle RDS 19c & MongoDB). 
                        It features 35+ ML models including XGBoost, LightGBM, CatBoost, Random Forest, SVC, and more for regression, classification, 
                        time series, clustering, dimensionality reduction, and anomaly detection. The platform integrates Azure OpenAI (GPT-4o) for 
                        AI-powered insights, natural language chart generation, and model recommendations. Additional features include hyperparameter tuning, 
                        training metadata tracking, and localStorage persistence for analysis results.
                      </p>
                    </CollapsibleContent>
                  </Collapsible>

                  <Collapsible open={expandedSections['faq-2']} onOpenChange={() => toggleSection('faq-2')}>
                    <CollapsibleTrigger className="flex items-center justify-between w-full p-3 hover:bg-gray-50 rounded">
                      <h3 className="font-semibold text-left">Q: How do I know which model to use?</h3>
                      {expandedSections['faq-2'] ? <ChevronDown className="w-5 h-5" /> : <ChevronRight className="w-5 h-5" />}
                    </CollapsibleTrigger>
                    <CollapsibleContent className="px-3 py-2">
                      <p className="text-gray-700 text-sm">
                        <strong>A:</strong> Use the always-visible Model Selector to choose specific models or click "AI Recommend" to let Azure OpenAI 
                        suggest the best models for your dataset. PROMISE AI trains all selected models and ranks them by performance (🏆 marks the best). 
                        Generally, XGBoost, LightGBM, and CatBoost excel on most datasets. For large time series data, use Prophet or LSTM. 
                        Results persist in localStorage and include training time for each model. Use Hyperparameter Tuning to further optimize performance.
                      </p>
                    </CollapsibleContent>
                  </Collapsible>

                  <Collapsible open={expandedSections['faq-3']} onOpenChange={() => toggleSection('faq-3')}>
                    <CollapsibleTrigger className="flex items-center justify-between w-full p-3 hover:bg-gray-50 rounded">
                      <h3 className="font-semibold text-left">Q: What's the difference between the 4 analysis tabs?</h3>
                      {expandedSections['faq-3'] ? <ChevronDown className="w-5 h-5" /> : <ChevronRight className="w-5 h-5" />}
                    </CollapsibleTrigger>
                    <CollapsibleContent className="px-3 py-2">
                      <div className="text-gray-700 text-sm space-y-2">
                        <p><strong>A:</strong> Each tab serves a specific purpose:</p>
                        <ul className="list-disc list-inside ml-4 space-y-1">
                          <li><strong>Predictive Analysis & Forecasting:</strong> Core ML models for regression and classification</li>
                          <li><strong>Time Series:</strong> Dedicated forecasting with Prophet/LSTM for temporal data</li>
                          <li><strong>Tune Models:</strong> Optimize model performance through hyperparameter search</li>
                          <li><strong>Feedback & Learning:</strong> Track predictions and retrain models based on real-world results</li>
                        </ul>
                        <p className="mt-2 text-xs text-gray-600">💡 Your results persist across tabs - switch freely without losing work!</p>
                      </div>
                    </CollapsibleContent>
                  </Collapsible>

                  {/* Data & Models FAQs */}
                  <div className="border-b pb-3 pt-4">
                    <h3 className="font-bold text-lg text-green-600 mb-3">📊 Data & Models</h3>
                  </div>

                  <Collapsible open={expandedSections['faq-3a']} onOpenChange={() => toggleSection('faq-3a')}>
                    <CollapsibleTrigger className="flex items-center justify-between w-full p-3 hover:bg-gray-50 rounded">
                      <h3 className="font-semibold text-left">Q: What's the difference between Oracle and MongoDB? Can I switch?</h3>
                      {expandedSections['faq-3a'] ? <ChevronDown className="w-5 h-5" /> : <ChevronRight className="w-5 h-5" />}
                    </CollapsibleTrigger>
                    <CollapsibleContent className="px-3 py-2">
                      <div className="text-gray-700 text-sm space-y-2">
                        <p><strong>A:</strong> PROMISE AI supports dual databases:</p>
                        <ul className="list-disc list-inside ml-4 space-y-1">
                          <li><strong>Oracle RDS 19c (Default):</strong> Enterprise-grade relational database with BLOB storage, connection pooling (2-10), 
                          and JSON columns for flexible schema. Ideal for production environments.</li>
                          <li><strong>MongoDB (Alternative):</strong> NoSQL document database with GridFS for file storage and flexible schema. 
                          Great for rapid development and prototyping.</li>
                        </ul>
                        <p className="mt-2"><strong>Switching:</strong> Use the compact database toggle in the header (top-right) to seamlessly switch 
                        between Oracle and MongoDB. The application restarts automatically and all functionality works identically on both databases.</p>
                      </div>
                    </CollapsibleContent>
                  </Collapsible>

                  <Collapsible open={expandedSections['faq-4']} onOpenChange={() => toggleSection('faq-4')}>
                    <CollapsibleTrigger className="flex items-center justify-between w-full p-3 hover:bg-gray-50 rounded">
                      <h3 className="font-semibold text-left">Q: What data sources are supported?</h3>
                      {expandedSections['faq-4'] ? <ChevronDown className="w-5 h-5" /> : <ChevronRight className="w-5 h-5" />}
                    </CollapsibleTrigger>
                    <CollapsibleContent className="px-3 py-2">
                      <div className="text-gray-700 text-sm space-y-2">
                        <p><strong>A:</strong> PROMISE AI supports multiple data sources:</p>
                        <ul className="list-disc list-inside ml-4 space-y-1">
                          <li>CSV file upload (recommended up to 100MB)</li>
                          <li>PostgreSQL (with optional Kerberos authentication)</li>
                          <li>MySQL (with optional Kerberos authentication)</li>
                          <li>SQL Server</li>
                          <li>Oracle</li>
                          <li>MongoDB</li>
                        </ul>
                        <p className="mt-2">For larger datasets, use database connections. The system automatically samples intelligently 
                        for datasets over 10,000 rows while maintaining statistical representativeness.</p>
                      </div>
                    </CollapsibleContent>
                  </Collapsible>

                  <Collapsible open={expandedSections['faq-5']} onOpenChange={() => toggleSection('faq-5')}>
                    <CollapsibleTrigger className="flex items-center justify-between w-full p-3 hover:bg-gray-50 rounded">
                      <h3 className="font-semibold text-left">Q: What's the maximum dataset size?</h3>
                      {expandedSections['faq-5'] ? <ChevronDown className="w-5 h-5" /> : <ChevronRight className="w-5 h-5" />}
                    </CollapsibleTrigger>
                    <CollapsibleContent className="px-3 py-2">
                      <p className="text-gray-700 text-sm">
                        <strong>A:</strong> For CSV uploads, we recommend up to 100MB. For larger datasets, use database connections. 
                        The system automatically samples large datasets (intelligently stratified) to ensure analysis completes 
                        in reasonable time while maintaining representativeness. Datasets over 100,000 rows are sampled to 10,000-20,000 rows 
                        based on complexity.
                      </p>
                    </CollapsibleContent>
                  </Collapsible>

                  <Collapsible open={expandedSections['faq-6']} onOpenChange={() => toggleSection('faq-6')}>
                    <CollapsibleTrigger className="flex items-center justify-between w-full p-3 hover:bg-gray-50 rounded">
                      <h3 className="font-semibold text-left">Q: Which data types are supported?</h3>
                      {expandedSections['faq-6'] ? <ChevronDown className="w-5 h-5" /> : <ChevronRight className="w-5 h-5" />}
                    </CollapsibleTrigger>
                    <CollapsibleContent className="px-3 py-2">
                      <div className="text-gray-700 text-sm space-y-2">
                        <p><strong>A:</strong> PROMISE AI handles all common data types:</p>
                        <ul className="list-disc list-inside ml-4 space-y-1">
                          <li><strong>Numeric:</strong> int, float (directly used in models)</li>
                          <li><strong>Categorical:</strong> Automatically one-hot encoded</li>
                          <li><strong>Text/NLP:</strong> TF-IDF feature extraction with dimensionality reduction</li>
                          <li><strong>Datetime:</strong> Extracts year, month, day, hour, day of week, is_weekend, quarter</li>
                          <li><strong>Boolean:</strong> Converted to 0/1</li>
                        </ul>
                        <p className="mt-2">The system automatically detects and processes each type appropriately!</p>
                      </div>
                    </CollapsibleContent>
                  </Collapsible>

                  {/* Metrics & Results FAQs */}
                  <div className="border-b pb-3 pt-4">
                    <h3 className="font-bold text-lg text-purple-600 mb-3">📈 Metrics & Results</h3>
                  </div>

                  <Collapsible open={expandedSections['faq-7']} onOpenChange={() => toggleSection('faq-7')}>
                    <CollapsibleTrigger className="flex items-center justify-between w-full p-3 hover:bg-gray-50 rounded">
                      <h3 className="font-semibold text-left">Q: What does "confidence" mean in model results?</h3>
                      {expandedSections['faq-7'] ? <ChevronDown className="w-5 h-5" /> : <ChevronRight className="w-5 h-5" />}
                    </CollapsibleTrigger>
                    <CollapsibleContent className="px-3 py-2">
                      <div className="text-gray-700 text-sm space-y-2">
                        <p><strong>A:</strong> Confidence indicates model reliability based on performance metrics:</p>
                        <div className="bg-gray-50 p-3 rounded mt-2">
                          <p className="font-semibold mb-2">For Regression:</p>
                          <ul className="list-disc list-inside ml-4 space-y-1">
                            <li><span className="text-green-600 font-bold">High:</span> R² &gt; 0.7 (explains 70%+ of variance)</li>
                            <li><span className="text-yellow-600 font-bold">Medium:</span> R² 0.5-0.7 (moderate predictive power)</li>
                            <li><span className="text-red-600 font-bold">Low:</span> R² &lt; 0.5 (weak predictions)</li>
                          </ul>
                        </div>
                        <div className="bg-gray-50 p-3 rounded mt-2">
                          <p className="font-semibold mb-2">For Classification:</p>
                          <ul className="list-disc list-inside ml-4 space-y-1">
                            <li><span className="text-green-600 font-bold">High:</span> Accuracy &gt; 85%</li>
                            <li><span className="text-yellow-600 font-bold">Medium:</span> Accuracy 70-85%</li>
                            <li><span className="text-red-600 font-bold">Low:</span> Accuracy &lt; 70%</li>
                          </ul>
                        </div>
                      </div>
                    </CollapsibleContent>
                  </Collapsible>

                  <Collapsible open={expandedSections['faq-8']} onOpenChange={() => toggleSection('faq-8')}>
                    <CollapsibleTrigger className="flex items-center justify-between w-full p-3 hover:bg-gray-50 rounded">
                      <h3 className="font-semibold text-left">Q: Why are some charts empty?</h3>
                      {expandedSections['faq-8'] ? <ChevronDown className="w-5 h-5" /> : <ChevronRight className="w-5 h-5" />}
                    </CollapsibleTrigger>
                    <CollapsibleContent className="px-3 py-2">
                      <div className="text-gray-700 text-sm space-y-2">
                        <p><strong>A:</strong> Charts may be empty due to several reasons:</p>
                        <ul className="list-disc list-inside ml-4 space-y-1">
                          <li><strong>Low Correlations:</strong> No feature correlations above threshold (0.3)</li>
                          <li><strong>Insufficient Data:</strong> Not enough data points for meaningful visualization</li>
                          <li><strong>Data Type Issues:</strong> Incompatible data types for the chart type</li>
                          <li><strong>All Values Identical:</strong> No variance to visualize</li>
                        </ul>
                        <p className="mt-2">💡 <strong>Tip:</strong> Check the AI Insights section for specific explanations and recommendations 
                        on how to improve your data for better visualizations.</p>
                      </div>
                    </CollapsibleContent>
                  </Collapsible>

                  <Collapsible open={expandedSections['faq-9']} onOpenChange={() => toggleSection('faq-9')}>
                    <CollapsibleTrigger className="flex items-center justify-between w-full p-3 hover:bg-gray-50 rounded">
                      <h3 className="font-semibold text-left">Q: How accurate is the AI auto-detection?</h3>
                      {expandedSections['faq-9'] ? <ChevronDown className="w-5 h-5" /> : <ChevronRight className="w-5 h-5" />}
                    </CollapsibleTrigger>
                    <CollapsibleContent className="px-3 py-2">
                      <div className="text-gray-700 text-sm space-y-2">
                        <p><strong>A:</strong> The AI auto-detection is highly accurate for standard datasets. It analyzes:</p>
                        <ul className="list-disc list-inside ml-4 space-y-1">
                          <li>Data types and distributions (numeric, categorical, text, datetime)</li>
                          <li>Correlations and feature importance scores</li>
                          <li>Missing value patterns and data quality</li>
                          <li>Cardinality and uniqueness ratios</li>
                          <li>Target variable characteristics (for problem type detection)</li>
                        </ul>
                        <p className="mt-2">For best results, use <strong>Manual</strong> or <strong>Hybrid</strong> mode if you have 
                        domain expertise. The system will validate your selections with AI intelligence.</p>
                      </div>
                    </CollapsibleContent>
                  </Collapsible>

                  {/* Advanced Features FAQs */}
                  <div className="border-b pb-3 pt-4">
                    <h3 className="font-bold text-lg text-orange-600 mb-3">🚀 Advanced Features</h3>
                  </div>

                  <Collapsible open={expandedSections['faq-10']} onOpenChange={() => toggleSection('faq-10')}>
                    <CollapsibleTrigger className="flex items-center justify-between w-full p-3 hover:bg-gray-50 rounded">
                      <h3 className="font-semibold text-left">Q: How does hyperparameter tuning improve results?</h3>
                      {expandedSections['faq-10'] ? <ChevronDown className="w-5 h-5" /> : <ChevronRight className="w-5 h-5" />}
                    </CollapsibleTrigger>
                    <CollapsibleContent className="px-3 py-2">
                      <div className="text-gray-700 text-sm space-y-2">
                        <p><strong>A:</strong> Hyperparameter tuning systematically searches for optimal model parameters and can improve 
                        performance by 5-20% typically. The system offers two search methods:</p>
                        <div className="grid md:grid-cols-2 gap-3 mt-2">
                          <div className="bg-blue-50 p-3 rounded">
                            <strong className="text-blue-900">Grid Search</strong>
                            <p className="text-xs mt-1">Tests all parameter combinations exhaustively. More thorough but slower. 
                            Best when you know the approximate parameter ranges.</p>
                          </div>
                          <div className="bg-orange-50 p-3 rounded">
                            <strong className="text-orange-900">Random Search</strong>
                            <p className="text-xs mt-1">Random sampling of parameter space. Faster with good results. 
                            Best for initial exploration or large parameter spaces.</p>
                          </div>
                        </div>
                        <p className="mt-2">Most beneficial for Random Forest, XGBoost, and LightGBM models.</p>
                      </div>
                    </CollapsibleContent>
                  </Collapsible>

                  <Collapsible open={expandedSections['faq-11']} onOpenChange={() => toggleSection('faq-11')}>
                    <CollapsibleTrigger className="flex items-center justify-between w-full p-3 hover:bg-gray-50 rounded">
                      <h3 className="font-semibold text-left">Q: What is the Training Metadata feature?</h3>
                      {expandedSections['faq-11'] ? <ChevronDown className="w-5 h-5" /> : <ChevronRight className="w-5 h-5" />}
                    </CollapsibleTrigger>
                    <CollapsibleContent className="px-3 py-2">
                      <div className="text-gray-700 text-sm space-y-2">
                        <p><strong>A:</strong> Training Metadata automatically tracks every model training session. This includes:</p>
                        <ul className="list-disc list-inside ml-4 space-y-1">
                          <li>All models trained and their performance metrics</li>
                          <li>Dataset used, target variable, and features selected</li>
                          <li>Problem type (regression/classification/time series)</li>
                          <li>Training timestamps and session duration</li>
                          <li>Hyperparameters and model configurations</li>
                        </ul>
                        <p className="mt-2"><strong>Use Cases:</strong></p>
                        <ul className="list-disc list-inside ml-4 space-y-1">
                          <li>Compare performance across different experiments</li>
                          <li>Track model improvements over time</li>
                          <li>Reproduce successful training sessions</li>
                          <li>Maintain audit trail for compliance</li>
                        </ul>
                        <p className="mt-2">Access via the <strong>Training Metadata</strong> tab in Dashboard.</p>
                      </div>
                    </CollapsibleContent>
                  </Collapsible>

                  <Collapsible open={expandedSections['faq-12']} onOpenChange={() => toggleSection('faq-12')}>
                    <CollapsibleTrigger className="flex items-center justify-between w-full p-3 hover:bg-gray-50 rounded">
                      <h3 className="font-semibold text-left">Q: How does the Feedback Loop / Active Learning work?</h3>
                      {expandedSections['faq-12'] ? <ChevronDown className="w-5 h-5" /> : <ChevronRight className="w-5 h-5" />}
                    </CollapsibleTrigger>
                    <CollapsibleContent className="px-3 py-2">
                      <div className="text-gray-700 text-sm space-y-2">
                        <p><strong>A:</strong> The Feedback Loop enables continuous model improvement based on real-world performance:</p>
                        <div className="bg-green-50 p-3 rounded mt-2">
                          <p className="font-semibold mb-2">4-Step Process:</p>
                          <ol className="list-decimal list-inside ml-4 space-y-1">
                            <li>Model makes predictions on new data</li>
                            <li>You mark predictions as correct/incorrect or provide actual outcome</li>
                            <li>System tracks accuracy and identifies improvement areas</li>
                            <li>Retrain model with feedback data for better performance</li>
                          </ol>
                        </div>
                        <p className="mt-2"><strong>Active Learning:</strong> The system automatically identifies uncertain predictions 
                        (low confidence) and prioritizes them for your review, maximizing learning efficiency.</p>
                        <p className="mt-2">Navigate to <strong>Feedback & Learning</strong> tab to track and retrain models.</p>
                      </div>
                    </CollapsibleContent>
                  </Collapsible>

                  <Collapsible open={expandedSections['faq-13']} onOpenChange={() => toggleSection('faq-13')}>
                    <CollapsibleTrigger className="flex items-center justify-between w-full p-3 hover:bg-gray-50 rounded">
                      <h3 className="font-semibold text-left">Q: What's the difference between Prophet and LSTM for time series?</h3>
                      {expandedSections['faq-13'] ? <ChevronDown className="w-5 h-5" /> : <ChevronRight className="w-5 h-5" />}
                    </CollapsibleTrigger>
                    <CollapsibleContent className="px-3 py-2">
                      <div className="text-gray-700 text-sm space-y-2">
                        <div className="grid md:grid-cols-2 gap-3 mt-2">
                          <div className="bg-blue-50 p-3 rounded">
                            <strong className="text-blue-900">Prophet (Facebook)</strong>
                            <p className="text-xs mt-2"><strong>Best For:</strong></p>
                            <ul className="text-xs list-disc list-inside ml-2">
                              <li>Business forecasting</li>
                              <li>Seasonal patterns</li>
                              <li>Holiday effects</li>
                              <li>Missing data tolerance</li>
                            </ul>
                            <p className="text-xs mt-2"><strong>Strengths:</strong> Interpretable trend decomposition, handles outliers well</p>
                          </div>
                          <div className="bg-purple-50 p-3 rounded">
                            <strong className="text-purple-900">LSTM (Deep Learning)</strong>
                            <p className="text-xs mt-2"><strong>Best For:</strong></p>
                            <ul className="text-xs list-disc list-inside ml-2">
                              <li>Complex patterns</li>
                              <li>Long-term dependencies</li>
                              <li>Large datasets (1000+ points)</li>
                              <li>Multivariate forecasting</li>
                            </ul>
                            <p className="text-xs mt-2"><strong>Strengths:</strong> Captures non-linear patterns, learns from data</p>
                          </div>
                        </div>
                        <p className="mt-2">💡 <strong>Tip:</strong> Use "Both" option to compare and choose the best performer!</p>
                      </div>
                    </CollapsibleContent>
                  </Collapsible>

                  {/* Usage & Deployment FAQs */}
                  <div className="border-b pb-3 pt-4">
                    <h3 className="font-bold text-lg text-indigo-600 mb-3">⚙️ Usage & Deployment</h3>
                  </div>

                  <Collapsible open={expandedSections['faq-14']} onOpenChange={() => toggleSection('faq-14')}>
                    <CollapsibleTrigger className="flex items-center justify-between w-full p-3 hover:bg-gray-50 rounded">
                      <h3 className="font-semibold text-left">Q: Can I use PROMISE AI for real-time predictions?</h3>
                      {expandedSections['faq-14'] ? <ChevronDown className="w-5 h-5" /> : <ChevronRight className="w-5 h-5" />}
                    </CollapsibleTrigger>
                    <CollapsibleContent className="px-3 py-2">
                      <p className="text-gray-700 text-sm">
                        <strong>A:</strong> PROMISE AI is designed for batch analysis and model training/evaluation. For production deployment 
                        with real-time predictions, export your trained model configurations and deploy them in your infrastructure using 
                        standard ML serving frameworks (TensorFlow Serving, TorchServe, FastAPI microservice, etc.). The Training Metadata 
                        feature provides all parameters needed to reproduce models. The Feedback Loop allows you to improve models based 
                        on real-world performance.
                      </p>
                    </CollapsibleContent>
                  </Collapsible>

                  <Collapsible open={expandedSections['faq-15']} onOpenChange={() => toggleSection('faq-15')}>
                    <CollapsibleTrigger className="flex items-center justify-between w-full p-3 hover:bg-gray-50 rounded">
                      <h3 className="font-semibold text-left">Q: How do I interpret business recommendations?</h3>
                      {expandedSections['faq-15'] ? <ChevronDown className="w-5 h-5" /> : <ChevronRight className="w-5 h-5" />}
                    </CollapsibleTrigger>
                    <CollapsibleContent className="px-3 py-2">
                      <div className="text-gray-700 text-sm space-y-2">
                        <p><strong>A:</strong> Business recommendations are AI-generated strategic actions based on your analysis results. 
                        They're categorized by priority:</p>
                        <div className="space-y-2 mt-2">
                          <div className="bg-red-50 p-3 rounded border-l-4 border-red-500">
                            <strong className="text-red-900">🔴 High Priority</strong>
                            <p className="text-xs mt-1">Critical actions with high expected impact. Implement immediately. 
                            Usually addresses data quality issues or significant business opportunities.</p>
                          </div>
                          <div className="bg-yellow-50 p-3 rounded border-l-4 border-yellow-500">
                            <strong className="text-yellow-900">🟡 Medium Priority</strong>
                            <p className="text-xs mt-1">Important improvements that can be scheduled. 
                            Good ROI but not urgent.</p>
                          </div>
                          <div className="bg-green-50 p-3 rounded border-l-4 border-green-500">
                            <strong className="text-green-900">🟢 Low Priority</strong>
                            <p className="text-xs mt-1">Nice-to-have enhancements with lower effort. 
                            Consider for future optimization.</p>
                          </div>
                        </div>
                        <p className="mt-2">⚠️ <strong>Important:</strong> Treat recommendations as starting points. Always validate with 
                        domain expertise before implementation.</p>
                      </div>
                    </CollapsibleContent>
                  </Collapsible>

                  <Collapsible open={expandedSections['faq-16']} onOpenChange={() => toggleSection('faq-16')}>
                    <CollapsibleTrigger className="flex items-center justify-between w-full p-3 hover:bg-gray-50 rounded">
                      <h3 className="font-semibold text-left">Q: Do my results persist when I switch between tabs?</h3>
                      {expandedSections['faq-16'] ? <ChevronDown className="w-5 h-5" /> : <ChevronRight className="w-5 h-5" />}
                    </CollapsibleTrigger>
                    <CollapsibleContent className="px-3 py-2">
                      <p className="text-gray-700 text-sm">
                        <strong>A:</strong> Yes! All your analysis results are cached and persist across tab switches. You can freely navigate 
                        between Predictive Analysis, Time Series, Tune Models, and Feedback tabs without losing any work. Results remain 
                        available until you load a different dataset or refresh the browser. This allows you to compare different analysis 
                        approaches efficiently.
                      </p>
                    </CollapsibleContent>
                  </Collapsible>

                  <Collapsible open={expandedSections['faq-17']} onOpenChange={() => toggleSection('faq-17')}>
                    <CollapsibleTrigger className="flex items-center justify-between w-full p-3 hover:bg-gray-50 rounded">
                      <h3 className="font-semibold text-left">Q: How secure is Kerberos authentication?</h3>
                      {expandedSections['faq-17'] ? <ChevronDown className="w-5 h-5" /> : <ChevronRight className="w-5 h-5" />}
                    </CollapsibleTrigger>
                    <CollapsibleContent className="px-3 py-2">
                      <p className="text-gray-700 text-sm">
                        <strong>A:</strong> Kerberos authentication provides enterprise-grade security using ticket-based authentication. 
                        It eliminates the need to transmit passwords over the network and provides mutual authentication between client and server. 
                        PROMISE AI supports Kerberos for PostgreSQL, MySQL, and other enterprise databases. Your credentials are never stored - 
                        only temporary tickets are used for authentication. This is the same security standard used by major enterprises worldwide.
                      </p>
                    </CollapsibleContent>
                  </Collapsible>

                  <Collapsible open={expandedSections['faq-18']} onOpenChange={() => toggleSection('faq-18')}>
                    <CollapsibleTrigger className="flex items-center justify-between w-full p-3 hover:bg-gray-50 rounded">
                      <h3 className="font-semibold text-left">Q: What happens to my data after analysis?</h3>
                      {expandedSections['faq-18'] ? <ChevronDown className="w-5 h-5" /> : <ChevronRight className="w-5 h-5" />}
                    </CollapsibleTrigger>
                    <CollapsibleContent className="px-3 py-2">
                      <p className="text-gray-700 text-sm">
                        <strong>A:</strong> Your uploaded data is stored securely in MongoDB for the duration of your analysis session. 
                        Analysis results, model metadata, and training history are saved separately. You can delete datasets at any time from 
                        the Dashboard. For database connections, we only query and cache a sample for analysis - your source data remains in 
                        your database. All data transmission is encrypted, and we follow enterprise security best practices.
                      </p>
                    </CollapsibleContent>
                  </Collapsible>

                  <Collapsible open={expandedSections['faq-19']} onOpenChange={() => toggleSection('faq-19')}>
                    <CollapsibleTrigger className="flex items-center justify-between w-full p-3 hover:bg-gray-50 rounded">
                      <h3 className="font-semibold text-left">Q: Can I export my models or analysis results?</h3>
                      {expandedSections['faq-19'] ? <ChevronDown className="w-5 h-5" /> : <ChevronRight className="w-5 h-5" />}
                    </CollapsibleTrigger>
                    <CollapsibleContent className="px-3 py-2">
                      <div className="text-gray-700 text-sm space-y-2">
                        <p><strong>A:</strong> Yes, multiple export options are available:</p>
                        <ul className="list-disc list-inside ml-4 space-y-1">
                          <li><strong>PDF Download:</strong> Export entire analysis with charts and insights (Ctrl+P / Cmd+P)</li>
                          <li><strong>Training Metadata:</strong> Download model parameters and performance metrics for reproduction</li>
                          <li><strong>Model Recreation:</strong> Use saved hyperparameters from Training Metadata to recreate models in your environment</li>
                          <li><strong>API Integration:</strong> Training metadata includes all information needed for API-based model serving</li>
                        </ul>
                        <p className="mt-2">For production deployment, we recommend exporting model configurations and retraining with 
                        the same parameters in your ML infrastructure.</p>
                      </div>
                    </CollapsibleContent>
                  </Collapsible>

                  <Collapsible open={expandedSections['faq-20']} onOpenChange={() => toggleSection('faq-20')}>
                    <CollapsibleTrigger className="flex items-center justify-between w-full p-3 hover:bg-gray-50 rounded">
                      <h3 className="font-semibold text-left">Q: What should I do if analysis is taking too long?</h3>
                      {expandedSections['faq-20'] ? <ChevronDown className="w-5 h-5" /> : <ChevronRight className="w-5 h-5" />}
                    </CollapsibleTrigger>
                    <CollapsibleContent className="px-3 py-2">
                      <div className="text-gray-700 text-sm space-y-2">
                        <p><strong>A:</strong> If analysis is slower than expected, try these optimization strategies:</p>
                        <ul className="list-disc list-inside ml-4 space-y-1">
                          <li><strong>Reduce Features:</strong> Use Variable Selection to choose only relevant features</li>
                          <li><strong>Sample Data:</strong> For very large datasets, the system auto-samples, but you can manually sample before upload</li>
                          <li><strong>Skip LSTM:</strong> LSTM is powerful but slowest - may not be needed for simpler patterns</li>
                          <li><strong>Use Faster Models:</strong> Decision Tree and Logistic Regression are fastest</li>
                          <li><strong>Database Connection:</strong> For large CSVs, use database connection instead</li>
                        </ul>
                        <p className="mt-2">💡 Typical analysis times: Small datasets (&lt;1K rows): 30-60s | Medium (1-10K): 1-3 mins | Large (10K+): 3-8 mins</p>
                      </div>
                    </CollapsibleContent>
                  </Collapsible>
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
