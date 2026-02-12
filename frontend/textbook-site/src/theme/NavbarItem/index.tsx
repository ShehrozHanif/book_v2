/**
 * Custom NavbarItem to conditionally show login/profile based on auth state
 */

import React, { useEffect, useState, useRef } from 'react';
import { siteUrl } from '../../utils/paths';

interface NavbarItemProps {
  className?: string;
  to?: string;
  href?: string;
  label?: string;
  [key: string]: any;
}

function getInitial(username: string): string {
  return username.charAt(0).toUpperCase();
}

function getAvatarColor(username: string): string {
  const colors = ['#667eea', '#764ba2', '#4caf50', '#ff9800', '#e91e63', '#00bcd4'];
  let hash = 0;
  for (let i = 0; i < username.length; i++) {
    hash = username.charCodeAt(i) + ((hash << 5) - hash);
  }
  return colors[Math.abs(hash) % colors.length];
}

export default function NavbarItem(props: NavbarItemProps): JSX.Element | null {
  const { className, to, href, label, ...rest } = props;
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [username, setUsername] = useState<string | null>(null);
  const [isMounted, setIsMounted] = useState(false);
  const [dropdownOpen, setDropdownOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    setIsMounted(true);
    const token = localStorage.getItem('access_token');
    setIsAuthenticated(!!token);

    try {
      const savedUser = localStorage.getItem('user');
      if (savedUser && savedUser !== 'undefined') {
        const parsed = JSON.parse(savedUser);
        setUsername(parsed.username || null);
      }
    } catch {
      // ignore
    }

    const handleStorageChange = () => {
      const newToken = localStorage.getItem('access_token');
      setIsAuthenticated(!!newToken);
      try {
        const savedUser = localStorage.getItem('user');
        if (savedUser && savedUser !== 'undefined') {
          const parsed = JSON.parse(savedUser);
          setUsername(parsed.username || null);
        } else {
          setUsername(null);
        }
      } catch {
        setUsername(null);
      }
    };

    window.addEventListener('storage', handleStorageChange);

    // Close dropdown on outside click
    const handleClickOutside = (e: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(e.target as Node)) {
        setDropdownOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);

    return () => {
      window.removeEventListener('storage', handleStorageChange);
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, []);

  if (!isMounted) {
    return null;
  }

  // Replace login link with profile avatar + dropdown when authenticated
  if (className?.includes('navbar-login-link')) {
    if (isAuthenticated && username) {
      const initial = getInitial(username);
      const color = getAvatarColor(username);

      const handleLogout = () => {
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        localStorage.removeItem('user');
        window.location.href = siteUrl('/login');
      };

      return (
        <div ref={dropdownRef} style={{ position: 'relative' }}>
          <button
            onClick={() => setDropdownOpen(!dropdownOpen)}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '8px',
              background: 'none',
              border: 'none',
              cursor: 'pointer',
              padding: '4px 12px',
              borderRadius: '20px',
              color: 'inherit',
              transition: 'background 0.2s',
            }}
            title={`Logged in as ${username}`}
          >
            <span
              style={{
                display: 'inline-flex',
                alignItems: 'center',
                justifyContent: 'center',
                width: '32px',
                height: '32px',
                borderRadius: '50%',
                background: color,
                color: 'white',
                fontWeight: 700,
                fontSize: '14px',
                flexShrink: 0,
              }}
            >
              {initial}
            </span>
            <span
              style={{
                fontWeight: 600,
                fontSize: '14px',
                maxWidth: '120px',
                overflow: 'hidden',
                textOverflow: 'ellipsis',
                whiteSpace: 'nowrap',
              }}
            >
              {username}
            </span>
            <span style={{ fontSize: '10px', marginLeft: '2px' }}>
              {dropdownOpen ? '\u25B2' : '\u25BC'}
            </span>
          </button>

          {dropdownOpen && (
            <div
              style={{
                position: 'absolute',
                top: '100%',
                right: 0,
                marginTop: '8px',
                background: 'white',
                borderRadius: '8px',
                boxShadow: '0 4px 20px rgba(0,0,0,0.15)',
                minWidth: '180px',
                zIndex: 1000,
                overflow: 'hidden',
                border: '1px solid #e0e0e0',
              }}
            >
              <a
                href={siteUrl('/dashboard')}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '10px',
                  padding: '12px 16px',
                  color: '#333',
                  textDecoration: 'none',
                  fontSize: '14px',
                  fontWeight: 500,
                  transition: 'background 0.15s',
                  borderBottom: '1px solid #f0f0f0',
                }}
                onMouseEnter={(e) => (e.currentTarget.style.background = '#f5f7ff')}
                onMouseLeave={(e) => (e.currentTarget.style.background = 'transparent')}
              >
                <span style={{ fontSize: '16px' }}>📊</span>
                Dashboard
              </a>
              <button
                onClick={handleLogout}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '10px',
                  padding: '12px 16px',
                  width: '100%',
                  background: 'none',
                  border: 'none',
                  color: '#c33',
                  fontSize: '14px',
                  fontWeight: 600,
                  cursor: 'pointer',
                  transition: 'background 0.15s',
                  textAlign: 'left',
                }}
                onMouseEnter={(e) => (e.currentTarget.style.background = '#fee')}
                onMouseLeave={(e) => (e.currentTarget.style.background = 'transparent')}
              >
                <span style={{ fontSize: '16px' }}>🚪</span>
                Logout
              </button>
            </div>
          )}
        </div>
      );
    }

    // Not authenticated - show login link
    return (
      <a className={className} href={to || href} {...rest}>
        {label}
      </a>
    );
  }

  // Hide dashboard link if not authenticated
  if (className?.includes('navbar-dashboard-link') && !isAuthenticated) {
    return null;
  }

  const hrefUrl = to || href;

  return (
    <a
      className={className}
      href={hrefUrl}
      {...rest}
    >
      {label}
    </a>
  );
}
