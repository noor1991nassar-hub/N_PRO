"use client"

import { useState, useEffect } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Upload, FileText, Music, Video } from "lucide-react"
import { Progress } from "@/components/ui/progress"
import { uploadFile } from "@/lib/api"

export default function DatabasePage() {
    const [file, setFile] = useState<File | null>(null)
    const [uploading, setUploading] = useState(false)
    const [uploadProgress, setUploadProgress] = useState(0)

    const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        if (e.target.files) {
            setFile(e.target.files[0])
            setUploadProgress(0)
        }
    }

    const handleUpload = async () => {
        if (!file) return
        setUploading(true)
        setUploadProgress(0)

        try {
            await uploadFile(file, false, (percent) => {
                setUploadProgress(percent)
            })
            setUploadProgress(100)
            alert("تم رفع الملف بنجاح! جاري الفهرسة...")
            setFile(null)
        } catch (error: any) {
            console.error(error)
            alert("فشل الرفع: " + (error.message || "Unknown error"))
        } finally {
            setUploading(false)
            setUploadProgress(0)
        }
    }

    return (
        <div className="space-y-6">
            <div className="flex items-center justify-between">
                <div>
                    <h2 className="text-2xl font-bold tracking-tight">قاعدة البيانات</h2>
                    <p className="text-muted-foreground">أضف الملفات (PDF, MP3, MP4) لتدريب الذاكرة المؤسسية.</p>
                </div>
            </div>

            <div className="grid gap-6 md:grid-cols-2">
                <Card>
                    <CardHeader>
                        <CardTitle>رفع ملف جديد</CardTitle>
                        <CardDescription>اختر ملفاً من جهازك لرفعه إلى مساحة العمل.</CardDescription>
                    </CardHeader>
                    <CardContent className="space-y-4">
                        <div className="grid w-full max-w-sm items-center gap-1.5">
                            <Label htmlFor="file">الملف</Label>
                            <Input id="file" type="file" onChange={handleFileChange} />
                        </div>
                        {uploading && (
                            <div className="space-y-1">
                                <Progress value={uploadProgress} className="h-2" />
                                <p className="text-xs text-muted-foreground text-center">{uploadProgress}%</p>
                            </div>
                        )}
                        <Button onClick={handleUpload} disabled={!file || uploading} className="w-full">
                            {uploading ? "جاري الرفع..." : "رفع الملف"}
                            <Upload className="mr-2 h-4 w-4" />
                        </Button>
                    </CardContent>
                </Card>

                <Card>
                    <CardHeader>
                        <CardTitle>حالة الفهرسة</CardTitle>
                        <CardDescription>حالة معالجة الملفات في Gemini.</CardDescription>
                    </CardHeader>
                    <CardContent>
                        <DocList />
                    </CardContent>
                </Card>
            </div>
        </div>
    )
}

function DocList() {
    const [docs, setDocs] = useState<any[]>([])

    // Simple polling
    useEffect(() => {
        const fetchDocs = async () => {
            try {
                const data = await import("@/lib/api").then(m => m.getDocuments())
                setDocs(data)
            } catch (e) {
                console.error("Failed to fetch docs", e)
            }
        }

        fetchDocs()
        const interval = setInterval(fetchDocs, 5000)
        return () => clearInterval(interval)
    }, [])

    if (docs.length === 0) {
        return <p className="text-sm text-muted-foreground">لا توجد ملفات حتى الآن.</p>
    }

    return (
        <div className="space-y-4">
            {docs.map((doc: any) => (
                <div key={doc.id} className="flex items-center gap-4 rounded-lg border p-4">
                    <div className="flex h-10 w-10 items-center justify-center rounded-full bg-blue-100 text-blue-600">
                        <FileText className="h-5 w-5" />
                    </div>
                    <div className="flex-1 space-y-1">
                        <p className="text-sm font-medium leading-none truncate max-w-[200px]" title={doc.title}>{doc.title}</p>
                        <StatusBadge status={doc.status} />
                    </div>
                </div>
            ))}
        </div>
    )
}

function StatusBadge({ status }: { status: string }) {
    const styles: Record<string, string> = {
        "uploaded": "text-yellow-600 bg-yellow-100",
        "indexing": "text-blue-600 bg-blue-100",
        "active": "text-green-600 bg-green-100",
        "failed": "text-red-600 bg-red-100",
    }

    const labels: Record<string, string> = {
        "uploaded": "جاري الرفع...",
        "indexing": "جاري الفهرسة...",
        "active": "جاهز (Active)",
        "failed": "فشل",
    }

    return (
        <span className={`text-xs px-2 py-0.5 rounded-full ${styles[status.toLowerCase()] || "text-gray-500"}`}>
            {labels[status.toLowerCase()] || status}
        </span>
    )
}


