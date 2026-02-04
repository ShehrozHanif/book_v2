/**
 * User preferences form component
 */

import React, { useState } from "react";
import styles from "./PreferencesForm.module.css";
import { User, UserPreferences } from "../../types/personalization";
import { useAuth } from "../../hooks/useAuth";

interface PreferencesFormProps {
  user: User;
}

const PreferencesForm: React.FC<PreferencesFormProps> = ({ user }) => {
  const { updatePreferences } = useAuth();
  const [preferences, setPreferences] = useState<UserPreferences>(user.preferences);
  const [isLoading, setIsLoading] = useState(false);
  const [message, setMessage] = useState<{ type: "success" | "error"; text: string } | null>(
    null
  );

  const handleChange = (field: keyof UserPreferences, value: string) => {
    setPreferences((prev) => ({
      ...prev,
      [field]: value,
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setMessage(null);

    try {
      await updatePreferences(preferences);
      setMessage({
        type: "success",
        text: "Preferences updated successfully!",
      });
    } catch (error) {
      const errorText = error instanceof Error ? error.message : "Failed to update preferences";
      setMessage({
        type: "error",
        text: errorText,
      });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className={styles.container}>
      <h2 className={styles.title}>⚙️ Learning Preferences</h2>

      <form onSubmit={handleSubmit} className={styles.form}>
        <div className={styles.section}>
          <h3 className={styles.sectionTitle}>Explanation Style</h3>
          <p className={styles.sectionDescription}>How do you prefer to learn?</p>

          <div className={styles.options}>
            {[
              {
                value: "theory_first",
                label: "Theory First",
                description: "Start with concepts, then show examples",
                icon: "📚",
              },
              {
                value: "example_first",
                label: "Example First",
                description: "Show practical examples, then explain theory",
                icon: "💡",
              },
            ].map((option) => (
              <label key={option.value} className={styles.radioOption}>
                <input
                  type="radio"
                  name="explanation_style"
                  value={option.value}
                  checked={preferences.explanation_style === option.value}
                  onChange={(e) =>
                    handleChange("explanation_style", e.target.value as any)
                  }
                  className={styles.radioInput}
                />
                <div className={styles.optionContent}>
                  <span className={styles.optionIcon}>{option.icon}</span>
                  <div className={styles.optionText}>
                    <span className={styles.optionLabel}>{option.label}</span>
                    <span className={styles.optionDescription}>{option.description}</span>
                  </div>
                </div>
              </label>
            ))}
          </div>
        </div>

        <div className={styles.section}>
          <h3 className={styles.sectionTitle}>Programming Language</h3>
          <p className={styles.sectionDescription}>Which language do you prefer?</p>

          <div className={styles.options}>
            {[
              { value: "python", label: "Python", icon: "🐍" },
              { value: "cpp", label: "C++", icon: "⚡" },
              { value: "both", label: "Both", icon: "🔄" },
            ].map((option) => (
              <label key={option.value} className={styles.radioOption}>
                <input
                  type="radio"
                  name="code_language"
                  value={option.value}
                  checked={preferences.code_language === option.value}
                  onChange={(e) => handleChange("code_language", e.target.value as any)}
                  className={styles.radioInput}
                />
                <div className={styles.optionContent}>
                  <span className={styles.optionIcon}>{option.icon}</span>
                  <span className={styles.optionLabel}>{option.label}</span>
                </div>
              </label>
            ))}
          </div>
        </div>

        <div className={styles.section}>
          <h3 className={styles.sectionTitle}>Learning Pace</h3>
          <p className={styles.sectionDescription}>How fast do you like to learn?</p>

          <div className={styles.options}>
            {[
              {
                value: "slow",
                label: "Slow",
                description: "In-depth coverage with extra examples",
                icon: "🐢",
              },
              {
                value: "medium",
                label: "Medium",
                description: "Balanced approach with essential details",
                icon: "⚖️",
              },
              {
                value: "fast",
                label: "Fast",
                description: "Quick explanations, focus on key concepts",
                icon: "🚀",
              },
            ].map((option) => (
              <label key={option.value} className={styles.radioOption}>
                <input
                  type="radio"
                  name="learning_pace"
                  value={option.value}
                  checked={preferences.learning_pace === option.value}
                  onChange={(e) => handleChange("learning_pace", e.target.value as any)}
                  className={styles.radioInput}
                />
                <div className={styles.optionContent}>
                  <span className={styles.optionIcon}>{option.icon}</span>
                  <div className={styles.optionText}>
                    <span className={styles.optionLabel}>{option.label}</span>
                    <span className={styles.optionDescription}>{option.description}</span>
                  </div>
                </div>
              </label>
            ))}
          </div>
        </div>

        <div className={styles.section}>
          <h3 className={styles.sectionTitle}>Content Focus</h3>
          <p className={styles.sectionDescription}>What's your main interest?</p>

          <div className={styles.options}>
            {[
              { value: "simulation", label: "Simulation & Modeling", icon: "🖥️" },
              { value: "hardware", label: "Hardware & Robotics", icon: "🤖" },
              { value: "balanced", label: "Balanced", icon: "⚙️" },
            ].map((option) => (
              <label key={option.value} className={styles.radioOption}>
                <input
                  type="radio"
                  name="content_focus"
                  value={option.value}
                  checked={preferences.content_focus === option.value}
                  onChange={(e) => handleChange("content_focus", e.target.value as any)}
                  className={styles.radioInput}
                />
                <div className={styles.optionContent}>
                  <span className={styles.optionIcon}>{option.icon}</span>
                  <span className={styles.optionLabel}>{option.label}</span>
                </div>
              </label>
            ))}
          </div>
        </div>

        {message && (
          <div className={`${styles.message} ${styles[message.type]}`}>
            {message.type === "success" ? "✅" : "❌"} {message.text}
          </div>
        )}

        <div className={styles.buttonGroup}>
          <button type="submit" className={styles.submitButton} disabled={isLoading}>
            {isLoading ? "Saving..." : "Save Preferences"}
          </button>
        </div>
      </form>
    </div>
  );
};

export default PreferencesForm;
