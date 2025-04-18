import React, { useState, useEffect } from 'react';
import { fetchOriginalTrace } from '../API/requests';
import { OriginalTraceWindowProps } from '../interface/interfaces';
import { useUser } from '../contexts/UserContext';



const OriginalTraceWindow: React.FC<OriginalTraceWindowProps> = ({ traceName }) => {
    const { userId } = useUser();
    const [originalTrace, setOriginalTrace] = useState<string>('');
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        const loadOriginalTrace = async () => {
            try {
                const traceContent = await fetchOriginalTrace(traceName, userId || '');
                setOriginalTrace(traceContent);
            } catch (error) {
                console.error("Error fetching original trace:", error);
                setError("Failed to load original trace.");
            }
        };
        loadOriginalTrace();
    }, [traceName, userId]);

    return (
        <div className="trace-window">
            <h2>Original Trace</h2>

            <div className="trace-content">
                {error ? (
                    <p className="error">{error}</p>
                ) : (
                    <pre>{originalTrace}</pre>
                )}
            </div>
        </div>
    );
};

export default OriginalTraceWindow;
