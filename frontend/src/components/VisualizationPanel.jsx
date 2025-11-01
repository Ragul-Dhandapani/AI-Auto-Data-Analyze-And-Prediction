import { useState, useEffect } from "react";
import axios from "axios";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { toast } from "sonner";
import { Loader2, BarChart3 } from "lucide-react";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Load Plotly script
const loadPlotly = () => {
  return new Promise((resolve) => {
    if (window.Plotly) {
      resolve(window.Plotly);
      return;
    }
    
    const script = document.createElement('script');
    script.src = 'https://cdn.plot.ly/plotly-2.27.0.min.js';
    script.async = true;
    script.onload = () => resolve(window.Plotly);
    document.head.appendChild(script);
  });
};

const ChartComponent = ({ chart, index }) => {
  const chartId = `plotly-chart-${index}`;
  
  useEffect(() => {
    const renderChart = async () => {
      await loadPlotly();
      
      if (window.Plotly && chart.data) {
        const container = document.getElementById(chartId);
        if (container) {
          window.Plotly.newPlot(
            chartId,
            chart.data.data,
            {
              ...chart.data.layout,
              autosize: true,
              height: 400,
              paper_bgcolor: 'rgba(0,0,0,0)',
              plot_bgcolor: 'rgba(0,0,0,0)',
              font: { family: 'Inter, sans-serif' }
            },
            { 
              responsive: true, 
              displayModeBar: false 
            }
          );
        }
      }
    };
    
    renderChart();
    
    return () => {
      if (window.Plotly) {
        const container = document.getElementById(chartId);
        if (container) {
          window.Plotly.purge(chartId);
        }
      }
    };
  }, [chart, chartId]);
  
  return (
    <Card className="p-6" data-testid={`chart-${index}`}>
      <h4 className="text-lg font-semibold mb-2">{chart.title}</h4>
      <p className="text-sm text-gray-600 mb-4 italic">{chart.description}</p>
      <div className="w-full bg-white rounded-lg p-4">
        <div id={chartId} style={{ width: '100%', height: '400px' }} />
      </div>
    </Card>
  );
};

const VisualizationPanel = ({ dataset }) => {
  const [loading, setLoading] = useState(false);
  const [charts, setCharts] = useState([]);
  const [hasGenerated, setHasGenerated] = useState(false);

  const generateCharts = async () => {
    setLoading(true);
    try {
      const response = await axios.post(`${API}/analysis/run`, {
        dataset_id: dataset.id,
        analysis_type: "visualize"
      });
      setCharts(response.data.charts || []);
      setHasGenerated(true);
      if (response.data.charts?.length > 0) {
        toast.success(`Generated ${response.data.charts.length} visualizations!`);
      }
    } catch (error) {
      toast.error("Chart generation failed: " + (error.response?.data?.detail || error.message));
    } finally {
      setLoading(false);
    }
  };

  // Auto-generate charts only once on mount
  useEffect(() => {
    if (dataset && !hasGenerated) {
      generateCharts();
    }
  }, [dataset, hasGenerated]);

  const refreshCharts = () => {
    setHasGenerated(false);
    setCharts([]);
    generateCharts();
  };

  // Filter charts to only show those with valid data
  const validCharts = charts.filter(chart => 
    chart.data && 
    chart.data.data && 
    Array.isArray(chart.data.data) &&
    chart.data.data.length > 0
  );

  if (loading && validCharts.length === 0) {
    return (
      <div className="flex items-center justify-center py-12" data-testid="visualization-panel">
        <Loader2 className="w-8 h-8 animate-spin text-blue-600" />
        <span className="ml-3 text-lg">Generating comprehensive visualizations...</span>
      </div>
    );
  }

  if (validCharts.length === 0) {
    return (
      <div className="flex items-center justify-center py-12" data-testid="visualization-panel">
        <p className="text-gray-600">No visualizations available. Please select a dataset.</p>
      </div>
    );
  }

  return (
    <div className="space-y-6" data-testid="visualization-panel">
      <Card className="p-6 bg-gradient-to-br from-blue-50 to-cyan-50 border-blue-200">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-xl font-semibold flex items-center gap-2">
              <BarChart3 className="w-6 h-6 text-blue-600" />
              Data Visualization & Insights
            </h3>
            <p className="text-sm text-gray-600 mt-2">
              Comprehensive charts automatically generated based on your data characteristics. 
              {validCharts.length > 0 && ` Showing ${validCharts.length} detailed visualizations with insights.`}
            </p>
          </div>
          {validCharts.length > 0 && (
            <Button 
              data-testid="refresh-charts-btn"
              onClick={refreshCharts}
              disabled={loading}
              variant="outline"
            >
              {loading ? (
                <><Loader2 className="w-4 h-4 animate-spin mr-2" /> Refreshing...</>
              ) : (
                <><BarChart3 className="w-4 h-4 mr-2" /> Refresh Charts</>
              )}
            </Button>
          )}
        </div>
      </Card>

      {charts.length === 0 && !loading && (
        <Card className="p-12 text-center">
          <BarChart3 className="w-16 h-16 mx-auto mb-4 text-gray-400" />
          <p className="text-gray-600">Loading visualizations...</p>
        </Card>
      )}

      <div className="grid md:grid-cols-2 gap-6">
        {charts.map((chart, idx) => (
          <ChartComponent key={`${dataset.id}-${idx}`} chart={chart} index={idx} />
        ))}
      </div>
    </div>
  );
};

export default VisualizationPanel;