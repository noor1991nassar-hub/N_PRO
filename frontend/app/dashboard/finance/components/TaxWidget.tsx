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

                    <div className="space-y-2">
                        <h4 className="text-xs font-semibold text-slate-500">سجل الإقرارات</h4>
                        {history.slice(0, 3).map((report: any) => (
                            <div key={report.id} className="flex justify-between items-center bg-slate-50 p-2 rounded text-xs border">
                                <span className="flex items-center gap-2">
                                    <FileText className="w-3 h-3 text-slate-400" />
                                    {report.period_end?.split('T')[0]}
                                </span>
                                <span className="font-mono">{report.net_vat_payable?.toLocaleString()}</span>
                            </div>
                        ))}
                    </div>
                </div>
            </CardContent>
        </Card>
    );
}
