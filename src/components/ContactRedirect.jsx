import { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';

export default function ContactRedirect() {
  const navigate = useNavigate();

  useEffect(() => {
    navigate('/', { replace: true });
    requestAnimationFrame(() => {
      document.getElementById('contact')?.scrollIntoView({ behavior: 'smooth' });
    });
  }, [navigate]);

  return null;
}
