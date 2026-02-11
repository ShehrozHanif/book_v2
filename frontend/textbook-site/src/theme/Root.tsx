import React, { Suspense, useEffect } from 'react';
import { PersonalizationProvider } from '../components/PersonalizationProvider';
import SidebarProgressInjector from '../components/SidebarProgressInjector';
import PracticeWidgetInjector from '../components/PracticeWidgetInjector';
import PersonalizationButtonInjector from '../components/PersonalizationButtonInjector';

interface RootProps {
  children: React.ReactNode;
}

// Lazy load ChatBot component
const ChatBot = React.lazy(() =>
  import('../components/ChatBot')
    .then(mod => ({ default: mod.ChatBot }))
    .catch(err => {
      console.error('ChatBot loading error:', err);
      return { default: () => null };
    })
);

/**
 * Custom Docusaurus Root component that wraps the app with PersonalizationProvider
 * and injects the ChatBot on every page
 */
export default function Root({ children }: RootProps): JSX.Element {
  useEffect(() => {
    // Update body attribute for auth state to control navbar visibility
    const token = localStorage.getItem('access_token');
    const isAuthenticated = !!token;
    document.body.setAttribute('data-auth', isAuthenticated ? 'true' : 'false');

    // Listen for auth changes
    const handleStorageChange = () => {
      const newToken = localStorage.getItem('access_token');
      const newIsAuth = !!newToken;
      document.body.setAttribute('data-auth', newIsAuth ? 'true' : 'false');
    };

    window.addEventListener('storage', handleStorageChange);
    return () => window.removeEventListener('storage', handleStorageChange);
  }, []);

  return (
    <PersonalizationProvider>
      <SidebarProgressInjector />
      <PersonalizationButtonInjector />
      <PracticeWidgetInjector />
      {children}
      <Suspense fallback={null}>
        <ChatBot />
      </Suspense>
    </PersonalizationProvider>
  );
}
