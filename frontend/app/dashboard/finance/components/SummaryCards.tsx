import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { ArrowUpIcon, ArrowDownIcon, WalletIcon, ActivityIcon } from "lucide-react";

export function SummaryCards({ data }: { data: any }) {
    // Default to placeholders if data is waiting or failed
    const safeData = data || {};

    const formatDate = (d: string) => d ? new Date(d).toLocaleDateString("ar-EG") : "-";
    const formatCurrency = (val: number) => (val || 0).toLocaleString() + " SAR";

    return (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4 mb-8">
            {/* 1. Documents */}
            <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                    <CardTitle className="text-sm font-medium">الوثائق</CardTitle>
                    <ArrowUpIcon className="h-4 w-4 text-blue-500" />
                </CardHeader>
                <CardContent>
                    <div className="text-2xl font-bold">{formatDate(safeData.last_document_date)}</div>
                    <p className="text-xs text-muted-foreground">تاريخ آخر وثيقة</p>
                </CardContent>
            </Card>

            {/* 2. Records */}
            <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                    <CardTitle className="text-sm font-medium">السجلات</CardTitle>
                    <ActivityIcon className="h-4 w-4 text-purple-500" />
                </CardHeader>
                <CardContent>
                    <div className="text-xl font-bold truncate" title={safeData.last_entity_name}>{safeData.last_entity_name || "-"}</div>
                    <p className="text-xs text-muted-foreground">آخر عميل / مورد مضاف</p>
                </CardContent>
            </Card>

            {/* 3. Reports: Net Income */}
            <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                    <CardTitle className="text-sm font-medium">صافي الدخل (شهري)</CardTitle>
                    <WalletIcon className="h-4 w-4 text-emerald-500" />
                </CardHeader>
                <CardContent>
                    <div className={`text-2xl font-bold ${safeData.net_income_last_month >= 0 ? 'text-emerald-600' : 'text-red-600'}`}>
                        {formatCurrency(safeData.net_income_last_month)}
                    </div>
                </CardContent>
            </Card>

            {/* 4. Reports: Cash Flow */}
            <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                    <CardTitle className="text-sm font-medium">السيولة النقدية</CardTitle>
                    <ActivityIcon className="h-4 w-4 text-emerald-500" />
                </CardHeader>
                <CardContent>
                    <div className="text-2xl font-bold">{formatCurrency(safeData.cash_flow_last_month)}</div>
                    <p className="text-xs text-muted-foreground">التدفقات النقدية (تشغيلي)</p>
                </CardContent>
            </Card>

            {/* 5. Reports: Payments */}
            <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                    <CardTitle className="text-sm font-medium">المدفوعات</CardTitle>
                    <ArrowDownIcon className="h-4 w-4 text-red-500" />
                </CardHeader>
                <CardContent>
                    <div className="text-2xl font-bold">{formatCurrency(safeData.total_payments_last_month)}</div>
                    <p className="text-xs text-muted-foreground">إجمالي ما تم دفعه</p>
                </CardContent>
            </Card>

            {/* 6. Reconciliation */}
            <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                    <CardTitle className="text-sm font-medium">المطابقة البنكية</CardTitle>
                    <ActivityIcon className="h-4 w-4 text-indigo-500" />
                </CardHeader>
                <CardContent>
                    <div className="text-2xl font-bold">{formatDate(safeData.last_reconciliation_date)}</div>
                    <p className="text-xs text-muted-foreground">تاريخ آخر مطابقة</p>
                </CardContent>
            </Card>

            {/* 7. Tax */}
            <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                    <CardTitle className="text-sm font-medium">الضرائب</CardTitle>
                    <ActivityIcon className="h-4 w-4 text-teal-500" />
                </CardHeader>
                <CardContent>
                    <div className="text-2xl font-bold">{formatDate(safeData.last_tax_return_date)}</div>
                    <p className="text-xs text-muted-foreground">تاريخ آخر إقرار</p>
                </CardContent>
            </Card>

            {/* 8. Payroll */}
            <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                    <CardTitle className="text-sm font-medium">الرواتب</CardTitle>
                    <ArrowDownIcon className="h-4 w-4 text-orange-500" />
                </CardHeader>
                <CardContent>
                    <div className="text-2xl font-bold">{formatCurrency(safeData.total_payroll_last_run)}</div>
                    <p className="text-xs text-muted-foreground">إجمالي الرواتب (آخر مسير)</p>
                </CardContent>
            </Card>
        </div>
    );
}
