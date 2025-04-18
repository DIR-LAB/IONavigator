import React, { useState } from 'react';
import { Trace } from '../interface/interfaces';
import '../styles/TraceTable.css';
import deleteIcon from '../assets/delete-icon.png';
import analysisIcon from '../assets/start-analysis.svg';
import inspectIcon from '../assets/inspect-process.svg';
import interactIcon from '../assets/interact.svg';
import editIcon from '../assets/edit-icon.svg';
import rerunIcon from '../assets/rerun-analysis.svg';

interface TraceTableProps {
  traces: Array<Trace>;
  onInteract: (trace: Trace) => void;
  onAnalyze: (e: React.MouseEvent, trace: Trace) => void;
  onDelete: (e: React.MouseEvent, trace: Trace) => void;
  onInspect: (e: React.MouseEvent, trace: Trace) => void;
  onRename: (trace: Trace, newName: string) => void;
  onStopAnalysis: (e: React.MouseEvent, trace: Trace) => void;
  onModelChange: (trace: Trace, model: string) => void;
  availableModels: Array<{ value: string; label: string }>;
  analysisStatuses?: {[key: string]: {
    taskId: string;
    status: string;
    progress: number;
  }};
}

const TraceTable: React.FC<TraceTableProps> = ({
  traces,
  onInteract,
  onAnalyze,
  onDelete,
  onInspect,
  onRename,
  onStopAnalysis,
  onModelChange,
  availableModels,
  analysisStatuses = {}
}) => {
  const [editingTraceId, setEditingTraceId] = useState<string | null>(null);
  const [editingName, setEditingName] = useState<string>('');
  const [isRenaming, setIsRenaming] = useState<boolean>(false);

  const getStatus = (trace: Trace) => {
    const analysisStatus = analysisStatuses[trace.trace_name];
    if (analysisStatus) {
      if (analysisStatus.status === 'running') {
        return {
          text: `Analyzing (${analysisStatus.progress}%)`,
          className: 'running'
        };
      }
      return {
        text: analysisStatus.status.charAt(0).toUpperCase() + analysisStatus.status.slice(1),
        className: analysisStatus.status
      };
    }
    
    switch (trace.status) {
      case 'not_started':
        return {
          text: 'Not Started',
          className: 'not_started'
        };
      case 'running':
        return {
          text: 'Running',
          className: 'running'
        };
      case 'completed':
        return {
          text: 'Completed',
          className: 'completed'
        };
      case 'failed':
        return {
          text: 'Failed',
          className: 'failed'
        };
      default:
        return {
          text: trace.status ? trace.status.charAt(0).toUpperCase() + trace.status.slice(1) : 'Not Started',
          className: trace.status ? trace.status.toLowerCase() : 'not_started'
        };
    }
  };

  const isAnalyzing = (trace: Trace) => {
    const analysisStatus = analysisStatuses[trace.trace_name]?.status;
    return analysisStatus === 'running' || analysisStatus === 'pending' || trace.status === 'running';
  };

  const isAnalysisComplete = (trace: Trace) => {
    const analysisStatus = analysisStatuses[trace.trace_name]?.status;
    return analysisStatus === 'completed' || trace.status === 'completed';
  };

  const handleDoubleClick = (trace: Trace) => {
    setEditingTraceId(trace.trace_name);
    setEditingName(trace.trace_name);
  };

  const handleNameChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setEditingName(e.target.value);
  };

  const handleNameSubmit = async (trace: Trace) => {
    if (editingName.trim() && editingName !== trace.trace_name) {
      setIsRenaming(true);
      try {
        await onRename(trace, editingName.trim());
        setEditingTraceId(null);
        setEditingName('');
      } finally {
        setIsRenaming(false);
      }
    } else {
      setEditingTraceId(null);
    }
  };

  const handleKeyPress = async (e: React.KeyboardEvent, trace: Trace) => {
    if (e.key === 'Enter') {
      await handleNameSubmit(trace);
    } else if (e.key === 'Escape') {
      setEditingTraceId(null);
    }
  };

  return (
    <div className="trace-table-container">
      <table className="trace-table">
        <thead>
          <tr>
            <th>
              <div>Trace Name</div>
              <div className="edit-hint">(double-click to edit)</div>
            </th>
            <th>Upload Date</th>
            <th>Model</th>
            <th>Status</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          {traces.map((trace, index) => (
            <tr key={index} className={isRenaming && editingTraceId === trace.trace_name ? 'renaming' : ''}>
              <td 
                onDoubleClick={() => handleDoubleClick(trace)}
                className="trace-name-cell"
                title="Double-click to edit trace name"
              >
                {editingTraceId === trace.trace_name ? (
                  <input
                    type="text"
                    value={editingName}
                    onChange={handleNameChange}
                    onBlur={() => handleNameSubmit(trace)}
                    onKeyDown={(e) => handleKeyPress(e, trace)}
                    autoFocus
                    className={`trace-name-input ${isRenaming ? 'renaming' : ''}`}
                    disabled={isRenaming}
                  />
                ) : (
                  <div className="trace-name-wrapper">
                    <span>{trace.trace_name}</span>
                    <img 
                      src={editIcon} 
                      alt="Edit" 
                      className="edit-icon"
                      aria-label="Double-click to edit"
                    />
                  </div>
                )}
              </td>
              <td>{new Date(trace.upload_date).toLocaleDateString()}</td>
              <td>
                <select
                  value={trace.model || availableModels[0].value}
                  onChange={(e) => onModelChange(trace, e.target.value)}
                  className="model-select"
                  disabled={isAnalyzing(trace)}
                >
                  {availableModels.map((model) => (
                    <option key={model.value} value={model.value}>
                      {model.label}
                    </option>
                  ))}
                </select>
              </td>
              <td className="status-cell">
                <span className={`status-badge ${getStatus(trace).className}`}>
                  {getStatus(trace).text}
                </span>
              </td>
              <td className="action-cell">
                {isAnalyzing(trace) ? (
                  <button 
                    onClick={(e) => onStopAnalysis(e, trace)}
                    className="analysis-button stop"
                    title="Stop Analysis"
                  >
                    <svg className="stop-icon" viewBox="0 0 24 24" fill="currentColor">
                      <rect x="6" y="6" width="12" height="12" />
                    </svg>
                  </button>
                ) : (
                  <button 
                    onClick={(e) => onAnalyze(e, trace)}
                    className={`analysis-button ${isAnalysisComplete(trace) ? 'rerun' : ''}`}
                    title={isAnalysisComplete(trace) ? "Rerun Analysis" : "Start Analysis"}
                  >
                    <img 
                      src={isAnalysisComplete(trace) ? rerunIcon : analysisIcon} 
                      alt={isAnalysisComplete(trace) ? "Rerun" : "Analyze"} 
                      className="analysis-icon" 
                    />
                  </button>
                )}
                <button 
                  onClick={(e) => { e.stopPropagation(); onInteract(trace); }}
                  className="interact-button"
                  title={isAnalysisComplete(trace) ? 
                    "Interact with Trace" : 
                    "Analysis must be completed before interaction"}
                  disabled={!isAnalysisComplete(trace)}
                >
                  <img src={interactIcon} alt="Interact" className="interact-icon" />
                </button>
                <button 
                  onClick={(e) => onInspect(e, trace)}
                  className="inspect-button"
                  title={isAnalysisComplete(trace) ? 
                    "Inspect Analysis Process" : 
                    "Analysis must be completed before inspection"}
                  disabled={!isAnalysisComplete(trace)}
                >
                  <img src={inspectIcon} alt="Inspect" className="inspect-icon" />
                </button>
                <button 
                  onClick={(e) => onDelete(e, trace)}
                  className="delete-button"
                  title="Delete trace"
                >
                  <img src={deleteIcon} alt="Delete" className="delete-icon" />
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default TraceTable; 