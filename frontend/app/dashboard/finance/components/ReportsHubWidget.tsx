'use client';
import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs";
// Badge and ScrollArea removed as they are missing in UI components
// Replaced with custom styling
import { ArrowUpRight, ArrowDownLeft, Wallet, Building2, Calendar } from "lucide-react";

export function ReportsHubWidget() {
    const [period, setPeriod] = useState("this_year");
    const [entityType, setEntityType] = useState("vendors");
    const [selectedEntity, setSelectedEntity] = useState<any>(null);

    // Mock Data (Replace with fetch from API later)
    const stats = { net_income: 45000, assets: 120000, liabilities: 30000 };
    const entities = [
        { id: 1, name: "مكتبة جرير", balance_due: 1200, status: "Active" },
        { id: 2, name: "شركة الكهرباء", balance_due: 450, status: "Active" },
        { id: 3, name: "المقاولون العرب", balance_due: 50000, status: "Payment Pending" },
    ];

    return (
        <div className="space-y-8 h-full" dir="rtl">

            {/* --- Zone 1: Time Control --- */}
            <div className="flex items-center justify-between bg-white p-4 rounded-xl shadow-sm border">
                <h2 className="text-xl font-bold flex items-center gap-2">
                    <Calendar className="w-5 h-5 text-emerald-600" />
                    مركز التقارير المالية
                </h2>
                <div className="flex gap-2">
                    {["this_month", "this_quarter", "this_year"].map((p) => (
                        <Button
                            key={p}
                            variant={period === p ? "default" : "outline"}
                            onClick={() => setPeriod(p)}
                            className="text-sm"
                        >
                            {p === "this_month" ? "هذا الشهر" : p === "this_quarter" ? "الربع الحالي" : "السنة الحالية"}
                        </Button>
                    ))}
                </div>
            </div>

            {/* --- Zone 2: Financial Statements Buttons --- */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                <ReportCard title="ميزان المراجعة" value="متوازن ✅" desc="آخر تحديث: الآن" color="bg-blue-50 text-blue-700" />
                <ReportCard title="قائمة الدخل" value={`SAR ${stats.net_income.toLocaleString()}`} desc="صافي الأرباح" color="bg-emerald-50 text-emerald-700" />
                <ReportCard title="الميزانية العمومية" value={`SAR ${stats.assets.toLocaleString()}`} desc="إجمالي الأصول" color="bg-purple-50 text-purple-700" />
                <ReportCard title="تقرير الضرائب" value="SAR 9,200" desc="مستحق للدفع" color="bg-amber-50 text-amber-700" />
            </div>

            {/* --- Zone 3: Entity Explorer --- */}
            <div className="grid grid-cols-1 md:grid-cols-12 gap-6 h-[600px] pb-10">

                {/* Right Side: Entity List */}
                <Card className="col-span-12 md:col-span-4 flex flex-col h-full">
                    <div className="p-4 border-b">
                        <Tabs defaultValue="vendors" onValueChange={setEntityType} className="w-full">
                            <TabsList className="w-full grid grid-cols-2">
                                <TabsTrigger value="vendors">الموردين</TabsTrigger>
                                <TabsTrigger value="customers">العملاء</TabsTrigger>
                            </TabsList>
                        </Tabs>
                    </div>
                    {/* Custom Scroll Area */}
                    <div className="flex-1 p-2 overflow-y-auto">
                        {entities.map((ent) => (
                            <div
                                key={ent.id}
                                onClick={() => setSelectedEntity(ent)}
                                className={`p-4 mb-2 rounded-lg cursor-pointer transition-colors border ${selectedEntity?.id === ent.id ? 'bg-slate-100 border-slate-400' : 'bg-white hover:bg-slate-50'}`}
                            >
                                <div className="flex justify-between items-center">
                                    <span className="font-bold text-slate-800">{ent.name}</span>
                                    {ent.balance_due > 0 && <span className="px-2 py-1 text-xs font-bold text-white bg-red-500 rounded-full">{ent.balance_due}</span>}
                                </div>
                                <div className="text-xs text-slate-500 mt-1 flex justify-between">
                                    <span>{ent.status}</span>
                                    <span>ID: #{ent.id}</span>
                                </div>
                            </div>
                        ))}
                    </div>
                </Card>

                {/* Left Side: The Entity Card (Details) */}
                <Card className="col-span-12 md:col-span-8 bg-white h-full">
                    {selectedEntity ? (
                        <div className="p-6 h-full flex flex-col overflow-y-auto">
                            {/* Header */}
                            <div className="flex justify-between items-start mb-8">
                                <div>
                                    <h2 className="text-3xl font-bold text-slate-800">{selectedEntity.name}</h2>
                                    <p className="text-slate-500">مورد معتمد - الرياض، السعودية</p>
                                </div>
                                <Button variant="outline">كشف حساب PDF</Button>
                            </div>

                            {/* Stats Circles */}
                            <div className="grid grid-cols-3 gap-6 mb-8">
                                <div className="p-4 bg-slate-50 rounded-xl text-center border">
                                    <p className="text-slate-500 text-sm mb-1">إجمالي التعاملات</p>
                                    <p className="text-2xl font-bold text-slate-800">150,000</p>
                                </div>
                                <div className="p-4 bg-emerald-50 rounded-xl text-center border border-emerald-100">
                                    <p className="text-emerald-600 text-sm mb-1">المدفوع</p>
                                    <p className="text-2xl font-bold text-emerald-700">100,000</p>
                                </div>
                                <div className="p-4 bg-red-50 rounded-xl text-center border border-red-100">
                                    <p className="text-red-600 text-sm mb-1">المتبقي (Due)</p>
                                    <p className="text-2xl font-bold text-red-700">{selectedEntity.balance_due.toLocaleString()}</p>
                                </div>
                            </div>

                            {/* Mini Ledger Table */}
                            <h3 className="font-bold text-lg mb-4">آخر الحركات</h3>
                            <div className="border rounded-lg overflow-hidden">
                                <table className="w-full text-sm text-right">
                                    <thead className="bg-slate-100 text-slate-600">
                                        <tr>
                                            <th className="p-3">التاريخ</th>
                                            <th className="p-3">الوصف</th>
                                            <th className="p-3">القيمة</th>
                                            <th className="p-3">الحالة</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        <tr className="border-t">
                                            <td className="p-3">2023-10-01</td>
                                            <td className="p-3">فاتورة مشتريات #INV-001</td>
                                            <td className="p-3 font-medium">50,000</td>
                                            <td className="p-3"><span className="px-2 py-1 rounded text-red-600 bg-red-50 border border-red-200 text-xs">غير مدفوع</span></td>
                                        </tr>
                                        <tr className="border-t">
                                            <td className="p-3">2023-09-15</td>
                                            <td className="p-3">دفعة مقدمة</td>
                                            <td className="p-3 font-medium text-emerald-600">-20,000</td>
                                            <td className="p-3"><span className="px-2 py-1 rounded text-emerald-600 bg-emerald-50 border border-emerald-200 text-xs">تم الدفع</span></td>
                                        </tr>
                                    </tbody>
                                </table>
                            </div>
                        </div>
                    ) : (
                        <div className="h-full flex flex-col items-center justify-center text-slate-400">
                            <Building2 className="w-16 h-16 mb-4 opacity-20" />
                            <p>اختر مورداً أو عميلاً من القائمة لعرض التفاصيل</p>
                        </div>
                    )}
                </Card>
            </div>

        </div>
    );
}

function ReportCard({ title, value, desc, color }: any) {
    return (
        <Card className={`${color} border-none shadow-sm cursor-pointer hover:shadow-md transition-all`}>
            <CardContent className="p-6">
                <p className="text-sm font-medium opacity-80 mb-2">{title}</p>
                <h3 className="text-2xl font-bold mb-1">{value}</h3>
                <p className="text-xs opacity-70">{desc}</p>
            </CardContent>
        </Card>
    )
}
