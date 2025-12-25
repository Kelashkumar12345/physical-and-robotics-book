import React from 'react';
import Layout from '@theme/Layout';
import useBaseUrl from '@docusaurus/useBaseUrl';
import { useEffect } from 'react';

export default function Home(): JSX.Element {
  const introUrl = useBaseUrl('/docs/intro');

  useEffect(() => {
    window.location.href = introUrl;
  }, [introUrl]);

  return (
    <Layout title="Home">
      <div style={{
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        height: '50vh'
      }}>
        <p>Redirecting to course introduction...</p>
      </div>
    </Layout>
  );
}
