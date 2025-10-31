import { useState, useEffect } from "react";
import axios from "axios";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { toast } from "sonner";
import { Loader2, BarChart3 } from "lucide-react";
import PlotlyChart from "@/components/PlotlyChart";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const VisualizationPanel = ({ dataset }) => {
  const [loading, setLoading] = useState(false);
  const [charts, setCharts] = useState([]);

  const generateCharts = async () => {
    setLoading(true);
    try {
      const response = await axios.post(`${API}/analysis/run`, {
        dataset_id: dataset.id,
        analysis_type: "visualize"
      });
      setCharts(response.data.charts || []);
      toast.success("Charts generated successfully!");
    } catch (error) {
      toast.error("Chart generation failed: " + (error.response?.data?.detail || error.message));
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (dataset && charts.length === 0) {
      generateCharts();
    }
  }, [dataset]);

  if (loading && charts.length === 0) {
    return (
      <div className="flex items-center justify-center py-12">
        <Loader2 className="w-8 h-8 animate-spin text-blue-600" />
        <span className="ml-3 text-lg">Generating visualizations...</span>
      </div>
    );
  }

  return (
    <div className="space-y-6" data-testid="visualization-panel">
      <Card className="p-6 bg-gradient-to-br from-blue-50 to-cyan-50 border-blue-200">
        <h3 className="text-xl font-semibold mb-4 flex items-center gap-2">
          <BarChart3 className="w-6 h-6 text-blue-600" />
          Smart Visualizations
        </h3>
        <p className="text-sm text-gray-600 mb-4">
          AI-recommended charts based on your data characteristics and types.
        </p>
        <Button 
          data-testid="regenerate-charts-btn"
          onClick={generateCharts}
          disabled={loading}
          className="bg-gradient-to-r from-blue-600 to-cyan-600 hover:from-blue-700 hover:to-cyan-700"
        >
          {loading ? (
            <><Loader2 className="w-4 h-4 animate-spin mr-2" /> Generating...</>
          ) : (
            <><BarChart3 className="w-4 h-4 mr-2" /> Regenerate Charts</>
          )}
        </Button>
      </Card>

      {charts.length === 0 && !loading && (
        <Card className="p-12 text-center">
          <BarChart3 className="w-16 h-16 mx-auto mb-4 text-gray-400" />
          <p className="text-gray-600">No visualizations yet. Click "Regenerate Charts" to create them.</p>
        </Card>
      )}

      {charts.map((chart, idx) => (
        <Card key={idx} className="p-6" data-testid={`chart-${idx}`}>
          <h4 className="text-lg font-semibold mb-2">{chart.title}</h4>
          <p className="text-sm text-gray-600 mb-4 italic">{chart.description}</p>
          <div className="w-full overflow-x-auto bg-white rounded-lg p-4">
            <PlotlyChart
              data={chart.data.data}
              layout={{
                ...chart.data.layout,
                paper_bgcolor: 'rgba(0,0,0,0)',
                plot_bgcolor: 'rgba(0,0,0,0)'
              }}
              config={{}}
            />
          </div>
        </Card>
      ))}
    </div>
  );
};

export default VisualizationPanel;