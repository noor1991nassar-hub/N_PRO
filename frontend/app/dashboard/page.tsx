export default function DashboardPage() {
    return (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
            <div className="rounded-xl border bg-card p-6 shadow-sm">
                <h3 className="font-semibold text-muted-foreground">الملفات النشطة</h3>
                <p className="mt-2 text-3xl font-bold">12</p>
            </div>
            <div className="rounded-xl border bg-card p-6 shadow-sm">
                <h3 className="font-semibold text-muted-foreground">حجم الذاكرة</h3>
                <p className="mt-2 text-3xl font-bold">2.4 GB</p>
            </div>
        </div>
    )
}
