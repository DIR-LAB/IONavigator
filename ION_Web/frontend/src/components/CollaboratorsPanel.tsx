import React, { useState } from 'react';
import chris from '../assets/collaborator_imgs/chris.jpeg';
import arnav from '../assets/collaborator_imgs/Arnav.png';
import DongDai from '../assets/collaborator_imgs/DongDai.png';
import Suren from '../assets/collaborator_imgs/Suren-Byna.png';
import JeanLuca from '../assets/collaborator_imgs/Bez.jpg';
import Dongkuan from '../assets/collaborator_imgs/DK.png';

const collaborators = [
  {
    name: 'Chris Egersdoerfer',
    image: chris,
    role: 'Lead Developer',
    affiliation: 'University of Delaware',
    email: 'cegersdo@udel.edu'
  },
  {
    name: 'Arnav Sareen',
    image: arnav,
    role: 'Supporting Developer',
    affiliation: 'University of North Carolina at Charlotte',
    email: 'asareen2@charlotte.edu'
  },
  {
    name: 'Dong Dai',
    image: DongDai,
    role: 'Principal Investigator',
    affiliation: 'University of Delaware',
    email: 'dai@udel.edu'
  },
  {
    name: 'Suren Byna',
    image: Suren,
    role: 'Co-Principal Investigator',
    affiliation: 'The Ohio State University',
    email: 'byna.1@osu.edu'
  },
  {
    name: 'Jean Luca Bez',
    image: JeanLuca,
    role: 'Co-Principal Investigator',
    affiliation: 'Lawrence Berkeley National Laboratory',
    email: 'jlbez@lbl.gov'
  },
  {
    name: 'Dongkuan (DK) Xu',
    image: Dongkuan,
    role: 'Co-Principal Investigator',
    affiliation: 'North Carolina State University',
    email: 'dxu27@ncsu.edu'
  },
];

const CollaboratorsPanel: React.FC = () => {
  const [isExpanded, setIsExpanded] = useState(false);

  return (
    <div className="collaborators-panel">
      <div 
        className="panel-header" 
        onClick={() => setIsExpanded(!isExpanded)}
        style={{ cursor: 'pointer' }}
      >
        <h2 className="panel-title">
            About | Contact 
        </h2>
      </div>
      
      {isExpanded && (
        <>
          <div className="panel-description">
            <p>This work was created by the <a href="https://sites.google.com/udel.edu/dirlab/home" target="_blank" rel="noopener noreferrer">DIRLab</a> team at University of Delaware in collaboration with Lawrence Berkeley National Laboratory, The Ohio State University, and NC State University.</p>
            <p>This demo represents an ongoing extension of <a href="https://dl.acm.org/doi/10.1145/3655038.3665950" target="_blank" rel="noopener noreferrer">ION: Navigating the HPC I/O Optimization Journey using Large Language Models [HotStorage'24]</a>.</p>
            <p>Any questions can be directed to lead developer, Chris Egersdoerfer at <a href="mailto:cegersdo@udel.edu">cegersdo@udel.edu</a>.</p>
          </div>
          <div className="collaborators-container">
            {collaborators.map((collaborator, index) => (
              <div key={index} className="collaborator-card">
                <img src={collaborator.image} alt={collaborator.name} className="collaborator-image" />
                <h3 className="collaborator-name">{collaborator.name}</h3>
                <h3 className="collaborator-role">{collaborator.role}</h3>
                <p className="collaborator-affiliation">{collaborator.affiliation}</p>
                <a href={`mailto:${collaborator.email}`} className="collaborator-email">
                  {collaborator.email}
                </a>
              </div>
            ))}
          </div>
        </>
      )}
    </div>
  );
};

export default CollaboratorsPanel; 