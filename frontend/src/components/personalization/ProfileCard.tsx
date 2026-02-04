/**
 * User profile card component
 */

import React from "react";
import styles from "./ProfileCard.module.css";
import { User } from "../../types/personalization";

interface ProfileCardProps {
  user: User;
}

const ProfileCard: React.FC<ProfileCardProps> = ({ user }) => {
  const getSkillLevelLabel = (level: number): string => {
    if (level < 30) return "Beginner";
    if (level < 70) return "Intermediate";
    return "Advanced";
  };

  const getSkillLevelColor = (level: number): string => {
    if (level < 30) return "#4CAF50";
    if (level < 70) return "#FF9800";
    return "#2196F3";
  };

  return (
    <div className={styles.card}>
      <div className={styles.header}>
        <div className={styles.avatarContainer}>
          {user.profile_picture_url ? (
            <img src={user.profile_picture_url} alt={user.username} className={styles.avatar} />
          ) : (
            <div className={styles.avatarPlaceholder}>
              {user.username.charAt(0).toUpperCase()}
            </div>
          )}
        </div>
        <div className={styles.userInfo}>
          <h2 className={styles.username}>{user.username}</h2>
          <p className={styles.email}>{user.email}</p>
        </div>
      </div>

      <div className={styles.skillSection}>
        <div className={styles.skillLabel}>
          <span>Skill Level</span>
          <span className={styles.skillName}>{getSkillLevelLabel(user.skill_level)}</span>
        </div>
        <div className={styles.skillBar}>
          <div
            className={styles.skillFill}
            style={{
              width: `${user.skill_level}%`,
              backgroundColor: getSkillLevelColor(user.skill_level),
            }}
          />
        </div>
        <span className={styles.skillScore}>{user.skill_level}/100</span>
      </div>

      {user.bio && (
        <div className={styles.bio}>
          <p>{user.bio}</p>
        </div>
      )}

      <div className={styles.stats}>
        <div className={styles.stat}>
          <span className={styles.statLabel}>Member Since</span>
          <span className={styles.statValue}>
            {new Date(user.created_at).toLocaleDateString()}
          </span>
        </div>
        {user.last_login_at && (
          <div className={styles.stat}>
            <span className={styles.statLabel}>Last Active</span>
            <span className={styles.statValue}>
              {new Date(user.last_login_at).toLocaleDateString()}
            </span>
          </div>
        )}
      </div>
    </div>
  );
};

export default ProfileCard;
