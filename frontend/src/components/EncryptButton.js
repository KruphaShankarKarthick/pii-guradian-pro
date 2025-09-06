import React, { useState } from 'react';
import { Lock, AlertCircle } from 'lucide-react';

export default function EncryptButton() {
  const [showModal, setShowModal] = useState(false);
  const [passkey, setPasskey] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handleEncrypt = async () => {
    if (passkey.length < 8) {
      alert('Passkey must be at least 8 characters');
      return;
    }

    setIsLoading(true);
    try {
      const formData = new FormData();
      formData.append('documentId', localStorage.getItem('currentDocumentId'));
      formData.append('passkey', passkey);

      const response = await fetch('/api/encrypt', {
        method: 'POST',
        body: formData,
      });

      if (response.ok) {
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'encrypted_document.pdf';
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
        
        setShowModal(false);
        setPasskey('');
        alert('Document encrypted and downloaded successfully!');
      }
    } catch (error) {
      console.error('Encryption error:', error);
      alert('Failed to encrypt document');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <>
      <button
        className="bg-blue-600 text-white px-8 py-3 font-semibold hover:bg-blue-700 transition-colors rounded-lg flex items-center"
        onClick={() => setShowModal(true)}
      >
        <Lock className="w-5 h-5 mr-2" />
        Encrypt PDF
      </button>

      {showModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-md w-full mx-4">
            <h3 className="text-lg font-semibold mb-4">Set Encryption Passkey</h3>
            <div className="space-y-4">
              <div>
                <input
                  type="password"
                  placeholder="Enter a strong passkey (min 8 characters)"
                  value={passkey}
                  onChange={(e) => setPasskey(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
                {passkey.length > 0 && passkey.length < 8 && (
                  <p className="text-sm text-red-600 mt-1 flex items-center">
                    <AlertCircle className="w-4 h-4 mr-1" />
                    Passkey must be at least 8 characters
                  </p>
                )}
              </div>
              <div className="flex gap-4">
                <button
                  className="flex-1 bg-blue-600 text-white py-2 rounded-lg hover:bg-blue-700 disabled:opacity-50"
                  onClick={handleEncrypt}
                  disabled={passkey.length < 8 || isLoading}
                >
                  {isLoading ? 'Encrypting...' : 'Encrypt'}
                </button>
                <button
                  className="flex-1 border border-gray-300 text-gray-700 py-2 rounded-lg hover:bg-gray-50"
                  onClick={() => setShowModal(false)}
                >
                  Cancel
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </>
  );
}