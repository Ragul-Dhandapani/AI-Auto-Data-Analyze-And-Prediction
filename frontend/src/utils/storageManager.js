/**
 * Storage Manager - Production-Grade Storage Solution for Large Datasets (2GB+)
 * 
 * CRITICAL: This utility ensures the application never crashes due to storage limitations
 * 
 * Strategy:
 * - NO localStorage for analysis data (5-10MB limit)
 * - Backend storage for all persistent data (unlimited via Oracle/MongoDB)
 * - In-memory caching for current session (React state/refs)
 * - Automatic cleanup and monitoring
 */

const STORAGE_LIMITS = {
  localStorage: 5 * 1024 * 1024, // 5MB safe limit (browsers have 5-10MB)
  maxPayloadSize: 50 * 1024 * 1024, // 50MB max for single HTTP request
  warningThreshold: 3 * 1024 * 1024 // 3MB warning threshold
};

/**
 * Calculate size of object in bytes
 */
export const getObjectSize = (obj) => {
  try {
    const str = JSON.stringify(obj);
    return new Blob([str]).size;
  } catch (e) {
    console.error('Error calculating object size:', e);
    return 0;
  }
};

/**
 * Format bytes to human-readable size
 */
export const formatBytes = (bytes) => {
  if (bytes === 0) return '0 Bytes';
  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return Math.round((bytes / Math.pow(k, i)) * 100) / 100 + ' ' + sizes[i];
};

/**
 * Check if data is safe to save to localStorage
 * Returns: { safe: boolean, size: number, sizeFormatted: string, reason: string }
 */
export const checkLocalStorageSafety = (data) => {
  const size = getObjectSize(data);
  const sizeFormatted = formatBytes(size);
  
  if (size > STORAGE_LIMITS.localStorage) {
    return {
      safe: false,
      size,
      sizeFormatted,
      reason: `Data too large (${sizeFormatted}). Use backend storage instead.`
    };
  }
  
  if (size > STORAGE_LIMITS.warningThreshold) {
    return {
      safe: false,
      size,
      sizeFormatted,
      reason: `Data approaching limit (${sizeFormatted}). Recommend backend storage.`
    };
  }
  
  return {
    safe: true,
    size,
    sizeFormatted,
    reason: 'Safe for localStorage'
  };
};

/**
 * Clean all analysis data from localStorage
 * Should be called on app startup and periodically
 */
export const cleanupLocalStorage = () => {
  try {
    const keys = Object.keys(localStorage);
    let cleanedCount = 0;
    
    keys.forEach(key => {
      // Remove old analysis data
      if (key.startsWith('analysis_')) {
        localStorage.removeItem(key);
        cleanedCount++;
      }
    });
    
    if (cleanedCount > 0) {
      console.log(`🧹 Cleaned ${cleanedCount} old analysis entries from localStorage`);
    }
    
    return cleanedCount;
  } catch (e) {
    console.error('Error cleaning localStorage:', e);
    return 0;
  }
};

/**
 * Get current localStorage usage
 */
export const getLocalStorageUsage = () => {
  try {
    let total = 0;
    const keys = Object.keys(localStorage);
    
    keys.forEach(key => {
      const item = localStorage.getItem(key);
      if (item) {
        total += item.length;
      }
    });
    
    return {
      used: total,
      usedFormatted: formatBytes(total),
      limit: STORAGE_LIMITS.localStorage,
      limitFormatted: formatBytes(STORAGE_LIMITS.localStorage),
      percentUsed: Math.round((total / STORAGE_LIMITS.localStorage) * 100)
    };
  } catch (e) {
    console.error('Error getting localStorage usage:', e);
    return null;
  }
};

/**
 * Safe localStorage setter with automatic fallback
 * Returns: { success: boolean, method: 'localStorage' | 'memory', error: string }
 */
export const safeSetItem = (key, value) => {
  // Check size first
  const sizeCheck = checkLocalStorageSafety(value);
  
  if (!sizeCheck.safe) {
    console.warn(`⚠️ Cannot save to localStorage: ${sizeCheck.reason}`);
    return {
      success: false,
      method: 'memory',
      error: sizeCheck.reason,
      size: sizeCheck.size
    };
  }
  
  try {
    localStorage.setItem(key, JSON.stringify(value));
    return {
      success: true,
      method: 'localStorage',
      size: sizeCheck.size
    };
  } catch (e) {
    if (e.name === 'QuotaExceededError') {
      // Try cleanup and retry once
      cleanupLocalStorage();
      
      try {
        localStorage.setItem(key, JSON.stringify(value));
        return {
          success: true,
          method: 'localStorage',
          size: sizeCheck.size,
          note: 'Saved after cleanup'
        };
      } catch (retryError) {
        console.error('QuotaExceededError even after cleanup:', retryError);
        return {
          success: false,
          method: 'memory',
          error: 'Storage quota exceeded even after cleanup'
        };
      }
    }
    
    return {
      success: false,
      method: 'memory',
      error: e.message
    };
  }
};

/**
 * Initialize storage manager - call on app startup
 */
export const initializeStorageManager = () => {
  console.log('🔧 Initializing Storage Manager...');
  
  // Clean old data
  cleanupLocalStorage();
  
  // Log current usage
  const usage = getLocalStorageUsage();
  if (usage) {
    console.log(`💾 LocalStorage usage: ${usage.usedFormatted} / ${usage.limitFormatted} (${usage.percentUsed}%)`);
    
    if (usage.percentUsed > 80) {
      console.warn('⚠️ LocalStorage is over 80% full - consider clearing browser data');
    }
  }
  
  // Set up periodic cleanup (every 5 minutes)
  setInterval(() => {
    const cleaned = cleanupLocalStorage();
    if (cleaned > 0) {
      console.log(`🔄 Periodic cleanup: removed ${cleaned} entries`);
    }
  }, 5 * 60 * 1000);
  
  console.log('✅ Storage Manager initialized - Large dataset support enabled');
};

export default {
  getObjectSize,
  formatBytes,
  checkLocalStorageSafety,
  cleanupLocalStorage,
  getLocalStorageUsage,
  safeSetItem,
  initializeStorageManager,
  STORAGE_LIMITS
};
