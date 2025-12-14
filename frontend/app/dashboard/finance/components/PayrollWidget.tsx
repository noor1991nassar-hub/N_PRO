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

                {/* Employee Table */}
                <div className="mt-8 border-t pt-4">
                    <h4 className="text-sm font-bold mb-3 text-slate-700 flex justify-between items-center">
                        <span>سجل الموظفين والرواتب</span>
                        <Button variant="ghost" size="sm" className="text-xs h-6">عرض الكل</Button>
                    </h4>
                    <div className="border rounded-md overflow-hidden">
                        <table className="w-full text-xs text-right">
                            <thead className="bg-slate-50 text-slate-500 font-medium">
                                <tr>
                                    <th className="p-2">الموظف</th>
                                    <th className="p-2">المنصب</th>
                                    <th className="p-2">الراتب الأساسي</th>
                                    <th className="p-2">آخر راتب</th>
                                </tr>
                            </thead>
                            <tbody className="bg-white divide-y">
                                <tr>
                                    <td className="p-2 font-medium">أحمد محمد</td>
                                    <td className="p-2 text-slate-500">مدير مبيعات</td>
                                    <td className="p-2">8,000 SAR</td>
                                    <td className="p-2 text-emerald-600">تم التحويل</td>
                                </tr>
                                <tr>
                                    <td className="p-2 font-medium">سارة علي</td>
                                    <td className="p-2 text-slate-500">محاسبة</td>
                                    <td className="p-2">6,500 SAR</td>
                                    <td className="p-2 text-emerald-600">تم التحويل</td>
                                </tr>
                                <tr>
                                    <td className="p-2 font-medium">خالد عبدالله</td>
                                    <td className="p-2 text-slate-500">مهندس موقع</td>
                                    <td className="p-2">12,000 SAR</td>
                                    <td className="p-2 text-emerald-600">تم التحويل</td>
                                </tr>
                                <tr>
                                    <td className="p-2 font-medium">نورة السعيد</td>
                                    <td className="p-2 text-slate-500">HR Specialist</td>
                                    <td className="p-2">7,200 SAR</td>
                                    <td className="p-2 text-amber-600">معلق</td>
                                </tr>
                            </tbody>
                        </table>
                    </div>
                </div>

                {message && <p className="text-xs text-center mt-4 text-muted-foreground animate-pulse">{message}</p>}
            </CardContent>
        </Card>
    );
}
