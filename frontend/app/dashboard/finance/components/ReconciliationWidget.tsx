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
            </CardContent>
        </Card>
    );
}
