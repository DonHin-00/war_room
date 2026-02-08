import React, { useState } from 'react';
import PropTypes from 'prop-types';
import { Globe, Shield, Bug, Play, AlertTriangle } from 'lucide-react';

const WebAppAttackDashboard = ({ initialUrl }) => {
  const [targetUrl, setTargetUrl] = useState(initialUrl || 'http://target-site.com');
  const [scanResults, setScanResults] = useState(null);
  const [scanning, setScanning] = useState(false);

  const startScan = () => {
      setScanning(true);
      setTimeout(() => {
          setScanResults({
              vulnerabilities: [
                  { id: 'v1', type: 'SQL Injection', severity: 'Critical', loc: '/login.php' },
                  { id: 'v2', type: 'XSS Reflected', severity: 'Medium', loc: '/search?q=' }
              ]
          });
          setScanning(false);
      }, 2000);
  };

  return (
    <div className="flex flex-col h-full bg-gray-900 text-green-400 p-4 font-mono">
        <div className="flex items-center gap-4 mb-6 border-b border-green-800 pb-4">
            <Globe className="text-blue-400" />
            <input
                type="text"
                value={targetUrl}
                onChange={(e) => setTargetUrl(e.target.value)}
                className="bg-black border border-green-700 p-2 rounded w-96 text-white focus:outline-none focus:border-green-400"
            />
            <button
                onClick={startScan}
                disabled={scanning}
                className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded font-bold disabled:opacity-50"
            >
                {scanning ? 'SCANNING...' : 'START RECON'}
            </button>
        </div>

        <div className="flex gap-4 h-full">
            {/* Site Map / Visualizer */}
            <div className="w-2/3 bg-black border border-green-900 rounded p-4 relative">
                <div className="absolute top-2 left-2 text-xs text-green-600">SITE TOPOLOGY MAP</div>
                <div className="flex items-center justify-center h-full text-gray-700">
                    {/* Placeholder for complex D3/Canvas graph */}
                    [ Interactive Site Map Visualization ]
                </div>
            </div>

            {/* Vulnerability Matrix */}
            <div className="w-1/3 flex flex-col gap-4">
                <div className="bg-gray-800 border border-green-900 rounded p-4 flex-grow">
                    <h3 className="text-white font-bold mb-4 flex items-center">
                        <Bug className="mr-2 text-red-500" /> VULNERABILITY MATRIX
                    </h3>

                    {scanResults ? (
                        <div className="space-y-2">
                            {scanResults.vulnerabilities.map(v => (
                                <div key={v.id} className="bg-black border border-gray-700 p-3 rounded hover:border-red-500 cursor-pointer group">
                                    <div className="flex justify-between items-center mb-1">
                                        <span className="font-bold text-white group-hover:text-red-400">{v.type}</span>
                                        <span className={`text-xs px-2 py-0.5 rounded ${v.severity === 'Critical' ? 'bg-red-900 text-red-200' : 'bg-yellow-900 text-yellow-200'}`}>
                                            {v.severity}
                                        </span>
                                    </div>
                                    <div className="text-xs text-gray-500 truncate">{v.loc}</div>

                                    <div className="mt-3 flex gap-2">
                                        <button className="flex-1 bg-gray-700 hover:bg-red-600 text-white text-xs py-1 rounded transition-colors">
                                            EXPLOIT
                                        </button>
                                        <button className="flex-1 bg-gray-700 hover:bg-blue-600 text-white text-xs py-1 rounded transition-colors">
                                            VALIDATE
                                        </button>
                                    </div>
                                </div>
                            ))}
                        </div>
                    ) : (
                        <div className="text-center text-gray-500 mt-10">
                            No scan data available.
                        </div>
                    )}
                </div>

                <div className="bg-gray-800 border border-green-900 rounded p-4">
                     <h3 className="text-white font-bold mb-2 flex items-center">
                        <AlertTriangle className="mr-2 text-yellow-500" /> ACTIVE PAYLOADS
                    </h3>
                    <div className="text-xs text-gray-400 text-center py-4">
                        No payloads currently deployed.
                    </div>
                </div>
            </div>
        </div>
    </div>
  );
};

WebAppAttackDashboard.propTypes = {
  initialUrl: PropTypes.string
};

export default WebAppAttackDashboard;
