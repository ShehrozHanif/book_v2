/**
 * PersonalizationButton - Interactive button for chapter personalization
 * Shows login prompt for unauthenticated users, modal for authenticated users
 */

import React, { useState } from 'react';
import { usePersonalization } from './PersonalizationProvider';
import { siteUrl } from '../utils/paths';
import styles from './PersonalizationButton.module.css';

interface PersonalizationButtonProps {
  chapterId: number;
}

const PersonalizationButton: React.FC<PersonalizationButtonProps> = ({ chapterId }) => {
  const { user, isAuthenticated, isLoading } = usePersonalization();
  const [isModalOpen, setIsModalOpen] = useState(false);

  if (isLoading) {
    return null;
  }

  const handleButtonClick = () => {
    if (isAuthenticated) {
      setIsModalOpen(true);
    }
  };

  const handleOpenQuiz = () => {
    window.open(siteUrl(`/chapter-quiz?chapter=${chapterId}`), '_blank', 'noopener,noreferrer');
    setIsModalOpen(false);
  };

  const handleCloseModal = () => {
    setIsModalOpen(false);
  };

  // Overlay click handler - close modal when clicking outside
  const handleOverlayClick = (e: React.MouseEvent<HTMLDivElement>) => {
    if (e.target === e.currentTarget) {
      setIsModalOpen(false);
    }
  };

  if (!isAuthenticated) {
    // Show login link for unauthenticated users
    const currentPath = typeof window !== 'undefined' ? window.location.pathname : '';
    const loginUrl = siteUrl(`/login?redirect=${encodeURIComponent(currentPath)}`);

    return (
      <div className={styles.buttonContainer}>
        <a href={loginUrl} className={styles.loginLink}>
          <span className={styles.buttonIcon}>🎯</span>
          <span className={styles.buttonText}>Personalize Your Learning</span>
          <span className={styles.buttonArrow}>→</span>
        </a>
      </div>
    );
  }

  // Show button and modal for authenticated users
  return (
    <>
      <div className={styles.buttonContainer}>
        <button
          className={styles.button}
          onClick={handleButtonClick}
          type="button"
        >
          <span className={styles.buttonIcon}>🎯</span>
          <span className={styles.buttonText}>Personalize Your Learning</span>
          <span className={styles.buttonArrow}>→</span>
        </button>
      </div>

      {/* Modal */}
      {isModalOpen && (
        <div className={styles.modalOverlay} onClick={handleOverlayClick}>
          <div className={styles.modalContent}>
            <div className={styles.modalIcon}>✨</div>
            <h2 className={styles.modalTitle}>Personalization Active!</h2>
            <p className={styles.modalText}>
              A quiz is available at the end of this chapter to track your progress and unlock achievements.
              Your results are saved to your profile.
            </p>
            <div className={styles.modalActions}>
              <button
                className={styles.modalPrimary}
                onClick={handleOpenQuiz}
                type="button"
              >
                Open Quiz
              </button>
              <button
                className={styles.modalSecondary}
                onClick={handleCloseModal}
                type="button"
              >
                Got it!
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
};

export default PersonalizationButton;
