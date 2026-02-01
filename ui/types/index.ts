export type Role = 'agent' | 'customer';

export interface Message {
    role: Role;
    content: string;
    timestamp?: string;
}

export interface Conversation {
    id?: string;
    messages: Message[];
    created_at?: string;
}

export interface Improvement {
    issue: string;
    original: string;
    suggested: string;
    reason: string;
    priority: 'critical' | 'important' | 'nice_to_have';
}

export interface AnalysisResult {
    request_id: string;
    conversation_id?: string;
    total_score: number;
    clarification_score: number;
    empathy_tone_score: number;
    solution_accuracy_score: number;
    actionability_score: number;
    confirmation_closure_score: number;
    compliance_safety_score: number;
    strengths: string[];
    improvements: Improvement[];
    overall_feedback: string;

    // KPI
    is_resolved?: boolean;
    csat_score?: number;

    analyzed_at?: string;
}

export interface FAQDocument {
    id: string;
    filename: string;
    file_type: string;
    content_preview: string;
    is_active: boolean;
    created_at: string | null;
    url: string | null;
}

export interface DashboardStats {
    total_analyzed: number;
    avg_score: number;
    resolution_rate: number;
    avg_analysis_seconds: number;
}

export interface AnalysisHistorySummary {
    request_id: string;
    analyzed_at: string;
    total_score: number;
    grade: string;
}

export interface HistoryListResponse {
    items: AnalysisHistorySummary[];
    count: number;
}
