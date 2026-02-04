/**
 * Dashboard header component with navigation
 */

import React, { useState } from "react";
import styles from "./Header.module.css";
import { useAuth } from "../../hooks/useAuth";

interface HeaderProps {
  userName: string;
}

const Header: React.FC<HeaderProps> = ({ userName }) => {
  const { logout } = useAuth();
  const [showMenu, setShowMenu] = useState(false);

  const handleLogout = () => {
    logout();
    window.location.href = "/";
  };

  return (
    <header className={styles.header}>
      <div className={styles.container}>
        <div className={styles.logo}>
          <span className={styles.logoIcon}>🤖</span>
          <h1 className={styles.logoText}>Humanoid Robotics</h1>
        </div>

        <div className={styles.userMenu}>
          <span className={styles.userName}>Welcome, {userName}! 👋</span>
          <div className={styles.menuContainer}>
            <button
              className={styles.menuButton}
              onClick={() => setShowMenu(!showMenu)}
              aria-label="Open menu"
            >
              ≡
            </button>
            {showMenu && (
              <div className={styles.dropdown}>
                <button className={styles.dropdownItem} onClick={() => setShowMenu(false)}>
                  📊 Dashboard
                </button>
                <button className={styles.dropdownItem} onClick={() => setShowMenu(false)}>
                  💬 Chatbot
                </button>
                <button className={styles.dropdownItem} onClick={() => setShowMenu(false)}>
                  ⚙️ Settings
                </button>
                <hr className={styles.divider} />
                <button className={styles.dropdownItem} onClick={handleLogout}>
                  🚪 Logout
                </button>
              </div>
            )}
          </div>
        </div>
      </div>
    </header>
  );
};

export default Header;
