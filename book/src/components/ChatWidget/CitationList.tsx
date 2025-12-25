import React from 'react';
import type { Citation } from './index';
import styles from './styles.module.css';

interface CitationListProps {
  citations: Citation[];
}

export default function CitationList({
  citations,
}: CitationListProps): JSX.Element {
  const handleClick = (url: string) => {
    // Navigate to the cited section
    if (url.startsWith('/')) {
      window.location.href = url;
    } else {
      window.open(url, '_blank', 'noopener,noreferrer');
    }
  };

  return (
    <div className={styles.citations}>
      <span className={styles.citationsLabel}>Sources:</span>
      <ul className={styles.citationsList}>
        {citations.map((citation, index) => (
          <li key={index}>
            <button
              onClick={() => handleClick(citation.url)}
              className={styles.citationLink}
              title={`Relevance: ${Math.round((citation.relevanceScore || 0) * 100)}%`}
            >
              📄 {citation.title}
            </button>
          </li>
        ))}
      </ul>
    </div>
  );
}
