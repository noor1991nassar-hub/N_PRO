import axios from "axios";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

// Hardcoded for demo purposes
const TENANT_ID = "demo-tenant";

export async function uploadFile(file: File, onProgress?: (percent: number) => void) {
    const formData = new FormData();
    formData.append("file", file);

    try {
        const res = await axios.post(`${API_URL}/workspaces/document`, formData, {
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

export async function chatWithWorkspace(query: string) {
    const res = await fetch(`${API_URL}/workspaces/chat`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-Tenant-ID": TENANT_ID,
        },
        body: JSON.stringify({ query }),
    });

    if (!res.ok) {
        const error = await res.json();
        throw new Error(error.detail || "Chat failed");
    }

    return res.json();
}

export async function getDocuments() {
    const res = await fetch(`${API_URL}/workspaces/document`, {
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
