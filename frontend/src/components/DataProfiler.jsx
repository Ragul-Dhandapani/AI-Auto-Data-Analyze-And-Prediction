import { useState, useEffect } from "react";
import axios from "axios";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { toast } from "sonner";
import { Loader2, Sparkles, Trash2, AlertCircle, Download, ChevronDown, ChevronUp, Plus } from "lucide-react";
import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from "@/components/ui/accordion";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const DataProfiler = ({ dataset, onLoadNewDataset }) => {
  const [loading, setLoading] = useState(false);
  const [profileData, setProfileData] = useState(null);
  const [insights, setInsights] = useState(null);
  const [cleaningReport, setCleaningReport] = useState(null);
  const [originalRowCount, setOriginalRowCount] = useState(null);
  const [collapsedSections, setCollapsedSections] = useState({
    summary: false,
    cleaning: false,
    insights: false,
    columns: false,
    preview: false
  });

  useEffect(() => {
    if (dataset) {
      setOriginalRowCount(dataset.row_count);
      runProfileAnalysis();
    }
  }, [dataset]);

  const toggleSection = (section) => {
    setCollapsedSections(prev => ({
      ...prev,
      [section]: !prev[section]
    }));
  };

  const expandAll = () => {
    setCollapsedSections({
      summary: false,
      cleaning: false,
      insights: false,
      columns: false,
      preview: false
    });
  };

  const collapseAll = () => {
    setCollapsedSections({
      summary: true,
      cleaning: true,
      insights: true,
      columns: true,
      preview: true
    });
  };

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
      
      if (response.data.cleaning_report && response.data.cleaning_report.length > 0) {
        toast.success("Data cleaned successfully!");
        // Reload profile to show updated stats
        await runProfileAnalysis();
      } else {
        toast.info("Your data is already clean! No cleaning actions were needed.");
      }
    } catch (error) {
      toast.error("Cleaning failed: " + (error.response?.data?.detail || error.message));
    } finally {
      setLoading(false);
    }
  };

  const downloadCleanedData = async () => {
    try {
      const response = await axios.get(`${API}/datasets/${dataset.id}/download`, {
        responseType: 'blob'
      });
      
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `${dataset.name.replace(/\.[^/.]+$/, '')}_cleaned.csv`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
      
      toast.success("Cleaned data downloaded!");
    } catch (error) {
      toast.error("Download failed: " + (error.response?.data?.detail || error.message));
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

  const dataWasCleaned = cleaningReport && cleaningReport.cleaning_report && cleaningReport.cleaning_report.length > 0;
  const rowsChanged = originalRowCount && cleaningReport?.new_row_count && originalRowCount !== cleaningReport.new_row_count;

  return (
    <div className="space-y-6" data-testid="data-profiler">
      {/* Header with Controls */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold">Data Profile</h2>
          <p className="text-sm text-gray-600">Comprehensive data quality and statistics analysis</p>
        </div>
        <div className="flex gap-2">
          <Button onClick={expandAll} variant="outline" size="sm">
            <ChevronDown className="w-4 h-4 mr-2" />
            Expand All
          </Button>
          <Button onClick={collapseAll} variant="outline" size="sm">
            <ChevronUp className="w-4 h-4 mr-2" />
            Collapse All
          </Button>
          {onLoadNewDataset && (
            <Button 
              data-testid="load-new-dataset-btn"
              onClick={onLoadNewDataset} 
              variant="default"
            >
              <Plus className="w-4 h-4 mr-2" />
              Load New Dataset
            </Button>
          )}
        </div>
      </div>

      {/* Summary Cards */}
      {profileData && !collapsedSections.summary && (
        <div>
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold">Summary Statistics</h3>
            <Button onClick={() => toggleSection('summary')} variant="ghost" size="sm">
              <ChevronUp className="w-4 h-4" />
            </Button>
          </div>
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
        </div>
      )}

      {collapsedSections.summary && (
        <Card className="p-4 cursor-pointer hover:bg-gray-50" onClick={() => toggleSection('summary')}>
          <div className="flex items-center justify-between">
            <h3 className="text-lg font-semibold">Summary Statistics</h3>
            <ChevronDown className="w-5 h-5" />
          </div>
        </Card>
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
      {cleaningReport && !collapsedSections.cleaning && (
        <div>
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold">Cleaning Report</h3>
            <Button onClick={() => toggleSection('cleaning')} variant="ghost" size="sm">
              <ChevronUp className="w-4 h-4" />
            </Button>
          </div>
          
          {dataWasCleaned ? (
            <Card className="p-6 bg-green-50 border-green-200">
              <div className="flex items-start justify-between mb-4">
                <div className="flex items-start gap-3 flex-1">
                  <AlertCircle className="w-5 h-5 text-green-600 mt-0.5" />
                  <div>
                    <h4 className="font-semibold mb-2">Data Cleaned Successfully</h4>
                    <ul className="space-y-2">
                      {cleaningReport.cleaning_report.map((item, idx) => (
                        <li key={idx} className="text-sm text-gray-700">✓ {item}</li>
                      ))}
                    </ul>
                  </div>
                </div>
              </div>

              {/* Before/After Comparison */}
              <div className="mt-4 p-4 bg-white rounded-lg">
                <h4 className="font-semibold mb-3">Before vs After Comparison</h4>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <p className="text-xs text-gray-600 mb-1">Original Data</p>
                    <div className="space-y-1">
                      <p className="text-sm">
                        <span className="font-medium">Rows:</span> {originalRowCount?.toLocaleString()}
                      </p>
                      <p className="text-sm">
                        <span className="font-medium">Missing:</span> {profileData.missing_values_total}
                      </p>
                      <p className="text-sm">
                        <span className="font-medium">Duplicates:</span> {profileData.duplicate_rows}
                      </p>
                    </div>
                  </div>
                  <div>
                    <p className="text-xs text-gray-600 mb-1">Cleaned Data</p>
                    <div className="space-y-1">
                      <p className="text-sm">
                        <span className="font-medium">Rows:</span> {cleaningReport.new_row_count?.toLocaleString()}
                      </p>
                      <p className="text-sm text-green-600">
                        <span className="font-medium">Missing:</span> 0
                      </p>
                      <p className="text-sm text-green-600">
                        <span className="font-medium">Duplicates:</span> 0
                      </p>
                    </div>
                  </div>
                </div>
              </div>

              {/* Download Button */}
              <Button
                data-testid="download-cleaned-data-btn"
                onClick={downloadCleanedData}
                className="mt-4 bg-green-600 hover:bg-green-700"
              >
                <Download className="w-4 h-4 mr-2" />
                Download Cleaned Data
              </Button>
            </Card>
          ) : cleaningReport ? (
            <Card className="p-6 bg-blue-50 border-blue-200">
              <div className="flex items-start gap-3">
                <AlertCircle className="w-5 h-5 text-blue-600 mt-0.5" />
                <div>
                  <h4 className="font-semibold mb-2">Data is Already Clean!</h4>
                  <p className="text-sm text-gray-700">
                    Your data doesn't require any cleaning. No missing values, duplicates, or outliers were detected.
                  </p>
                  <p className="text-sm text-gray-600 mt-2">
                    Download not required - your original data is in optimal condition.
                  </p>
                </div>
              </div>
            </Card>
          ) : null}
        </div>
      )}

      {cleaningReport && collapsedSections.cleaning && (
        <Card className="p-4 cursor-pointer hover:bg-gray-50" onClick={() => toggleSection('cleaning')}>
          <div className="flex items-center justify-between">
            <h3 className="text-lg font-semibold">Cleaning Report</h3>
            <ChevronDown className="w-5 h-5" />
          </div>
        </Card>
      )}

      {/* AI Insights */}
      {insights && !collapsedSections.insights && (
        <div>
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold">AI-Powered Insights</h3>
            <Button onClick={() => toggleSection('insights')} variant="ghost" size="sm">
              <ChevronUp className="w-4 h-4" />
            </Button>
          </div>
          <Card className="p-6 bg-gradient-to-br from-purple-50 to-blue-50 border-purple-200">
            <div className="flex items-start gap-3">
              <Sparkles className="w-5 h-5 text-purple-600 mt-0.5" />
              <div className="prose prose-sm max-w-none">
                <p className="whitespace-pre-wrap text-gray-700">{insights}</p>
              </div>
            </div>
          </Card>
        </div>
      )}

      {insights && collapsedSections.insights && (
        <Card className="p-4 cursor-pointer hover:bg-gray-50" onClick={() => toggleSection('insights')}>
          <div className="flex items-center justify-between">
            <h3 className="text-lg font-semibold">AI-Powered Insights</h3>
            <ChevronDown className="w-5 h-5" />
          </div>
        </Card>
      )}

      {/* Column Details */}
      {profileData && profileData.columns && !collapsedSections.columns && (
        <div>
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold">Column Details</h3>
            <Button onClick={() => toggleSection('columns')} variant="ghost" size="sm">
              <ChevronUp className="w-4 h-4" />
            </Button>
          </div>
          <Card className="p-6">
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
        </div>
      )}

      {profileData && profileData.columns && collapsedSections.columns && (
        <Card className="p-4 cursor-pointer hover:bg-gray-50" onClick={() => toggleSection('columns')}>
          <div className="flex items-center justify-between">
            <h3 className="text-lg font-semibold">Column Details ({profileData.columns.length} columns)</h3>
            <ChevronDown className="w-5 h-5" />
          </div>
        </Card>
      )}

      {/* Data Preview */}
      {!collapsedSections.preview && (
        <div>
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold">Data Preview</h3>
            <Button onClick={() => toggleSection('preview')} variant="ghost" size="sm">
              <ChevronUp className="w-4 h-4" />
            </Button>
          </div>
          <Card className="p-6">
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
      )}

      {collapsedSections.preview && (
        <Card className="p-4 cursor-pointer hover:bg-gray-50" onClick={() => toggleSection('preview')}>
          <div className="flex items-center justify-between">
            <h3 className="text-lg font-semibold">Data Preview</h3>
            <ChevronDown className="w-5 h-5" />
          </div>
        </Card>
      )}
    </div>
  );
};

export default DataProfiler;
