'use client';

import React, { useState, useEffect } from 'react';
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
    LayoutDashboard,
    UploadCloud,
    Table as TableIcon,
    ShieldAlert,
    Bot,
    TrendingUp,
    AlertCircle,
    FileCheck,
    Loader2,
    Database,
    Send,
    User,
    RefreshCw,
    CheckCircle,
    XCircle,
    Cpu
} from "lucide-react";
import { uploadFile, chatWithWorkspace, triggerExtraction, fetchInvoices } from '@/lib/api';

// API Functions (Local/Prod aware via ENV)


export default function FinanceDashboard() {
    const [status, setStatus] = useState<'idle' | 'uploading' | 'analyzing' | 'success' | 'error'>('idle');
    const [uploadProgress, setUploadProgress] = useState(0);
    const [errorMessage, setErrorMessage] = useState("");
    const [invoices, setInvoices] = useState<any[]>([]);
    const [activeTab, setActiveTab] = useState("dashboard");

    // Duplicate Handling State
    const [showDuplicateAlert, setShowDuplicateAlert] = useState(false);
    const [pendingFile, setPendingFile] = useState<File | null>(null);

    // Load Data on Tab Change
    useEffect(() => {
        if (activeTab === "datagrid") {
            fetchInvoices().then(setInvoices).catch(console.error);
        }
    }, [activeTab]);

    // Chat State
    const [messages, setMessages] = useState<{ role: 'user' | 'ai', content: string }[]>([
        { role: 'ai', content: 'مرحباً، أنا محلك المالي الشخصي. جاهز للإجابة عن أسئلتك بخصوص الفواتير والميزانية.' }
    ]);
    const [chatInput, setChatInput] = useState("");
    const [isChatting, setIsChatting] = useState(false);

    const handleChat = async () => {
        if (!chatInput.trim()) return;
        const userMsg = chatInput;
        setMessages(prev => [...prev, { role: 'user', content: userMsg }]);
        setChatInput("");
        setIsChatting(true);

        try {
            // Using a demo email that maps to 'accountant' role
            const res = await chatWithWorkspace(userMsg, "finance@demo.com");
            setMessages(prev => [...prev, { role: 'ai', content: res.answer }]);
        } catch (error) {
            setMessages(prev => [...prev, { role: 'ai', content: "عذراً، حدث خطأ أثناء الاتصال بالخادم." }]);
        } finally {
            setIsChatting(false);
        }
    };

    const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
        if (!e.target.files?.length) return;

        setStatus('uploading');
        setUploadProgress(0);
        setErrorMessage("");

        const file = e.target.files[0];

        try {
            // 1. Upload with Progress (Force=false)
            const doc = await uploadFile(file, false, (percent) => {
                setUploadProgress(percent);
            });
            console.log("Uploaded:", doc);

            // 2. Trigger Extraction (AI Analysis)
            setStatus('analyzing');
            await triggerExtraction(doc.id);

            // Artificial delay to let user see the "Analyzing" state for a moment
            await new Promise(r => setTimeout(r, 1500));

            setStatus('success');
            setTimeout(() => {
                setActiveTab("datagrid");
                setStatus('idle');
                setUploadProgress(0);
            }, 1000);

        } catch (err: any) {
            console.error(err);

            // Handle Duplicate (409)
            if (err.message && err.message.includes("already exists")) {
                setPendingFile(file);
                setShowDuplicateAlert(true);
                setStatus('idle'); // Reset status so UI doesn't look broken
                return;
            }

            setStatus('error');
            setErrorMessage(err.message || "فشل غير معروف في معالجة الملف");
        }
    };

    const confirmOverwrite = async () => {
        if (!pendingFile) return;

        setShowDuplicateAlert(false);
        setStatus('uploading');
        setUploadProgress(0);

        try {
            // Force Upload
            const doc = await uploadFile(pendingFile, true, (percent) => {
                setUploadProgress(percent);
            });

            // Proceed as normal
            setStatus('analyzing');
            await triggerExtraction(doc.id);
            await new Promise(r => setTimeout(r, 1500));
            setStatus('success');
            setTimeout(() => {
                setActiveTab("datagrid");
                setStatus('idle');
                setUploadProgress(0);
                setPendingFile(null);
            }, 1000);

        } catch (err: any) {
            setStatus('error');
            setErrorMessage(err.message);
        }
    };

    return (
        <div className="p-8 w-full font-sans" dir="rtl">

            {/* 1. رأس الصفحة (Header) */}
            <div className="flex justify-between items-center mb-8">
                <div>
                    <h1 className="text-3xl font-bold text-foreground flex items-center gap-3">
                        <span className="p-2 bg-emerald-100 dark:bg-emerald-900/20 rounded-lg">
                            <TrendingUp className="w-8 h-8 text-emerald-600 dark:text-emerald-400" />
                        </span>
                        الإدارة المالية الذكية
                    </h1>
                    <p className="text-muted-foreground mt-2 mr-14">
                        نظام تدقيق ومعالجة الفواتير الآلي - CorporateMemory
                    </p>
                </div>

                {/* أزرار إجراءات سريعة */}
                <div className="flex gap-3">
                    <Button variant="outline">تصدير تقرير شهري</Button>
                    <div className="relative">
                        <input type="file" onChange={handleFileUpload} className="absolute inset-0 opacity-0 cursor-pointer" disabled={status !== 'idle'} />
                        <Button className="bg-emerald-600 hover:bg-emerald-700 text-white gap-2" disabled={status !== 'idle'}>
                            {status !== 'idle' ? <Loader2 className="animate-spin w-4 h-4" /> : <UploadCloud className="w-4 h-4" />}
                            رفع فواتير جديدة
                        </Button>
                    </div>
                </div>
            </div>

            {/* 2. منطقة التابات الخمسة (The 5 Tabs) */}
            <Tabs defaultValue="dashboard" value={activeTab} onValueChange={setActiveTab} className="w-full space-y-6">

                {/* شريط التنقل */}
                <TabsList className="grid w-full grid-cols-5 h-14 bg-card border border-border shadow-sm rounded-xl p-1">
                    <TabsTrigger value="dashboard" className="data-[state=active]:bg-emerald-50 data-[state=active]:text-emerald-700 text-base gap-2">
                        <LayoutDashboard className="w-4 h-4" /> نظرة عامة
                    </TabsTrigger>
                    <TabsTrigger value="documents" className="data-[state=active]:bg-blue-50 data-[state=active]:text-blue-700 text-base gap-2">
                        <UploadCloud className="w-4 h-4" /> مركز الوثائق
                    </TabsTrigger>
                    <TabsTrigger value="datagrid" className="data-[state=active]:bg-purple-50 data-[state=active]:text-purple-700 text-base gap-2">
                        <TableIcon className="w-4 h-4" /> سجل البيانات
                    </TabsTrigger>
                    <TabsTrigger value="audit" className="data-[state=active]:bg-red-50 data-[state=active]:text-red-700 text-base gap-2">
                        <ShieldAlert className="w-4 h-4" /> المدقق الذكي
                    </TabsTrigger>
                    <TabsTrigger value="analyst" className="data-[state=active]:bg-amber-50 data-[state=active]:text-amber-700 text-base gap-2">
                        <Bot className="w-4 h-4" /> المحلل المالي
                    </TabsTrigger>
                </TabsList>

                {/* --- التاب 1: لوحة القيادة (Dashboard) --- */}
                <TabsContent value="dashboard" className="space-y-4">
                    <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
                        <StatsCard title="إجمالي المصروفات" value="SAR 45,231.89" change="+20.1% من الشهر الماضي" icon={TrendingUp} />
                        <StatsCard title="الفواتير المعلقة" value="12" change="3 تستحق الدفع غداً" icon={FileCheck} />
                        <StatsCard title="مخالفات مكتشفة" value="2" change="تتطلب مراجعة فورية" icon={ShieldAlert} alert />
                        <StatsCard title="الميزانية المتبقية" value="SAR 12,000" change="88% تم استهلاكه" icon={LayoutDashboard} />
                    </div>

                    <Card className="h-[400px] flex items-center justify-center border-dashed">
                        <p className="text-muted-foreground">هنا سيتم وضع الرسم البياني للتدفق النقدي (Cash Flow Chart)</p>
                    </Card>
                </TabsContent>

                {/* --- التاب 2: مركز الوثائق (Documents) --- */}
                <TabsContent value="documents" className="space-y-6">
                    <div className="grid gap-6 md:grid-cols-2">
                        {/* 1. مربع الرفع (Upload Box) */}
                        <Card className="h-[430px]">
                            <CardHeader>
                                <CardTitle>رفع ملفات جديدة</CardTitle>
                                <CardDescription>قم بسحب وإفلات الفواتير هنا.</CardDescription>
                            </CardHeader>
                            <CardContent className="h-[320px] flex flex-col items-center justify-center border-2 border-dashed border-border rounded-lg m-4 bg-muted/20 hover:bg-muted/30 transition-colors relative overflow-hidden">
                                {status === 'idle' && (
                                    <>
                                        <UploadCloud className="w-12 h-12 text-muted-foreground mb-4" />
                                        <h3 className="text-lg font-medium text-foreground">اضغط أو اسحب الملف</h3>
                                        <div className="relative mt-4">
                                            <input type="file" onChange={handleFileUpload} className="absolute inset-0 opacity-0 cursor-pointer" />
                                            <Button>اختيار ملف</Button>
                                        </div>
                                    </>
                                )}

                                {/* وضع المعالجة (Status View) */}
                                {status !== 'idle' && (
                                    <div className="w-full max-w-xs space-y-6">
                                        {/* Step 1: Upload */}
                                        <div className="space-y-2">
                                            <div className="flex justify-between text-sm">
                                                <span className={status === 'uploading' ? 'text-primary font-bold' : 'text-muted-foreground'}>
                                                    1. رفع الملف للصندوق
                                                </span>
                                                <span className="text-muted-foreground">{uploadProgress}%</span>
                                            </div>
                                            <div className="h-2 w-full bg-slate-200 dark:bg-slate-700 rounded-full overflow-hidden">
                                                <div
                                                    className="h-full bg-blue-500 transition-all duration-300"
                                                    style={{ width: `${uploadProgress}%` }}
                                                />
                                            </div>
                                        </div>

                                        {/* Step 2: AI Analysis */}
                                        <div className="flex items-center gap-3">
                                            <div className={`p-2 rounded-full ${status === 'analyzing' ? 'bg-amber-100 text-amber-600 animate-pulse' :
                                                status === 'success' ? 'bg-emerald-100 text-emerald-600' :
                                                    status === 'error' ? 'bg-red-100 text-red-600' :
                                                        'bg-slate-100 text-slate-400'
                                                }`}>
                                                {status === 'analyzing' && <Cpu className="w-5 h-5 animate-spin-slow" />}
                                                {status === 'success' && <CheckCircle className="w-5 h-5" />}
                                                {status === 'error' && <XCircle className="w-5 h-5" />}
                                                {status === 'uploading' && <Cpu className="w-5 h-5" />}
                                            </div>
                                            <div>
                                                <p className={`font-medium ${status === 'analyzing' ? 'text-amber-600' : 'text-foreground'}`}>
                                                    2. التحليل الذكي (AI)
                                                </p>
                                                {status === 'analyzing' && <p className="text-xs text-muted-foreground">جاري قراءة البيانات...</p>}
                                                {status === 'success' && <p className="text-xs text-emerald-600">تم الاستخراج بنجاح!</p>}
                                                {status === 'error' && <p className="text-xs text-red-600">{errorMessage}</p>}
                                            </div>
                                        </div>
                                    </div>
                                )}
                            </CardContent>
                        </Card>

                        {/* 2. مربع الإحصائيات (Statistics Box) */}
                        <Card className="h-[430px]">
                            <CardHeader>
                                <CardTitle>إحصائيات الأرشيف</CardTitle>
                                <CardDescription>ملخص سريع للمستندات المعالجة.</CardDescription>
                            </CardHeader>
                            <CardContent className="space-y-4">
                                {/* Stat 1 */}
                                <div className="flex items-center gap-4 p-4 border rounded-lg bg-card text-card-foreground">
                                    <div className="p-3 bg-blue-100 dark:bg-blue-900/30 rounded-full">
                                        <FileCheck className="w-6 h-6 text-blue-600 dark:text-blue-400" />
                                    </div>
                                    <div>
                                        <p className="text-sm text-muted-foreground">إجمالي الملفات المعالجة</p>
                                        <h4 className="text-2xl font-bold">{invoices.length}</h4>
                                    </div>
                                </div>

                                {/* Stat 2 */}
                                <div className="flex items-center gap-4 p-4 border rounded-lg bg-card text-card-foreground">
                                    <div className="p-3 bg-purple-100 dark:bg-purple-900/30 rounded-full">
                                        <TrendingUp className="w-6 h-6 text-purple-600 dark:text-purple-400" />
                                    </div>
                                    <div>
                                        <p className="text-sm text-muted-foreground">آخر ملف تمت إضافته</p>
                                        <h4 className="text-base font-semibold truncate max-w-[200px]">
                                            {invoices.length > 0 ? (invoices[0].invoice_number || "فاتورة جديدة") : "-"}
                                        </h4>
                                        <p className="text-xs text-muted-foreground">
                                            {invoices.length > 0 && invoices[0].invoice_date ? new Date(invoices[0].invoice_date).toLocaleDateString() : "لا يوجد"}
                                        </p>
                                    </div>
                                </div>

                                {/* Stat 3: Storage Used (Mock) */}
                                <div className="flex items-center gap-4 p-4 border rounded-lg bg-card text-card-foreground">
                                    <div className="p-3 bg-green-100 dark:bg-green-900/30 rounded-full">
                                        <Database className="w-6 h-6 text-green-600 dark:text-green-400" />
                                    </div>
                                    <div>
                                        <p className="text-sm text-muted-foreground">مساحة التخزين المستخدمة</p>
                                        <h4 className="text-2xl font-bold">2.4 GB</h4>
                                    </div>
                                </div>
                            </CardContent>
                        </Card>
                    </div>
                </TabsContent>

                {/* --- التاب 3: سجل البيانات (Data Grid) --- */}
                <TabsContent value="datagrid">
                    <Card>
                        <CardHeader className="flex flex-row items-center justify-between">
                            <div>
                                <CardTitle>البيانات المستخرجة</CardTitle>
                                <CardDescription>جدول تفاعلي بجميع البنود المستخرجة من الفواتير.</CardDescription>
                            </div>
                            <Button variant="outline" size="sm" onClick={() => fetchInvoices().then(setInvoices)} className="gap-2">
                                <RefreshCw className="w-4 h-4" />
                                تحديث البيانات
                            </Button>
                        </CardHeader>
                        <CardContent>
                            {invoices.length === 0 ? (
                                <div className="rounded-md border p-8 text-center bg-muted/20">
                                    <TableIcon className="w-12 h-12 text-muted-foreground mx-auto mb-3" />
                                    <p className="text-muted-foreground mb-4">لا توجد بيانات مستخرجة بعد.</p>
                                    <Button variant="outline" onClick={() => fetchInvoices().then(setInvoices)}>
                                        <RefreshCw className="w-4 h-4 mr-2" />
                                        تحديث القائمة
                                    </Button>
                                </div>
                            ) : (
                                <div className="overflow-x-auto">
                                    <table className="w-full text-sm text-right">
                                        <thead className="bg-slate-100 text-slate-700">
                                            <tr>
                                                <th className="p-3">رقم الفاتورة</th>
                                                <th className="p-3">المورد</th>
                                                <th className="p-3">التاريخ</th>
                                                <th className="p-3">القيمة الإجمالية</th>
                                                <th className="p-3">الحالة</th>
                                            </tr>
                                        </thead>
                                        <tbody>
                                            {invoices.map((inv) => (
                                                <tr key={inv.id} className="border-b hover:bg-slate-50">
                                                    <td className="p-3 font-medium">{inv.invoice_number}</td>
                                                    <td className="p-3">{inv.vendor?.name}</td>
                                                    <td className="p-3">{new Date(inv.invoice_date).toLocaleDateString()}</td>
                                                    <td className="p-3 font-bold">{inv.total_amount} {inv.currency}</td>
                                                    <td className="p-3">
                                                        <span className="px-2 py-1 rounded-full text-xs bg-emerald-100 text-emerald-700">
                                                            {inv.extraction_status}
                                                        </span>
                                                    </td>
                                                </tr>
                                            ))}
                                        </tbody>
                                    </table>
                                </div>
                            )}
                        </CardContent>
                    </Card>
                </TabsContent>

                {/* --- التاب 4: المدقق الذكي (Audit) --- */}
                <TabsContent value="audit">
                    <Card className="border-red-100 bg-red-50/10">
                        <CardHeader>
                            <CardTitle className="flex items-center gap-2 text-red-700">
                                <ShieldAlert className="w-5 h-5" />
                                سجل المخاطر والامتثال
                            </CardTitle>
                            <CardDescription>يقوم الذكاء الاصطناعي بمراجعة كل فاتورة لكشف الاحتيال أو الأخطاء.</CardDescription>
                        </CardHeader>
                        <CardContent>
                            <div className="space-y-4">
                                {/* مثال على تنبيه */}
                                <div className="flex items-start gap-4 p-4 bg-white border border-red-200 rounded-lg shadow-sm">
                                    <div className="p-2 bg-red-100 rounded-full mt-1">
                                        <AlertCircle className="w-5 h-5 text-red-600" />
                                    </div>
                                    <div>
                                        <h4 className="font-bold text-slate-800">اشتباه في فاتورة مكررة</h4>
                                        <p className="text-sm text-slate-600 mt-1">
                                            الفاتورة رقم #INV-2024-001 من المورد "مكتبة جرير" تتطابق في القيمة والتاريخ مع الفاتورة رقم #998.
                                        </p>
                                        <div className="mt-3 flex gap-2">
                                            <Button size="sm" variant="destructive">رفض الدفع</Button>
                                            <Button size="sm" variant="outline">تجاهل التنبيه</Button>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </CardContent>
                    </Card>
                </TabsContent>

                {/* --- التاب 5: المحلل المالي (Analyst) --- */}
                <TabsContent value="analyst">
                    <Card className="h-[600px] flex flex-col">
                        <CardHeader className="border-b bg-slate-50/50">
                            <CardTitle className="flex items-center gap-2">
                                <Bot className="w-5 h-5 text-amber-600" />
                                المساعد المالي الشخصي
                            </CardTitle>
                            <CardDescription>اسأل عن أي تفاصيل مالية أو اطلب تحليلات معقدة.</CardDescription>
                        </CardHeader>
                        <CardContent className="flex-1 flex flex-col p-4 overflow-hidden">
                            {/* منطقة الرسائل */}
                            <div className="flex-1 overflow-y-auto space-y-4 mb-4 p-4 border rounded-lg bg-muted/10">
                                {messages.map((msg, idx) => (
                                    <div key={idx} className={`flex ${msg.role === 'user' ? 'justify-start' : 'justify-end'}`}>
                                        <div className={`max-w-[80%] rounded-lg p-3 ${msg.role === 'user'
                                            ? 'bg-primary text-primary-foreground rounded-tr-none'
                                            : 'bg-muted text-foreground rounded-tl-none border border-border'
                                            }`}>
                                            <div className="flex items-center gap-2 mb-1 opacity-70 text-xs">
                                                {msg.role === 'user' ? <User className="w-3 h-3" /> : <Bot className="w-3 h-3" />}
                                                <span>{msg.role === 'user' ? 'أنت' : 'المساعد'}</span>
                                            </div>
                                            <p className="whitespace-pre-wrap">{msg.content}</p>
                                        </div>
                                    </div>
                                ))}
                                {isChatting && (
                                    <div className="flex justify-end">
                                        <div className="bg-muted text-foreground p-3 rounded-lg rounded-tl-none border border-border">
                                            <div className="flex items-center gap-2">
                                                <Loader2 className="w-3 h-3 animate-spin" />
                                                <span className="text-sm">جاري التحليل...</span>
                                            </div>
                                        </div>
                                    </div>
                                )}
                            </div>

                            {/* منطقة الإدخال */}
                            <div className="flex gap-2">
                                <Button onClick={handleChat} disabled={isChatting} className="gap-2">
                                    <Send className={`w-4 h-4 ${isChatting ? 'opacity-0' : ''}`} />
                                    {isChatting ? <Loader2 className="w-4 h-4 animate-spin absolute" /> : "إرسال"}
                                </Button>
                                <Input
                                    placeholder="اكتب سؤالك المالي هنا..."
                                    value={chatInput}
                                    onChange={(e) => setChatInput(e.target.value)}
                                    onKeyDown={(e) => e.key === 'Enter' && handleChat()}
                                    disabled={isChatting}
                                    className="flex-1" // Make it stretch to fill space
                                />
                            </div>
                        </CardContent>
                    </Card>
                </TabsContent>

            </Tabs>
        </div>
    );
}

// مكون بسيط للبطاقات الإحصائية
function StatsCard({ title, value, change, icon: Icon, alert = false }: any) {
    return (
        <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium text-slate-500">
                    {title}
                </CardTitle>
                <Icon className={`h-4 w-4 ${alert ? 'text-red-500' : 'text-slate-500'}`} />
            </CardHeader>
            <CardContent>
                <div className={`text-2xl font-bold ${alert ? 'text-red-600' : 'text-slate-900'}`}>{value}</div>
                <p className="text-xs text-slate-500 mt-1">
                    {change}
                </p>
            </CardContent>
        </Card>
    );
}
