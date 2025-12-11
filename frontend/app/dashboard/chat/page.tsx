"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Send, Loader2 } from "lucide-react"
import { chatWithWorkspace } from "@/lib/api"

type Message = {
    role: 'user' | 'assistant',
    content: string
}

export default function ChatPage() {
    const [messages, setMessages] = useState<Message[]>([
        { role: 'assistant', content: 'مرحباً بك! كيف يمكنني مساعدتك في استعراض بيانات شركتك اليوم؟' }
    ])
    const [input, setInput] = useState("")
    const [loading, setLoading] = useState(false)

    const handleSend = async (e: React.FormEvent) => {
        e.preventDefault()
        if (!input.trim() || loading) return

        const userMsg = input
        setInput("")
        setMessages(prev => [...prev, { role: 'user', content: userMsg }])
        setLoading(true)

        try {
            const response = await chatWithWorkspace(userMsg)
            setMessages(prev => [...prev, { role: 'assistant', content: response.answer }])
        } catch (error) {
            console.error(error)
            setMessages(prev => [...prev, { role: 'assistant', content: "عذراً، حدث خطأ في الاتصال." }])
        } finally {
            setLoading(false)
        }
    }

    return (
        <div className="flex h-[calc(100vh-8rem)] flex-col rounded-xl border bg-card shadow-sm">
            <div className="flex-1 overflow-y-auto p-4 space-y-4">
                {messages.map((msg, i) => (
                    <div key={i} className={`flex gap-3 ${msg.role === 'user' ? 'flex-row-reverse' : ''}`}>
                        <div className={`h-8 w-8 rounded-full flex items-center justify-center text-xs font-bold ${msg.role === 'user' ? 'bg-primary text-primary-foreground' : 'bg-primary/10 text-primary'}`}>
                            {msg.role === 'user' ? 'ME' : 'AI'}
                        </div>
                        <div className={`rounded-lg p-3 text-sm max-w-[80%] ${msg.role === 'user' ? 'bg-primary text-primary-foreground' : 'bg-muted'}`}>
                            {msg.content}
                        </div>
                    </div>
                ))}
                {loading && (
                    <div className="flex gap-3">
                        <div className="h-8 w-8 rounded-full bg-primary/10 flex items-center justify-center text-xs font-bold text-primary">AI</div>
                        <div className="rounded-lg bg-muted p-3 text-sm flex items-center">
                            <Loader2 className="h-4 w-4 animate-spin" />
                        </div>
                    </div>
                )}
            </div>

            <div className="border-t p-4">
                <form onSubmit={handleSend} className="flex gap-2">
                    <Input
                        value={input}
                        onChange={(e) => setInput(e.target.value)}
                        placeholder="كتب رسالتك هنا..."
                        className="flex-1"
                    />
                    <Button type="submit" size="icon" disabled={loading}>
                        <Send className="h-4 w-4" />
                        <span className="sr-only">إرسال</span>
                    </Button>
                </form>
            </div>
        </div>
    )
}
