"use client";
import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { RefreshCw, UploadCloud } from "lucide-react";
import { seedBankTransactions, runReconciliation } from "@/lib/api";

export function ReconciliationWidget({ onReconcileComplete }: { onReconcileComplete: () => void }) {
    const [loading, setLoading] = useState(false);
    const [message, setMessage] = useState("");

    const handleSeed = async () => {
        setLoading(true);
        try {
            await seedBankTransactions();
            setMessage("تم إضافة عمليات بنكية وهمية.");
        } catch (e) {
            setMessage("فشل إضافة البيانات.");
        } finally {
            setLoading(false);
        }
    };

    const handleRun = async () => {
        setLoading(true);
        try {
            const res = await runReconciliation();
            setMessage(`تمت المطابقة: ${res.matches} عمليات.`);
            if (res.matches > 0) onReconcileComplete();
        } catch (e) {
            setMessage("فشل تشغيل المطابقة.");
        } finally {
            setLoading(false);
        }
    };

    return (
        <Card className="h-full">
            <CardHeader>
                <CardTitle className="flex items-center gap-2">
                    <RefreshCw className="w-5 h-5" />
                    المطابقة البنكية
                </CardTitle>
            </CardHeader>
            <CardContent>
                <div className="space-y-4">
                    <p className="text-sm text-muted-foreground">
                        قم برفع كشف الحساب البنكي لمطابقته مع الفواتير المسجلة تلقائياً.
                    </p>

                    <div className="flex gap-2">
                        <Button variant="outline" onClick={handleSeed} disabled={loading} className="flex-1 text-xs">
                            <UploadCloud className="w-3 h-3 mr-2" />
                            محاكاة كشف حساب
                        </Button>
                        <Button onClick={handleRun} disabled={loading} className="flex-1 text-xs bg-slate-800">
                            بدء المطابقة الآلية
                        </Button>
                    </div>

                    {message && (
                        <div className="p-2 bg-slate-100 text-xs rounded text-center font-medium animate-pulse">
                            {message}
                        </div>
                    )}
                </div>

                {/* History Table */}
                <div className="mt-8 pt-4 border-t">
                    <h4 className="text-sm font-bold mb-3 text-slate-700">سجل المطابقات السابقة</h4>
                    <div className="border rounded-md overflow-hidden">
                        <table className="w-full text-xs text-right">
                            <thead className="bg-slate-50 text-slate-500 font-medium">
                                <tr>
                                    <th className="p-2">التاريخ</th>
                                    <th className="p-2">عدد العمليات</th>
                                    <th className="p-2">تطابق</th>
                                    <th className="p-2">الحالة</th>
                                </tr>
                            </thead>
                            <tbody className="bg-white divide-y">
                                <tr>
                                    <td className="p-2">2023-11-01</td>
                                    <td className="p-2">142</td>
                                    <td className="p-2 text-emerald-600 font-bold">100%</td>
                                    <td className="p-2"><span className="bg-emerald-100 text-emerald-700 px-2 py-0.5 rounded text-[10px]">مكتمل</span></td>
                                </tr>
                                <tr>
                                    <td className="p-2">2023-10-01</td>
                                    <td className="p-2">98</td>
                                    <td className="p-2 text-emerald-600 font-bold">100%</td>
                                    <td className="p-2"><span className="bg-emerald-100 text-emerald-700 px-2 py-0.5 rounded text-[10px]">مكتمل</span></td>
                                </tr>
                                <tr>
                                    <td className="p-2">2023-09-01</td>
                                    <td className="p-2">115</td>
                                    <td className="p-2 text-amber-600 font-bold">92%</td>
                                    <td className="p-2"><span className="bg-amber-100 text-amber-700 px-2 py-0.5 rounded text-[10px]">معلق</span></td>
                                </tr>
                            </tbody>
                        </table>
                    </div>
                </div>
            </CardContent>
        </Card>
    );
}
