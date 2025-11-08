import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { motion } from "framer-motion";
import { Button } from "@/components/ui/button";
import CompactDatabaseToggle from "@/components/CompactDatabaseToggle";
import { 
  Database, 
  Upload, 
  BarChart3, 
  Brain, 
  Sparkles,
  TrendingUp,
  Zap,
  Shield,
  ArrowRight,
  Award,
  BookOpen,
  Target,
  Settings,
  MessageSquare,
  Activity
} from "lucide-react";

const HomePage = () => {
  const navigate = useNavigate();
  const [workspaceCount, setWorkspaceCount] = useState(0);
  
  // Fetch workspace count
  useEffect(() => {
    const fetchWorkspaceCount = async () => {
      try {
        const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/training/metadata/by-workspace`);
        const data = await response.json();
        const total = data.datasets?.reduce((sum, ds) => sum + ds.total_workspaces, 0) || 0;
        setWorkspaceCount(total);
      } catch (error) {
        console.error('Error fetching workspace count:', error);
      }
    };
    fetchWorkspaceCount();
  }, []);

  const features = [
    {
      icon: <Database className="w-6 h-6" />,
      title: "Multi-Source Data",
      description: "Connect to Oracle RDS, MongoDB, or upload CSV/Excel files with seamless switching"
    },
    {
      icon: <MessageSquare className="w-6 h-6" />,
      title: "Enhanced AI Chat Assistant",
      description: "Natural language interface with dataset awareness, chart creation, and intelligent recommendations powered by Azure OpenAI"
    },
    {
      icon: <Target className="w-6 h-6" />,
      title: "35+ ML Models",
      description: "Advanced classification & regression with XGBoost, Random Forest, Neural Networks, and more for superior predictions"
    },
    {
      icon: <TrendingUp className="w-6 h-6" />,
      title: "Time Series Forecasting",
      description: "Prophet and LSTM forecasting with anomaly detection, trend analysis, and seasonality insights"
    },
    {
      icon: <Brain className="w-6 h-6" />,
      title: "AI-Powered Insights",
      description: "Intelligent business recommendations, model explainability with SHAP, and automated feature importance"
    },
    {
      icon: <Sparkles className="w-6 h-6" />,
      title: "Interactive Visualizations",
      description: "Create charts with natural language commands, get statistical insights, and explore data correlations"
    },
    {
      icon: <Settings className="w-6 h-6" />,
      title: "Hyperparameter Tuning",
      description: "Automated optimization with grid and random search strategies to maximize model performance"
    },
    {
      icon: <Activity className="w-6 h-6" />,
      title: "Comprehensive Analytics",
      description: "NLP support, multi-table joins, training metadata tracking, and active learning with user feedback"
    }
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-100">
      {/* Navigation */}
      <nav className="fixed top-0 left-0 right-0 z-50 backdrop-blur-md bg-white/70 border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-blue-600 to-indigo-600 flex items-center justify-center">
              <Sparkles className="w-6 h-6 text-white" />
            </div>
            <span className="text-2xl font-bold bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent">
              PROMISE AI
            </span>
          </div>
          <div className="flex items-center gap-3">
            {/* Compact Database Toggle */}
            <CompactDatabaseToggle />
            
            <Button 
              onClick={() => navigate('/documentation')}
              variant="outline"
              className="px-4 py-2 rounded-full border-2 border-blue-600 text-blue-600 hover:bg-blue-50"
            >
              <BookOpen className="w-4 h-4 mr-2" />
              Documentation
            </Button>
            <Button 
              data-testid="nav-get-started-btn"
              onClick={() => navigate('/dashboard')}
              className="bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 text-white px-6 py-2 rounded-full"
            >
              Get Started <ArrowRight className="w-4 h-4 ml-2" />
            </Button>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="pt-32 pb-20 px-6">
        <div className="max-w-7xl mx-auto text-center">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
          >
            <h1 className="text-5xl sm:text-6xl lg:text-7xl font-bold mb-6 leading-tight">
              Predictive Real-time Operational
              <br />
              <span className="bg-gradient-to-r from-blue-600 via-indigo-600 to-purple-600 bg-clip-text text-transparent">
                Monitoring & Intelligence
              </span>
            </h1>
            <p className="text-lg sm:text-xl text-gray-600 mb-10 max-w-3xl mx-auto">
              Enterprise ML platform with 35+ advanced models, AI Chat Assistant, time series forecasting, and Azure OpenAI-powered insights. 
              Chat naturally with your data, create visualizations instantly, and transform raw data into actionable intelligence.
            </p>
            <div className="flex gap-4 justify-center flex-wrap">
              <Button 
                data-testid="hero-start-analyzing-btn"
                onClick={() => navigate('/dashboard')}
                size="lg"
                className="bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 text-white px-8 py-6 text-lg rounded-full shadow-lg hover:shadow-xl"
              >
                Start Analyzing <Sparkles className="w-5 h-5 ml-2" />
              </Button>
              <Button 
                onClick={() => navigate('/training-metadata')}
                size="lg"
                variant="outline"
                className="px-8 py-6 text-lg rounded-full border-2 border-purple-600 text-purple-600 hover:bg-purple-50"
              >
                <Award className="w-5 h-5 mr-2" />
                Training Metadata
              </Button>
            </div>
          </motion.div>

          {/* Key Highlights */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.4 }}
            className="mt-16 grid grid-cols-2 md:grid-cols-4 gap-6 max-w-5xl mx-auto"
          >
            {[
              { number: "35+", label: "ML Models" },
              { number: "7", label: "AI Features" },
              { number: "2", label: "Databases" },
              { number: "Azure", label: "OpenAI" }
            ].map((stat, idx) => (
              <div key={idx} className="text-center p-4 bg-white/60 backdrop-blur-sm rounded-2xl border border-gray-200">
                <div className="text-3xl font-bold bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent">
                  {stat.number}
                </div>
                <div className="text-sm text-gray-600 mt-1">{stat.label}</div>
              </div>
            ))}
          </motion.div>

          {/* Feature Preview Cards */}
          <motion.div
            initial={{ opacity: 0, y: 40 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.2 }}
            className="mt-20 grid md:grid-cols-4 gap-6 max-w-7xl mx-auto"
          >
            {features.map((feature, idx) => (
              <div
                key={idx}
                className="bg-white/80 backdrop-blur-sm rounded-2xl p-6 border border-gray-200 hover:shadow-xl hover:scale-105 transition-all"
                data-testid={`feature-card-${idx}`}
              >
                <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-blue-100 to-indigo-100 flex items-center justify-center text-blue-600 mb-4">
                  {feature.icon}
                </div>
                <h3 className="text-lg font-semibold mb-2 text-gray-800">
                  {feature.title}
                </h3>
                <p className="text-sm text-gray-600">
                  {feature.description}
                </p>
              </div>
            ))}
          </motion.div>
        </div>
      </section>

      {/* How It Works */}
      <section className="py-20 px-6 bg-white/50">
        <div className="max-w-6xl mx-auto">
          <h2 className="text-4xl font-bold text-center mb-16">
            How It Works
          </h2>
          <div className="grid md:grid-cols-4 gap-8">
            {[
              { step: "1", title: "Connect Data", desc: "Upload CSV/Excel or connect to Oracle/MongoDB" },
              { step: "2", title: "Chat with AI", desc: "Ask questions, create charts naturally with AI Chat" },
              { step: "3", title: "Train Models", desc: "35+ ML algorithms analyze and predict automatically" },
              { step: "4", title: "Get Insights", desc: "Azure OpenAI-powered recommendations and visualizations" }
            ].map((item, idx) => (
              <div key={idx} className="text-center" data-testid={`step-${idx}`}>
                <div className="w-16 h-16 rounded-full bg-gradient-to-br from-blue-600 to-indigo-600 text-white text-2xl font-bold flex items-center justify-center mx-auto mb-4">
                  {item.step}
                </div>
                <h3 className="text-xl font-semibold mb-2">{item.title}</h3>
                <p className="text-gray-600">{item.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 px-6">
        <div className="max-w-4xl mx-auto text-center bg-gradient-to-r from-blue-600 to-indigo-600 rounded-3xl p-12 text-white">
          <h2 className="text-4xl font-bold mb-6">
            Ready to Transform Your Data?
          </h2>
          <p className="text-xl mb-8 opacity-90">
            Join thousands of users leveraging AI for smarter data decisions.
          </p>
          <Button 
            data-testid="cta-get-started-btn"
            onClick={() => navigate('/dashboard')}
            size="lg"
            className="bg-white text-blue-600 hover:bg-gray-100 px-8 py-6 text-lg rounded-full font-semibold"
          >
            Get Started Free
          </Button>
        </div>
      </section>

      {/* Footer */}
      <footer className="py-8 px-6 border-t border-gray-200 bg-white/50">
        <div className="max-w-7xl mx-auto text-center text-gray-600">
          <p>© 2025 PROMISE AI. Predictive Real-time Operational Monitoring & Intelligent System Evaluation.</p>
        </div>
      </footer>
    </div>
  );
};

export default HomePage;