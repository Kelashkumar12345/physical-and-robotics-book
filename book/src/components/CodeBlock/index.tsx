import React from 'react';
import CodeBlockDocusaurus from '@theme/CodeBlock';
import CopyButton from './CopyButton';
import styles from './styles.module.css';

interface CodeBlockProps {
  children: string;
  className?: string;
  language?: string;
  title?: string;
  showLineNumbers?: boolean;
}

/**
 * Enhanced CodeBlock component with copy functionality.
 * Wraps Docusaurus default CodeBlock with additional features.
 */
export default function CodeBlock({
  children,
  className,
  language,
  title,
  showLineNumbers = false,
}: CodeBlockProps): JSX.Element {
  // Extract language from className if not provided directly
  const lang = language || className?.replace('language-', '') || 'text';

  return (
    <div className={styles.codeBlockWrapper}>
      {title && <div className={styles.codeBlockTitle}>{title}</div>}
      <div className={styles.codeBlockContainer}>
        <CopyButton code={children} />
        <CodeBlockDocusaurus
          language={lang}
          showLineNumbers={showLineNumbers}
        >
          {children}
        </CodeBlockDocusaurus>
      </div>
    </div>
  );
}
