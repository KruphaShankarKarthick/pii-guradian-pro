import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import NavigationHeader from './components/NavigationHeader';
import HeroSection from './components/HeroSection';
import DragDropUpload from './components/DragDropUpload';
import EncryptButton from './components/EncryptButton';
import DecryptButton from './components/DecryptButton';
import './App.css';

function App() {
  return (
    <Router>
      <div className="App">
        <NavigationHeader />
        <Routes>
          <Route path="/" element={<HomePage />} />
        </Routes>
      </div>
    </Router>
  );
}

function HomePage() {
  return (
    <>
      <HeroSection />
      <div className="upload-section">
        <DragDropUpload />
        <div className="action-buttons">
          <EncryptButton />
          <DecryptButton />
        </div>
      </div>
    </>
  );
}

export default App;