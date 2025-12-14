"use client";
import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { FileText, PlayCircle, DownloadCloud, UploadCloud, Users } from "lucide-react";
import { uploadContract, runPayroll, downloadWPS } from "@/lib/api";

export function PayrollWidget() {
    const [loading, setLoading] = useState(false);
    const [message, setMessage] = useState("");

    // Contract State
    const [empId, setEmpId] = useState("");
    const [contractFile, setContractFile] = useState<File | null>(null);

    // Run State
    const [month, setMonth] = useState("5");
    const [year, setYear] = useState("2025");

    // WPS State
    const [runId, setRunId] = useState("");

    const handleContractUpload = async () => {
        if (!empId || !contractFile) return;
        setLoading(true);
        try {
            await uploadContract(Number(empId), contractFile);
            setMessage("تم تحليل العقد وحفظ البيانات بنجاح.");
        } catch (e) {
            setMessage("فشل رفع العقد.");
        } finally {
            setLoading(false);
        }
    };

    const handleRunPayroll = async () => {
        setLoading(true);
        try {
            // Mock attendance data for MVP demo
            const attendance = { "1": { "absent": 0 }, "2": { "absent": 2 } };
            await runPayroll(Number(month), Number(year), attendance);
            setMessage(`تم حساب الرواتب لشهر ${month}/${year} بنجاح.`);
        } catch (e) {
            setMessage("فشل تشغيل مسير الرواتب.");
        } finally {
            setLoading(false);
        }
    };

    const handleDownloadWPS = async () => {
        if (!runId) return;
        setLoading(true);
        try {
            const data = await downloadWPS(Number(runId));
            // Create Blob and Download
            const blob = new Blob([data.content], { type: 'text/csv' });
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = data.filename;
            a.click();
            setMessage("تم تحميل ملف حماية الأجور.");
        } catch (e) {
            setMessage("فشل تحميل WPS.");
        } finally {
            setLoading(false);
        }
    };

    return (
        <Card className="h-full border-t-4 border-t-blue-500">
            <CardHeader>
                <CardTitle className="flex items-center gap-2">
                    <Users className="w-5 h-5" />
                    نظام الرواتب والأجور
                </CardTitle>
            </CardHeader>
            <CardContent>
                <Tabs defaultValue="contracts" className="w-full">
                    <TabsList className="grid w-full grid-cols-3 mb-4">
                        <TabsTrigger value="contracts">العقود</TabsTrigger>
                        <TabsTrigger value="run">المسير</TabsTrigger>
                        <TabsTrigger value="wps">WPS</TabsTrigger>
                    </TabsList>

                    <TabsContent value="contracts" className="space-y-4">
                        <div className="space-y-2">
                            <Label>رقم الموظف</Label>
                            <Input placeholder="مثال: 101" value={empId} onChange={e => setEmpId(e.target.value)} />
                        </div>
                        <div className="space-y-2">
                            <Label>ملف العقد (PDF)</Label>
                            <Input type="file" onChange={e => setContractFile(e.target.files?.[0] || null)} />
                        </div>
                        <Button onClick={handleContractUpload} disabled={loading} className="w-full">
                            <UploadCloud className="w-4 h-4 ml-2" />
                            تحليل العقد
                        </Button>
                    </TabsContent>

                    <TabsContent value="run" className="space-y-4">
                        <div className="flex gap-2">
                            <div className="flex-1 space-y-2">
                                <Label>الشهر</Label>
                                <Input type="number" value={month} onChange={e => setMonth(e.target.value)} />
                            </div>
                            <div className="flex-1 space-y-2">
                                <Label>السنة</Label>
                                <Input type="number" value={year} onChange={e => setYear(e.target.value)} />
                            </div>
                        </div>
                        <Button onClick={handleRunPayroll} disabled={loading} className="w-full bg-green-600 hover:bg-green-700">
                            <PlayCircle className="w-4 h-4 ml-2" />
                            تشغيل المسير
                        </Button>
                    </TabsContent>

                    <TabsContent value="wps" className="space-y-4">
                        <div className="space-y-2">
                            <Label>رقم المسير (Run ID)</Label>
                            <Input placeholder="مثال: 1" value={runId} onChange={e => setRunId(e.target.value)} />
                        </div>
                        <Button onClick={handleDownloadWPS} disabled={loading} className="w-full bg-slate-800">
                            <DownloadCloud className="w-4 h-4 ml-2" />
                            تحميل ملف البنك
                        </Button>
                    </TabsContent>
                </Tabs>

                {message && <p className="text-xs text-center mt-4 text-muted-foreground animate-pulse">{message}</p>}
            </CardContent>
        </Card>
    );
}
