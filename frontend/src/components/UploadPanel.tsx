"use client";

import { useState } from 'react';

export default function UploadPanel() {
  const [file, setFile] = useState<File | null>(null);
  const [status, setStatus] = useState<string>('');
  const [loading, setLoading] = useState<boolean>(false);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      setFile(e.target.files[0]);
    }
  };

  const handleUpload = async () => {
    if (!file) {
      setStatus("Please select a file first.");
      return;
    }

    setLoading(true);
    setStatus("Uploading and processing...");
    
    const formData = new FormData();
    formData.append("file", file);

    try {
      // Need a hardcoded localhost:8000 since it's the FastAPI backend
      const response = await fetch("http://localhost:8000/api/v1/documents/upload", {
        method: "POST",
        body: formData,
      });

      if (response.ok) {
        const docData = await response.json();
        setStatus("Upload successful! Processing document...");
        setFile(null);
        // Reset file input
        const fileInput = document.getElementById('file-upload') as HTMLInputElement;
        if (fileInput) fileInput.value = '';

        // Poll for status
        const pollInterval = setInterval(async () => {
          try {
            const docsRes = await fetch("http://localhost:8000/api/v1/documents/");
            if (docsRes.ok) {
              const docs = await docsRes.json();
              const myDoc = docs.find((d: any) => d.id === docData.id);
              if (myDoc) {
                if (myDoc.status?.toLowerCase() === 'completed') {
                  setStatus("Processing completed! Document is ready.");
                  clearInterval(pollInterval);
                  setLoading(false);
                } else if (myDoc.status?.toLowerCase() === 'failed') {
                  setStatus("Processing failed! Please try again.");
                  clearInterval(pollInterval);
                  setLoading(false);
                }
              }
            }
          } catch (e) {
            console.error("Failed to poll status", e);
          }
        }, 2000);
        
        // We do not set loading to false here because we are polling
        return;
      } else {
        const errorData = await response.json();
        setStatus(`Upload failed: ${errorData.detail || 'Unknown error'}`);
      }
    } catch (error) {
      setStatus("Failed to connect to the server.");
      console.error(error);
    } 
    
    setLoading(false);
  };

  return (
    <div className="glass-panel p-8 w-full max-w-md animate-fade-in flex flex-col gap-6">
      <div className="text-center">
        <h2 className="text-2xl font-bold mb-2 tracking-tight" style={{ color: 'var(--neon-blue)' }}>Knowledge Base</h2>
        <p className="text-sm text-gray-400">Ingest PDFs, TXTs, and Word Documents.</p>
      </div>
      
      <div className="flex flex-col gap-4">
        <div className="relative border-2 border-dashed border-gray-600 rounded-xl p-8 text-center hover:border-blue-400 transition-colors">
          <input 
            type="file" 
            id="file-upload" 
            className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
            accept=".pdf,.txt,.docx"
            onChange={handleFileChange}
          />
          <div className="text-gray-300">
            {file ? (
              <span className="font-semibold text-blue-300">{file.name}</span>
            ) : (
              <span>Drag & drop a file here or click to browse</span>
            )}
          </div>
        </div>

        <button 
          onClick={handleUpload} 
          disabled={!file || loading}
          className="glass-button w-full"
        >
          {loading ? 'Processing...' : 'Upload to Graph'}
        </button>

        {status && (
          <div className={`text-sm text-center p-3 rounded-lg ${status.includes('failed') || status.includes('Failed') || status.includes('Please') ? 'bg-red-900/30 text-red-300' : 'bg-green-900/30 text-green-300'}`}>
            {status}
          </div>
        )}
      </div>
    </div>
  );
}
