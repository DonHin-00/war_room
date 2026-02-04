import React, { useState } from 'react';
import { Network, Terminal, Share2, ArrowRight } from 'lucide-react';

const LateralMovementController = () => {
  const [pivotPath, setPivotPath] = useState([]);
  const [selectedExploit, setSelectedExploit] = useState(null);
  const [compromisedHost, setCompromisedHost] = useState({
      id: 'h1', ip: '192.168.1.105', os: 'Linux', role: 'Gateway'
  });

  const targets = [
      { id: 't1', ip: '192.168.1.20', os: 'Windows Server 2019', services: ['SMB', 'RDP'], score: 85 },
      { id: 't2', ip: '192.168.1.50', os: 'Ubuntu 20.04', services: ['SSH', 'HTTP'], score: 40 }
  ];

  const exploits = [
      { id: 'e1', name: 'SMBGhost', type: 'RCE', reliability: 'High' },
      { id: 'e2', name: 'EternalBlue', type: 'RCE', reliability: 'Medium' }
  ];

  const handleExecutePivot = () => {
      console.log(`Pivoting from ${compromisedHost.ip} to target using ${selectedExploit.name}`);
      alert(`Pivot execution started: ${selectedExploit.name}`);
  };

  return (
    <div className="flex h-full bg-gray-900 text-green-400 font-mono p-4 gap-4">
        {/* Topology Map (simplified list for now) */}
        <div className="w-1/3 border border-green-800 bg-black p-4">
            <h3 className="text-lg font-bold border-b border-green-800 pb-2 mb-4 flex items-center">
                <Share2 className="mr-2" /> NETWORK TOPOLOGY
            </h3>

            <div className="mb-4">
                <div className="text-xs text-gray-500 mb-1">COMPROMISED NODE (PIVOT POINT)</div>
                <div className="bg-red-900/30 border border-red-600 p-2 rounded flex justify-between items-center">
                    <div>
                        <div className="font-bold text-red-400">{compromisedHost.ip}</div>
                        <div className="text-xs">{compromisedHost.os}</div>
                    </div>
                    <Terminal className="text-red-500 w-4 h-4" />
                </div>
            </div>

            <div className="flex justify-center my-2">
                <ArrowRight className="text-gray-600" />
            </div>

            <div className="space-y-2">
                <div className="text-xs text-gray-500 mb-1">REACHABLE TARGETS</div>
                {targets.map(t => (
                    <div
                        key={t.id}
                        onClick={() => setPivotPath([t])}
                        className={`p-2 border rounded cursor-pointer hover:bg-green-900/30 transition-colors ${
                            pivotPath[0]?.id === t.id ? 'border-green-400 bg-green-900/20' : 'border-gray-700'
                        }`}
                    >
                        <div className="flex justify-between">
                            <span className="font-bold">{t.ip}</span>
                            <span className="text-xs bg-gray-800 px-1 rounded">{t.score}% Vuln</span>
                        </div>
                        <div className="text-xs text-gray-400 mt-1">{t.os}</div>
                        <div className="flex gap-1 mt-1">
                            {t.services.map(s => (
                                <span key={s} className="text-[10px] bg-blue-900 text-blue-200 px-1 rounded">{s}</span>
                            ))}
                        </div>
                    </div>
                ))}
            </div>
        </div>

        {/* Exploit Config */}
        <div className="flex-1 border border-green-800 bg-gray-900 p-4 flex flex-col">
             <h3 className="text-lg font-bold border-b border-green-800 pb-2 mb-4">EXPLOIT CONFIGURATION</h3>

             {pivotPath.length > 0 ? (
                 <>
                    <div className="mb-6">
                        <div className="text-sm text-gray-400 mb-2">RECOMMENDED VECTORS</div>
                        <div className="grid grid-cols-2 gap-4">
                            {exploits.map(e => (
                                <button
                                    key={e.id}
                                    onClick={() => setSelectedExploit(e)}
                                    className={`p-4 border rounded text-left hover:bg-gray-800 ${
                                        selectedExploit?.id === e.id ? 'border-green-400 bg-green-900/20' : 'border-gray-600'
                                    }`}
                                >
                                    <div className="font-bold">{e.name}</div>
                                    <div className="text-sm text-gray-400">{e.type}</div>
                                    <div className="text-xs mt-2 text-yellow-500">Reliability: {e.reliability}</div>
                                </button>
                            ))}
                        </div>
                    </div>

                    {selectedExploit && (
                        <div className="mt-auto bg-black p-4 border-t border-green-800">
                             <div className="flex items-center justify-between mb-4">
                                 <div>
                                     <div className="text-xs text-gray-500">ACTION</div>
                                     <div className="font-bold text-white">PIVOT: {compromisedHost.ip} → {pivotPath[0].ip}</div>
                                 </div>
                                 <div>
                                     <div className="text-xs text-gray-500">METHOD</div>
                                     <div className="font-bold text-red-400">{selectedExploit.name}</div>
                                 </div>
                             </div>

                             <button
                                onClick={handleExecutePivot}
                                className="w-full bg-red-600 hover:bg-red-700 text-white font-bold py-3 rounded tracking-wider"
                             >
                                 AUTHORIZE & EXECUTE
                             </button>
                        </div>
                    )}
                 </>
             ) : (
                 <div className="flex items-center justify-center h-full text-gray-600">
                     Select a target to configure pivot attack.
                 </div>
             )}
        </div>
    </div>
  );
};

export default LateralMovementController;
