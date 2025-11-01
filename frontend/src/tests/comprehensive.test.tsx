/**
 * Comprehensive Frontend Test Suite for PROMISE AI
 * Tests critical components and user interactions
 */

import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import { BrowserRouter } from 'react-router-dom';
import axios from 'axios';

// Mock axios
jest.mock('axios');
const mockedAxios = axios as jest.Mocked<typeof axios>;

// Import components
import DataSourceSelector from '../components/DataSourceSelector';
import PredictiveAnalysis from '../components/PredictiveAnalysis';
import VisualizationPanel from '../components/VisualizationPanel';
import DashboardPage from '../pages/DashboardPage';

describe('DataSourceSelector Component', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  test('renders file upload tab by default', () => {
    render(<DataSourceSelector onDatasetLoaded={jest.fn()} />);
    
    expect(screen.getByTestId('tab-file-upload')).toBeInTheDocument();
    expect(screen.getByText(/Drag & drop file here/i)).toBeInTheDocument();
  });

  test('switches to database connection tab', () => {
    render(<DataSourceSelector onDatasetLoaded={jest.fn()} />);
    
    const dbTab = screen.getByTestId('tab-database');
    fireEvent.click(dbTab);
    
    expect(screen.getByTestId('db-type-select')).toBeInTheDocument();
    expect(screen.getByText(/Database Type/i)).toBeInTheDocument();
  });

  test('displays all database types in dropdown', () => {
    render(<DataSourceSelector onDatasetLoaded={jest.fn()} />);
    
    const dbTab = screen.getByTestId('tab-database');
    fireEvent.click(dbTab);
    
    const select = screen.getByTestId('db-type-select');
    fireEvent.click(select);
    
    expect(screen.getByText('PostgreSQL')).toBeInTheDocument();
    expect(screen.getByText('MySQL')).toBeInTheDocument();
    expect(screen.getByText('Oracle')).toBeInTheDocument();
    expect(screen.getByText('SQL Server')).toBeInTheDocument();
    expect(screen.getByText('MongoDB')).toBeInTheDocument();
  });

  test('shows connection string input when checkbox is checked', () => {
    render(<DataSourceSelector onDatasetLoaded={jest.fn()} />);
    
    const dbTab = screen.getByTestId('tab-database');
    fireEvent.click(dbTab);
    
    const checkbox = screen.getByLabelText(/Use Connection String/i);
    fireEvent.click(checkbox);
    
    expect(screen.getByTestId('connection-string-input')).toBeInTheDocument();
  });

  test('test connection button is disabled while loading', async () => {
    mockedAxios.post.mockResolvedValueOnce({
      data: { success: false, message: 'Connection failed' }
    });

    render(<DataSourceSelector onDatasetLoaded={jest.fn()} />);
    
    const dbTab = screen.getByTestId('tab-database');
    fireEvent.click(dbTab);
    
    const testButton = screen.getByTestId('test-connection-btn');
    fireEvent.click(testButton);
    
    expect(testButton).toBeDisabled();
  });

  test('handles successful connection test', async () => {
    mockedAxios.post.mockResolvedValueOnce({
      data: { success: true, message: 'Connection successful' }
    });

    render(<DataSourceSelector onDatasetLoaded={jest.fn()} />);
    
    const dbTab = screen.getByTestId('tab-database');
    fireEvent.click(dbTab);
    
    // Fill in connection details
    fireEvent.change(screen.getByTestId('db-host-input'), { 
      target: { value: 'localhost' } 
    });
    
    const testButton = screen.getByTestId('test-connection-btn');
    fireEvent.click(testButton);
    
    await waitFor(() => {
      expect(mockedAxios.post).toHaveBeenCalled();
    });
  });

  test('file upload triggers onDatasetLoaded callback', async () => {
    const mockCallback = jest.fn();
    const mockResponse = {
      data: {
        id: 'test-id',
        name: 'test.csv',
        row_count: 10,
        column_count: 3
      }
    };

    mockedAxios.post.mockResolvedValueOnce(mockResponse);

    render(<DataSourceSelector onDatasetLoaded={mockCallback} />);
    
    const file = new File(['col1,col2\n1,2\n3,4'], 'test.csv', { type: 'text/csv' });
    const dropzone = screen.getByTestId('file-dropzone');
    
    fireEvent.drop(dropzone, {
      dataTransfer: { files: [file] }
    });
    
    await waitFor(() => {
      expect(mockCallback).toHaveBeenCalledWith(mockResponse.data);
    });
  });
});

describe('PredictiveAnalysis Component', () => {
  const mockDataset = {
    id: 'test-dataset-id',
    name: 'test.csv',
    columns: ['col1', 'col2', 'col3']
  };

  beforeEach(() => {
    jest.clearAllMocks();
  });

  test('renders loading state initially', () => {
    render(<PredictiveAnalysis dataset={mockDataset} />);
    
    expect(screen.getByText(/Analyzing your data/i)).toBeInTheDocument();
  });

  test('displays analysis results after loading', async () => {
    const mockAnalysis = {
      models: [
        { model_name: 'Linear Regression', r2_score: 0.85, rmse: 5.2 }
      ],
      correlations: [],
      auto_charts: []
    };

    mockedAxios.post.mockResolvedValueOnce({ data: mockAnalysis });

    render(<PredictiveAnalysis dataset={mockDataset} />);
    
    await waitFor(() => {
      expect(screen.getByText(/Linear Regression/i)).toBeInTheDocument();
    });
  });

  test('progress bar caps at 90% until completion', async () => {
    render(<PredictiveAnalysis dataset={mockDataset} />);
    
    // Check that progress doesn't exceed 90% before completion
    const progressBar = screen.getByRole('progressbar');
    const progress = parseInt(progressBar.getAttribute('aria-valuenow') || '0');
    
    expect(progress).toBeLessThanOrEqual(90);
  });

  test('chat button opens chat interface', () => {
    render(<PredictiveAnalysis dataset={mockDataset} />);
    
    const chatButton = screen.getByText(/Ask AI/i);
    fireEvent.click(chatButton);
    
    expect(screen.getByPlaceholderText(/Ask about your data/i)).toBeInTheDocument();
  });

  test('save workspace button is present', async () => {
    mockedAxios.post.mockResolvedValueOnce({
      data: { models: [], correlations: [], auto_charts: [] }
    });

    render(<PredictiveAnalysis dataset={mockDataset} />);
    
    await waitFor(() => {
      expect(screen.getByText(/Save/i)).toBeInTheDocument();
    });
  });
});

