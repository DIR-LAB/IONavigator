import React, { useState, useMemo } from 'react';
import { Trace } from '../interface/interfaces';
import '../styles/TraceTable.css';
import deleteIcon from '../assets/delete-icon.png';
import analysisIcon from '../assets/start-analysis.svg';
import inspectIcon from '../assets/inspect-process.svg';
import interactIcon from '../assets/interact.svg';
import editIcon from '../assets/edit-icon.svg';
import rerunIcon from '../assets/rerun-analysis.svg';

type SortField = 'trace_name' | 'upload_date' | 'status';
type SortDirection = 'asc' | 'desc';

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
  const [sortField, setSortField] = useState<SortField>('upload_date');
  const [sortDirection, setSortDirection] = useState<SortDirection>('desc');

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

  const handleSort = (field: SortField) => {
    if (sortField === field) {
      setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc');
    } else {
      setSortField(field);
      setSortDirection('asc');
    }
  };

  const getSortIcon = (field: SortField) => {
    if (sortField !== field) {
      return '↕️';
    }
    return sortDirection === 'asc' ? '↑' : '↓';
  };

  const sortedTraces = useMemo(() => {
    const sorted = [...traces].sort((a, b) => {
      let aValue: string | number;
      let bValue: string | number;

      switch (sortField) {
        case 'trace_name':
          aValue = a.trace_name.toLowerCase();
          bValue = b.trace_name.toLowerCase();
          break;
        case 'upload_date':
          aValue = new Date(a.upload_date).getTime();
          bValue = new Date(b.upload_date).getTime();
          break;
        case 'status':
          // Get the actual display status for sorting
          const aStatus = analysisStatuses[a.trace_name]?.status || a.status || 'not_started';
          const bStatus = analysisStatuses[b.trace_name]?.status || b.status || 'not_started';
          aValue = aStatus.toLowerCase();
          bValue = bStatus.toLowerCase();
          break;
        default:
          return 0;
      }

      if (aValue < bValue) {
        return sortDirection === 'asc' ? -1 : 1;
      }
      if (aValue > bValue) {
        return sortDirection === 'asc' ? 1 : -1;
      }
      return 0;
    });
    return sorted;
  }, [traces, sortField, sortDirection, analysisStatuses]);

  return (
    <div className="trace-table-container">
      <table className="trace-table">
        <thead>
          <tr>
            <th className="sortable" onClick={() => handleSort('trace_name')}>
              <div className="header-content">
                <div>Trace Name <span className="sort-icon">{getSortIcon('trace_name')}</span></div>
                <div className="edit-hint">(double-click to edit)</div>
              </div>
            </th>
            <th className="sortable" onClick={() => handleSort('upload_date')}>
              <div className="header-content">
                Upload Date <span className="sort-icon">{getSortIcon('upload_date')}</span>
              </div>
            </th>
            <th>Model</th>
            <th className="sortable" onClick={() => handleSort('status')}>
              <div className="header-content">
                Status <span className="sort-icon">{getSortIcon('status')}</span>
              </div>
            </th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          {sortedTraces.map((trace, index) => (
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