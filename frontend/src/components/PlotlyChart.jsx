import { useEffect, useRef } from 'react';

const PlotlyChart = ({ data, layout, config }) => {
  const chartRef = useRef(null);
  const plotlyRef = useRef(null);

  useEffect(() => {
    const loadPlotly = async () => {
      if (!window.Plotly) {
        const script = document.createElement('script');
        script.src = 'https://cdn.plot.ly/plotly-2.27.0.min.js';
        script.async = true;
        document.head.appendChild(script);
        
        await new Promise((resolve) => {
          script.onload = resolve;
        });
      }

      if (chartRef.current && window.Plotly) {
        window.Plotly.newPlot(
          chartRef.current,
          data,
          {
            ...layout,
            autosize: true,
            responsive: true,
            margin: { l: 60, r: 40, t: 60, b: 60 }  // Better margins for axis labels
          },
          { 
            ...config,
            responsive: true,
            displayModeBar: true,
            displaylogo: false,
            modeBarButtonsToRemove: ['lasso2d', 'select2d']
          }
        );
        
        plotlyRef.current = chartRef.current;
      }
    };

    loadPlotly();

    return () => {
      if (plotlyRef.current && window.Plotly) {
        window.Plotly.purge(plotlyRef.current);
      }
    };
  }, [data, layout, config]);

  return (
    <div 
      ref={chartRef} 
      className="w-full overflow-hidden" 
      style={{ 
        minHeight: '400px', 
        maxHeight: '450px',
        maxWidth: '100%'
      }} 
    />
  );
};

export default PlotlyChart;
