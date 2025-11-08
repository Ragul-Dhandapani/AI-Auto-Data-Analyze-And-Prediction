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
    preview: false,
    missing_details: true  // Collapsed by default
  });
  
  // New state for data preview filters
  const [columnFilter, setColumnFilter] = useState('');
  const [dataFilter, setDataFilter] = useState('');
  const [selectedColumns, setSelectedColumns] = useState([]);
  const [showColumnSelector, setShowColumnSelector] = useState(false);
  const [columnFilters, setColumnFilters] = useState({}); // Per-column filters

  useEffect(() => {
    if (dataset && dataset.id) {
      setOriginalRowCount(dataset.row_count);
      // Initialize selected columns with first 10
      if (dataset.columns && dataset.columns.length > 0) {
        setSelectedColumns(dataset.columns.slice(0, 10));
      }
      // Only run profile if we don't have data or dataset changed
      if (!profileData || profileData.dataset_id !== dataset.id) {
        runProfileAnalysis();
      }
    }
  }, [dataset?.id]); // Only re-run if dataset ID changes

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
      preview: false,
      missing_details: false
    });
  };

  const collapseAll = () => {
    setCollapsedSections({
      summary: true,
      cleaning: true,
      insights: true,
      columns: true,
      preview: true,
      missing_details: true
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
            <Card className="p-4 bg-gradient-to-br from-orange-50 to-red-50 border-orange-200 cursor-pointer hover:shadow-md transition-shadow" onClick={() => toggleSection('missing_details')}>
              <p className="text-sm text-gray-600 mb-1">Missing Values</p>
              <p className="text-3xl font-bold text-orange-600">{profileData.missing_values_total.toLocaleString()}</p>
              {profileData.missing_values_total > 0 && (
                <p className="text-xs text-orange-500 mt-1">Click to see details →</p>
              )}
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

      {/* Missing Values Details */}
      {profileData && profileData.missing_values_total > 0 && !collapsedSections.missing_details && (
        <Card className="p-6">
          <div className="flex items-start justify-between mb-4">
            <div>
              <h3 className="text-lg font-semibold">Missing Values Details</h3>
              <p className="text-sm text-gray-600 italic mt-1">
                Shows columns with incomplete data (null, NaN, empty, or undefined values).
                <br />
                Missing data can affect analysis accuracy and model performance - consider cleaning or imputing these values.
              </p>
            </div>
            <Button onClick={() => toggleSection('missing_details')} variant="ghost" size="sm">
              <ChevronUp className="w-4 h-4" />
            </Button>
          </div>
          
          <div className="space-y-3">
            {profileData.columns_info && profileData.columns_info
              .filter(col => col.missing_count > 0)
              .sort((a, b) => b.missing_count - a.missing_count)
              .map((col, idx) => {
                const missingPercent = ((col.missing_count / profileData.row_count) * 100).toFixed(1);
                return (
                  <div key={idx} className="p-4 bg-gray-50 rounded-lg border border-gray-200">
                    <div className="flex items-center justify-between mb-2">
                      <span className="font-semibold text-gray-800">{col.name}</span>
                      <span className="text-sm bg-orange-100 text-orange-700 px-2 py-1 rounded">{col.dtype}</span>
                    </div>
                    <div className="flex items-center gap-4">
                      <div>
                        <span className="text-2xl font-bold text-orange-600">{col.missing_count.toLocaleString()}</span>
                        <span className="text-sm text-gray-600 ml-2">missing values</span>
                      </div>
                      <div className="flex-1">
                        <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
                          <div 
                            className="h-full bg-orange-500" 
                            style={{ width: `${missingPercent}%` }}
                          ></div>
                        </div>
                      </div>
                      <span className="text-sm font-semibold text-orange-600">{missingPercent}%</span>
                    </div>
                  </div>
                );
              })}
          </div>
        </Card>
      )}

      {profileData && profileData.missing_values_total > 0 && collapsedSections.missing_details && (
        <Card className="p-4 cursor-pointer hover:bg-gray-50" onClick={() => toggleSection('missing_details')}>
          <div className="flex items-center justify-between">
            <h3 className="text-lg font-semibold">Missing Values Details ({profileData.columns_info.filter(c => c.missing_count > 0).length} columns affected)</h3>
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
                        <li key={idx} className="text-sm text-gray-700">
                          ✓ {typeof item === 'object' ? `${item.action}: ${item.details}` : item}
                        </li>
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
            <div className="space-y-2">
              {/* Header */}
              <div className="grid grid-cols-12 gap-2 pb-2 border-b border-gray-300 font-semibold text-sm text-gray-700">
                <div className="col-span-3">Column Name</div>
                <div className="col-span-2">Data Type</div>
                <div className="col-span-2">Unique Values</div>
                <div className="col-span-2">Missing</div>
                <div className="col-span-3">Statistics</div>
              </div>
              
              {/* Column Rows */}
              {profileData.columns.map((col, idx) => (
                <div key={idx} className="grid grid-cols-12 gap-2 py-3 border-b border-gray-200 hover:bg-gray-50 rounded transition-colors" data-testid={`column-row-${idx}`}>
                  {/* Column Name */}
                  <div className="col-span-3 font-medium text-gray-900 truncate" title={col.name}>
                    {col.name}
                  </div>
                  
                  {/* Data Type */}
                  <div className="col-span-2">
                    <span className="inline-block px-2 py-1 text-xs rounded bg-blue-100 text-blue-800 font-mono">
                      {col.dtype}
                    </span>
                  </div>
                  
                  {/* Unique Values */}
                  <div className="col-span-2 text-sm">
                    <span className="font-semibold text-gray-900">{col.unique_count?.toLocaleString() || 0}</span>
                    <span className="text-gray-500 ml-1">
                      ({((col.unique_count / (profileData.total_rows || 1)) * 100).toFixed(1)}%)
                    </span>
                  </div>
                  
                  {/* Missing Values */}
                  <div className="col-span-2 text-sm">
                    <span className={`font-semibold ${col.missing_count > 0 ? 'text-red-600' : 'text-green-600'}`}>
                      {col.missing_count?.toLocaleString() || 0}
                    </span>
                    <span className={`ml-1 ${col.missing_count > 0 ? 'text-red-500' : 'text-gray-500'}`}>
                      ({col.missing_percentage?.toFixed(1) || 0}%)
                    </span>
                  </div>
                  
                  {/* Statistics */}
                  <div className="col-span-3 text-xs text-gray-600">
                    {col.stats ? (
                      <div className="space-y-1">
                        <div>
                          <span className="font-semibold">Range:</span> {col.stats.min?.toFixed(2)} - {col.stats.max?.toFixed(2)}
                        </div>
                        <div>
                          <span className="font-semibold">Mean:</span> {col.stats.mean?.toFixed(2)} | 
                          <span className="font-semibold ml-1">Std:</span> {col.stats.std?.toFixed(2)}
                        </div>
                      </div>
                    ) : (
                      <span className="text-gray-400 italic">Categorical column</span>
                    )}
                  </div>
                </div>
              ))}
            </div>
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

      {/* Data Preview with Filters */}
      {!collapsedSections.preview && (
        <div>
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold">Data Preview</h3>
            <Button onClick={() => toggleSection('preview')} variant="ghost" size="sm">
              <ChevronUp className="w-4 h-4" />
            </Button>
          </div>
          <Card className="p-6">
            {/* Filter Controls */}
            <div className="mb-4 space-y-3">
              <div className="flex gap-3 items-center flex-wrap">
                {/* Data Filter */}
                <input
                  type="text"
                  placeholder="Filter data (search in all columns)..."
                  value={dataFilter}
                  onChange={(e) => setDataFilter(e.target.value)}
                  className="px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent flex-1 min-w-[250px]"
                />
                
                {/* Column Selector Button */}
                <Button 
                  onClick={() => setShowColumnSelector(!showColumnSelector)}
                  variant="outline"
                  size="sm"
                  className="whitespace-nowrap"
                >
                  <Plus className="w-4 h-4 mr-2" />
                  Select Columns ({selectedColumns.length}/{dataset.columns?.length || 0})
                </Button>
                
                {/* Reset Filters */}
                {(dataFilter || columnFilter) && (
                  <Button 
                    onClick={() => {
                      setDataFilter('');
                      setColumnFilter('');
                    }}
                    variant="ghost"
                    size="sm"
                  >
                    Clear Filters
                  </Button>
                )}
              </div>
              
              {/* Column Selector Dropdown */}
              {showColumnSelector && (
                <div className="border border-gray-200 rounded-md p-3 bg-gray-50 max-h-64 overflow-y-auto">
                  <div className="mb-2">
                    <input
                      type="text"
                      placeholder="Search columns..."
                      value={columnFilter}
                      onChange={(e) => setColumnFilter(e.target.value)}
                      className="w-full px-3 py-1 border border-gray-300 rounded-md text-sm"
                    />
                  </div>
                  <div className="space-y-1">
                    <div className="flex gap-2 mb-2">
                      <button
                        onClick={() => setSelectedColumns(dataset.columns)}
                        className="text-xs text-blue-600 hover:underline"
                      >
                        Select All
                      </button>
                      <button
                        onClick={() => setSelectedColumns([])}
                        className="text-xs text-blue-600 hover:underline"
                      >
                        Clear All
                      </button>
                    </div>
                    {dataset.columns
                      ?.filter(col => col.toLowerCase().includes(columnFilter.toLowerCase()))
                      .map((col, idx) => (
                      <label key={idx} className="flex items-center gap-2 cursor-pointer hover:bg-gray-100 p-1 rounded">
                        <input
                          type="checkbox"
                          checked={selectedColumns.includes(col)}
                          onChange={(e) => {
                            if (e.target.checked) {
                              setSelectedColumns([...selectedColumns, col]);
                            } else {
                              setSelectedColumns(selectedColumns.filter(c => c !== col));
                            }
                          }}
                          className="rounded border-gray-300"
                        />
                        <span className="text-sm">{col}</span>
                      </label>
                    ))}
                  </div>
                </div>
              )}
            </div>
            
            {/* Data Table */}
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  {/* Column Headers with Per-Column Filters */}
                  <tr className="border-b bg-gray-50">
                    {selectedColumns.length > 0 ? (
                      selectedColumns.map((col, idx) => (
                        <th key={idx} className="text-left p-2 font-semibold">
                          <div className="flex flex-col gap-1">
                            <span className="truncate" title={col}>{col}</span>
                            <input
                              type="text"
                              placeholder="🔍 Filter..."
                              value={columnFilters[col] || ''}
                              className="text-xs px-2 py-1 border border-gray-300 rounded focus:ring-1 focus:ring-blue-500 focus:border-blue-500 font-normal"
                              onClick={(e) => e.stopPropagation()}
                              onChange={(e) => {
                                const value = e.target.value;
                                setColumnFilters(prev => ({
                                  ...prev,
                                  [col]: value
                                }));
                              }}
                            />
                          </div>
                        </th>
                      ))
                    ) : (
                      <th className="text-left p-2 text-gray-500">No columns selected</th>
                    )}
                  </tr>
                </thead>
                <tbody>
                  {selectedColumns.length > 0 && dataset.data_preview && dataset.data_preview.length > 0 ? (
                    dataset.data_preview
                      .filter(row => {
                        // Global filter
                        if (dataFilter && !selectedColumns.some(col => 
                          String(row[col] || '').toLowerCase().includes(dataFilter.toLowerCase())
                        )) {
                          return false;
                        }
                        
                        // Per-column filters
                        for (const col of selectedColumns) {
                          const colFilter = columnFilters[col];
                          if (colFilter && !String(row[col] || '').toLowerCase().includes(colFilter.toLowerCase())) {
                            return false;
                          }
                        }
                        
                        return true;
                      })
                      .map((row, idx) => (
                        <tr key={idx} className="border-b hover:bg-gray-50">
                          {selectedColumns.map((col, colIdx) => (
                            <td key={colIdx} className="p-2">{String(row[col] || '-')}</td>
                          ))}
                        </tr>
                      ))
                  ) : (
                    <tr>
                      <td colSpan={selectedColumns.length || 1} className="p-4 text-center text-gray-500">
                        {!dataset.data_preview || dataset.data_preview.length === 0 
                          ? "No data preview available" 
                          : "Select columns to view data"}
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
            
            {/* Results Count */}
            {selectedColumns.length > 0 && dataset.data_preview && (
              <div className="mt-3 text-xs text-gray-500">
                Showing {dataset.data_preview.filter(row => {
                  if (!dataFilter) return true;
                  return selectedColumns.some(col => 
                    String(row[col] || '').toLowerCase().includes(dataFilter.toLowerCase())
                  );
                }).length} of {dataset.data_preview.length} rows
                {dataFilter && ` (filtered)`}
              </div>
            )}
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
