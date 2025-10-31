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
            responsive: true
          },
          { 
            ...config,
            responsive: true,
            displayModeBar: false 
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

  return <div ref={chartRef} style={{ width: '100%', height: '400px' }} />;
};

export default PlotlyChart;
