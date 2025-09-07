import React, { useState } from 'react'
import ReactDOM from 'react-dom/client'
import { Button } from '@/components/ui/button'
import HtmlViewer from '@/components/viewer/html-viewer'
import './index.css'

function App() {
  const [selectedFile, setSelectedFile] = useState<string>('')

  // 获取当前域名和端口，用于构建文件路径
  const baseUrl = `${window.location.origin}/output/`

  return (
    <div className="p-8 max-w-6xl mx-auto">
      <h1 className="text-3xl font-bold mb-6">Screenshot to React Converter</h1>
      
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* 左侧：文件选择和控制面板 */}
        <div className="border rounded-lg p-6">
          <h2 className="text-xl font-semibold mb-4">Generated HTML Files</h2>
          
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium mb-2">Select HTML File:</label>
              <select 
                className="w-full p-2 border rounded"
                value={selectedFile}
                onChange={(e) => setSelectedFile(e.target.value)}
              >
                <option value="">Choose a file...</option>
                <option value="element_1.html">Element 1</option>
                <option value="element_2.html">Element 2</option>
                <option value="element_3.html">Element 3</option>
              </select>
            </div>
            
            <div className="flex gap-2">
              <Button 
                onClick={() => {
                  // 刷新当前选中的文件
                  setSelectedFile('')
                  setTimeout(() => setSelectedFile(selectedFile), 100)
                }}
              >
                Refresh Viewer
              </Button>
              
              <Button 
                variant="outline"
                onClick={() => {
                  // 清除选择
                  setSelectedFile('')
                }}
              >
                Clear Selection
              </Button>
            </div>
          </div>
          
          <div className="mt-8">
            <h3 className="text-lg font-medium mb-2">Instructions</h3>
            <ul className="list-disc pl-5 space-y-1 text-sm text-gray-600">
              <li>Run the Python script to generate HTML files</li>
              <li>Select a generated HTML file from the dropdown</li>
              <li>View the converted HTML with Tailwind CSS styling</li>
            </ul>
          </div>
        </div>
        
        {/* 右侧：HTML查看器 */}
        <div>
          <h2 className="text-xl font-semibold mb-4">HTML Preview</h2>
          
          {selectedFile ? (
            <HtmlViewer filePath={`${baseUrl}${selectedFile}`} />
          ) : (
            <div className="border rounded-lg p-8 text-center text-gray-500">
              <p>Select an HTML file to preview</p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
)
