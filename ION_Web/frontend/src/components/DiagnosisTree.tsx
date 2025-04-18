import React, { useRef, useEffect, useState } from 'react';
import Tree from 'react-d3-tree';
import { renderContent } from '../API/requests';

interface TreeNode {
  id: string;
  name: string;
  content: string;
  step: string;
  module: string;
  parents: TreeNode[];
}

interface DiagnosisTreeProps {
  treeData: TreeNode[];
}

const stepColors = {
    summary_fragments: '#FFB3BA',
    rag_diagnoses: '#BAE1FF',
    intra_module_merges: '#BAFFC9',
    inter_module_merges: '#FFFFBA',
    final_diagnosis: '#00FF00'
  };
  

const DiagnosisTree: React.FC<DiagnosisTreeProps> = ({ treeData }) => {
  const treeContainer = useRef<HTMLDivElement>(null);
  const [dimensions, setDimensions] = useState({ width: 0, height: 0 });
  const [zoom, setZoom] = useState(1);

  useEffect(() => {
    const updateDimensions = () => {
      if (treeContainer.current) {
        setDimensions({
          width: treeContainer.current.offsetWidth,
          height: treeContainer.current.offsetHeight,
        });
      }
    };

    // Initial update
    updateDimensions();

    // Add resize listener
    window.addEventListener('resize', updateDimensions);

    return () => window.removeEventListener('resize', updateDimensions);
  }, []);

  useEffect(() => {
    // Calculate initial zoom based on the number of nodes
    const nodeCount = countNodes(treeData);
    const initialZoom = 0.3;
    setZoom(initialZoom);
  }, [treeData]);

  const countNodes = (nodes: TreeNode[]): number => {
    return nodes.reduce((count, node) => {
      return count + 1 + (node.parents ? countNodes(node.parents) : 0);
    }, 0);
  };

  const renderForeignObjectNode = ({
    nodeDatum,
    toggleNode,
    foreignObjectProps
  }: any) => (
    <g>
      <circle r={10} onClick={toggleNode} />
      <foreignObject {...foreignObjectProps}>
        <div
          style={{ 
            border: "1px solid black", 
            backgroundColor: stepColors[nodeDatum.attributes.step as keyof typeof stepColors] || '#f0f0f0', 
            padding: "1px", 
            overflowY: "auto", 
            fontSize: "0.9em",
            cursor: "pointer"
          }}
          onClick={() => formatAndRenderJson(nodeDatum.attributes.content, nodeDatum.name)}
          title={`File: ${nodeDatum.name}\nStep: ${nodeDatum.attributes.step}`}
        >
          <div style={{ 
            textAlign: "center",
            padding: "5px",
            whiteSpace: "nowrap",
            overflow: "hidden",
            textOverflow: "ellipsis"
          }}>
            {nodeDatum.attributes.step === 'final_diagnosis' 
              ? 'Final Diagnosis'
              : nodeDatum.attributes.module}
          </div>
        </div>
      </foreignObject>
    </g>
  );

  const processTreeData = (data: TreeNode[]): any => {
    return data.map(node => ({
      name: node.name,
      attributes: {
        step: node.step,
        module: node.module,
        content: node.content
      },
      children: node.parents ? processTreeData(node.parents) : []
    }));
  };

  const formatAndRenderJson = async (content: any, name: string) => {
    try {
      const responseData = await renderContent(content, name);
      const newWindow = window.open();
      if (newWindow) {
        const isTextFile = name.endsWith('.txt') || name.endsWith('.md');
        
        const additionalStyles = `
          <style>
            body, html {
              margin: 0;
              padding: 0;
              width: 100%;
              max-width: 100%;
              overflow-x: hidden;
            }
            .content-wrapper {
              position: relative;
              width: 100%;
              height: 100vh;
              overflow: hidden;
              max-width: 100%;
            }
            .diagnosis-content { 
              width: 60%;
              max-width: 1200px;
              margin: 0 auto;
              height: 100%;
              overflow-y: auto;
              padding: 0 20px;
            }
            .diagnosis-content * {
              max-width: 100% !important;
              word-wrap: break-word;
            }
            .sources-section {
              margin-top: 20px;
              padding: 10px;
              border-top: 1px solid #ccc;
              background-color: #f8f8f8;
              width: 100%;
              max-width: 1200px;
              margin: 20px auto;
            }
            .source-item {
              margin-bottom: 10px;
              width: 100%;
            }
            .source-header {
              cursor: pointer;
              padding: 5px;
              background-color: #e0e0e0;
              border-radius: 4px;
              display: flex;
              justify-content: space-between;
              align-items: center;
              width: 100%;
            }
            .source-header:hover {
              background-color: #d0d0d0;
            }
            .source-content {
              padding: 10px;
              border: 1px solid #ddd;
              border-top: none;
              background-color: white;
              max-height: 500px;
              overflow-y: auto;
              display: none;
              width: 100%;
            }
            .source-content pre {
              white-space: pre-wrap;
              word-wrap: break-word;
              max-width: 100%;
            }
            .source-content code {
              background-color: #f5f5f5;
              padding: 2px 4px;
              border-radius: 3px;
              max-width: 100%;
              word-wrap: break-word;
            }
            .source-content p {
              margin: 0.5em 0;
              max-width: 100%;
            }
            .source-content h1, .source-content h2, .source-content h3, 
            .source-content h4, .source-content h5, .source-content h6 {
              margin-top: 1em;
              margin-bottom: 0.5em;
            }
            .source-content ul, .source-content ol {
              padding-left: 2em;
            }
            .source-toggle {
              font-weight: bold;
            }
            
            /* Force any potential fixed-width elements to be responsive */
            table, img, div, pre {
              max-width: 100% !important;
            }
            
            /* Ensure text doesn't overflow */
            p, span, h1, h2, h3, h4, h5, h6, li {
              word-wrap: break-word;
              overflow-wrap: break-word;
            }
            
            /* Style for dividers between array items */
            .source-divider {
              border-top: 1px solid #eaeaea;
              margin: 10px 0;
              opacity: 0.6;
            }
          </style>
        `;

        // Include marked.js for markdown rendering
        const markedScript = `
          <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
          <script>
            // Configure marked options
            marked.setOptions({
              breaks: true,
              gfm: true
            });
            
            // Custom function to handle array of texts with dividers
            function renderMarkdownWithDividers(container) {
              const rawMarkdown = container.getAttribute('data-markdown');
              if (rawMarkdown) {
                // Check if it contains our divider marker
                if (rawMarkdown.includes('||DIVIDER||')) {
                  const parts = rawMarkdown.split('||DIVIDER||');
                  let html = '';
                  
                  parts.forEach((part, index) => {
                    // Decode the URL-encoded content before parsing
                    const decodedMarkdown = decodeURIComponent(part);
                    html += marked.parse(decodedMarkdown);
                    
                    // Add divider after each part except the last one
                    if (index < parts.length - 1) {
                      html += '<div class="source-divider"></div>';
                    }
                  });
                  
                  container.innerHTML = html;
                } else {
                  // Regular single text handling
                  const decodedMarkdown = decodeURIComponent(rawMarkdown);
                  container.innerHTML = marked.parse(decodedMarkdown);
                }
              }
            }
            
            // Render markdown content when the page loads
            document.addEventListener('DOMContentLoaded', function() {
              const markdownContainers = document.querySelectorAll('.markdown-content');
              markdownContainers.forEach(container => {
                renderMarkdownWithDividers(container);
              });
            });
          </script>
        `;

        const toggleScript = `
          <script>
            function toggleSource(id) {
              const content = document.getElementById('source-content-' + id);
              const toggle = document.getElementById('source-toggle-' + id);
              if (content.style.display === 'none' || content.style.display === '') {
                content.style.display = 'block';
                toggle.textContent = '−';
              } else {
                content.style.display = 'none';
                toggle.textContent = '+';
              }
            }

            // Render markdown content when the page loads
            document.addEventListener('DOMContentLoaded', function() {
              const markdownContainers = document.querySelectorAll('.markdown-content');
              markdownContainers.forEach(container => {
                const rawMarkdown = container.getAttribute('data-markdown');
                if (rawMarkdown) {
                  // Decode the URL-encoded content before parsing
                  const decodedMarkdown = decodeURIComponent(rawMarkdown);
                  container.innerHTML = marked.parse(decodedMarkdown);
                }
              });
            });
          </script>
        `;

        // Extract sources if they exist in the content
        let sourcesHtml = '';
        if (content.sources && Array.isArray(content.sources)) {
          sourcesHtml = `
            <div class="sources-section">
              <h3>Sources</h3>
              ${content.sources.map((source: any, index: number) => {
                // Handle case where source.text is an array of strings
                let sourceText = '';
                if (Array.isArray(source.text)) {
                  sourceText = source.text.map((text: string) => 
                    encodeURIComponent(text)
                  ).join('||DIVIDER||'); // Use a marker for dividers
                } else {
                  sourceText = encodeURIComponent(source.text || 'No content available');
                }
                
                return `
                  <div class="source-item">
                    <div class="source-header" onclick="toggleSource(${index + 1})">
                      <span>[${index + 1}]: ${source.file || 'Unknown file'}</span>
                      <span id="source-toggle-${index + 1}" class="source-toggle">+</span>
                    </div>
                    <div id="source-content-${index + 1}" class="source-content">
                      <div class="markdown-content" data-markdown="${sourceText}"></div>
                    </div>
                  </div>
                `;
              }).join('')}
            </div>
          `;
        } else if (content.sources && typeof content.sources === 'object') {
          // Handle case where sources is an object instead of array
          const sourcesList = Object.entries(content.sources).map(([key, value]: [string, any], index) => {
            // Handle case where value.text is an array of strings
            let sourceText = '';
            if (Array.isArray(value.text)) {
              sourceText = value.text.map((text: string) => 
                encodeURIComponent(text)
              ).join('||DIVIDER||'); // Use a marker for dividers
            } else {
              sourceText = encodeURIComponent(value.text || 'No content available');
            }
            
            return `
              <div class="source-item">
                <div class="source-header" onclick="toggleSource(${index + 1})">
                  <span>[${index + 1}]: ${value.file || key || 'Unknown file'}</span>
                  <span id="source-toggle-${index + 1}" class="source-toggle">+</span>
                </div>
                <div id="source-content-${index + 1}" class="source-content">
                  <div class="markdown-content" data-markdown="${sourceText}"></div>
                </div>
              </div>
            `;
          });
          sourcesHtml = `
            <div class="sources-section">
              <h3>Sources</h3>
              ${sourcesList.join('')}
            </div>
          `;
        }

        if (isTextFile) {
          newWindow.document.write(`
            <!DOCTYPE html>
            <html lang="en">
            <head>
              <meta charset="UTF-8">
              <meta name="viewport" content="width=device-width, initial-scale=1.0">
              <title>Diagnosis Content</title>
              ${additionalStyles}
            </head>
            <body>
              <div class="content-wrapper">
                <div class="diagnosis-content">
                  ${responseData}
                  ${sourcesHtml}
                </div>
              </div>
              ${markedScript}
              ${toggleScript}
            </body>
            </html>
          `);
        } else {
          const bodyContent = responseData.match(/<body>([\s\S]*?)<\/body>/)?.[1] || '';
          const originalStyles = responseData.match(/<style>([\s\S]*?)<\/style>/)?.[0] || '';
          const originalScripts = responseData.match(/<script>([\s\S]*?)<\/script>/)?.[0] || '';

          newWindow.document.write(`
            <!DOCTYPE html>
            <html lang="en">
            <head>
              <meta charset="UTF-8">
              <meta name="viewport" content="width=device-width, initial-scale=1.0">
              <title>Diagnosis Content</title>
              ${originalStyles}
              ${additionalStyles}
            </head>
            <body>
              <div class="content-wrapper">
                <div class="diagnosis-content">
                  ${bodyContent}
                  ${sourcesHtml}
                </div>
              </div>
              ${originalScripts}
              ${markedScript}
              ${toggleScript}
            </body>
            </html>
          `);
        }
        newWindow.document.close();
      }
    } catch (error) {
      console.error('Error formatting content:', error);
    }
  };

const processedTreeData = processTreeData(treeData);

  return (
    <div ref={treeContainer} style={{ 
      width: '95vw',
      height: 'calc(100vh - 200px)',
      margin: '0 auto'
    }}>
      {processedTreeData.length > 0 ? (
        <Tree
          data={processedTreeData[0]}
          orientation="vertical"
          pathFunc="step"
          renderCustomNodeElement={(rd3tProps: any) =>
            renderForeignObjectNode({ 
              ...rd3tProps, 
              foreignObjectProps: { 
                width: 150,
                height: 50,
                y: -25,
                x: -75
              } 
            })
          }
          translate={{ x: dimensions.width / 2, y: 100 }}
          separation={{ siblings: 1.2, nonSiblings: 1.5 }}
          zoom={zoom}
          scaleExtent={{ min: 0.1, max: 2 }}
          nodeSize={{ x: 200, y: 200 }}
        />
      ) : (
        <div>No tree data available</div>
      )}
    </div>
  );
};

export default DiagnosisTree;