import { useState, useEffect } from 'react';
import { toast } from 'sonner';
import { Database, RefreshCw } from 'lucide-react';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const CompactDatabaseToggle = () => {
  const [currentDb, setCurrentDb] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadCurrentDatabase();
  }, []);

  const loadCurrentDatabase = async () => {
    try {
      const response = await axios.get(`${API}/config/current-database`);
      setCurrentDb(response.data.current_database);
    } catch (error) {
      console.error('Failed to load database status:', error);
      // Retry once
      setTimeout(async () => {
        try {
          const response = await axios.get(`${API}/config/current-database`);
          setCurrentDb(response.data.current_database);
        } catch (err) {
          setCurrentDb('oracle'); // Default to oracle per user requirement
        }
      }, 2000);
    }
  };

  const switchDatabase = async (dbType) => {
    if (dbType === currentDb) {
      return;
    }

    if (!confirm(`Switch to ${dbType.toUpperCase()}?\n\nBackend will restart (~15 seconds).`)) {
      return;
    }

    setLoading(true);
    try {
      toast.info(`Switching to ${dbType.toUpperCase()}...`);
      
      try {
        await axios.post(`${API}/config/switch-database`, {
          db_type: dbType
        }, { timeout: 3000 });
      } catch (error) {
        // Expected during restart
        if (error.code === 'ECONNABORTED' || error.response?.status === 502) {
          console.log('Backend restarting (expected)');
        }
      }

      toast.success('Database switched!');
      await new Promise(resolve => setTimeout(resolve, 15000));
      await loadCurrentDatabase();
    } catch (error) {
      toast.error('Switch failed: ' + error.message);
    } finally {
      setLoading(false);
    }
  };

  if (!currentDb) {
    return (
      <div className="flex items-center gap-2 px-3 py-1.5 bg-gray-100 rounded-lg text-xs">
        <RefreshCw className="w-3 h-3 animate-spin" />
        <span className="text-gray-600">Loading...</span>
      </div>
    );
  }

  return (
    <div className="flex items-center gap-2 bg-white border rounded-lg shadow-sm">
      {/* MongoDB Button */}
      <button
        onClick={() => switchDatabase('mongodb')}
        disabled={loading}
        className={`flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium rounded-l-lg transition-all ${
          currentDb === 'mongodb'
            ? 'bg-green-500 text-white'
            : 'bg-gray-50 text-gray-600 hover:bg-gray-100'
        } ${loading ? 'opacity-50 cursor-not-allowed' : ''}`}
      >
        <Database className="w-3 h-3" />
        <span>MongoDB</span>
        {currentDb === 'mongodb' && <span className="text-xs">●</span>}
      </button>

      {/* Divider */}
      <div className="h-6 w-px bg-gray-200"></div>

      {/* Oracle Button */}
      <button
        onClick={() => switchDatabase('oracle')}
        disabled={loading}
        className={`flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium rounded-r-lg transition-all ${
          currentDb === 'oracle'
            ? 'bg-red-500 text-white'
            : 'bg-gray-50 text-gray-600 hover:bg-gray-100'
        } ${loading ? 'opacity-50 cursor-not-allowed' : ''}`}
      >
        <Database className="w-3 h-3" />
        <span>Oracle</span>
        {currentDb === 'oracle' && <span className="text-xs">●</span>}
      </button>
    </div>
  );
};

export default CompactDatabaseToggle;
