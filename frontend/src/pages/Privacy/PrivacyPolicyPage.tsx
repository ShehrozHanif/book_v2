/**
 * Privacy Policy page
 */

import React, { useState, useEffect } from "react";
import styles from "./PrivacyPage.module.css";
import { personalizationApi } from "../../services/personalizationApi";
import Header from "../../components/personalization/Header";
import LoadingIndicator from "../../components/LoadingIndicator";

interface PrivacyPolicy {
  title: string;
  last_updated: string;
  content: string;
}

const PrivacyPolicyPage: React.FC = () => {
  const [policy, setPolicy] = useState<PrivacyPolicy | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const loadPolicy = async () => {
      setIsLoading(true);
      setError(null);

      try {
        // Since we're not passing user_id to the endpoint, we'll use a dummy UUID
        // In a real scenario, the endpoint wouldn't require user_id
        const dummyUserId = "00000000-0000-0000-0000-000000000000";
        const data = await personalizationApi.getPrivacyPolicy(dummyUserId);
        setPolicy(data);
      } catch (err) {
        const message = err instanceof Error ? err.message : "Failed to load privacy policy";
        setError(message);
        console.error("Error loading privacy policy:", err);
      } finally {
        setIsLoading(false);
      }
    };

    loadPolicy();
  }, []);

  return (
    <div className={styles.pageContainer}>
      <Header userName="Guest" />

      <div className={styles.contentWrapper}>
        <div className={styles.documentHeader}>
          <h1>Privacy Policy</h1>
          {policy && <p className={styles.lastUpdated}>Last updated: {policy.last_updated}</p>}
        </div>

        {isLoading && <LoadingIndicator />}

        {error && (
          <div className={styles.errorContainer}>
            <p className={styles.error}>Error loading privacy policy: {error}</p>
          </div>
        )}

        {policy && !isLoading && (
          <div className={styles.documentContent}>
            <div className={styles.policyText}>
              {policy.content.split("\n").map((line, index) => {
                if (line.trim() === "") {
                  return <div key={index} className={styles.spacer} />;
                }

                // Check if it's a heading (starts with number and period)
                if (/^\d+\./.test(line.trim())) {
                  return (
                    <h2 key={index} className={styles.sectionHeading}>
                      {line.trim()}
                    </h2>
                  );
                }

                // Check if it's a bullet point
                if (line.trim().startsWith("-")) {
                  return (
                    <li key={index} className={styles.bulletPoint}>
                      {line.trim().substring(1).trim()}
                    </li>
                  );
                }

                // Regular paragraph
                return (
                  <p key={index} className={styles.paragraph}>
                    {line}
                  </p>
                );
              })}
            </div>

            <div className={styles.sideInfo}>
              <div className={styles.infoBox}>
                <h3>Your Rights</h3>
                <ul>
                  <li>Access your personal data</li>
                  <li>Export your data</li>
                  <li>Delete your account</li>
                  <li>Update your information</li>
                  <li>Withdraw consent</li>
                </ul>
              </div>

              <div className={styles.infoBox}>
                <h3>Contact</h3>
                <p>For privacy inquiries:</p>
                <a href="mailto:privacy@roboticslearning.edu">
                  privacy@roboticslearning.edu
                </a>
              </div>

              <div className={styles.infoBox}>
                <h3>GDPR Compliance</h3>
                <p>This service complies with GDPR regulations including:</p>
                <ul>
                  <li>Data access rights</li>
                  <li>Data portability</li>
                  <li>Right to be forgotten</li>
                  <li>Transparent processing</li>
                </ul>
              </div>
            </div>
          </div>
        )}

        <div className={styles.footer}>
          <p>
            Last modified: {policy ? policy.last_updated : "Loading..."} | GDPR Compliant |
            <a href="/terms"> Terms of Service</a>
          </p>
        </div>
      </div>
    </div>
  );
};

export default PrivacyPolicyPage;
