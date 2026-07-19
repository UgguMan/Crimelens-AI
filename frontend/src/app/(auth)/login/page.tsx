'use client';
/* ============================================================
   CrimeLens AI — Login Page
   Premium auth page with glass card and animated background.
   ============================================================ */

import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { motion } from 'framer-motion';
import { Crosshair, Mail, Lock, ArrowRight } from 'lucide-react';
import { AuthProvider, useAuth } from '@/lib/auth';

function LoginForm() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const { login, loginWithGoogle } = useAuth();
  const router = useRouter();

  const hasGoogleClientId = !!process.env.NEXT_PUBLIC_GOOGLE_CLIENT_ID;

  // Load Google Identity Services SDK dynamically
  useEffect(() => {
    if (!hasGoogleClientId) return;

    const script = document.createElement('script');
    script.src = 'https://accounts.google.com/gsi/client';
    script.async = true;
    script.defer = true;
    document.body.appendChild(script);

    script.onload = () => {
      if ((window as any).google) {
        (window as any).google.accounts.id.initialize({
          client_id: process.env.NEXT_PUBLIC_GOOGLE_CLIENT_ID || '', 
          callback: handleGoogleResponse,
        });
        (window as any).google.accounts.id.renderButton(
          document.getElementById('google-signin-btn'),
          { theme: 'filled_black', size: 'large', width: 316 }
        );
      }
    };

    return () => {
      try {
        document.body.removeChild(script);
      } catch (e) {}
    };
  }, [hasGoogleClientId]);

  const handleGoogleResponse = async (response: any) => {
    setError('');
    setLoading(true);
    try {
      await loginWithGoogle(response.credential);
      router.push('/dashboard');
    } catch (err: any) {
      setError(err.message || 'Google sign-in failed.');
    } finally {
      setLoading(false);
    }
  };

  const handleMockGoogleLogin = async () => {
    setError('');
    setLoading(true);
    try {
      await loginWithGoogle('mock_google_token');
      router.push('/dashboard');
    } catch (err: any) {
      setError(err.message || 'Google sign-in failed.');
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      await login(email, password);
      router.push('/dashboard');
    } catch (err: any) {
      setError(err.message || 'Login failed. Please check your credentials.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-page">
      <motion.div
        className="auth-card glass-card"
        initial={{ opacity: 0, y: 30 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, ease: 'easeOut' }}
      >
        {/* Logo */}
        <motion.div
          style={{ display: 'flex', justifyContent: 'center', marginBottom: 'var(--space-6)' }}
          initial={{ scale: 0 }}
          animate={{ scale: 1 }}
          transition={{ delay: 0.2, type: 'spring', stiffness: 200 }}
        >
          <div className="sidebar-logo-icon" style={{ width: 56, height: 56, fontSize: 28 }}>
            <Crosshair size={28} color="#06080f" />
          </div>
        </motion.div>

        <h1 className="auth-title">Welcome Back</h1>
        <p className="auth-subtitle">Sign in to CID platform</p>

        {error && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            style={{
              background: 'var(--color-danger-bg)',
              border: '1px solid rgba(239,68,68,0.3)',
              borderRadius: 'var(--border-radius-md)',
              padding: 'var(--space-3) var(--space-4)',
              color: 'var(--color-danger)',
              fontSize: 'var(--font-size-sm)',
              marginBottom: 'var(--space-4)',
            }}
          >
            {error}
          </motion.div>
        )}

        <form onSubmit={handleSubmit} className="auth-form">
          <div className="input-group">
            <label>Email Address</label>
            <div style={{ position: 'relative' }}>
              <Mail size={16} style={{
                position: 'absolute', left: 12, top: '50%',
                transform: 'translateY(-50%)', color: 'var(--text-muted)',
              }} />
              <input
                type="email"
                className="input"
                placeholder="investigator@crimelens.ai"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                style={{ paddingLeft: 40 }}
              />
            </div>
          </div>

          <div className="input-group">
            <label>Password</label>
            <div style={{ position: 'relative' }}>
              <Lock size={16} style={{
                position: 'absolute', left: 12, top: '50%',
                transform: 'translateY(-50%)', color: 'var(--text-muted)',
              }} />
              <input
                type="password"
                className="input"
                placeholder="Enter your password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                style={{ paddingLeft: 40 }}
              />
            </div>
          </div>

          <button
            type="submit"
            className="btn btn-primary btn-lg"
            disabled={loading}
            style={{ width: '100%', marginTop: 'var(--space-2)' }}
          >
            {loading ? (
              <div style={{
                width: 20, height: 20,
                border: '2px solid rgba(6,8,15,0.3)',
                borderTopColor: '#06080f',
                borderRadius: '50%',
                animation: 'spin 1s linear infinite',
              }} />
            ) : (
              <>Sign In <ArrowRight size={18} /></>
            )}
          </button>
        </form>

        <div style={{
          display: 'flex', alignItems: 'center', justifyContent: 'center',
          gap: 'var(--space-3)', margin: 'var(--space-4) 0',
          fontSize: 'var(--font-size-xs)', color: 'var(--text-secondary)'
        }}>
          <div style={{ flex: 1, height: '1px', background: 'var(--border-default)' }} />
          <span>OR</span>
          <div style={{ flex: 1, height: '1px', background: 'var(--border-default)' }} />
        </div>

        {hasGoogleClientId ? (
          <div id="google-signin-btn" style={{ display: 'flex', justifyContent: 'center', minHeight: '40px' }} />
        ) : (
          <button
            type="button"
            onClick={handleMockGoogleLogin}
            className="btn btn-secondary"
            style={{
              width: '100%',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              gap: '12px',
              backgroundColor: '#09090b',
              border: '1px solid #27272a',
              color: '#ffffff',
              fontSize: '14px',
              fontWeight: 500,
              padding: '10px 16px',
              borderRadius: '6px',
              transition: 'background-color 0.2s, border-color 0.2s',
              cursor: 'pointer'
            }}
          >
            <svg viewBox="0 0 24 24" width="18" height="18" xmlns="http://www.w3.org/2000/svg">
              <path d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" fill="#4285F4"/>
              <path d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" fill="#34A853"/>
              <path d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.06H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.94l2.85-2.22.81-.63z" fill="#FBBC05"/>
              <path d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.06l3.66 2.84c.87-2.6 3.3-4.52 6.16-4.52z" fill="#EA4335"/>
            </svg>
            Sign in with Google
          </button>
        )}

        <div className="auth-footer">
          Don&apos;t have an account?{' '}
          <Link href="/register" style={{ color: 'var(--accent-primary)', fontWeight: 600 }}>
            Create Account
          </Link>
        </div>
      </motion.div>
    </div>
  );
}

export default function LoginPage() {
  return (
    <AuthProvider>
      <LoginForm />
    </AuthProvider>
  );
}
