import React, { useState, useEffect, useRef } from 'react';
import ReactMarkdown from 'react-markdown';
import { fetchTraceDiagnosis, updateFeedback, fetchSampleQuestions, initializeSocket, sendChatMessage } from '../API/requests';
import { ChatWindowProps, traceDiagnosis, chatHistory } from '../interface/interfaces';
import botIcon from '../assets/bot-icon.svg';
import userIcon from '../assets/user-icon.svg';
import likeIcon_filled from '../assets/like-filled-icon.svg';
import likeIcon_empty from '../assets/like-unfilled-icon.svg';
import dislikeIcon_filled from '../assets/dislike-filled-icon.svg';
import dislikeIcon_empty from '../assets/dislike-unfilled-icon.svg';
import commentIcon_filled from '../assets/comment-filled-icon.svg';
import commentIcon_empty from '../assets/comment-unfilled-icon.svg';
import toolIcon from '../assets/tool-icon.svg';
import { useUser } from '../contexts/UserContext';

const ChatWindow: React.FC<ChatWindowProps> = ({ selectedTrace }) => {
    const { userId } = useUser();
    const [traceDiagnosis, setTraceDiagnosis] = useState<traceDiagnosis | null>(null);
    const [sampleQuestions, setSampleQuestions] = useState<Array<string>>([]);
    const [chatHistory, setChatHistory] = useState<chatHistory | null>(null);
    const [messageContent, setMessageContent] = useState<string>('');
    const [isLoading, setIsLoading] = useState<boolean>(false);
    const [error, setError] = useState<string | null>(null);
    const [commentIndex, setCommentIndex] = useState<number | null>(null);
    const [commentText, setCommentText] = useState<string>('');
    const [isExpanded, setIsExpanded] = useState<boolean>(false);
    const [collapsedTools, setCollapsedTools] = useState<Set<number>>(new Set());

    const chatHistoryRef = useRef<HTMLDivElement | null>(null);

    useEffect(() => {
        const loadTraceDiagnosis = async () => {
            setIsLoading(true);
            
            const data = await fetchTraceDiagnosis(selectedTrace.trace_name, userId || '');
            console.log(data);

            setTraceDiagnosis(data.trace_diagnosis);
            
            const sampleQuestionsData = await fetchSampleQuestions(selectedTrace.trace_name, userId || '');
            setSampleQuestions(sampleQuestionsData);
            console.log(data.trace_diagnosis.content);
            console.log(data.trace_diagnosis.sources);
            setChatHistory({ messages: [{ role: 'assistant', content: data.trace_diagnosis.content, sources: data.trace_diagnosis.sources }], id: data.id });

            setIsLoading(false);
        };
        loadTraceDiagnosis();
    }, [selectedTrace]);

    useEffect(() => {
        if (chatHistoryRef.current) {
            chatHistoryRef.current.scrollTop = chatHistoryRef.current.scrollHeight;
        }
    }, [chatHistory]);

    useEffect(() => {
        const socket = initializeSocket();

        socket.on('receive_message', (message) => {
            setChatHistory((prevChatHistory) => {
                if (!prevChatHistory) return null;
                return {
                    ...prevChatHistory,
                    messages: [...prevChatHistory.messages, message]
                };
            });
        });

        socket.on('response_complete', () => {
            setIsLoading(false);
        });

        return () => {
            socket.disconnect();
        };
    }, []);

    const handleSendMessage = async () => {
        if (messageContent.trim() === '' || !chatHistory || !traceDiagnosis) return;

        const newMessage = { role: 'user', content: messageContent };
        setChatHistory((prevChatHistory) => {
            if (!prevChatHistory) return null;
            return {
                ...prevChatHistory,
                messages: [...prevChatHistory.messages, newMessage]
            };
        });
        setMessageContent('');
        setIsLoading(true);

        try {
            sendChatMessage(
                [...chatHistory.messages, newMessage],
                traceDiagnosis,
                selectedTrace,
                userId || ''
            );
        } catch (error) {
            console.error("Error sending message:", error);
            setError("Failed to send message.");
        }
    };

    const handleKeyPress = async (event: React.KeyboardEvent<HTMLTextAreaElement>) => {
        if (event.key === 'Enter' && !event.shiftKey) {
            event.preventDefault(); // Prevents a new line from being added
            await handleSendMessage();
        }
    };

    const toggleLike = async (index: number) => {
        if (!chatHistory) return;
        const updatedChatHistory = chatHistory.messages.map((chat, i) =>
            i === index ? { ...chat, liked: !chat.liked, disliked: chat.liked ? chat.disliked : false } : chat
        );
        setChatHistory((prevChatHistory) => {
            if (!prevChatHistory) return null;
            return { ...prevChatHistory, messages: updatedChatHistory };
        });

        try {
            if (userId) {
                await updateFeedback(chatHistory, userId);
            }
        } catch (error) {
            console.error('Failed to update like feedback:', error);
        }
    };

    const toggleDislike = async (index: number) => {
        if (!chatHistory) return;
        const updatedChatHistory = chatHistory.messages.map((chat, i) =>
            i === index ? { ...chat, disliked: !chat.disliked, liked: chat.disliked ? chat.liked : false } : chat
        );
        setChatHistory((prevChatHistory) => {
            if (!prevChatHistory) return null;
            return { ...prevChatHistory, messages: updatedChatHistory };
        });

        try {    
            if (userId) {
                await updateFeedback(chatHistory, userId);
            }
        } catch (error) {       
            console.error('Failed to update dislike feedback:', error);
        }
    };

    const addComment = async (index: number, comment: string) => {
        if (!chatHistory) return;
        const updatedChatHistory = chatHistory.messages.map((chat, i) =>
            i === index ? { ...chat, comment } : chat
        );
        setChatHistory((prevChatHistory) => {
            if (!prevChatHistory) return null;
            return { ...prevChatHistory, messages: updatedChatHistory };
        });

        try {
            if (userId) {
                await updateFeedback(chatHistory, userId);
            }
        } catch (error) {
            console.error('Failed to update comment feedback:', error);
        }
    };

    const handleCommentIconClick = (index: number) => {
        setCommentIndex(index);
        setCommentText(chatHistory?.messages[index].comment || '');
    };

    const submitComment = (index: number) => {
        if (commentIndex !== null) {
            addComment(index, commentText);
            setCommentIndex(null);
            setCommentText('');
        }
    };

    const toggleExpand = () => {
        setIsExpanded(!isExpanded);
    };

    const handleSampleQuestionClick = async (question: string) => {
        const newMessage = { role: 'user', content: question };
        setChatHistory((prevChatHistory) => {
            if (!prevChatHistory) return null;
            return { ...prevChatHistory, messages: [...prevChatHistory.messages, newMessage] };
        });

        setIsLoading(true);

        if (traceDiagnosis && chatHistory) {
            try {
                sendChatMessage(
                    [...chatHistory.messages, newMessage],
                    traceDiagnosis,
                    selectedTrace,
                    userId || ''
                );
            } catch (error) {
                console.error("Error fetching chatbot response:", error);
                setError("Failed to get response from chatbot.");
                setIsLoading(false);
            }
        } else {
            setError("Trace diagnosis data is not available.");
            setIsLoading(false);
        }
    };

    const toggleToolMessage = (index: number) => {
        setCollapsedTools(prev => {
            const newSet = new Set(prev);
            if (newSet.has(index)) {
                newSet.delete(index);
            } else {
                newSet.add(index);
            }
            return newSet;
        });
    };

    return (
        <div className="chat-window">
            <style>{`
                .icon {
                    width: 20px; /* Adjust the width as needed */
                    height: 20px; /* Adjust the height as needed */
                }
            `}</style>
            <h2>Chat</h2>
            <div className="chat-history" ref={chatHistoryRef}>
                {chatHistory?.messages
                    .filter(chat => chat.content?.trim())
                    .map((chat, index) => (
                        <div key={index} className={`chat-message ${chat.role}`}>
                            <img
                                src={chat.role === 'assistant' ? botIcon : 
                                     chat.role === 'tool' ? toolIcon : userIcon}
                                alt={`${chat.role} icon`}
                                className='chat-icon'
                            />
                            <div className="chat-bubble">
                                {chat.role === 'tool' ? (
                                    <>
                                        <div 
                                            className="tool-header" 
                                            onClick={() => toggleToolMessage(index)}
                                            style={{ cursor: 'pointer' }}
                                        >
                                            <span>Analysis summary</span>
                                        </div>
                                        {!collapsedTools.has(index) && (
                                            <ReactMarkdown>{chat.content}</ReactMarkdown>
                                        )}
                                    </>
                                ) : chat.role === 'assistant' ? (
                                    <>
                                        <ReactMarkdown>{chat.content}</ReactMarkdown>
                                        {chat.sources && (
                                            <button onClick={toggleExpand}>
                                                {isExpanded ? 'Hide Sources' : 'Show Sources'}
                                            </button>
                                        )}
                                        {isExpanded && chat.sources && Array.isArray(chat.sources) && chat.sources.map((source, idx) => (
                                            <div key={idx} className="source-citation">
                                                <ReactMarkdown>{`[${source.id}]: ${source.file}`}</ReactMarkdown>
                                            </div>
                                        ))}
                                    </>
                                ) : (
                                    <span>{chat.content}</span>
                                )}
                                {chat.role === 'assistant' && (
                                    <div className="feedback-icons">
                                        <span className="feedback-message">Please provide feedback for this message to help us improve:</span>
                                        <img
                                            src={chat.liked ? likeIcon_filled : likeIcon_empty}
                                            alt="Like"
                                            className="icon"
                                            title="Like this message"
                                            onClick={() => toggleLike(index)}
                                        />
                                        <img
                                            src={chat.disliked ? dislikeIcon_filled : dislikeIcon_empty}
                                            alt="Dislike"
                                            className="icon"
                                            title="Dislike this message"
                                            onClick={() => toggleDislike(index)}
                                        />
                                        <img
                                            src={chat.comment ? commentIcon_filled : commentIcon_empty}
                                            alt="Comment"
                                            className="icon"
                                            title="Comment on this message"
                                            onClick={() => handleCommentIconClick(index)}
                                        />
                                        {commentIndex === index && (
                                            <div className="comment-input">
                                                <textarea
                                                    value={commentText}
                                                    onChange={(e) => setCommentText(e.target.value)}
                                                    placeholder="Enter your comment..."
                                                />
                                                <button onClick={() => submitComment(index)}>Submit</button>
                                            </div>
                                        )}
                                    </div>
                                )}
                            </div>
                        </div>
                    ))}
                {isLoading && (
                    <div className="chat-message assistant">
                        <img src={botIcon} alt="assistant icon" className="chat-icon" />
                        <div className="chat-bubble loading">
                            <span className="dot">.</span>
                            <span className="dot">.</span>
                            <span className="dot">.</span>
                        </div>
                    </div>
                )}
            <div className="sample-questions">
                {sampleQuestions && sampleQuestions.map((question, idx) => (
                    <button key={idx} onClick={() => handleSampleQuestionClick(question)}>
                        {question}
                    </button>
                ))}
            </div>
            </div>
            
            <div className="chat-input">
                <textarea
                    placeholder="Type your message here..."
                    value={messageContent}
                    onChange={(e) => setMessageContent(e.target.value)}
                    onKeyDown={handleKeyPress}
                ></textarea>
                <button onClick={handleSendMessage}>Send</button>
            </div>
        </div>
    );
};

export default ChatWindow;