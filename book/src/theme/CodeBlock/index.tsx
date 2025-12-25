import React from 'react';
import CodeBlock from '@theme-original/CodeBlock';
import type CodeBlockType from '@theme/CodeBlock';
import type { WrapperProps } from '@docusaurus/types';

type Props = WrapperProps<typeof CodeBlockType>;

/**
 * Swizzled CodeBlock component.
 * Docusaurus already provides excellent code block functionality with:
 * - Syntax highlighting via Prism
 * - Copy button (built-in since Docusaurus 2.0)
 * - Line highlighting
 * - Line numbers
 *
 * This wrapper allows for future customization if needed.
 */
export default function CodeBlockWrapper(props: Props): JSX.Element {
  return (
    <>
      <CodeBlock {...props} />
    </>
  );
}
