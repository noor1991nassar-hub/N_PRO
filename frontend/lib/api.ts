import axios from "axios";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

// Hardcoded for demo purposes
const TENANT_ID = "Construction Corp";

// --- Document & Chat APIs ---
export async function uploadFile(file: File, force: boolean = false, onProgress?: (percent: number) => void) {
    const formData = new FormData();
    formData.append("file", file);

    try {
        const res = await axios.post(`${API_URL}/app/document?force=${force}`, formData, {
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
        const status = error.response?.status;
        const detail = error.response?.data?.detail || "Upload failed";
        throw { status, message: detail };
    }
}

export async function chatWithWorkspace(query: string, user_email: string = "eng@demo.com") {
    const res = await fetch(`${API_URL}/app/chat`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-Tenant-ID": TENANT_ID,
        },
        body: JSON.stringify({ query, user_email }),
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
        headers: { "X-Tenant-ID": TENANT_ID },
    });
    if (!res.ok) throw new Error("Fetch failed");
    return res.json();
}

// --- Finance Extraction APIs ---
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

// --- Finance Dashboard APIs ---
export async function getFinancialSummary() {
    try {
        const res = await axios.get(`${API_URL}/app/finance/summary`, { headers: { "X-Tenant-ID": TENANT_ID } });
        return res.data;
    } catch (error) { console.error(error); return null; }
}

export async function getAccountantTasks() {
    try {
        const res = await axios.get(`${API_URL}/app/finance/tasks`, { headers: { "X-Tenant-ID": TENANT_ID } });
        return res.data;
    } catch (error) { console.error(error); return []; }
}

// --- Reconciliation APIs ---
export async function seedBankTransactions() {
    await axios.post(`${API_URL}/app/finance/reconcile/seed`, {}, { headers: { "X-Tenant-ID": TENANT_ID } });
}

export async function runReconciliation() {
    const res = await axios.post(`${API_URL}/app/finance/reconcile/run`, {}, { headers: { "X-Tenant-ID": TENANT_ID } });
    return res.data;
}

// --- Tax APIs ---
export async function generateTaxReport(startDate: string, endDate: string) {
    const res = await axios.post(`${API_URL}/app/finance/tax/generate`, { start_date: startDate, end_date: endDate }, { headers: { "X-Tenant-ID": TENANT_ID } });
    return res.data;
}

export async function getTaxHistory() {
    const res = await axios.get(`${API_URL}/app/finance/tax/history`, { headers: { "X-Tenant-ID": TENANT_ID } });
    return res.data;
}

// --- Payroll APIs ---
export async function uploadContract(employeeId: number, file: File) {
    const formData = new FormData();
    formData.append("file", file);
    const res = await axios.post(`${API_URL}/app/payroll/contracts/upload?employee_id=${employeeId}`, formData, {
        headers: { "X-Tenant-ID": TENANT_ID, "Content-Type": "multipart/form-data" }
    });
    return res.data;
}

export async function runPayroll(month: number, year: number, attendanceData: any) {
    const res = await axios.post(`${API_URL}/app/payroll/run/generate`, { month, year, attendance_data: attendanceData }, { headers: { "X-Tenant-ID": TENANT_ID } });
    return res.data;
}

export async function downloadWPS(runId: number) {
    const res = await axios.get(`${API_URL}/app/payroll/run/${runId}/wps`, { headers: { "X-Tenant-ID": TENANT_ID } });
    return res.data; // Note: In real app, we might need 'blob' logic here or at call site.
}
