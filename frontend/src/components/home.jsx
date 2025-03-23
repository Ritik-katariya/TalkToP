import React, { useState } from 'react';
import icon from '../image/icon.png';
import logo from '../image/logo.png';
import { uploadPDF } from '../api/api'; // Import actual API functions
import { askQuestion } from '../api/api';
import axios from "axios";
import MessageList from './Messagelist';


const PDFUploadInterface = () => {
  const [documentId, setDocumentId] = useState(null);
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [pdfName, setPdfName] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  

  const handleFileUpload = async (event) => {
    const file = event.target.files[0]; // Get the first file
    if (!file) return;

    const formData = new FormData();
    formData.append("file", file); // Append the actual file object
  const url=process.env.REACT_APP_BackendURL
    try {
      setIsLoading(true);
      const response = await axios.post(`${url}/upload`, formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });
      
      // Update state with the response
      setDocumentId(response.data.document.document_id);
      setPdfName(file.name);
      
      // Add a system message
      setMessages(prev => [...prev, {
        id: Date.now(),
        sender: 'system',
        text: `PDF "${file.name}" uploaded successfully!`
      }]);
      
      return response.data;
    } catch (error) {
      console.error("Upload failed:", error);
      setMessages(prev => [...prev, {
        id: Date.now(),
        sender: 'system',
        text: 'Failed to upload PDF. Please try again.'
      }]);
      return null;
    } finally {
      setIsLoading(false);
    }
  };
  

  const handleSendMessage = async (e) => {
    e.preventDefault();
    if (!inputMessage.trim() || !documentId) return;

    const userMessage = {
      id: Date.now(),
      sender: 'user',
      text: inputMessage,
      avatar: 'R'
    };
    setMessages((prev) => [...prev, userMessage]);
    setInputMessage('');
    setIsLoading(true);

    try {
      const response = await askQuestion(documentId, inputMessage); 
      console.log(response?.data.answer?.output_text)// Call actual askQuestion function
      setMessages((prev) => [
        ...prev,
        {
          id: Date.now() + 1,
          sender: 'ai',
          text: response?.data.answer?.output_text
        }
      ]);
    } catch (error) {
      console.error('Question error:', error);
      setMessages((prev) => [
        ...prev,
        {
          id: Date.now() + 1,
          sender: 'system',
          text: 'Error getting response. Please try again.'
        }
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-white">
      {/* Header */}
      <header className="border-b border-gray-200 py-4 px-4 bg-white flex justify-between items-center sticky top-0 z-[100]">
        <div className="flex items-center space-x-2">
          <img src={icon} alt="AI Planet Logo" className="h-8" />
        </div>
        <div className="flex items-center space-x-4">
          {pdfName && (
            <div className="flex items-center text-green-500">
              <span className="mr-2">{pdfName}</span>
              <svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
                <polyline points="14 2 14 8 20 8"></polyline>
                <line x1="16" y1="13" x2="8" y2="13"></line>
                <line x1="16" y1="17" x2="8" y2="17"></line>
                <polyline points="10 9 9 9 8 9"></polyline>
              </svg>
            </div>
          )}
          <div className="relative">
            <input
              type="file"
              onChange={handleFileUpload}
              className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
              accept=".pdf"
              disabled={isLoading}
            />
            <button className={`bg-white border border-gray-300 rounded-lg px-4 py-2 flex items-center space-x-2 ${isLoading ? 'opacity-50' : ''}`}>
              <svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
                <polyline points="17 8 12 3 7 8"></polyline>
                <line x1="12" y1="3" x2="12" y2="15"></line>
              </svg>
              <span>{isLoading ? 'Uploading...' : 'Upload PDF'}</span>
            </button>
          </div>
        </div>
      </header>

    <div className='h-full overflow-auto mb-[200px] z-10'>
        {/* Chat Container */}
        <MessageList messages={messages}/>

      {/* Message Input */}
      <div className="fixed bottom-0 left-0 right-0 bg-white border-t border-gray-200 p-4">
        <div className="max-w-4xl mx-auto">
          <form onSubmit={handleSendMessage} className="flex items-center bg-white border border-gray-200 rounded-lg px-4 py-2">
            <input
              type="text"
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              placeholder={documentId ? "Ask a question..." : "Please upload a PDF first"}
              className="flex-1 outline-none"
              disabled={!documentId || isLoading}
            />
            <button
              type="submit"
              disabled={!documentId || !inputMessage.trim() || isLoading}
              className="disabled:opacity-50"
            >
              <svg
                className="w-5 h-5 text-gray-400 cursor-pointer"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
              >
                <line x1="22" y1="2" x2="11" y2="13"></line>
                <polygon points="22 2 15 22 11 13 2 9 22 2"></polygon>
              </svg>
            </button>
          </form>
        </div>
      </div>
    </div>
    </div>
  );
};

export default PDFUploadInterface;
