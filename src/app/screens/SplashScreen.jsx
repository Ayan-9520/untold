import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AppAuthContext';
import Logo from '../../components/brand/Logo';

export default function SplashScreen() {
  const navigate = useNavigate();
  const { isAuthenticated, loading } = useAuth();
  const [phase, setPhase] = useState(0);

  useEffect(() => {
    const t1 = setTimeout(() => setPhase(1), 300);
    const t2 = setTimeout(() => setPhase(2), 1200);
    return () => { clearTimeout(t1); clearTimeout(t2); };
  }, []);

  useEffect(() => {
    if (loading || phase < 2) return;
    const timer = setTimeout(() => {
      navigate(isAuthenticated ? '/app/home' : '/app/login', { replace: true });
    }, 800);
    return () => clearTimeout(timer);
  }, [loading, phase, isAuthenticated, navigate]);

  return (
    <div className="flex flex-col items-center justify-center min-h-dvh dark:bg-untold-dark light:bg-white overflow-hidden">
      <div className={`transition-all duration-700 ${phase >= 1 ? 'opacity-100 scale-100' : 'opacity-0 scale-90'}`}>
        <Logo variant="full" className="mx-auto max-w-[220px]" />
      </div>
      <div className={`mt-10 w-8 h-0.5 bg-untold-gold rounded-full transition-all duration-500 ${phase >= 2 ? 'w-20 opacity-100' : 'opacity-0'}`} />
    </div>
  );
}
