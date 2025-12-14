import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { AlertCircle, CheckCircle2, FileText } from "lucide-react";
import { Button } from "@/components/ui/button";

export function TaskWidget({ tasks }: { tasks: any[] }) {
    if (!tasks || tasks.length === 0) {
        return (
            <Card className="h-full">
                <CardHeader>
                    <CardTitle>المهام المطلوبة</CardTitle>
                </CardHeader>
                <CardContent className="flex flex-col items-center justify-center p-6 text-slate-400">
                    <CheckCircle2 className="w-12 h-12 mb-2 text-green-500" />
                    <p>لا توجد مهام معلقة. عمل ممتاز!</p>
                </CardContent>
            </Card>
        );
    }

    return (
        <Card className="h-full border-l-4 border-l-orange-400">
            <CardHeader>
                <CardTitle className="flex items-center gap-2">
                    <FileText className="w-5 h-5" />
                    قائمة المهام
                </CardTitle>
            </CardHeader>
            <CardContent>
                <ul className="space-y-4">
                    {tasks.map((task) => (
                        <li key={task.id} className="flex items-start justify-between p-3 bg-slate-50 rounded-lg border border-slate-100">
                            <div className="flex gap-3">
                                <div className={`mt-1 p-1 rounded-full ${task.severity === 'high' ? 'bg-red-100 text-red-600' : 'bg-blue-100 text-blue-600'}`}>
                                    <AlertCircle className="w-4 h-4" />
                                </div>
                                <div>
                                    <h4 className="font-semibold text-sm">{task.title}</h4>
                                    <p className="text-xs text-muted-foreground">{task.description}</p>
                                </div>
                            </div>
                            <Button size="sm" variant="outline" className="text-xs h-7">
                                معالجة
                            </Button>
                        </li>
                    ))}
                </ul>
            </CardContent>
        </Card>
    );
}
