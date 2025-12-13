import axios from "axios";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

// Hardcoded for demo purposes
const TENANT_ID = "Construction Corp"; // Updated to match Seed

export async function uploadFile(file: File, onProgress?: (percent: number) => void) {
    const formData = new FormData();
    formData.append("file", file);

    try {
        const res = await axios.post(`${API_URL}/app/document`, formData, {
            headers: {
                "X-Tenant-ID": TENANT_ID,
                "Content-Type": "multipart/form-data",
            },
            onUploadProgress: (progressEvent) => {
                if (progressEvent.total) {
                    const percentCompleted = Math.round((progressEvent.loaded * 100) / progressEvent.total);
                    if (onProgress) {
                        onProgress(percentCompleted);
                    }
                }
            },
        });
        return res.data;
    } catch (error: any) {
        throw new Error(error.response?.data?.detail || "Upload failed");
    }
}

export async function chatWithWorkspace(query: string, user_email: string = "eng@demo.com") {
    const res = await fetch(`${API_URL}/app/chat`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-Tenant-ID": TENANT_ID,
        },
        body: JSON.stringify({ query, user_email }), // Send Email for Role resolution
    });

    if (!res.ok) {
        const error = await res.json();
        throw new Error(error.detail || "Chat failed");
    }

    return res.json();
}

export async function getDocuments() {
    const res = await fetch(`${API_URL}/app/document`, {
        method: "GET",
        headers: {
            "X-Tenant-ID": TENANT_ID,
        },
    });

    if (!res.ok) {
        const error = await res.json();
        throw new Error(error.detail || "Fetch failed");
    }

    return res.json();
}

export async function triggerExtraction(docId: number) {
    const res = await axios.post(`${API_URL}/app/finance/extract/${docId}`, {}, {
        headers: { "X-Tenant-ID": TENANT_ID }
    });
    return res.data;
}

export async function fetchInvoices() {
    const res = await axios.get(`${API_URL}/app/finance/invoices`, {
        headers: { "X-Tenant-ID": TENANT_ID }
    });
    return res.data;
}
