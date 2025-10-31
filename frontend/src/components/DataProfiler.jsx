import { useState, useEffect } from "react";
import axios from "axios";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { toast } from "sonner";
import { Loader2, Sparkles, Trash2, AlertCircle } from "lucide-react";
import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from "@/components/ui/accordion";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const DataProfiler = ({ dataset }) => {
  const [loading, setLoading] = useState(false);
  const [profileData, setProfileData] = useState(null);
  const [insights, setInsights] = useState(null);
  const [cleaningReport, setCleaningReport] = useState(null);

  useEffect(() => {
    if (dataset) {
      runProfileAnalysis();
    }
  }, [dataset]);

  const runProfileAnalysis = async () => {
    setLoading(true);
    try {
      const response = await axios.post(`${API}/analysis/run`, {
        dataset_id: dataset.id,
        analysis_type: "profile"
      });
      setProfileData(response.data);
    } catch (error) {
      toast.error("Profiling failed: " + (error.response?.data?.detail || error.message));
    } finally {
      setLoading(false);
    }
  };

  const runCleaningAnalysis = async () => {
    setLoading(true);
    try {
      const response = await axios.post(`${API}/analysis/run`, {
        dataset_id: dataset.id,
        analysis_type: "clean"
      });
      setCleaningReport(response.data);
      toast.success("Data cleaned successfully!");
      // Reload profile
      await runProfileAnalysis();
    } catch (error) {
      toast.error("Cleaning failed: " + (error.response?.data?.detail || error.message));
    } finally {
      setLoading(false);
    }
  };

  const generateInsights = async () => {
    setLoading(true);
    try {
      const response = await axios.post(`${API}/analysis/run`, {
        dataset_id: dataset.id,
        analysis_type: "insights"
      });
      setInsights(response.data.insights);
      toast.success("AI insights generated!");
    } catch (error) {
      toast.error("Insight generation failed: " + (error.response?.data?.detail || error.message));
    } finally {
      setLoading(false);
    }
  };

  if (loading && !profileData) {
    return (
      <div className="flex items-center justify-center py-12">
        <Loader2 className="w-8 h-8 animate-spin text-blue-600" />
        <span className="ml-3 text-lg">Analyzing data...</span>
      </div>
    );
  }

  return (
    <div className="space-y-6" data-testid="data-profiler">
      {/* Summary Cards */}
      {profileData && (
        <div className="grid md:grid-cols-4 gap-4">
          <Card className="p-4 bg-gradient-to-br from-blue-50 to-indigo-50 border-blue-200">
            <p className="text-sm text-gray-600 mb-1">Total Rows</p>
            <p className="text-3xl font-bold text-blue-600">{profileData.row_count.toLocaleString()}</p>
          </Card>
          <Card className="p-4 bg-gradient-to-br from-purple-50 to-pink-50 border-purple-200">
            <p className="text-sm text-gray-600 mb-1">Columns</p>
            <p className="text-3xl font-bold text-purple-600">{profileData.column_count}</p>
          </Card>
          <Card className="p-4 bg-gradient-to-br from-orange-50 to-red-50 border-orange-200">
            <p className="text-sm text-gray-600 mb-1">Missing Values</p>
            <p className="text-3xl font-bold text-orange-600">{profileData.missing_values_total.toLocaleString()}</p>
          </Card>
          <Card className="p-4 bg-gradient-to-br from-green-50 to-emerald-50 border-green-200">
            <p className="text-sm text-gray-600 mb-1">Duplicates</p>
            <p className="text-3xl font-bold text-green-600">{profileData.duplicate_rows}</p>
          </Card>
        </div>
      )}

      {/* Action Buttons */}
      <div className="flex gap-3 flex-wrap">
        <Button 
          data-testid="clean-data-btn"
          onClick={runCleaningAnalysis}
          disabled={loading}
          className="bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700"
        >
          {loading ? <Loader2 className="w-4 h-4 animate-spin mr-2" /> : <Trash2 className="w-4 h-4 mr-2" />}
          Auto Clean Data
        </Button>
        <Button 
          data-testid="generate-insights-btn"
          onClick={generateInsights}
          disabled={loading}
          variant="outline"
        >
          {loading ? <Loader2 className="w-4 h-4 animate-spin mr-2" /> : <Sparkles className="w-4 h-4 mr-2" />}
          Generate AI Insights
        </Button>
      </div>

      {/* Cleaning Report */}
      {cleaningReport && (
        <Card className="p-6 bg-green-50 border-green-200">
          <h3 className="text-lg font-semibold mb-3 flex items-center gap-2">
            <AlertCircle className="w-5 h-5 text-green-600" />
            Cleaning Report
          </h3>
          <ul className="space-y-2">
            {cleaningReport.cleaning_report.map((item, idx) => (
              <li key={idx} className="text-sm text-gray-700">✓ {item}</li>
            ))}
          </ul>
          <p className="mt-4 text-sm font-medium">New row count: {cleaningReport.new_row_count}</p>
        </Card>
      )}

      {/* AI Insights */}
      {insights && (
        <Card className="p-6 bg-gradient-to-br from-purple-50 to-blue-50 border-purple-200">
          <h3 className="text-lg font-semibold mb-3 flex items-center gap-2">
            <Sparkles className="w-5 h-5 text-purple-600" />
            AI-Powered Insights
          </h3>
          <div className="prose prose-sm max-w-none">
            <p className="whitespace-pre-wrap text-gray-700">{insights}</p>
          </div>
        </Card>
      )}

      {/* Column Details */}
      {profileData && profileData.columns && (
        <Card className="p-6">
          <h3 className="text-xl font-semibold mb-4">Column Details</h3>
          <Accordion type="single" collapsible className="w-full">
            {profileData.columns.map((col, idx) => (
              <AccordionItem key={idx} value={`col-${idx}`}>
                <AccordionTrigger data-testid={`column-${idx}-trigger`}>
                  <div className="flex items-center justify-between w-full pr-4">
                    <span className="font-medium">{col.name}</span>
                    <span className="text-sm text-gray-500">{col.dtype}</span>
                  </div>
                </AccordionTrigger>
                <AccordionContent>
                  <div className="grid md:grid-cols-2 gap-4 p-4 bg-gray-50 rounded-lg">
                    <div>
                      <p className="text-sm text-gray-600">Unique Values</p>
                      <p className="text-lg font-semibold">{col.unique_count}</p>
                    </div>
                    <div>
                      <p className="text-sm text-gray-600">Missing</p>
                      <p className="text-lg font-semibold">{col.missing_count} ({col.missing_percentage.toFixed(1)}%)</p>
                    </div>
                    {col.stats && (
                      <>
                        <div>
                          <p className="text-sm text-gray-600">Mean</p>
                          <p className="text-lg font-semibold">{col.stats.mean?.toFixed(2) || 'N/A'}</p>
                        </div>
                        <div>
                          <p className="text-sm text-gray-600">Median</p>
                          <p className="text-lg font-semibold">{col.stats.median?.toFixed(2) || 'N/A'}</p>
                        </div>
                        <div>
                          <p className="text-sm text-gray-600">Std Dev</p>
                          <p className="text-lg font-semibold">{col.stats.std?.toFixed(2) || 'N/A'}</p>
                        </div>
                        <div>
                          <p className="text-sm text-gray-600">Range</p>
                          <p className="text-lg font-semibold">
                            {col.stats.min?.toFixed(2)} - {col.stats.max?.toFixed(2)}
                          </p>
                        </div>
                      </>
                    )}
                  </div>
                </AccordionContent>
              </AccordionItem>
            ))}
          </Accordion>
        </Card>
      )}

      {/* Data Preview */}
      <Card className="p-6">
        <h3 className="text-xl font-semibold mb-4">Data Preview</h3>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b">
                {dataset.columns.slice(0, 10).map((col, idx) => (
                  <th key={idx} className="text-left p-2 font-semibold">{col}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {dataset.data_preview.map((row, idx) => (
                <tr key={idx} className="border-b hover:bg-gray-50">
                  {dataset.columns.slice(0, 10).map((col, colIdx) => (
                    <td key={colIdx} className="p-2">{String(row[col] || '-')}</td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Card>
    </div>
  );
};

export default DataProfiler;