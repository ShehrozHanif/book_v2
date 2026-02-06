/**
 * Terms of Service page
 */

import React, { useState, useEffect } from "react";
import styles from "./PrivacyPage.module.css";
import { personalizationApi } from "../../services/personalizationApi";
import Header from "../../components/personalization/Header";
import LoadingIndicator from "../../components/LoadingIndicator";

interface TermsOfService {
  title: string;
  last_updated: string;
  content: string;
}

const TermsOfServicePage: React.FC = () => {
  const [terms, setTerms] = useState<TermsOfService | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const loadTerms = async () => {
      setIsLoading(true);
      setError(null);

      try {
        // Since we're not passing user_id to the endpoint, we'll use a dummy UUID
        const dummyUserId = "00000000-0000-0000-0000-000000000000";
        const data = await personalizationApi.getTermsOfService(dummyUserId);
        setTerms(data);
      } catch (err) {
        const message = err instanceof Error ? err.message : "Failed to load terms of service";
        setError(message);
        console.error("Error loading terms of service:", err);
      } finally {
        setIsLoading(false);
      }
    };

    loadTerms();
  }, []);

  return (
    <div className={styles.pageContainer}>
      <Header userName="Guest" />

      <div className={styles.contentWrapper}>
        <div className={styles.documentHeader}>
          <h1>Terms of Service</h1>
          {terms && <p className={styles.lastUpdated}>Last updated: {terms.last_updated}</p>}
        </div>

        {isLoading && <LoadingIndicator />}

        {error && (
          <div className={styles.errorContainer}>
            <p className={styles.error}>Error loading terms of service: {error}</p>
          </div>
        )}

        {terms && !isLoading && (
          <div className={styles.documentContent}>
            <div className={styles.policyText}>
              {terms.content.split("\n").map((line, index) => {
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
                <h3>User Responsibilities</h3>
                <ul>
                  <li>Maintain account confidentiality</li>
                  <li>Accept responsibility for all activities</li>
                  <li>Comply with all applicable laws</li>
                </ul>
              </div>

              <div className={styles.infoBox}>
                <h3>Prohibited Conduct</h3>
                <p>You may not:</p>
                <ul>
                  <li>Use automated tools</li>
                  <li>Gain unauthorized access</li>
                  <li>Share credentials</li>
                  <li>Upload malicious content</li>
                </ul>
              </div>

              <div className={styles.infoBox}>
                <h3>Contact</h3>
                <p>For questions about these terms:</p>
                <a href="mailto:legal@roboticslearning.edu">
                  legal@roboticslearning.edu
                </a>
              </div>
            </div>
          </div>
        )}

        <div className={styles.footer}>
          <p>
            Last modified: {terms ? terms.last_updated : "Loading..."} |
            <a href="/privacy"> Privacy Policy</a>
          </p>
        </div>
      </div>
    </div>
  );
};

export default TermsOfServicePage;
