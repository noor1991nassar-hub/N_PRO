'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Card, CardContent, CardDescription, CardHeader, CardTitle, CardFooter } from '@/components/ui/card';
import { Loader2, Lock, Building2, Briefcase } from 'lucide-react';

export default function LoginPage() {
    const router = useRouter();
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState('');

    const handleLogin = async (e: React.FormEvent) => {
        e.preventDefault();
        setIsLoading(true);
        setError('');

        try {
            // ---------------------------------------------------------
            // محاكاة الاتصال بالسيرفر (استبدل هذا الجزء بـ fetch حقيقي لاحقاً)
            // ---------------------------------------------------------
            await new Promise(resolve => setTimeout(resolve, 1500)); // تأخير مصطنع 1.5 ثانية

            // هذه البيانات المفترض أن تأتي من الباك إند بعد نجاح الدخول
            // يمكنك تغيير role هنا لتجربة توجيهات مختلفة: 'engineer', 'lawyer', 'accountant', 'hr'
            const mockResponse = {
                token: "ey_fake_jwt_token_123456",
                user: {
                    name: "م. أحمد الشريف",
                    role: "engineer", // <--- هذا المفتاح هو الذي يحدد الوجهة
                    company: "شركة المقاولون المتحدون"
                }
            };

            // ---------------------------------------------------------
            // منطق التوجيه الذكي (Smart Routing Logic)
            // ---------------------------------------------------------

            // 1. تخزين التوكن وبيانات المستخدم
            localStorage.setItem('token', mockResponse.token);
            localStorage.setItem('user', JSON.stringify(mockResponse.user));

            // 2. التوجيه حسب التخصص
            const role = mockResponse.user.role;

            switch (role) {
                case 'engineer':
                    router.push('/dashboard/engineering');
                    break;
                case 'lawyer':
                    router.push('/dashboard/legal');
                    break;
                case 'accountant':
                    router.push('/dashboard/finance');
                    break;
                case 'hr':
                    router.push('/dashboard/hr');
                    break;
                default:
                    router.push('/dashboard'); // أدمن عام
            }

        } catch (err) {
            setError('فشل تسجيل الدخول. يرجى التحقق من البيانات.');
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="min-h-screen w-full flex flex-col lg:flex-row bg-slate-50 dark:bg-slate-950 font-sans" dir="rtl">

            {/* القسم الأيمن (الصورة والهوية) - يظهر فقط في الشاشات الكبيرة */}
            <div className="hidden lg:flex w-1/2 bg-slate-900 relative items-center justify-center overflow-hidden">
                {/* خلفية جمالية */}
                <div className="absolute inset-0 bg-[url('https://images.unsplash.com/photo-1497366216548-37526070297c?q=80&w=2301&auto=format&fit=crop')] bg-cover bg-center opacity-40 mix-blend-overlay"></div>
                <div className="absolute inset-0 bg-gradient-to-br from-slate-900 via-slate-900/90 to-blue-900/40 z-10"></div>

                {/* النص الترحيبي */}
                <div className="relative z-20 p-12 text-white max-w-lg">
                    <div className="mb-6 inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-white/10 backdrop-blur-sm border border-white/20">
                        <Building2 className="w-8 h-8 text-blue-400" />
                    </div>
                    <h1 className="text-5xl font-bold mb-6 leading-tight">
                        الذاكرة المؤسسية <span className="text-blue-400">الذكية</span>
                    </h1>
                    <p className="text-lg text-slate-300 leading-relaxed mb-8">
                        منصة مركزية تعتمد على الذكاء الاصطناعي لإدارة وفهم بيانات شركتك المتخصصة.
                        <br />
                        <span className="text-sm text-slate-400 mt-2 block">• هندسة • قانون • مالية • موارد بشرية</span>
                    </p>

                    {/* شريط احصائيات وهمي كديكور */}
                    <div className="flex gap-6 pt-6 border-t border-white/10">
                        <div>
                            <div className="text-2xl font-bold text-white">1M+</div>
                            <div className="text-xs text-slate-400">مستند مفهرس</div>
                        </div>
                        <div>
                            <div className="text-2xl font-bold text-white">99%</div>
                            <div className="text-xs text-slate-400">دقة التحليل</div>
                        </div>
                    </div>
                </div>
            </div>

            {/* القسم الأيسر (نموذج الدخول) */}
            <div className="flex-1 flex items-center justify-center p-6 lg:p-12">
                <Card className="w-full max-w-[400px] border-slate-200 dark:border-slate-800 shadow-xl">
                    <CardHeader className="text-center space-y-2 pb-6">
                        <div className="mx-auto w-12 h-12 bg-blue-600/10 rounded-full flex items-center justify-center mb-2 lg:hidden">
                            <Building2 className="w-6 h-6 text-blue-600" />
                        </div>
                        <CardTitle className="text-2xl font-bold text-slate-900 dark:text-white">تسجيل الدخول</CardTitle>
                        <CardDescription className="text-slate-500">أدخل بيانات الاعتماد للوصول لمساحة العمل</CardDescription>
                    </CardHeader>

                    <CardContent>
                        <form onSubmit={handleLogin} className="space-y-5">

                            <div className="space-y-2">
                                <Label htmlFor="email">البريد الإلكتروني المهني</Label>
                                <div className="relative">
                                    <Briefcase className="absolute right-3 top-3 h-4 w-4 text-slate-400" />
                                    <Input
                                        id="email"
                                        type="email"
                                        placeholder="name@company.com"
                                        className="pr-10 h-11 bg-slate-50 dark:bg-slate-900/50"
                                        value={email}
                                        onChange={(e) => setEmail(e.target.value)}
                                        required
                                    />
                                </div>
                            </div>

                            <div className="space-y-2">
                                <div className="flex items-center justify-between">
                                    <Label htmlFor="password">كلمة المرور</Label>
                                    <a href="#" className="text-xs text-blue-600 hover:text-blue-500">نسيت كلمة المرور؟</a>
                                </div>
                                <div className="relative">
                                    <Lock className="absolute right-3 top-3 h-4 w-4 text-slate-400" />
                                    <Input
                                        id="password"
                                        type="password"
                                        className="pr-10 h-11 bg-slate-50 dark:bg-slate-900/50"
                                        value={password}
                                        onChange={(e) => setPassword(e.target.value)}
                                        required
                                    />
                                </div>
                            </div>

                            {error && (
                                <div className="p-3 rounded-md bg-red-50 border border-red-200 text-red-600 text-sm flex items-center gap-2">
                                    <span className="block w-1.5 h-1.5 rounded-full bg-red-600" />
                                    {error}
                                </div>
                            )}

                            <Button type="submit" className="w-full h-11 bg-blue-600 hover:bg-blue-700 text-white font-medium text-base transition-all" disabled={isLoading}>
                                {isLoading ? (
                                    <div className="flex items-center gap-2">
                                        <Loader2 className="h-4 w-4 animate-spin" />
                                        جاري التحقق...
                                    </div>
                                ) : (
                                    "دخول آمن"
                                )}
                            </Button>
                        </form>
                    </CardContent>

                    <CardFooter className="flex justify-center border-t p-6">
                        <p className="text-xs text-slate-400 text-center">
                            محمي بنظام التشفير المؤسسي CorporateMemory™
                            <br />
                            جميع الحقوق محفوظة 2025
                        </p>
                    </CardFooter>
                </Card>
            </div>
        </div>
    );
}
