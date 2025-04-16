export interface traceDiagnosis {
      content: string;
      sources: Array<{file: string; id: number}>;
  }

  
  export interface Trace {
    trace_name: string;
    upload_date: string;
    trace_description: string;
    status: string;
    model?: string;
  } 



export interface ChatWindowProps {
    selectedTrace: Trace;
  }

export interface OriginalTraceWindowProps {
    traceName: string;
    user_id: string;
  }


export interface EmailInputProps {
    onEmailSubmit: (userId: string) => void;
  }


export interface Message {
    role: string;
    content: string;
    sources?: Array<{file: string; id: number}>;
    liked?: boolean;
    disliked?: boolean;
    comment?: string;
}

export interface chatHistory {
    messages: Array<Message>;
    id: string;
}
