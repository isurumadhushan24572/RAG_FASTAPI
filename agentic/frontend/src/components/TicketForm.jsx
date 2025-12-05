import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Send, Loader2, FileText, Sparkles, Search, Database, Globe, BrainCircuit } from 'lucide-react';

const TicketForm = () => {
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    category: 'General',
    severity: 'Medium',
    application: '',
    environment: 'Production',
    affected_users: ''
  });
  const [submitting, setSubmitting] = useState(false);
  const [processingStep, setProcessingStep] = useState(0);

  const steps = [
    { icon: Search, text: "Analyzing ticket content..." },
    { icon: Database, text: "Querying Vector Knowledge Base..." },
    { icon: Globe, text: "Searching External Documentation..." },
    { icon: BrainCircuit, text: "Synthesizing AI Solution..." }
  ];

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSubmitting(true);
    setProcessingStep(0);

    // Simulate steps progress
    const interval = setInterval(() => {
      setProcessingStep(prev => {
        if (prev < steps.length - 1) return prev + 1;
        return prev;
      });
    }, 2000);
    
    try {
      const response = await axios.post('http://localhost:8000/api/v1/tickets/submit-user-input', formData);
      
      clearInterval(interval);
      setProcessingStep(steps.length - 1); // Ensure last step is shown
      
      console.log("API Response:", response.data); // Debug log
      
      // Validate response has required fields
      if (!response.data || !response.data.reasoning || !response.data.solution) {
        console.error("Invalid response structure:", response.data);
        alert("Received incomplete response from server. Please check console.");
        setSubmitting(false);
        return;
      }
      
      // Small delay to show completion
      setTimeout(() => {
        localStorage.setItem('ticketResult', JSON.stringify(response.data));
        console.log("Data saved to localStorage:", response.data);
        // Navigate to result page in the same window instead of opening new tab
        window.location.href = '/result';
      }, 1000);
      
    } catch (error) {
      console.error("Error submitting ticket:", error);
      console.error("Error details:", error.response?.data || error.message);
      clearInterval(interval);
      alert(`Failed to submit ticket: ${error.response?.data?.detail || error.message}`);
      setSubmitting(false);
    }
  };

  if (submitting) {
    return (
      <div className="bg-white rounded-2xl shadow-xl border border-slate-100 overflow-hidden min-h-[600px] flex flex-col items-center justify-center p-8 relative">
        <div className="absolute inset-0 bg-slate-50/50 backdrop-blur-sm z-0"></div>
        <div className="relative z-10 w-full max-w-md">
          <div className="text-center mb-8">
            <div className="w-20 h-20 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-4 animate-pulse">
              <Sparkles className="w-10 h-10 text-blue-600" />
            </div>
            <h3 className="text-2xl font-bold text-slate-800">Agent is working...</h3>
            <p className="text-slate-500">Please wait while I analyze your request</p>
          </div>

          <div className="space-y-6">
            {steps.map((step, index) => {
              const Icon = step.icon;
              const isActive = index === processingStep;
              const isCompleted = index < processingStep;
              const isPending = index > processingStep;

              return (
                <div 
                  key={index} 
                  className={`flex items-center p-4 rounded-xl transition-all duration-500 ${
                    isActive ? 'bg-white shadow-lg border-blue-200 border scale-105' : 
                    isCompleted ? 'bg-green-50 border-green-100 border opacity-70' : 
                    'opacity-40'
                  }`}
                >
                  <div className={`p-2 rounded-lg mr-4 ${
                    isActive ? 'bg-blue-100 text-blue-600' : 
                    isCompleted ? 'bg-green-100 text-green-600' : 
                    'bg-slate-100 text-slate-400'
                  }`}>
                    <Icon className="w-6 h-6" />
                  </div>
                  <div className="flex-1">
                    <p className={`font-medium ${
                      isActive ? 'text-blue-900' : 
                      isCompleted ? 'text-green-900' : 
                      'text-slate-500'
                    }`}>
                      {step.text}
                    </p>
                    {isActive && (
                      <div className="h-1 w-full bg-blue-100 mt-2 rounded-full overflow-hidden">
                        <div className="h-full bg-blue-500 animate-progress"></div>
                      </div>
                    )}
                  </div>
                  {isCompleted && (
                    <div className="w-6 h-6 bg-green-500 rounded-full flex items-center justify-center">
                      <svg className="w-4 h-4 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                      </svg>
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-2xl shadow-xl border border-slate-100 overflow-hidden">
      <div className="bg-gradient-to-r from-blue-600 to-indigo-600 p-8 text-white relative overflow-hidden">
        <div className="absolute top-0 right-0 w-64 h-64 bg-white rounded-full mix-blend-overlay filter blur-3xl opacity-10"></div>
        <div className="relative z-10">
          <div className="flex items-center space-x-3 mb-2">
            <Sparkles className="w-6 h-6 text-blue-200" />
            <h2 className="text-2xl font-bold">Submit New Ticket</h2>
          </div>
          <p className="text-blue-100">Describe your issue and let our AI Agent analyze it for you.</p>
        </div>
      </div>
      
      <div className="p-8">
        <form onSubmit={handleSubmit} className="space-y-8">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            <div className="col-span-2">
              <label className="block text-sm font-semibold text-slate-700 mb-2">Issue Title</label>
              <input
                type="text"
                name="title"
                required
                value={formData.title}
                onChange={handleChange}
                className="w-full px-4 py-3 bg-slate-50 border border-slate-200 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition-all placeholder:text-slate-400"
                placeholder="Brief summary of the issue (e.g., Pipeline failure in ADF)"
              />
            </div>

            <div className="col-span-2">
              <label className="block text-sm font-semibold text-slate-700 mb-2">Detailed Description</label>
              <textarea
                name="description"
                required
                rows={5}
                value={formData.description}
                onChange={handleChange}
                className="w-full px-4 py-3 bg-slate-50 border border-slate-200 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition-all placeholder:text-slate-400 resize-none"
                placeholder="Please provide error codes, logs, and steps to reproduce..."
              />
            </div>

            <div>
              <label className="block text-sm font-semibold text-slate-700 mb-2">Category</label>
              <div className="relative">
                <select
                  name="category"
                  value={formData.category}
                  onChange={handleChange}
                  className="w-full px-4 py-3 bg-slate-50 border border-slate-200 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none appearance-none cursor-pointer"
                >
                  <option>General</option>
                  <option>Azure Data Factory</option>
                  <option>Databricks</option>
                  <option>Database</option>
                  <option>Network</option>
                  <option>Security</option>
                </select>
                <div className="absolute inset-y-0 right-0 flex items-center px-4 pointer-events-none text-slate-500">
                  <svg className="w-4 h-4 fill-current" viewBox="0 0 20 20"><path d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" /></svg>
                </div>
              </div>
            </div>

            <div>
              <label className="block text-sm font-semibold text-slate-700 mb-2">Severity</label>
              <div className="relative">
                <select
                  name="severity"
                  value={formData.severity}
                  onChange={handleChange}
                  className="w-full px-4 py-3 bg-slate-50 border border-slate-200 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none appearance-none cursor-pointer"
                >
                  <option>Low</option>
                  <option>Medium</option>
                  <option>High</option>
                  <option>Critical</option>
                </select>
                <div className="absolute inset-y-0 right-0 flex items-center px-4 pointer-events-none text-slate-500">
                  <svg className="w-4 h-4 fill-current" viewBox="0 0 20 20"><path d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" /></svg>
                </div>
              </div>
            </div>

            <div>
              <label className="block text-sm font-semibold text-slate-700 mb-2">Application / Service</label>
              <input
                type="text"
                name="application"
                value={formData.application}
                onChange={handleChange}
                className="w-full px-4 py-3 bg-slate-50 border border-slate-200 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition-all"
                placeholder="e.g., ADF Pipeline, Web App"
              />
            </div>

            <div>
              <label className="block text-sm font-semibold text-slate-700 mb-2">Environment</label>
              <div className="relative">
                <select
                  name="environment"
                  value={formData.environment}
                  onChange={handleChange}
                  className="w-full px-4 py-3 bg-slate-50 border border-slate-200 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none appearance-none cursor-pointer"
                >
                  <option>Production</option>
                  <option>Staging</option>
                  <option>Development</option>
                  <option>Test</option>
                </select>
                <div className="absolute inset-y-0 right-0 flex items-center px-4 pointer-events-none text-slate-500">
                  <svg className="w-4 h-4 fill-current" viewBox="0 0 20 20"><path d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" /></svg>
                </div>
              </div>
            </div>

            <div className="col-span-2">
              <label className="block text-sm font-semibold text-slate-700 mb-2">Affected Users</label>
              <input
                type="text"
                name="affected_users"
                value={formData.affected_users}
                onChange={handleChange}
                className="w-full px-4 py-3 bg-slate-50 border border-slate-200 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition-all"
                placeholder="Who is impacted? (e.g., Finance Team, All Users)"
              />
            </div>
          </div>

          <div className="flex justify-end pt-6 border-t border-slate-100">
            <button
              type="submit"
              disabled={submitting}
              className="flex items-center px-8 py-4 bg-gradient-to-r from-blue-600 to-indigo-600 text-white font-bold rounded-xl hover:shadow-lg hover:scale-[1.02] focus:ring-4 focus:ring-blue-200 transition-all disabled:opacity-70 disabled:cursor-not-allowed disabled:hover:scale-100"
            >
              {submitting ? (
                <>
                  <Loader2 className="w-5 h-5 mr-2 animate-spin" />
                  Analyzing Ticket...
                </>
              ) : (
                <>
                  <Send className="w-5 h-5 mr-2" />
                  Submit & Analyze
                </>
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default TicketForm;
