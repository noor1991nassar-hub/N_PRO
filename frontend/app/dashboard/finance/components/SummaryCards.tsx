import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { ArrowUpIcon, ArrowDownIcon, WalletIcon, ActivityIcon } from "lucide-react";

export function SummaryCards({ data }: { data: any }) {
    // Default to zeros if data is waiting or failed
    const safeData = data || {
        total_revenue: 0,
        total_expenses: 0,
        net_income: 0,
        budget_limit: 100000,
        budget_usage_percent: 0
    };

    return (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4 mb-8">
            <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                    <CardTitle className="text-sm font-medium">إجمالي الإيرادات</CardTitle>
                    <ArrowUpIcon className="h-4 w-4 text-green-500" />
                </CardHeader>
                <CardContent>
                    <div className="text-2xl font-bold">{safeData.total_revenue?.toLocaleString()} SAR</div>
                    <p className="text-xs text-muted-foreground">+20.1% من الشهر الماضي</p>
                </CardContent>
            </Card>
            <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                    <CardTitle className="text-sm font-medium">إجمالي المصروفات</CardTitle>
                    <ArrowDownIcon className="h-4 w-4 text-red-500" />
                </CardHeader>
                <CardContent>
                    <div className="text-2xl font-bold">{safeData.total_expenses?.toLocaleString()} SAR</div>
                    <p className="text-xs text-muted-foreground">استخدام {safeData.budget_usage_percent}% من الميزانية</p>
                </CardContent>
            </Card>
            <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                    <CardTitle className="text-sm font-medium">صافي الدخل</CardTitle>
                    <WalletIcon className="h-4 w-4 text-blue-500" />
                </CardHeader>
                <CardContent>
                    <div className={`text-2xl font-bold ${safeData.net_income >= 0 ? "text-green-600" : "text-red-600"}`}>
                        {safeData.net_income?.toLocaleString()} SAR
                    </div>
                </CardContent>
            </Card>
            <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                    <CardTitle className="text-sm font-medium">حالة الميزانية</CardTitle>
                    <ActivityIcon className="h-4 w-4 text-orange-500" />
                </CardHeader>
                <CardContent>
                    <div className="text-2xl font-bold">{safeData.budget_limit?.toLocaleString()} SAR</div>
                    <div className="w-full bg-slate-100 h-2 mt-2 rounded-full overflow-hidden">
                        <div
                            className={`h-full ${safeData.budget_usage_percent > 90 ? 'bg-red-500' : 'bg-green-500'}`}
                            style={{ width: `${Math.min(safeData.budget_usage_percent || 0, 100)}%` }}
                        />
                    </div>
                </CardContent>
            </Card>
        </div>
    );
}
