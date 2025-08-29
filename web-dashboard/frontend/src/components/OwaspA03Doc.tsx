import React, { useEffect, useState } from 'react';
import ReactMarkdown from 'react-markdown';
import axios from 'axios';

const OwaspA03Doc: React.FC = () => {
  const [markdown, setMarkdown] = useState<string>('');
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchDoc = async () => {
      try {
        const response = await axios.get('/api/docs/owasp/A03');
        setMarkdown(response.data.content);
      } catch (err) {
        setError('Failed to load document.');
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    fetchDoc();
  }, []);

  if (loading) {
    return <div className="p-4 text-gray-700">Loading document...</div>;
  }

  if (error) {
    return <div className="p-4 text-red-600">Error: {error}</div>;
  }

  return (
    <div className="prose dark:prose-invert max-w-none p-4">
      <ReactMarkdown>{markdown}</ReactMarkdown>
    </div>
  );
};

export default OwaspA03Doc;
