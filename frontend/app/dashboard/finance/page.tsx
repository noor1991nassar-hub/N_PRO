'use client';

import React, { useState, useEffect } from 'react';
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import {
    LayoutDashboard,
    UploadCloud,
    Table as TableIcon,
    ShieldAlert,
    Bot,
    TrendingUp,
    AlertCircle,
    FileCheck,
    Loader2
} from "lucide-react";
import { uploadFile } from '@/lib/api';
import axios from 'axios';

// API Functions (Local/Prod aware via ENV)
const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";
const TENANT_ID = "Construction Corp";

async function triggerExtraction(docId: number) {
    await axios.post(`${API_URL}/app/finance/extract/${docId}`, {}, {
        headers: { "X-Tenant-ID": TENANT_ID }
    });
}

async function fetchInvoices() {
    const res = await axios.get(`${API_URL}/app/finance/invoices`, {
        headers: { "X-Tenant-ID": TENANT_ID }
    });
    return res.data;
}

export default function FinanceDashboard() {
    const [isUploading, setIsUploading] = useState(false);
    const [invoices, setInvoices] = useState<any[]>([]);
    const [activeTab, setActiveTab] = useState("dashboard");

    // Load Data on Tab Change
    useEffect(() => {
        if (activeTab === "datagrid") {
            fetchInvoices().then(setInvoices).catch(console.error);
        }
    }, [activeTab]);

    const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
        if (!e.target.files?.length) return;
        setIsUploading(true);
        try {
            const file = e.target.files[0];
            // 1. Upload
            const doc = await uploadFile(file);
            console.log("Uploaded:", doc);

            // 2. Trigger Extraction
            await triggerExtraction(doc.id);
            alert("تم رفع الملف وبدء عملية استخراج البيانات بذكاء!");

            // 3. Switch to Grid to see result (optimistic)
            setActiveTab("datagrid");
        } catch (err) {
            alert("فشل الرفع: " + err);
        } finally {
            setIsUploading(false);
        }
    };

    return (
        <div className="p-8 w-full font-sans" dir="rtl">

            {/* 1. رأس الصفحة (Header) */}
            <div className="flex justify-between items-center mb-8">
                <div>
                    <h1 className="text-3xl font-bold text-slate-900 dark:text-white flex items-center gap-3">
                        <span className="p-2 bg-emerald-100 rounded-lg">
                            <TrendingUp className="w-8 h-8 text-emerald-600" />
                        </span>
                        الإدارة المالية الذكية
                    </h1>
                    <p className="text-slate-500 mt-2 mr-14">
                        نظام تدقيق ومعالجة الفواتير الآلي - CorporateMemory
                    </p>
                </div>

                {/* أزرار إجراءات سريعة */}
                <div className="flex gap-3">
                    <Button variant="outline">تصدير تقرير شهري</Button>
                    <div className="relative">
                        <input type="file" onChange={handleFileUpload} className="absolute inset-0 opacity-0 cursor-pointer" disabled={isUploading} />
                        <Button className="bg-emerald-600 hover:bg-emerald-700 text-white gap-2" disabled={isUploading}>
                            {isUploading ? <Loader2 className="animate-spin w-4 h-4" /> : <UploadCloud className="w-4 h-4" />}
                            رفع فواتير جديدة
                        </Button>
                    </div>
                </div>
            </div>

            {/* 2. منطقة التابات الخمسة (The 5 Tabs) */}
            <Tabs defaultValue="dashboard" value={activeTab} onValueChange={setActiveTab} className="w-full space-y-6">

                {/* شريط التنقل */}
                <TabsList className="grid w-full grid-cols-5 h-14 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-sm rounded-xl p-1">
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
                        <p className="text-slate-400">هنا سيتم وضع الرسم البياني للتدفق النقدي (Cash Flow Chart)</p>
                    </Card>
                </TabsContent>

                {/* --- التاب 2: مركز الوثائق (Documents) --- */}
                <TabsContent value="documents">
                    <Card>
                        <CardHeader>
                            <CardTitle>أرشيف الملفات</CardTitle>
                            <CardDescription>إدارة ورفع الملفات المالية (PDF, Images, Excel).</CardDescription>
                        </CardHeader>
                        <CardContent className="h-[400px] flex flex-col items-center justify-center border-2 border-dashed border-slate-200 rounded-lg m-6 bg-slate-50">
                            <UploadCloud className="w-16 h-16 text-slate-300 mb-4" />
                            <h3 className="text-lg font-medium text-slate-700">اسحب الملفات هنا للرفع</h3>
                            <div className="relative mt-4">
                                <input type="file" onChange={handleFileUpload} className="absolute inset-0 opacity-0 cursor-pointer" disabled={isUploading} />
                                <Button disabled={isUploading}>{isUploading ? "جاري الرفع..." : "اختيار ملفات"}</Button>
                            </div>
                        </CardContent>
                    </Card>
                </TabsContent>

                {/* --- التاب 3: سجل البيانات (Data Grid) --- */}
                <TabsContent value="datagrid">
                    <Card>
                        <CardHeader>
                            <CardTitle>البيانات المستخرجة</CardTitle>
                            <CardDescription>جدول تفاعلي بجميع البنود المستخرجة من الفواتير.</CardDescription>
                        </CardHeader>
                        <CardContent>
                            {invoices.length === 0 ? (
                                <div className="rounded-md border p-8 text-center bg-slate-50">
                                    <TableIcon className="w-12 h-12 text-slate-300 mx-auto mb-3" />
                                    <p className="text-slate-600">لا توجد بيانات مستخرجة بعد.</p>
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
                        <CardContent className="flex-1 flex items-center justify-center">
                            <div className="text-center space-y-4 max-w-md">
                                <Bot className="w-16 h-16 text-slate-200 mx-auto" />
                                <h3 className="text-xl font-medium text-slate-700">كيف يمكنني مساعدتك اليوم؟</h3>
                                <div className="grid grid-cols-1 gap-2">
                                    <Button variant="outline" className="justify-start h-auto py-3 px-4 text-right">
                                        "ما هي أكثر 3 بنود استهلاكاً للميزانية هذا الشهر؟"
                                    </Button>
                                    <Button variant="outline" className="justify-start h-auto py-3 px-4 text-right">
                                        "أنشئ مقارنة بين مصاريف الربع الأول والربع الثاني."
                                    </Button>
                                </div>
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
