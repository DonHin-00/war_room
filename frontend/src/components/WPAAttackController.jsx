import React, { useState } from 'react';
import { Wifi, Lock, Crosshair, Radio, Shield } from 'lucide-react';
import CyberBattlefieldMap from './CyberBattlefieldMap';

const WPAAttackController = () => {
  const [phase, setPhase] = useState('DISCOVERY'); // DISCOVERY, CAPTURE, CRACK, SUCCESS
  const [targetNetwork, setTargetNetwork] = useState(null);
  const [handshakeStatus, setHandshakeStatus] = useState('not_captured');
  const [networks, setNetworks] = useState([
    { id: 'net1', ssid: 'Target_WiFi_01', bssid: '00:11:22:33:44:55', signal: -45, encryption: 'WPA2', x: 200, y: 200 },
    { id: 'net2', ssid: 'Guest_WiFi', bssid: 'AA:BB:CC:DD:EE:FF', signal: -80, encryption: 'WPA2', x: 400, y: 150 }
  ]);

  const handleSelectNetwork = (network) => {
    setTargetNetwork(network);
    setPhase('CAPTURE');
    // In real implementation, this would trigger FeasibilityCalculator
  };

  const startDeauthAttack = () => {
    console.log(`[ATTACK] Deauth started on ${targetNetwork.ssid}`);
    // Simulate handshake capture for UI flow
    setTimeout(() => {
        setHandshakeStatus('captured');
        setPhase('CRACK');
    }, 3000);
  };

  const startCracking = () => {
      console.log(`[ATTACK] Cracking initiated on ${targetNetwork.ssid}`);
      // Simulate crack success
      setTimeout(() => {
          setPhase('SUCCESS');
      }, 5000);
  };

  return (
    <div className="flex flex-col h-full bg-gray-900 text-green-400 p-4 font-mono">
      <div className="text-xl mb-4 border-b border-green-800 pb-2 flex items-center">
        <Wifi className="mr-2" /> WPA/WPA2 INTERCEPTION
      </div>

      <div className="flex-grow flex gap-4">
          {/* Main Visualizer */}
          <div className="flex-1 bg-black border border-green-900 relative">
             <CyberBattlefieldMap
                networks={networks}
                onSelectEntity={(entity, type) => type === 'NETWORK' && handleSelectNetwork(entity)}
             />
          </div>

          {/* Control Panel */}
          <div className="w-1/3 bg-gray-800 p-4 border-l border-green-900 flex flex-col gap-4">
              <div className="text-sm text-gray-400 mb-2">OPERATION PHASE: <span className="text-green-300 font-bold">{phase}</span></div>

              {phase === 'DISCOVERY' && (
                  <div className="text-center p-8 border border-dashed border-gray-600 rounded">
                      <p>Select a target from the Battlespace Map to begin analysis.</p>
                  </div>
              )}

              {phase === 'CAPTURE' && targetNetwork && (
                  <div className="flex flex-col gap-4">
                      <div className="bg-black p-3 rounded border border-green-800">
                          <h3 className="text-white font-bold">{targetNetwork.ssid}</h3>
                          <p className="text-sm">BSSID: {targetNetwork.bssid}</p>
                          <p className="text-sm">Signal: {targetNetwork.signal} dBm</p>
                          <p className="text-sm">Encryption: {targetNetwork.encryption}</p>
                      </div>

                      <div className="bg-red-900/20 p-4 border border-red-900/50 rounded">
                          <h4 className="flex items-center text-red-400 font-bold mb-2">
                              <Crosshair className="w-4 h-4 mr-2" /> ACTIVE MEASURES
                          </h4>
                          <button
                            onClick={startDeauthAttack}
                            className="w-full bg-red-600 hover:bg-red-700 text-white font-bold py-2 px-4 rounded mb-2 transition-colors"
                          >
                            FORCE REAUTHENTICATION
                          </button>
                          <p className="text-xs text-red-300">
                              Warning: This will disconnect clients to force handshake capture.
                          </p>
                      </div>
                  </div>
              )}

              {phase === 'CRACK' && (
                  <div className="flex flex-col gap-4">
                      <div className="bg-green-900/20 p-4 border border-green-500 rounded text-center">
                          <Lock className="w-8 h-8 mx-auto mb-2 text-green-500" />
                          <p>Handshake Captured!</p>
                          <p className="text-xs text-gray-400">hashcat-ready format</p>
                      </div>

                      <button
                        onClick={startCracking}
                        className="w-full bg-orange-600 hover:bg-orange-700 text-white font-bold py-2 px-4 rounded"
                      >
                        INITIATE DICTIONARY ATTACK
                      </button>
                  </div>
              )}

             {phase === 'SUCCESS' && (
                  <div className="flex flex-col gap-4">
                      <div className="bg-green-600 p-4 border border-green-400 rounded text-center text-white">
                          <Unlock className="w-12 h-12 mx-auto mb-2" />
                          <h3 className="text-2xl font-bold">CRACKED</h3>
                          <p className="font-mono text-xl mt-2 bg-black/50 p-2 rounded">supersecret123</p>
                      </div>
                      <button
                         onClick={() => setPhase('DISCOVERY')}
                         className="mt-4 border border-green-600 text-green-500 hover:bg-green-900 py-2 rounded"
                      >
                          RETURN TO DISCOVERY
                      </button>
                  </div>
              )}

          </div>
      </div>
    </div>
  );
};

export default WPAAttackController;
