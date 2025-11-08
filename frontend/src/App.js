import { useState, useEffect } from "react";
import "@/App.css";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import HomePage from "@/pages/HomePage";
import DashboardPage from "@/pages/DashboardPage";
import TrainingMetadataPage from "@/pages/TrainingMetadataPage";
import DocumentationPage from "@/pages/DocumentationPage";
import { Toaster } from "@/components/ui/sonner";
import { initializeStorageManager } from "@/utils/storageManager";

function App() {
  // Initialize storage manager on app startup for large dataset support (2GB+)
  useEffect(() => {
    initializeStorageManager();
    
    // Suppress non-critical WebSocket connection errors (chat feature connectivity)
    const originalConsoleError = console.error;
    console.error = function(...args) {
      // Suppress WebSocket connection errors (non-critical)
      const errorMessage = String(args[0] || '');
      if (errorMessage.includes('WebSocket connection') || 
          errorMessage.includes('wss://') ||
          errorMessage.includes('/ws failed')) {
        // Silently ignore WebSocket errors
        return;
      }
      // Pass through all other errors
      originalConsoleError.apply(console, args);
    };
    
    return () => {
      console.error = originalConsoleError;
    };
  }, []);
  
  return (
    <div className="App">
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/dashboard" element={<DashboardPage />} />
          <Route path="/training-metadata" element={<TrainingMetadataPage />} />
          <Route path="/documentation" element={<DocumentationPage />} />
        </Routes>
      </BrowserRouter>
      <Toaster position="top-right" />
    </div>
  );
}

export default App;