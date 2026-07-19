'use client';
/* ============================================================
   CrimeLens AI — Top Navigation Bar
   Search, notifications, and user actions.
   ============================================================ */

import React from 'react';
import { Search, Bell, Settings } from 'lucide-react';
import { useAuth } from '@/lib/auth';
import { getInitials } from '@/lib/utils';

export default function Topbar() {
  const { user } = useAuth();

  return (
    <header className="topbar">
      <div className="topbar-search">
        <Search size={16} style={{ color: 'var(--text-muted)' }} />
        <input type="text" placeholder="Search cases, evidence, entities..." />
      </div>

      <div className="topbar-actions">
        <button className="topbar-icon-btn" title="Notifications">
          <Bell size={20} />
        </button>
        {user && (
          <div className="user-avatar" title={user.full_name}>
            {getInitials(user.full_name)}
          </div>
        )}
      </div>
    </header>
  );
}
