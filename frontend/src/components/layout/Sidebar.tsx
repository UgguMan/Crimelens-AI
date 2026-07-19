'use client';
/* ============================================================
   CrimeLens AI — Sidebar Navigation
   Collapsible sidebar with gradient accents and cyber aesthetics.
   ============================================================ */

import React from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import {
  LayoutDashboard, FolderOpen, BarChart3, Activity,
  Shield, Users, LogOut, Crosshair,
} from 'lucide-react';
import { useAuth } from '@/lib/auth';
import { getInitials } from '@/lib/utils';

const navItems = [
  { label: 'Dashboard', href: '/dashboard', icon: LayoutDashboard },
  { label: 'Cases', href: '/cases', icon: FolderOpen },
  { label: 'Analytics', href: '/analytics', icon: BarChart3 },
  { label: 'Activity', href: '/activity', icon: Activity },
];

const adminItems = [
  { label: 'Admin', href: '/admin', icon: Shield },
];

export default function Sidebar() {
  const pathname = usePathname();
  const { user, logout } = useAuth();

  const isActive = (href: string) => {
    if (href === '/dashboard') return pathname === '/dashboard';
    return pathname.startsWith(href);
  };

  return (
    <aside className="sidebar">
      {/* Logo */}
      <div className="sidebar-logo">
        <div className="sidebar-logo-icon">
          <Crosshair size={22} color="#06080f" />
        </div>
        <div>
          <div className="sidebar-logo-text">CID</div>
          <div style={{ fontSize: 'var(--font-size-xs)', color: 'var(--text-muted)', fontWeight: 500 }}>
            Forensic Unit
          </div>
        </div>
      </div>

      {/* Navigation */}
      <nav className="sidebar-nav">
        <div className="sidebar-section-label">Main Menu</div>
        {navItems.map((item) => (
          <Link
            key={item.href}
            href={item.href}
            className={`nav-link ${isActive(item.href) ? 'active' : ''}`}
          >
            <item.icon size={20} />
            <span>{item.label}</span>
          </Link>
        ))}

        {user?.role === 'admin' && (
          <>
            <div className="sidebar-section-label" style={{ marginTop: 'var(--space-4)' }}>
              Administration
            </div>
            {adminItems.map((item) => (
              <Link
                key={item.href}
                href={item.href}
                className={`nav-link ${isActive(item.href) ? 'active' : ''}`}
              >
                <item.icon size={20} />
                <span>{item.label}</span>
              </Link>
            ))}
          </>
        )}
      </nav>

      {/* User Section */}
      {user && (
        <div style={{
          padding: 'var(--space-4)',
          borderTop: '1px solid var(--border-default)',
          display: 'flex',
          alignItems: 'center',
          gap: 'var(--space-3)',
        }}>
          <div className="user-avatar">{getInitials(user.full_name)}</div>
          <div style={{ flex: 1, minWidth: 0 }}>
            <div style={{
              fontSize: 'var(--font-size-sm)',
              fontWeight: 600,
              color: 'var(--text-primary)',
              whiteSpace: 'nowrap',
              overflow: 'hidden',
              textOverflow: 'ellipsis',
            }}>
              {user.full_name}
            </div>
            <div style={{
              fontSize: 'var(--font-size-xs)',
              color: 'var(--text-muted)',
              textTransform: 'capitalize',
            }}>
              {user.role}
            </div>
          </div>
          <button
            onClick={logout}
            className="topbar-icon-btn"
            title="Logout"
            style={{ flexShrink: 0 }}
          >
            <LogOut size={18} />
          </button>
        </div>
      )}
    </aside>
  );
}
