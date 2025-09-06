import React from 'react';
import { Shield, Zap, Play, CheckCircle } from 'lucide-react';

export default function HeroSection() {
  return (
    <section className="bg-gradient-to-br from-blue-600 via-blue-700 to-blue-300 text-white py-20">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="grid md:grid-cols-2 gap-12 items-center">
          <div>
            <div className="inline-flex items-center px-3 py-1 rounded-full text-sm bg-white/20 text-white mb-6">
              <Shield className="w-4 h-4 mr-2" />
              Enterprise-Grade PII Protection
            </div>
            <h1 className="text-5xl font-bold leading-tight mb-6">
              Secure Your<br />
              Sensitive Data
            </h1>
            <p className="text-xl text-blue-100 mb-8 leading-relaxed">
              AI-powered platform that automatically detects, redacts, and pseudonymizes PII from any document. HIPAA/GDPR compliant with advanced OCR and NLP capabilities.
            </p>
            <div className="flex flex-col sm:flex-row gap-4">
              <button className="bg-white text-blue-600 px-8 py-3 font-semibold hover:bg-gray-50 transition-colors rounded-lg flex items-center justify-center">
                <Zap className="w-5 h-5 mr-2" />
                Start Free Trial
              </button>
              <button className="border-2 border-white text-white px-8 py-3 font-semibold hover:bg-white/10 transition-colors rounded-lg flex items-center justify-center">
                <Play className="w-5 h-5 mr-2" />
                View Demo
              </button>
            </div>
            <div className="mt-8 flex items-center space-x-6 text-sm">
              <div className="flex items-center">
                <CheckCircle className="w-5 h-5 mr-2 text-green-400" />
                HIPAA Compliant
              </div>
              <div className="flex items-center">
                <CheckCircle className="w-5 h-5 mr-2 text-green-400" />
                GDPR Ready
              </div>
              <div className="flex items-center">
                <CheckCircle className="w-5 h-5 mr-2 text-green-400" />
                SOC 2 Certified
              </div>
            </div>
          </div>
          <div className="relative">
            <div className="bg-white/10 backdrop-blur-lg rounded-2xl p-8 border border-white/20">
              <div className="text-center">
                <div className="w-32 h-32 mx-auto mb-6 bg-gradient-to-br from-blue-400 to-blue-600 rounded-full flex items-center justify-center">
                  <Shield className="w-16 h-16 text-white" />
                </div>
                <div className="space-y-2 text-sm">
                  <div className="flex items-center justify-between bg-white/20 rounded-lg p-3">
                    <span>Document Analysis</span>
                    <span className="text-green-400">✓ Complete</span>
                  </div>
                  <div className="flex items-center justify-between bg-white/20 rounded-lg p-3">
                    <span>PII Detection</span>
                    <span className="text-green-400">✓ Complete</span>
                  </div>
                  <div className="flex items-center justify-between bg-white/20 rounded-lg p-3">
                    <span>AES Encryption</span>
                    <span className="text-blue-400">⟳ Processing</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}