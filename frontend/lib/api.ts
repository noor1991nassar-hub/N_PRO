const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

// Hardcoded for demo purposes
const TENANT_ID = "demo-tenant";

export async function uploadFile(file: File) {
    const formData = new FormData();
    formData.append("file", file);

    const res = await fetch(`${API_URL}/workspaces/document`, {
        method: "POST",
        headers: {
            "X-Tenant-ID": TENANT_ID,
        },
        body: formData,
    });

    if (!res.ok) {
        const error = await res.json();
        throw new Error(error.detail || "Upload failed");
    }

    return res.json();
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
