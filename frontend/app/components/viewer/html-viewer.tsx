import React, { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';

interface HtmlViewerProps {
  filePath: string;
}

const HtmlViewer: React.FC<HtmlViewerProps> = ({ filePath }) => {
  const [htmlContent, setHtmlContent] = useState<string>('');
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (filePath) {
      fetchHtmlContent();
    }
  }, [filePath]);

  const fetchHtmlContent = async () => {
    setLoading(true);
    setError(null);
    
    try {
      // 读取本地HTML文件内容
      const response = await fetch(filePath);
      if (!response.ok) {
        throw new Error(`Failed to load HTML file: ${response.status}`);
      }
      
      const content = await response.text();
      setHtmlContent(content);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load HTML content');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div className="p-4">Loading HTML content...</div>;
  }

  if (error) {
    return (
      <div className="p-4 text-red-500">
        <p>Error: {error}</p>
        <Button onClick={fetchHtmlContent} className="mt-2">Retry</Button>
      </div>
    );
  }

  return (
    <div className="border rounded-lg overflow-hidden">
      <div className="bg-gray-100 px-4 py-2 border-b flex justify-between items-center">
        <span className="text-sm font-medium">HTML Preview</span>
        <Button variant="outline" size="sm" onClick={fetchHtmlContent}>
          Refresh
        </Button>
      </div>
      <div className="p-4">
        {htmlContent ? (
          <div 
            className="border rounded p-4 min-h-[200px]"
            dangerouslySetInnerHTML={{ __html: htmlContent }}
          />
        ) : (
          <p className="text-gray-500 italic">No HTML content to display</p>
        )}
      </div>
    </div>
  );
};

export default HtmlViewer;