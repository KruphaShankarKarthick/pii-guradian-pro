import React, { useState } from 'react';
import { Unlock } from 'lucide-react';

export default function DecryptButton() {
  const [showModal, setShowModal] = useState(false);
  const [passkey, setPasskey] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handleDecrypt = async () => {
    if (!passkey) {
      alert('Please enter your passkey');
      return;
    }

    setIsLoading(true);
    try {
      const formData = new FormData();
      formData.append('documentId', localStorage.getItem('currentDocumentId'));
      formData.append('passkey', passkey);

      const response = await fetch('/api/decrypt', {
        method: 'POST',
        body: formData,
      });

      if (response.ok) {
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'decrypted_document.pdf';
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
        
        setShowModal(false);
        setPasskey('');
        alert('Document decrypted and downloaded successfully!');
      } else if (response.status === 401) {
        alert('Invalid passkey provided');
      }
    } catch (error) {
      console.error('Decryption error:', error);
      alert('Failed to decrypt document');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <>
      <button
        className="border-2 border-gray-300 text-gray-700 px-8 py-3 font-semibold hover:bg-gray-50 transition-colors rounded-lg flex items-center"
        onClick={() => setShowModal(true)}
      >
        <Unlock className="w-5 h-5 mr-2" />
        Decrypt PDF
      </button>

      {showModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-md w-full mx-4">
            <h3 className="text-lg font-semibold mb-4">Enter Decryption Passkey</h3>
            <div className="space-y-4">
              <input
                type="password"
                placeholder="Enter your passkey"
                value={passkey}
                onChange={(e) => setPasskey(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
              <div className="flex gap-4">
                <button
                  className="flex-1 bg-blue-600 text-white py-2 rounded-lg hover:bg-blue-700 disabled:opacity-50"
                  onClick={handleDecrypt}
                  disabled={!passkey || isLoading}
                >
                  {isLoading ? 'Decrypting...' : 'Decrypt'}
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