
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api';

export async function fetcher<T>(url: string): Promise<T> {
    const res = await fetch(`${API_BASE_URL}${url}`);
    if (!res.ok) {
        throw new Error('An error occurred while fetching the data.');
    }
    return res.json();
}

export const API = {
    uploadFile: async (file: File) => {
        const formData = new FormData();
        formData.append('file', file);
        const res = await fetch(`${API_BASE_URL}/analyze/file`, {
            method: 'POST',
            body: formData,
        });
        if (!res.ok) throw new Error('Upload failed');
        return res.json();
    },

    getHistoryList: async (limit = 100) => {
        const res = await fetch(`${API_BASE_URL}/history?limit=${limit}`);
        if (!res.ok) throw new Error('Failed to fetch history');
        return res.json();
    },

    getAnalysisResult: async (requestId: string) => {
        const res = await fetch(`${API_BASE_URL}/history/${requestId}`);
        if (!res.ok) throw new Error('Failed to fetch result');
        return res.json();
    },

    updateFeedback: async (requestId: string, feedback: { is_resolved?: boolean; csat_score?: number }) => {
        const res = await fetch(`${API_BASE_URL}/history/${requestId}/feedback`, {
            method: 'PATCH',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(feedback),
        });
        if (!res.ok) throw new Error('Failed to update feedback');
        return res.json();
    },

    // FAQ
    getFAQList: async () => {
        const res = await fetch(`${API_BASE_URL}/faq/list`);
        if (!res.ok) throw new Error('Failed to fetch FAQ list');
        return res.json();
    },

    toggleFAQActive: async (id: string, isActive: boolean) => {
        const res = await fetch(`${API_BASE_URL}/faq/${id}/status`, {
            method: 'PATCH',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ is_active: isActive }),
        });
        if (!res.ok) throw new Error('Failed to update FAQ status');
        return res.json();
    },

    deleteFAQ: async (id: string) => {
        const res = await fetch(`${API_BASE_URL}/faq/${id}`, {
            method: 'DELETE',
        });
        if (!res.ok) throw new Error('Failed to delete FAQ');
        return res.json();
    },

    uploadFAQ: async (file: File) => {
        const formData = new FormData();
        formData.append('file', file);
        // Assuming the endpoint is /api/faq/upload based on typical pattern, verifying in next step
        const res = await fetch(`${API_BASE_URL}/faq/file`, {
            method: 'POST',
            body: formData,
        });
        if (!res.ok) throw new Error('FAQ Upload failed');
        return res.json();
    }
};
