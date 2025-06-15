import React from 'react';
import IONLOGO from '../assets/IONLOGO.png';
import uploadIcon from '../assets/upload-icon.svg';
import '../styles/TopBanner.css';

interface TopBannerProps {
  currentUser: string | null;
  isTestUser: boolean;
  onUploadClick: () => void;
  onUserClick: () => void;
  uploading: boolean;
}

const TopBanner: React.FC<TopBannerProps> = ({ currentUser, isTestUser, onUploadClick, onUserClick, uploading }) => {
  return (
    <div className="top-banner">
      <div className="banner-left">
        <img src={IONLOGO} alt="ION Logo" className="banner-logo" />
        <h1 className="banner-title">IO Insight</h1>
      </div>
      
      <div className="banner-right">
        <div className="current-user" onClick={onUserClick}>
          <span className="user-label">User:</span>
          <span className={`user-email ${isTestUser ? 'test-user' : 'logged-user'}`}>
            {currentUser || 'Loading...'}
          </span>
          {isTestUser && <span className="test-badge">Test Account</span>}
          <span className="login-hint">Click to login</span>
        </div>
        
        <button 
          className="banner-upload-button"
          onClick={onUploadClick}
          disabled={uploading}
        >
          <img src={uploadIcon} alt="Upload" className="upload-icon" />
          {uploading ? 'Uploading...' : 'Upload New Trace'}
        </button>
      </div>
    </div>
  );
};

export default TopBanner;