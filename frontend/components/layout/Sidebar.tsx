"use client"
import Link from "next/link"
import { usePathname } from "next/navigation"
import { cn } from "@/lib/utils"
import { LayoutDashboard, Database, MessageSquare, Settings } from "lucide-react"

const sidebarItems = [
    {
        title: "لوحة التحكم", // Dashboard
        href: "/dashboard",
        icon: LayoutDashboard,
    },
    {
        title: "قاعدة البيانات", // Database
        href: "/dashboard/database",
        icon: Database,
    },
    {
        title: "المحادثة", // Chat
        href: "/dashboard/chat",
        icon: MessageSquare,
    },
    {
        title: "الإعدادات", // Settings
        href: "/dashboard/settings",
        icon: Settings,
    },
]

export function Sidebar() {
    const pathname = usePathname()

    return (
        <div className="flex h-screen w-64 flex-col border-l bg-card text-card-foreground">
            <div className="flex h-16 items-center border-b px-6">
                <h1 className="text-xl font-bold">الذاكرة المؤسسية</h1>
            </div>
            <div className="flex-1 overflow-auto py-4">
                <nav className="grid items-start px-4 text-sm font-medium">
                    {sidebarItems.map((item) => {
                        const Icon = item.icon
                        return (
                            <Link
                                key={item.href}
                                href={item.href}
                                className={cn(
                                    "flex items-center gap-3 rounded-lg px-3 py-2 transition-all hover:text-primary",
                                    pathname === item.href
                                        ? "bg-muted text-primary"
                                        : "text-muted-foreground"
                                )}
                            >
                                <Icon className="h-4 w-4" />
                                {item.title}
                            </Link>
                        )
                    })}
                </nav>
            </div>
        </div>
    )
}