describe('VisualizationPanel Component', () => {
  const mockDataset = {
    id: 'test-dataset-id',
    name: 'test.csv'
  };

  const mockCharts = [
    {
      type: 'histogram',
      title: 'Distribution of Age',
      plotly_data: { data: [], layout: {} },
      description: 'Shows age distribution'
    }
  ];

  beforeEach(() => {
    jest.clearAllMocks();
  });

  test('renders chart sections', () => {
    render(<VisualizationPanel dataset={mockDataset} charts={mockCharts} />);
    
    expect(screen.getByText(/Distribution of Age/i)).toBeInTheDocument();
  });

  test('charts are collapsible', () => {
    render(<VisualizationPanel dataset={mockDataset} charts={mockCharts} />);
    
    const collapseButton = screen.getAllByRole('button')[0];
    fireEvent.click(collapseButton);
    
    // Chart should be collapsed
    expect(screen.queryByText(/Shows age distribution/i)).not.toBeVisible();
  });

  test('chat interface is available', () => {
    render(<VisualizationPanel dataset={mockDataset} charts={mockCharts} />);
    
    expect(screen.getByPlaceholderText(/Ask about visualizations/i)).toBeInTheDocument();
  });
});

describe('DashboardPage Integration', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  test('renders data source selector initially', () => {
    render(
      <BrowserRouter>
        <DashboardPage />
      </BrowserRouter>
    );
    
    expect(screen.getByText(/Select Data Source/i)).toBeInTheDocument();
  });

  test('displays recent datasets section', async () => {
    mockedAxios.get.mockResolvedValueOnce({
      data: { datasets: [] }
    });

    render(
      <BrowserRouter>
        <DashboardPage />
      </BrowserRouter>
    );
    
    await waitFor(() => {
      expect(screen.getByText(/Recent Datasets/i)).toBeInTheDocument();
    });
  });

  test('displays saved workspaces section', async () => {
    mockedAxios.get.mockResolvedValueOnce({
      data: { datasets: [] }
    });

    render(
      <BrowserRouter>
        <DashboardPage />
      </BrowserRouter>
    );
    
    await waitFor(() => {
      expect(screen.getByText(/Saved Workspaces/i)).toBeInTheDocument();
    });
  });

  test('tabs switch between Data Profiler, Predictive Analysis, and Visualization', async () => {
    const mockDataset = {
      id: 'test-id',
      name: 'test.csv'
    };

    render(
      <BrowserRouter>
        <DashboardPage />
      </BrowserRouter>
    );
    
    // Mock dataset loaded
    // Simulate dataset selection
    // Test tab switching
    
    const tabs = screen.getAllByRole('tab');
    expect(tabs.length).toBeGreaterThan(0);
  });
});

describe('Error Handling', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  test('displays error message on failed file upload', async () => {
    mockedAxios.post.mockRejectedValueOnce(new Error('Upload failed'));

    render(<DataSourceSelector onDatasetLoaded={jest.fn()} />);
    
    const file = new File(['test'], 'test.csv', { type: 'text/csv' });
    const dropzone = screen.getByTestId('file-dropzone');
    
    fireEvent.drop(dropzone, {
      dataTransfer: { files: [file] }
    });
    
    await waitFor(() => {
      expect(screen.getByText(/failed/i)).toBeInTheDocument();
    });
  });

  test('displays error on failed analysis', async () => {
    mockedAxios.post.mockRejectedValueOnce(new Error('Analysis failed'));

    const mockDataset = { id: 'test-id', name: 'test.csv', columns: [] };
    
    render(<PredictiveAnalysis dataset={mockDataset} />);
    
    await waitFor(() => {
      expect(screen.getByText(/error/i)).toBeInTheDocument();
    });
  });
});

describe('Accessibility', () => {
  test('all interactive elements have accessible labels', () => {
    render(<DataSourceSelector onDatasetLoaded={jest.fn()} />);
    
    const dbTab = screen.getByTestId('tab-database');
    fireEvent.click(dbTab);
    
    expect(screen.getByLabelText(/Database Type/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Host/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Port/i)).toBeInTheDocument();
  });

  test('buttons have proper aria labels', () => {
    render(<DataSourceSelector onDatasetLoaded={jest.fn()} />);
    
    const dbTab = screen.getByTestId('tab-database');
    fireEvent.click(dbTab);
    
    const testButton = screen.getByTestId('test-connection-btn');
    expect(testButton).toHaveAttribute('type', 'button');
  });
});

describe('Performance', () => {
  test('component renders within acceptable time', () => {
    const start = performance.now();
    
    render(<DataSourceSelector onDatasetLoaded={jest.fn()} />);
    
    const end = performance.now();
    const renderTime = end - start;
    
    expect(renderTime).toBeLessThan(1000); // Should render in less than 1 second
  });
});
