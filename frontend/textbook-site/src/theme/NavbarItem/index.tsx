/**
 * Custom NavbarItem to conditionally show login/dashboard based on auth state
 */

import React, { useEffect, useState } from 'react';

interface NavbarItemProps {
  className?: string;
  to?: string;
  href?: string;
  label?: string;
  [key: string]: any;
}

export default function NavbarItem(props: NavbarItemProps): JSX.Element | null {
  const { className, to, href, label, ...rest } = props;
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isMounted, setIsMounted] = useState(false);

  useEffect(() => {
    setIsMounted(true);
    const token = localStorage.getItem('access_token');
    setIsAuthenticated(!!token);

    // Listen for storage changes to update auth state
    const handleStorageChange = () => {
      const newToken = localStorage.getItem('access_token');
      setIsAuthenticated(!!newToken);
    };

    window.addEventListener('storage', handleStorageChange);
    return () => window.removeEventListener('storage', handleStorageChange);
  }, []);

  if (!isMounted) {
    return null;
  }

  // Hide login link if authenticated
  if (className?.includes('navbar-login-link') && isAuthenticated) {
    return null;
  }

  // Hide dashboard link if not authenticated
  if (className?.includes('navbar-dashboard-link') && !isAuthenticated) {
    return null;
  }

  const Element = to ? 'a' : 'a';
  const hrefUrl = to || href;

  return (
    <Element
      className={className}
      href={hrefUrl}
      {...rest}
    >
      {label}
    </Element>
  );
}
