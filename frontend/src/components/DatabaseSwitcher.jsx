import { useState, useEffect } from 'react';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { toast } from 'sonner';
import { Database, RefreshCw, AlertCircle } from 'lucide-react';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const DatabaseSwitcher = () => {
  const [currentDb, setCurrentDb] = useState('mongodb');
  const [loading, setLoading] = useState(false);
  const [restarting, setRestarting] = useState(false);

  useEffect(() => {
    loadCurrentDatabase();
  }, []);

  const loadCurrentDatabase = async () => {
    try {
      const response = await axios.get(`${API}/config/current-database`);
      setCurrentDb(response.data.current_database);
    } catch (error) {
      console.error('Failed to load current database:', error);
    }
  };

  const switchDatabase = async (dbType) => {
    if (dbType === currentDb) {
      toast.info(`Already using ${dbType.toUpperCase()}`);
      return;
    }

    if (!confirm(`Switch to ${dbType.toUpperCase()}?\n\nThis will restart the backend (takes about 10 seconds).`)) {
      return;
    }

    setLoading(true);

    try {
      // Step 1: Switch database type (backend will auto-restart)
      toast.info('Switching database...');
      
      const switchResponse = await axios.post(`${API}/config/switch-database`, {
        db_type: dbType
      });

      toast.success(switchResponse.data.message);

      // Step 2: Wait for backend to restart
      setRestarting(true);
      toast.info('Backend is restarting... Please wait 10 seconds');

      // Wait 10 seconds for restart
      await new Promise(resolve => setTimeout(resolve, 10000));

      // Step 3: Verify new database
      let retries = 0;
      const maxRetries = 5;
      let success = false;

      while (retries < maxRetries && !success) {
        try {
          await new Promise(resolve => setTimeout(resolve, 2000));
          const verifyResponse = await axios.get(`${API}/config/current-database`);
          
          if (verifyResponse.data.current_database === dbType) {
            setCurrentDb(dbType);
            success = true;
            toast.success(`✅ Successfully switched to ${dbType.toUpperCase()}!`, {
              duration: 5000
            });
            
            // Reload page to ensure everything is fresh
            setTimeout(() => {
              window.location.reload();
            }, 1000);
          }
        } catch (error) {
          retries++;
          if (retries >= maxRetries) {
            toast.warning('Backend restarted but taking longer than expected. Please refresh the page manually.', {
              duration: 8000
            });
          }
        }
      }

    } catch (error) {
      const errorMsg = error.response?.data?.detail || error.message || 'Unknown error';
      toast.error('Failed to switch database: ' + errorMsg);
      console.error('Switch error:', error);
    } finally {
      setLoading(false);
      setRestarting(false);
    }
  };

  return (
    <Card className="p-6 bg-gradient-to-r from-blue-50 to-purple-50 border-2 border-dashed border-blue-300">
      <div className="flex items-center gap-3 mb-4">
        <Database className="w-6 h-6 text-blue-600" />
        <div>
          <h3 className="text-lg font-bold text-blue-900">
            Database Switcher (Temporary)
          </h3>
          <p className="text-sm text-blue-700">
            Switch between MongoDB and Oracle 23 in real-time
          </p>
        </div>
      </div>

      {/* Warning Notice */}
      <div className="bg-yellow-50 border border-yellow-300 rounded-lg p-3 mb-4 flex items-start gap-2">
        <AlertCircle className="w-5 h-5 text-yellow-600 flex-shrink-0 mt-0.5" />
        <div className="text-sm text-yellow-800">
          <strong>Note:</strong> This is a temporary testing feature. Switching will restart the backend (5-10 seconds downtime). 
          All existing data remains in the original database.
        </div>
      </div>

      {/* Current Database Display */}
      <div className="bg-white rounded-lg p-4 mb-4 border-2 border-blue-200">
        <div className="text-sm text-gray-600 mb-1">Currently Active Database:</div>
        <div className="text-2xl font-bold text-blue-600 uppercase flex items-center gap-2">
          <Database className="w-6 h-6" />
          {currentDb}
        </div>
      </div>

      {/* Database Selection Buttons */}
      <div className="grid grid-cols-2 gap-4">
        <Button
          onClick={() => switchDatabase('mongodb')}
          disabled={loading || restarting || currentDb === 'mongodb'}
          className={`h-20 text-lg font-semibold ${
            currentDb === 'mongodb'
              ? 'bg-green-600 hover:bg-green-700'
              : 'bg-gray-600 hover:bg-gray-700'
          }`}
        >
          {loading && currentDb !== 'mongodb' ? (
            <RefreshCw className="w-5 h-5 mr-2 animate-spin" />
          ) : (
            <Database className="w-5 h-5 mr-2" />
          )}
          MongoDB
          {currentDb === 'mongodb' && <span className="ml-2 text-xs">(Active)</span>}
        </Button>

        <Button
          onClick={() => switchDatabase('oracle')}
          disabled={loading || restarting || currentDb === 'oracle'}
          className={`h-20 text-lg font-semibold ${
            currentDb === 'oracle'
              ? 'bg-red-600 hover:bg-red-700'
              : 'bg-gray-600 hover:bg-gray-700'
          }`}
        >
          {loading && currentDb !== 'oracle' ? (
            <RefreshCw className="w-5 h-5 mr-2 animate-spin" />
          ) : (
            <Database className="w-5 h-5 mr-2" />
          )}
          Oracle 23
          {currentDb === 'oracle' && <span className="ml-2 text-xs">(Active)</span>}
        </Button>
      </div>

      {/* Status Messages */}
      {restarting && (
        <div className="mt-4 text-center text-sm text-blue-700 animate-pulse">
          🔄 Backend is restarting... Please wait 10 seconds
        </div>
      )}

      {/* Instructions */}
      <div className="mt-4 text-xs text-gray-600 bg-white rounded p-3">
        <strong>How it works:</strong>
        <ol className="list-decimal ml-4 mt-2 space-y-1">
          <li>Click a database button to switch</li>
          <li>Backend automatically restarts (5-10 sec)</li>
          <li>Page may need refresh after switch</li>
          <li>All features work identically on both databases</li>
        </ol>
      </div>
    </Card>
  );
};

export default DatabaseSwitcher;
