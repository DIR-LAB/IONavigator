import React, { useEffect, useState } from 'react';
import { fetchUserTraces, deleteTrace, startAnalysis, checkAnalysisStatus, fetchDiagnosisTree, stopAnalysis, uploadTrace } from '../API/requests';
import ChatWindow from '../components/ChatWindow';
import OriginalTraceWindow from '../components/originalTraceWindow';
import DiagnosisTree from '../components/DiagnosisTree';
import { Trace } from '../interface/interfaces';
import backIcon from '../assets/back-button.svg';
import { useUser } from '../contexts/UserContext';
import TopBanner from '../components/TopBanner';
import CollaboratorsPanel from '../components/CollaboratorsPanel';
import TraceTable from '../components/TraceTable';
import '../styles/HomePage.css';

const HomePage: React.FC = () => {
  const { userId } = useUser() || { userId: null };
  const [view, setView] = useState<'list' | 'details' | 'inspect'>('list');
  const [userTraces, setUserTraces] = useState<Array<Trace>>([]);
  const [selectedTrace, setSelectedTrace] = useState<Trace | null>(null);
  const [uploading, setUploading] = useState(false);
  const [analysisStatuses, setAnalysisStatuses] = useState<{[key: string]: {
    taskId: string;
    status: string;
    progress: number;
  }}>({});
  const [treeData, setTreeData] = useState<any>(null);

  // Add file input reference
  const fileInputRef = React.useRef<HTMLInputElement>(null);

  // Move availableModels here so it can be passed to TraceTable
  const availableModels = [
    { value: 'gpt-4o', label: 'GPT-4o' },
    { value: 'gpt-4.1-mini', label: 'GPT-4.1-mini' },
    { value: 'gpt-4.1', label: 'GPT-4.1' },
    { value: 'gpt-4o-mini', label: 'GPT-4o-mini' },
    { value: 'anthropic/claude-3-5-sonnet-20240620', label: 'Claude-3.5-Sonnet' },
    { value: 'anthropic/claude-3-7-sonnet-20250219', label: 'Claude-3.7-Sonnet' },
  ];

  useEffect(() => {
    const loadUserTraces = async (userId: string) => {
      try {
        const data = await fetchUserTraces(userId);
        setUserTraces(data);
        console.log(data);
      } catch (error) {
        console.error('Failed to load example cases:', error);
      }
    };

    if (userId) {
      loadUserTraces(userId);
    }
  }, [userId]);

  const handleTraceClick = (trace: Trace) => {
    setSelectedTrace(trace);
    setView('details');
  };

  const handleBackButtonClick = () => {
    setSelectedTrace(null);
    setView('list');
  };

  const handleUploadClick = () => {
    fileInputRef.current?.click();
  };

  const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file || !userId) return;

    setUploading(true);
    try {
      await uploadTrace(file, userId);
      
      // Refresh the trace list after successful upload
      const data = await fetchUserTraces(userId);
      setUserTraces(data);
    } catch (error) {
      console.error('Error uploading file:', error);
      if (error instanceof Error) {
        alert(error.message || 'Failed to upload file. Please try again.');
      } else {
        alert('Failed to upload file. Please try again.');
      }
    } finally {
      setUploading(false);
      // Clear the file input
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
    }
  };

  const pollAnalysisStatus = async (traceName: string, taskId: string) => {
    try {
      const status = await checkAnalysisStatus(taskId);
      
      setAnalysisStatuses(prev => ({
        ...prev,
        [traceName]: {
          taskId,
          status: status.status,
          progress: status.progress
        }
      }));

      // Stop polling if the analysis is stopped, failed, or completed
      if (status.status === 'running' || status.status === 'pending') {
        setTimeout(() => pollAnalysisStatus(traceName, taskId), 2000);
      } else {
        // Refresh the trace list when analysis is complete or stopped
        if (userId) {
          const data = await fetchUserTraces(userId);
          setUserTraces(data);
        }
      }
    } catch (error) {
      console.error('Error polling analysis status:', error);
      setAnalysisStatuses(prev => ({
        ...prev,
        [traceName]: {
          taskId,
          status: 'failed',
          progress: 0
        }
      }));
    }
  };

  const handleRunAnalysis = async (e: React.MouseEvent, trace: Trace) => {
    e.stopPropagation();
    
    if (!userId) return;
    
    try {
        const taskId = await startAnalysis(trace.trace_name, userId, trace.model || 'gpt-4.1-mini');
        
        setAnalysisStatuses(prev => ({
            ...prev,
            [trace.trace_name]: {
                taskId,
                status: 'pending',
                progress: 0
            }
        }));

        pollAnalysisStatus(trace.trace_name, taskId);
    } catch (error) {
        console.error('Failed to run analysis:', error);
        alert('Failed to start analysis. Please try again.');
    }
  };

  const handleDeleteTrace = async (e: React.MouseEvent, trace: Trace) => {
    e.stopPropagation(); // Prevent triggering the card click
    
    if (!userId) return;
    
    if (window.confirm(`Are you sure you want to delete "${trace.trace_name}"?`)) {
      try {
        await deleteTrace(trace.trace_name, userId);
        // Refresh the trace list after deletion
        const data = await fetchUserTraces(userId);
        setUserTraces(data);
      } catch (error) {
        console.error('Failed to delete trace:', error);
        alert('Failed to delete trace. Please try again.');
      }
    }
  };

  const handleInspectTrace = async (e: React.MouseEvent, trace: Trace) => {
    e.stopPropagation();
    
    if (!userId) return;
    
    try {
        console.log(`Fetching diagnosis tree for trace: ${trace.trace_name}`);
        const data = await fetchDiagnosisTree(trace.trace_name, userId);
        console.log('Received tree data:', data);
        
        if (!data) {
            throw new Error('No tree data received');
        }
        
        setTreeData(data);
        setSelectedTrace(trace);
        setView('inspect');
    } catch (error) {
        console.error('Failed to fetch diagnosis tree:', error);
        alert('Failed to load analysis process. The analysis results might not be complete. Please try running the analysis again.');
    }
  };

  const handleRename = async (trace: Trace, newName: string) => {
    if (!userId) return;
    
    try {
      const response = await fetch(`${process.env.REACT_APP_FLASK_API_BASE_URL}/api/rename_trace`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          user_id: userId,
          old_name: trace.trace_name,
          new_name: newName
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to rename trace');
      }

      // Immediately refresh the trace list after successful rename
      const data = await fetchUserTraces(userId);
      setUserTraces(data);
      
      // Update analysis statuses if there's an ongoing analysis
      if (analysisStatuses[trace.trace_name]) {
        setAnalysisStatuses(prev => {
          const { [trace.trace_name]: oldStatus, ...rest } = prev;
          return {
            ...rest,
            [newName]: oldStatus
          };
        });
      }
    } catch (error) {
      console.error('Error renaming trace:', error);
      alert('Failed to rename trace. Please try again.');
    }
  };

  const handleStopAnalysis = async (e: React.MouseEvent, trace: Trace) => {
    e.stopPropagation();
    
    if (!userId) return;
    
    try {
        await stopAnalysis(trace.trace_name, userId);
        
        // Immediately update the analysis status locally
        setAnalysisStatuses(prev => ({
            ...prev,
            [trace.trace_name]: {
                ...prev[trace.trace_name],
                status: 'stopped',
                progress: 0
            }
        }));

        // Refresh the trace list
        const data = await fetchUserTraces(userId);
        setUserTraces(data);
    } catch (error) {
        console.error('Failed to stop analysis:', error);
        alert('Failed to stop analysis. Please try again.');
    }
  };

  const handleModelChange = async (trace: Trace, model: string) => {
    if (!userId) return;
    
    try {
      const response = await fetch(`${process.env.REACT_APP_FLASK_API_BASE_URL}/api/update_trace_model`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          user_id: userId,
          trace_name: trace.trace_name,
          model: model
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to update model');
      }

      // Refresh the trace list
      const data = await fetchUserTraces(userId);
      setUserTraces(data);
    } catch (error) {
      console.error('Error updating model:', error);
      alert('Failed to update model. Please try again.');
    }
  };

  return (
    <div className="homepage-container">
      {view === 'list' && (
        <>
          <TopBanner 
            currentUser={userId}
            onUploadClick={handleUploadClick}
            uploading={uploading}
          />
          <input
            type="file"
            ref={fileInputRef}
            onChange={handleFileUpload}
            style={{ display: 'none' }}
            accept=".txt,.darshan"
          />
          <div className="main-content">
            <TraceTable
              traces={userTraces}
              onInteract={handleTraceClick}
              onAnalyze={handleRunAnalysis}
              onDelete={handleDeleteTrace}
              onInspect={handleInspectTrace}
              onRename={handleRename}
              onStopAnalysis={handleStopAnalysis}
              onModelChange={handleModelChange}
              availableModels={availableModels}
              analysisStatuses={analysisStatuses}
            />
          </div>
          <div className="footer-section">
            <CollaboratorsPanel />
          </div>
        </>
      )}
      {view === 'details' && selectedTrace && userId && (
        <div className="homepage-container">
          <TopBanner 
            currentUser={userId}
            onUploadClick={handleUploadClick}
            uploading={uploading}
          />
          <input
            type="file"
            ref={fileInputRef}
            onChange={handleFileUpload}
            style={{ display: 'none' }}
            accept=".txt,.darshan"
          />
          <div className="details-container">
            <div className="back-button-container">
              <button 
                onClick={handleBackButtonClick} 
                className="back-button" 
                title="Back to Trace Selection"
              >
                <img src={backIcon} alt="Back" />
              </button>
            </div>
            <div className="side-by-side">
              <OriginalTraceWindow traceName={selectedTrace.trace_name} user_id={userId} />
              <ChatWindow selectedTrace={selectedTrace} />
            </div>
            <section className="disclaimer">
                <p><strong>Disclaimer:</strong> As this demo is for research purposes, user interactions in the form of chat messages and like/dislike/comment feedback will be recorded. These will not be shared anywhere.</p>
              </section>
          </div>
        </div>
      )}
      {view === 'inspect' && selectedTrace && treeData && (
        <div className="homepage-container">
          <TopBanner 
            currentUser={userId}
            onUploadClick={handleUploadClick}
            uploading={uploading}
          />
          <input
            type="file"
            ref={fileInputRef}
            onChange={handleFileUpload}
            style={{ display: 'none' }}
            accept=".txt,.darshan"
          />
          <div className="inspect-container">
            <div className="back-button-container">
              <button 
                onClick={handleBackButtonClick} 
                className="back-button" 
                title="Back to Trace Selection"
              >
                <img src={backIcon} alt="Back" />
              </button>
            </div>
            <h2>Analysis Process for {selectedTrace.trace_name}</h2>
            <div className="tree-container">
              <DiagnosisTree treeData={treeData} />
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default HomePage;
