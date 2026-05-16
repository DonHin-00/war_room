import React, { useState, useEffect } from 'react';
import {
  Shield,
  Zap,
  Activity,
  AlertTriangle,
  Cpu,
  Globe,
  Terminal,
  ExternalLink,
  Lock,
  Unlock,
  TrendingUp
} from 'lucide-react';
import CyberBattlefieldMap from './CyberBattlefieldMap';

const WarRoom = () => {
  const [hiveState, setHiveState] = useState({
    defcon: 5,
    mood: 'NEUTRAL',
    active_threats: [],
    blue_level: 1,
    red_level: 1,
    blue_alert_level: 5
  });
  const [redStats, setRedStats] = useState({ learned_states: 0, avg_score: 0, max_score: 0 });
  const [blueStats, setBlueStats] = useState({ learned_states: 0, avg_score: 0, max_score: 0 });
  const [logs, setLogs] = useState([]);

  const [systemMetrics, setSystemMetrics] = useState({ cpu_load: 0, memory_usage: 0, latency_ms: 0, throughput_gbps: 0 });

  useEffect(() => {
    const fetchData = async () => {
      try {
        const res = await fetch('/api/macro/dashboard');
        const data = await res.json();
        if (data.success) {
          setHiveState(data.hive);
          setRedStats(data.red_stats);
          setBlueStats(data.blue_stats);
          setSystemMetrics(data.system);
        }
      } catch (err) {
        console.error("Failed to fetch macro status:", err);
      }
    };

    const interval = setInterval(fetchData, 2000);
    fetchData();
    return () => clearInterval(interval);
  }, []);

  // Simulate logs for now until backend provides a real stream
  useEffect(() => {
    const logInterval = setInterval(() => {
      const messages = [
        "RED_TEAM: Initiating reconnaissance on subnet 192.168.1.0/24",
        "BLUE_TEAM: Hardening firewall rules for port 80/443",
        "SRE: Auto-scaling mitigation services...",
        "THREAT_INTEL: New IOC detected - 45.22.11.9",
        "HIVE: Global DEFCON adjusted to " + (Math.floor(Math.random() * 5) + 1),
        "SENTINEL: Analyzing cross-vector correlation..."
      ];
      const newLog = {
        id: Date.now(),
        time: new Date().toLocaleTimeString(),
        msg: messages[Math.floor(Math.random() * messages.length)],
        type: Math.random() > 0.5 ? 'info' : 'warn'
      };
      setLogs(prev => [newLog, ...prev].slice(0, 50));
    }, 3000);
    return () => clearInterval(logInterval);
  }, []);

  const popOut = (path) => {
    window.open(path, '_blank');
  };

  return (
    <div className="h-full bg-black text-green-500 font-mono p-4 overflow-hidden flex flex-col gap-4">
      {/* Header Macro Stats */}
      <div className="grid grid-cols-4 gap-4">
        <div className="bg-gray-900/50 border border-green-900 p-4 rounded flex flex-col items-center justify-center">
          <div className="text-xs text-gray-500 uppercase tracking-widest mb-1">Hive Condition</div>
          <div className={`text-4xl font-black ${hiveState.defcon <= 2 ? 'text-red-500' : 'text-green-500'}`}>
            DEFCON {hiveState.defcon}
          </div>
          <div className="text-[10px] mt-2 text-gray-400">GLOBAL ALERT LEVEL</div>
        </div>
        <div className="bg-gray-900/50 border border-green-900 p-4 rounded flex flex-col items-center justify-center">
          <div className="text-xs text-gray-500 uppercase tracking-widest mb-1">Cognitive Mood</div>
          <div className="text-2xl font-bold text-blue-400">{hiveState.mood}</div>
          <div className="text-[10px] mt-2 text-gray-400">HIVE-MIND STATE</div>
        </div>
        <div className="bg-gray-900/50 border border-green-900 p-4 rounded flex flex-col items-center justify-center">
          <div className="text-xs text-gray-500 uppercase tracking-widest mb-1">Red Proficiency</div>
          <div className="text-2xl font-bold text-red-500">{redStats.learned_states} States</div>
          <div className="text-[10px] mt-2 text-gray-400">AVG REWARD: {redStats.avg_score?.toFixed(2)}</div>
        </div>
        <div className="bg-gray-900/50 border border-green-900 p-4 rounded flex flex-col items-center justify-center">
          <div className="text-xs text-gray-500 uppercase tracking-widest mb-1">Blue Resilience</div>
          <div className="text-2xl font-bold text-green-400">{blueStats.learned_states} Models</div>
          <div className="text-[10px] mt-2 text-gray-400">STABILITY: {(blueStats.avg_score || 0).toFixed(2)}</div>
        </div>
      </div>

      {/* Main Grid */}
      <div className="flex-1 grid grid-cols-12 gap-4 overflow-hidden">

        {/* Left Column: Visualizer & Active Threats */}
        <div className="col-span-8 flex flex-col gap-4 overflow-hidden">
          <div className="flex-1 bg-black border border-green-900 rounded relative group">
            <div className="absolute top-4 left-4 z-10 flex items-center gap-2">
              <Globe className="w-4 h-4 text-green-500 animate-pulse" />
              <span className="text-xs font-bold bg-black/80 px-2 py-1 rounded">BATTLESPACE_LIVE_FEED</span>
            </div>
            <button
              onClick={() => popOut('/lateral')}
              className="absolute top-4 right-4 z-10 p-2 bg-black/60 border border-green-900 rounded hover:bg-green-900/40 opacity-0 group-hover:opacity-100 transition-opacity"
            >
              <ExternalLink className="w-4 h-4" />
            </button>
            <CyberBattlefieldMap networks={[]} hosts={[]} onSelectEntity={() => {}} />
          </div>

          <div className="h-48 bg-gray-900/30 border border-green-900 rounded p-4 overflow-hidden flex flex-col">
            <div className="flex justify-between items-center mb-2">
              <h3 className="text-sm font-bold flex items-center gap-2">
                <AlertTriangle className="w-4 h-4 text-yellow-500" /> ACTIVE_THREAT_VECTORS
              </h3>
              <span className="text-[10px] text-gray-500">REAL-TIME ANALYSIS</span>
            </div>
            <div className="flex-1 overflow-y-auto space-y-2 pr-2">
              {hiveState.active_threats?.length > 0 ? (
                hiveState.active_threats.map((threat, i) => (
                  <div key={i} className="flex justify-between items-center text-xs bg-red-900/10 border border-red-900/30 p-2 rounded">
                    <span className="text-red-400 font-bold">{threat.type}</span>
                    <span className="text-gray-500">{threat.source}</span>
                    <span className="bg-red-900 text-red-100 px-1 rounded text-[10px]">CRITICAL</span>
                  </div>
                ))
              ) : (
                <div className="h-full flex items-center justify-center text-gray-600 text-xs italic">
                  No active high-priority threats detected.
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Right Column: Event Ticker & System Health */}
        <div className="col-span-4 flex flex-col gap-4 overflow-hidden">

          <div className="flex-1 bg-black border border-green-900 rounded flex flex-col overflow-hidden">
            <div className="p-3 border-b border-green-900 bg-green-900/10 flex justify-between items-center">
              <h3 className="text-xs font-bold flex items-center gap-2 uppercase tracking-tighter">
                <Terminal className="w-4 h-4" /> Global_Event_Log
              </h3>
              <Activity className="w-3 h-3 text-green-500 animate-pulse" />
            </div>
            <div className="flex-1 p-3 overflow-y-auto font-mono text-[10px] space-y-1">
              {logs.map(log => (
                <div key={log.id} className="border-l border-green-800 pl-2">
                  <span className="text-gray-600">[{log.time}]</span>{" "}
                  <span className={log.type === 'warn' ? 'text-yellow-500' : 'text-green-400'}>
                    {log.msg}
                  </span>
                </div>
              ))}
            </div>
          </div>

          <div className="h-64 bg-gray-900/40 border border-green-900 rounded p-4 group">
             <div className="flex justify-between items-center mb-4">
                <h3 className="text-xs font-bold flex items-center gap-2">
                    <Cpu className="w-4 h-4 text-blue-500" /> SYSTEM_HEARTBEAT
                </h3>
                <button onClick={() => popOut('/macro/system')} className="p-1 opacity-0 group-hover:opacity-100 transition-opacity">
                    <ExternalLink className="w-3 h-3" />
                </button>
             </div>
             <div className="space-y-4">
                <div>
                  <div className="flex justify-between text-[10px] mb-1">
                    <span>NEURAL_LOAD</span>
                    <span>{systemMetrics.cpu_load}%</span>
                  </div>
                  <div className="h-1 bg-gray-800 rounded-full overflow-hidden">
                    <div className="h-full bg-blue-500 transition-all duration-1000" style={{ width: `${systemMetrics.cpu_load}%` }}></div>
                  </div>
                </div>
                <div>
                  <div className="flex justify-between text-[10px] mb-1">
                    <span>MEMORY_FABRIC</span>
                    <span>{systemMetrics.memory_usage}%</span>
                  </div>
                  <div className="h-1 bg-gray-800 rounded-full overflow-hidden">
                    <div className="h-full bg-green-500 transition-all duration-1000" style={{ width: `${systemMetrics.memory_usage}%` }}></div>
                  </div>
                </div>
                <div className="grid grid-cols-2 gap-2 pt-2">
                  <div className="bg-black/40 p-2 border border-green-900/50 rounded flex items-center gap-2">
                    <Zap className="w-3 h-3 text-yellow-500" />
                    <div className="text-[10px]">
                      <div className="text-gray-500">LATENCY</div>
                      <div className="font-bold">{systemMetrics.latency_ms}ms</div>
                    </div>
                  </div>
                  <div className="bg-black/40 p-2 border border-green-900/50 rounded flex items-center gap-2">
                    <TrendingUp className="w-3 h-3 text-green-500" />
                    <div className="text-[10px]">
                      <div className="text-gray-500">THROUGHPUT</div>
                      <div className="font-bold">{systemMetrics.throughput_gbps} GB/s</div>
                    </div>
                  </div>
                </div>
             </div>
          </div>
        </div>
      </div>

      {/* Bottom Control Bar */}
      <div className="h-12 border border-green-900 bg-green-900/5 rounded flex items-center px-4 justify-between">
        <div className="flex gap-6 text-[10px]">
           <div className="flex items-center gap-2">
              <div className="w-2 h-2 bg-green-500 rounded-full animate-ping"></div>
              <span className="text-green-500 font-bold uppercase">Sentinel_Online</span>
           </div>
           <div className="text-gray-500">STATION: MACRO_V_01</div>
           <div className="text-gray-500">OPERATOR: AUTHORIZED</div>
        </div>
        <div className="flex gap-4">
          <button className="text-[10px] px-3 py-1 bg-red-900/20 border border-red-900/50 text-red-500 hover:bg-red-900/40 rounded transition-colors">
            EMERGENCY_VENT
          </button>
          <button className="text-[10px] px-3 py-1 bg-blue-900/20 border border-blue-900/50 text-blue-400 hover:bg-blue-900/40 rounded transition-colors">
            REBOOT_HIVE
          </button>
        </div>
      </div>
    </div>
  );
};

export default WarRoom;
