import React from 'react';
import { Shield } from 'lucide-react';

export default function NavigationHeader() {
  return (
    <header className="bg-white shadow-sm border-b">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-blue-600 rounded-lg flex items-center justify-center">
              <Shield className="w-6 h-6 text-white" />
            </div>
            <div>
              <h1 className="text-xl font-bold text-gray-900">PII Guardian Pro</h1>
              <p className="text-sm text-gray-500">AI-Powered Data Protection</p>
            </div>
          </div>
          <nav className="hidden md:flex space-x-8">
            <a href="#features" className="text-gray-500 hover:text-gray-900 font-medium">Features</a>
            <a href="#security" className="text-gray-500 hover:text-gray-900 font-medium">Security</a>
            <a href="#pricing" className="text-gray-500 hover:text-gray-900 font-medium">Pricing</a>
            <a href="#docs" className="text-gray-500 hover:text-gray-900 font-medium">Documentation</a>
            <a href="#contact" className="text-gray-500 hover:text-gray-900 font-medium">Contact</a>
          </nav>
          <div className="flex items-center space-x-4">
            <button className="text-gray-500 hover:text-gray-900 font-medium">
              Sign In
            </button>
            <button className="bg-blue-600 text-white px-4 py-2 font-medium hover:bg-blue-700 rounded-lg">
              Start Free Trial
            </button>
          </div>
        </div>
      </div>
    </header>
  );
}