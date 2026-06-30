import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { Navigate, useLocation } from 'react-router-dom';
import { useAuth } from './AuthProvider';
import GoogleLoginButton from './GoogleLoginButton';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';

const schema = z.object({
  email: z.string().email('Enter a valid email'),
  password: z.string().min(8, 'Password must be at least 8 characters'),
});

type FormValues = z.infer<typeof schema>;

export default function LoginPage() {
  const { login, isAuthenticated, loading } = useAuth();
  const location = useLocation();
  const [apiError, setApiError] = useState<string | null>(null);

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<FormValues>({
    resolver: zodResolver(schema),
    defaultValues: { email: 'admin@untold.com', password: 'ChangeMe123!' },
  });

  if (!loading && isAuthenticated) {
    const from = (location.state as { from?: { pathname: string } })?.from?.pathname || '/';
    return <Navigate to={from} replace />;
  }

  const onSubmit = async (data: FormValues) => {
    setApiError(null);
    try {
      await login(data);
    } catch {
      setApiError('Invalid credentials or no Studio access.');
    }
  };

  return (
    <div className="min-h-screen flex bg-studio-black">
      <div className="hidden lg:flex flex-1 flex-col justify-center px-16 border-r border-studio-border bg-gradient-to-br from-studio-surface to-studio-black">
        <p className="text-studio-gold text-xs font-bold tracking-[0.4em] uppercase">UNTOLD</p>
        <h1 className="text-5xl font-bold text-white mt-3 tracking-tight">Studio</h1>
        <p className="text-lg text-studio-muted mt-4 max-w-md leading-relaxed">
          Production operating system for researchers, writers, editors, and publishers.
        </p>
        <p className="text-xs text-studio-muted/80 mt-8 uppercase tracking-widest">Internal · Not public OTT</p>
      </div>

      <div className="flex-1 flex items-center justify-center p-8">
        <div className="w-full max-w-md studio-glass rounded-2xl p-8">
          <h2 className="text-xl font-bold text-white">Sign in</h2>
          <p className="text-sm text-studio-muted mt-1 mb-6">Team credentials or Google</p>

          <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
            <div>
              <label className="text-xs font-medium text-studio-muted mb-1.5 block">Email</label>
              <Input type="email" autoComplete="email" {...register('email')} />
              {errors.email && <p className="text-xs text-red-400 mt-1">{errors.email.message}</p>}
            </div>
            <div>
              <label className="text-xs font-medium text-studio-muted mb-1.5 block">Password</label>
              <Input type="password" autoComplete="current-password" {...register('password')} />
              {errors.password && <p className="text-xs text-red-400 mt-1">{errors.password.message}</p>}
            </div>
            {apiError && <p className="text-sm text-red-400">{apiError}</p>}
            <Button type="submit" variant="gold" className="w-full" disabled={isSubmitting}>
              {isSubmitting ? 'Signing in…' : 'Sign In'}
            </Button>
          </form>

          <div className="relative my-6">
            <div className="absolute inset-0 flex items-center">
              <div className="w-full border-t border-studio-border" />
            </div>
            <div className="relative flex justify-center text-xs">
              <span className="bg-studio-card px-2 text-studio-muted">or</span>
            </div>
          </div>

          <GoogleLoginButton />
        </div>
      </div>
    </div>
  );
}
