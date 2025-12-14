"use client";
import { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Calculator, FileText, Download } from "lucide-react";
import { generateTaxReport, getTaxHistory } from "@/lib/api";

export function TaxWidget() {
    const [loading, setLoading] = useState(false);
    const [history, setHistory] = useState<any[]>([]);
    const [latest, setLatest] = useState<any>(null);

    const refreshHistory = async () => {
        const data = await getTaxHistory();
        setHistory(data);
        if (data.length > 0) {
            setLatest(data[0]);
        }
    };

    useEffect(() => {
        refreshHistory();
    }, []);

    const handleGenerate = async () => {
        setLoading(true);
        try {
            // For Demo: Generate for Q1 2025
            await generateTaxReport("2025-01-01", "2025-03-31");
            await refreshHistory();
        } catch (e) {
            console.error(e);
        } finally {
            setLoading(false);
        }
    };

    return (
        <Card className="h-full border-t-4 border-t-purple-500">
            <CardHeader>
                <CardTitle className="flex items-center gap-2">
                    <Calculator className="w-5 h-5" />
                    الإقرارات الضريبية (ZATCA)
                </CardTitle>
            </CardHeader>
            <CardContent>
                <div className="space-y-6">
                    {/* Status Box */}
                    <div className="bg-purple-50 p-4 rounded-lg text-center border border-purple-100">
                        <p className="text-xs text-purple-600 mb-1">صافي ضريبة القيمة المضافة المستحقة</p>
                        <div className="text-2xl font-bold text-purple-800">
                            {latest ? `${latest.net_vat_payable?.toLocaleString()} SAR` : "0.00 SAR"}
                        </div>
                        <p className="text-[10px] text-muted-foreground mt-2">
                            {latest ? `الفترة: ${latest.period_start?.split('T')[0]} - ${latest.period_end?.split('T')[0]}` : "لم يتم إنشاء إقرار"}
                        </p>
                    </div>

                    <Button onClick={handleGenerate} disabled={loading} className="w-full bg-purple-600 hover:bg-purple-700">
                        {loading ? "جاري الحساب..." : "توليد إقرار الربع الحالي"}
                    </Button>

                    <div className="mt-1 pt-2">
                        <h4 className="text-xs font-semibold text-slate-500 mb-2">سجل الإقرارات الضريبية</h4>
                        <div className="border rounded-md overflow-hidden">
                            <table className="w-full text-xs text-right">
                                <thead className="bg-slate-50 text-slate-500 font-medium">
                                    <tr>
                                        <th className="p-2">الفترة</th>
                                        <th className="p-2">المبلغ</th>
                                        <th className="p-2">الحالة</th>
                                    </tr>
                                </thead>
                                <tbody className="bg-white divide-y">
                                    {history.length === 0 && (
                                        <tr>
                                            <td colSpan={3} className="p-4 text-center text-muted-foreground">لا توجد إقرارات سابقة</td>
                                        </tr>
                                    )}
                                    {history.map((report: any) => (
                                        <tr key={report.id}>
                                            <td className="p-2 font-medium">
                                                {report.period_start?.split('T')[0]} <span className="text-slate-400 mx-1">إلى</span> {report.period_end?.split('T')[0]}
                                            </td>
                                            <td className="p-2 font-mono dir-ltr text-left">{report.net_vat_payable?.toLocaleString()} SAR</td>
                                            <td className="p-2">
                                                <span className={`px-2 py-0.5 rounded text-[10px] ${report.status === 'Paid' ? 'bg-emerald-100 text-emerald-700' : 'bg-amber-100 text-amber-700'}`}>
                                                    {report.status || 'معلق'}
                                                </span>
                                            </td>
                                        </tr>
                                    ))}
                                    {/* Mock rows if history is empty for Demo */}
                                    {history.length === 0 && (
                                        <>
                                            <tr>
                                                <td className="p-2">2023-01-01 - 2023-03-31</td>
                                                <td className="p-2 dir-ltr text-left">45,200 SAR</td>
                                                <td className="p-2"><span className="bg-emerald-100 text-emerald-700 px-2 py-0.5 rounded text-[10px]">مدفوع</span></td>
                                            </tr>
                                            <tr>
                                                <td className="p-2">2023-04-01 - 2023-06-30</td>
                                                <td className="p-2 dir-ltr text-left">38,150 SAR</td>
                                                <td className="p-2"><span className="bg-emerald-100 text-emerald-700 px-2 py-0.5 rounded text-[10px]">مدفوع</span></td>
                                            </tr>
                                        </>
                                    )}
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
            </CardContent>
        </Card>
    );
}
