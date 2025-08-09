import React, { useState } from "react";
import "./App.css";
import axios from "axios";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

function App() {
  const [personalData, setPersonalData] = useState("");
  const [selectedFile, setSelectedFile] = useState(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [processedFileUrl, setProcessedFileUrl] = useState(null);
  const [sessionId, setSessionId] = useState(null);
  const [emailRecipient, setEmailRecipient] = useState("");
  const [emailSubject, setEmailSubject] = useState("Completed Form");
  const [emailMessage, setEmailMessage] = useState("Please find the completed form attached.");
  const [showEmailForm, setShowEmailForm] = useState(false);

  // Default personal data template
  const defaultData = `Last Name: ALSQOUR
First Name: NAEL OMAR MOHAMMAD
Middle Name: [Leave Blank]
Other Names Used: [Leave Blank]
Current Address: 3100 Van Buren Blvd Apt 611, Riverside, CA 92503
Home Phone: [Leave Blank]
Mobile Phone: +1 (832) 757-3013
Email: [Leave Blank]
Driver's License #: W9493684
How did you hear about us?: Friend referral
Worked at company before?: No
Relatives working here?: No
Proof of right to work in U.S.: Yes
Are you 18 or older?: Yes
Terminated before?: No
Can work any shift?: Yes
Can work overtime/weekends?: Yes
Position Applying For: Driver
Salary Desired: $20/hour
Special Skills/Training: College educated in Jordan; fluent in Arabic & English; proficient in Word; experienced with Uber, Lyft, DoorDash, student transportation apps
College: University in Jordan
Field of Study: Business/General
Degree: Bachelor's
Year Received: 2008
Other Skills: Transportation apps, navigation, rideshare & delivery platforms
Languages Speak: Arabic, English
Languages Read: Arabic, English
Languages Write: Arabic, English
License Type: Driver License
License Number: W9493684
State: CA
Expiration: 11/20/2028
CPR/BLS Certified: No
Employer #1: Upland Furniture LLC, 735 S Cactus Ave, Upland, CA 91786 — From 09/01/2024 to 09/30/2024 — Full-Time — May Contact: Yes — Supervisor: N/A — Position: Delivery Driver — Reason: Left for higher pay in apps
Employer #2: Self-Employed – Uber, Lyft, DoorDash, Student Transportation — From 10/2024 to Present — Full-Time — Position: Passenger transport, rideshare, deliveries — Reason: Current`;

  const handleFileChange = (event) => {
    const file = event.target.files[0];
    if (file && file.type === "application/pdf") {
      setSelectedFile(file);
    } else {
      alert("Please select a PDF file");
    }
  };

  const handleLoadDefaultData = () => {
    setPersonalData(defaultData);
  };

  const handleFillForm = async () => {
    if (!selectedFile) {
      alert("Please select a PDF file first");
      return;
    }
    
    if (!personalData.trim()) {
      alert("Please enter personal data");
      return;
    }

    setIsProcessing(true);
    try {
      const formData = new FormData();
      formData.append("file", selectedFile);
      formData.append("data", personalData);

      console.log("Submitting form to:", `${API}/fill-form`);

      const response = await axios.post(`${API}/fill-form`, formData, {
        headers: {
          "Content-Type": "multipart/form-data",
        },
        responseType: "blob",
      });

      console.log("Response received:", response);

      // Create download URL
      const blob = new Blob([response.data], { type: "application/pdf" });
      const downloadUrl = window.URL.createObjectURL(blob);
      setProcessedFileUrl(downloadUrl);

      // Get session ID from headers
      const sessionId = response.headers['x-session-id'];
      if (sessionId) {
        setSessionId(sessionId);
      }

      // Get filename from response headers or create default
      const contentDisposition = response.headers['content-disposition'];
      let filename = `filled_form_${new Date().toISOString().slice(0, 10)}.pdf`;
      
      if (contentDisposition) {
        const matches = contentDisposition.match(/filename="?([^"]*)"?/);
        if (matches && matches[1]) {
          filename = matches[1];
        }
      }

      console.log("Starting download with filename:", filename);

      // Force download with better browser compatibility
      const link = document.createElement("a");
      link.href = downloadUrl;
      link.download = filename;
      link.style.display = 'none';
      
      // Add to DOM, click, and remove
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);

      console.log("Download initiated successfully");

      // Clean up URL after a delay
      setTimeout(() => {
        window.URL.revokeObjectURL(downloadUrl);
      }, 5000);

    } catch (error) {
      console.error("Error filling form:", error);
      alert("Error filling form: " + (error.response?.data?.detail || error.message));
    } finally {
      setIsProcessing(false);
    }
  };

  const handleSendEmail = async () => {
    if (!emailRecipient || !sessionId) {
      alert("Please fill the form first and enter recipient email");
      return;
    }

    try {
      const response = await axios.post(`${API}/send-email`, {
        recipient_email: emailRecipient,
        subject: emailSubject,
        message: emailMessage,
        session_id: sessionId,
      });

      alert("Email sent successfully!");
      setShowEmailForm(false);
      setEmailRecipient("");
    } catch (error) {
      console.error("Error sending email:", error);
      if (error.response?.data?.detail?.includes("Email configuration not set")) {
        alert("⚠️ Email functionality requires setup:\n\n1. Add your Gmail credentials to backend/.env:\n   SENDER_EMAIL=\"your-email@gmail.com\"\n   SENDER_PASSWORD=\"your-app-password\"\n\n2. Restart the backend service\n\nFor now, please download the form and send it manually.");
      } else {
        alert("Error sending email: " + (error.response?.data?.detail || error.message));
      }
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 py-8 px-4">
      <div className="max-w-4xl mx-auto">
        <div className="bg-white rounded-lg shadow-lg p-8">
          <h1 className="text-3xl font-bold text-gray-800 mb-2">
            PDF Form Automation System
          </h1>
          <p className="text-gray-600 mb-8">
            Fill any PDF form automatically with your personal data
          </p>

          {/* File Upload Section */}
          <div className="mb-8">
            <h2 className="text-xl font-semibold mb-4">1. Select PDF Form</h2>
            <div className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center hover:border-blue-400 transition-colors">
              <input
                type="file"
                accept=".pdf"
                onChange={handleFileChange}
                className="hidden"
                id="pdf-upload"
              />
              <label htmlFor="pdf-upload" className="cursor-pointer">
                <div className="text-gray-600">
                  <svg className="mx-auto h-12 w-12 text-gray-400 mb-4" stroke="currentColor" fill="none" viewBox="0 0 48 48">
                    <path d="M28 8H12a4 4 0 00-4 4v20m32-12v8m0 0v8a4 4 0 01-4 4H12a4 4 0 01-4-4v-4m32-4l-3.172-3.172a4 4 0 00-5.656 0L28 28M8 32l9.172-9.172a4 4 0 015.656 0L28 28m0 0l4 4m4-24h8m-4-4v8m-12 4h.02" strokeWidth={2} strokeLinecap="round" strokeLinejoin="round" />
                  </svg>
                  <p className="text-lg">Click to upload PDF form</p>
                  <p className="text-sm text-gray-500 mt-2">Or drag and drop your PDF file here</p>
                </div>
              </label>
              {selectedFile && (
                <p className="mt-4 text-green-600 font-medium">
                  ✓ Selected: {selectedFile.name}
                </p>
              )}
            </div>
          </div>

          {/* Personal Data Section */}
          <div className="mb-8">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-xl font-semibold">2. Enter Personal Data</h2>
              <button
                onClick={handleLoadDefaultData}
                className="bg-blue-100 text-blue-700 px-4 py-2 rounded-md hover:bg-blue-200 transition-colors"
              >
                Load Default Data
              </button>
            </div>
            <textarea
              value={personalData}
              onChange={(e) => setPersonalData(e.target.value)}
              className="w-full h-64 p-4 border border-gray-300 rounded-lg resize-y focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="Paste your personal data here in the format:
Last Name: YOUR_LAST_NAME
First Name: YOUR_FIRST_NAME
Current Address: YOUR_ADDRESS
..."
            />
            <p className="text-sm text-gray-500 mt-2">
              Tip: Use the format "Field Name: Value" on each line. Click "Load Default Data" to see an example.
            </p>
          </div>

          {/* Process Button */}
          <div className="mb-8">
            <button
              onClick={handleFillForm}
              disabled={isProcessing || !selectedFile || !personalData.trim()}
              className={`w-full py-4 px-6 rounded-lg font-semibold text-lg transition-all ${
                isProcessing || !selectedFile || !personalData.trim()
                  ? "bg-gray-300 text-gray-500 cursor-not-allowed"
                  : "bg-blue-600 text-white hover:bg-blue-700 transform hover:scale-105"
              }`}
            >
              {isProcessing ? (
                <div className="flex items-center justify-center">
                  <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  Processing Form...
                </div>
              ) : (
                "Fill Form & Download"
              )}
            </button>
          </div>

          {/* Success Message & Email Options */}
          {processedFileUrl && (
            <div className="bg-green-50 border border-green-200 rounded-lg p-6">
              <div className="flex items-center mb-4">
                <svg className="h-6 w-6 text-green-600 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                </svg>
                <h3 className="text-lg font-semibold text-green-800">Form Filled Successfully!</h3>
              </div>
              
              <p className="text-green-700 mb-4">
                Your form has been filled and should have downloaded automatically. Check your Downloads folder for the PDF file.
              </p>

              <div className="flex gap-4">
                <a
                  href={processedFileUrl}
                  download={`filled_form_${new Date().toISOString().slice(0, 10)}.pdf`}
                  className="bg-green-600 text-white px-6 py-2 rounded-md hover:bg-green-700 transition-colors"
                >
                  Download Again
                </a>
                
                <button
                  onClick={() => setShowEmailForm(!showEmailForm)}
                  className="bg-blue-600 text-white px-6 py-2 rounded-md hover:bg-blue-700 transition-colors"
                >
                  Send via Email
                </button>
              </div>

              {/* Email Form */}
              {showEmailForm && (
                <div className="mt-6 p-4 bg-white rounded-md border border-gray-200">
                  <h4 className="font-semibold mb-3">Send via Email</h4>
                  <div className="grid grid-cols-1 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Recipient Email *
                      </label>
                      <input
                        type="email"
                        value={emailRecipient}
                        onChange={(e) => setEmailRecipient(e.target.value)}
                        className="w-full p-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                        placeholder="recipient@example.com"
                        required
                      />
                    </div>
                    
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Subject
                      </label>
                      <input
                        type="text"
                        value={emailSubject}
                        onChange={(e) => setEmailSubject(e.target.value)}
                        className="w-full p-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      />
                    </div>
                    
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Message
                      </label>
                      <textarea
                        value={emailMessage}
                        onChange={(e) => setEmailMessage(e.target.value)}
                        rows={3}
                        className="w-full p-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      />
                    </div>
                    
                    <div className="flex gap-2">
                      <button
                        onClick={handleSendEmail}
                        className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 transition-colors"
                      >
                        Send Email
                      </button>
                      <button
                        onClick={() => setShowEmailForm(false)}
                        className="bg-gray-300 text-gray-700 px-4 py-2 rounded-md hover:bg-gray-400 transition-colors"
                      >
                        Cancel
                      </button>
                    </div>
                  </div>
                </div>
              )}
            </div>
          )}

          {/* Instructions */}
          <div className="mt-8 p-6 bg-blue-50 rounded-lg">
            <h3 className="text-lg font-semibold text-blue-800 mb-3">How to Use:</h3>
            <ol className="list-decimal list-inside space-y-2 text-blue-700">
              <li>Upload any PDF form (job applications, legal forms, etc.)</li>
              <li>Enter your personal data or click "Load Default Data" for the example</li>
              <li>Click "Fill Form & Download" to process</li>
              <li>The filled form will download automatically to your Downloads folder</li>
              <li>Optionally send the form via email to others</li>
            </ol>
            
            <div className="mt-4 p-3 bg-yellow-100 rounded border-l-4 border-yellow-500">
              <p className="text-yellow-700 font-medium">
                📁 Files download to your browser's Downloads folder (usually C:\Users\YourName\Downloads)
              </p>
              <p className="text-yellow-600 text-sm mt-1">
                To save to D:\Completed Docs, change your browser's download location in settings
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;