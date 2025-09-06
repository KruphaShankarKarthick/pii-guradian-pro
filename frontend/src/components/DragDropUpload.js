import React, { useState, useCallback } from 'react';
import { Upload, AlertCircle } from 'lucide-react';

export default function DragDropUpload() {
  const [dragOver, setDragOver] = useState(false);
  const [selectedFile, setSelectedFile] = useState(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [detectedPII, setDetectedPII] = useState([]);

  const handleDragOver = useCallback((e) => {
    e.preventDefault();
    setDragOver(true);
  }, []);

  const handleDragLeave = useCallback((e) => {
    e.preventDefault();
    setDragOver(false);
  }, []);

  const handleDrop = useCallback((e) => {
    e.preventDefault();
    setDragOver(false);
    const files = Array.from(e.dataTransfer.files);
    const file = files[0];
    if (file && file.type === "application/pdf") {
      setSelectedFile(file);
      uploadFile(file);
    } else {
      alert("Please upload a PDF file.");
    }
  }, []);

  const handleFileSelect = useCallback((e) => {
    const file = e.target.files?.[0];
    if (file) {
      setSelectedFile(file);
      uploadFile(file);
    }
  }, []);

  const uploadFile = async (file) => {
    setIsProcessing(true);
    const formData = new FormData();
    formData.append("document", file);

    try {
      const response = await fetch("/api/upload", {
        method: "POST",
        body: formData,
      });
      const data = await response.json();
      
      if (response.ok) {
        // Analyze document for PII
        const analyzeResponse = await fetch(`/api/analyze/${data.document.id}`, {
          method: "POST",
        });
        const analyzeData = await analyzeResponse.json();
        
        if (analyzeResponse.ok) {
          setDetectedPII(analyzeData.detectedPII || []);
        }
      }
    } catch (error) {
      console.error("Upload error:", error);
    } finally {
      setIsProcessing(false);
    }
  };

  return (
    <section className="upload-section bg-yellow-400 py-16">
      <div className="max-w-4xl mx-auto px-4">
        <div className="text-center mb-12">
          <h2 className="text-4xl font-bold text-gray-900 mb-4">
            Upload Documents for PII Analysis
          </h2>
          <p className="text-lg text-gray-700 max-w-2xl mx-auto">
            Drag and drop your PDF documents, scanned images, or photos. Our AI will automatically detect and analyze any personally identifiable information.
          </p>
        </div>

        <div className="bg-white rounded-2xl shadow-lg p-8 mb-8">
          {!isProcessing && detectedPII.length === 0 && (
            <div
              className={`upload-zone border-2 border-dashed border-gray-300 rounded-xl p-12 text-center transition-colors ${
                dragOver ? "border-blue-500 bg-blue-50" : "hover:border-blue-400 hover:bg-gray-50"
              }`}
              onDragOver={handleDragOver}
              onDragLeave={handleDragLeave}
              onDrop={handleDrop}
            >
              <div className="mb-6">
                <Upload className="w-16 h-16 mx-auto text-gray-400 mb-4" />
                <h3 className="text-xl font-semibold text-gray-900 mb-2">
                  Upload your documents
                </h3>
                <p className="text-gray-600 mb-4">
                  Supports PDF, JPG, PNG, TIFF files up to 50MB each
                </p>
              </div>
              <label htmlFor="file-upload">
                <button className="bg-yellow-400 text-black px-8 py-3 font-semibold hover:bg-yellow-500 transition-colors mb-4 rounded-lg">
                  Choose Files
                </button>
              </label>
              <input
                id="file-upload"
                type="file"
                accept=".pdf"
                onChange={handleFileSelect}
                className="hidden"
              />
              <p className="text-sm text-gray-500">or drag and drop files here</p>
            </div>
          )}

          {isProcessing && (
            <div className="text-center py-8">
              <div className="animate-spin w-8 h-8 border-4 border-blue-600 border-t-transparent rounded-full mx-auto mb-4"></div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">
                Analyzing Document...
              </h3>
              <p className="text-gray-600">
                Detecting PII using OCR and NLP analysis
              </p>
            </div>
          )}

          {detectedPII.length > 0 && (
            <div className="mt-8">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">
                Detected PII Fields
              </h3>
              <div className="grid md:grid-cols-2 gap-4 mb-6">
                {detectedPII.map((item, index) => (
                  <div key={index} className="bg-red-50 border border-red-200 rounded-lg p-4">
                    <div className="flex items-center justify-between">
                      <div>
                        <span className="font-medium text-red-800">
                          {item.type}
                        </span>
                        <p className="text-sm text-red-600">
                          {item.value}
                        </p>
                      </div>
                      <span className="text-xs bg-red-100 text-red-800 px-2 py-1 rounded">
                        {Math.round(item.confidence * 100)}% confidence
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </section>
  );
}