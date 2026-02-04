/**
 * Learning paths recommendation card
 */

import React from "react";
import styles from "./LearningPathsCard.module.css";

interface LearningPathsCardProps {
  skillLevel: number;
}

const paths = [
  {
    name: "Beginner",
    description: "Perfect for newcomers to robotics",
    emoji: "🚀",
    minSkill: 0,
    maxSkill: 30,
  },
  {
    name: "Intermediate",
    description: "For those with basic robotics knowledge",
    emoji: "⚙️",
    minSkill: 31,
    maxSkill: 70,
  },
  {
    name: "Advanced",
    description: "For robotics enthusiasts and professionals",
    emoji: "🧠",
    minSkill: 71,
    maxSkill: 100,
  },
];

const LearningPathsCard: React.FC<LearningPathsCardProps> = ({ skillLevel }) => {
  const recommendedPath = paths.find(
    (p) => skillLevel >= p.minSkill && skillLevel <= p.maxSkill
  ) || paths[1];

  return (
    <div className={styles.card}>
      <h3 className={styles.title}>🛣️ Learning Path</h3>

      <div className={styles.recommendedPath}>
        <span className={styles.emoji}>{recommendedPath.emoji}</span>
        <div className={styles.pathInfo}>
          <h4 className={styles.pathName}>{recommendedPath.name}</h4>
          <p className={styles.pathDescription}>{recommendedPath.description}</p>
        </div>
      </div>

      <div className={styles.pathList}>
        <p className={styles.otherPathsLabel}>Other Paths</p>
        {paths
          .filter((p) => p.name !== recommendedPath.name)
          .map((path) => (
            <button key={path.name} className={styles.pathButton}>
              <span className={styles.pathEmoji}>{path.emoji}</span>
              <div className={styles.pathButtonInfo}>
                <span className={styles.pathButtonName}>{path.name}</span>
                <span className={styles.pathButtonDesc}>{path.description}</span>
              </div>
            </button>
          ))}
      </div>

      <div className={styles.nextChapter}>
        <h4>Next Steps</h4>
        <p>Complete chapter assessments to progress and unlock new content!</p>
      </div>
    </div>
  );
};

export default LearningPathsCard;
