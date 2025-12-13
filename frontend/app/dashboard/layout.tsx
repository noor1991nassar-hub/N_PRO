export default function DashboardLayout({
    children,
}: {
    children: React.ReactNode
}) {
    return (
        <div className="flex h-screen w-full bg-background">
            <div className="flex flex-1 flex-col overflow-hidden">
                <header className="flex h-16 items-center gap-4 border-b bg-background px-6">
                    <h2 className="text-lg font-semibold">مرحباً بك في مساحة العمل</h2>
                    <div className="mr-auto flex items-center gap-4">
                        {/* User Profile Placeholder */}
                        <div className="h-8 w-8 rounded-full bg-muted"></div>
                    </div>
                </header>
                <main className="flex-1 overflow-auto p-6">
                    {children}
                </main>
            </div>
        </div>
    )
}
