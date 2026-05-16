import React, { useState, useEffect } from 'react';
import { Terminal, Crosshair, Zap, Activity, Brain, ShieldAlert } from 'lucide-react';

const RedMacroView = () => {
  const [stats, setStats] = useState({ learned_states: 0, avg_score: 0, max_score: 0 });
  const [actions, setActions] = useState([]);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const res = await fetch('/api/red/status');
        const data = await res.json();
        if (data.success) {
          setStats(data.stats);
        }
      } catch (err) {
        console.error("Failed to fetch red stats:", err);
      }
    };
    fetchData();
    const interval = setInterval(fetchData, 3000);
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    // Simulate active Red Team operations
    const ops = [
      "T1059.003 - Command and Scripting Interpreter: Windows Command Shell",
      "T1078 - Valid Accounts",
      "T1210 - Exploitation of Remote Services",
      "T1566.001 - Phishing: Spearphishing Attachment",
      "T1046 - Network Service Scanning"
    ];
    setActions(ops.map((name, i) => ({ id: i, name, status: Math.random() > 0.3 ? 'EXECUTING' : 'SUCCESS' })));
  }, []);

  return (
    <div className="min-h-screen bg-black text-red-500 font-mono p-6">
      <div className="flex justify-between items-center border-b border-red-900 pb-4 mb-6">
        <div className="flex items-center gap-3">
          <Crosshair className="w-8 h-8" />
          <div>
            <h1 className="text-2xl font-black tracking-tighter">RED_TEAM_MACRO_OPS</h1>
            <div className="text-[10px] text-red-700 tracking-[0.2em]">OFFENSIVE CAPABILITY DASHBOARD</div>
          </div>
        </div>
        <div className="text-right">
          <div className="text-xs text-red-800">SENSITIVITY: TOP SECRET</div>
          <div className="text-xl font-bold uppercase">Authorized Access Only</div>
        </div>
      </div>

      <div className="grid grid-cols-3 gap-6 mb-6">
        <div className="bg-red-950/10 border border-red-900 p-6 rounded relative overflow-hidden">
          <Brain className="absolute -right-4 -bottom-4 w-24 h-24 text-red-900/20" />
          <div className="text-xs uppercase text-red-800 mb-2">Neural Maturity</div>
          <div className="text-4xl font-black">{stats.learned_states}</div>
          <div className="text-[10px] mt-1">TOTAL LEARNED STATES</div>
        </div>
        <div className="bg-red-950/10 border border-red-900 p-6 rounded">
          <div className="text-xs uppercase text-red-800 mb-2">Offensive Velocity</div>
          <div className="text-4xl font-black">{(stats.avg_score || 0).toFixed(2)}</div>
          <div className="text-[10px] mt-1">AVERAGE REWARD MAGNITUDE</div>
        </div>
        <div className="bg-red-950/10 border border-red-900 p-6 rounded">
          <div className="text-xs uppercase text-red-800 mb-2">Peak Payload Efficiency</div>
          <div className="text-4xl font-black">{stats.max_score || 0}</div>
          <div className="text-[10px] mt-1">MAXIMUM SUCCESS SCORE</div>
        </div>
      </div>

      <div className="grid grid-cols-12 gap-6">
        <div className="col-span-8 bg-black border border-red-900 rounded overflow-hidden">
          <div className="p-3 bg-red-900/20 border-b border-red-900 flex items-center gap-2">
            <Activity className="w-4 h-4" />
            <span className="text-xs font-bold">LIVE_EXPLOITATION_TELEMETRY</span>
          </div>
          <div className="p-4 space-y-4">
             {actions.map(op => (
               <div key={op.id} className="flex items-center justify-between bg-red-900/5 p-3 border border-red-900/20 rounded">
                 <div className="flex items-center gap-4">
                    <Terminal className="w-4 h-4 text-red-700" />
                    <div>
                      <div className="text-sm font-bold text-red-400">{op.name}</div>
                      <div className="text-[10px] text-red-900">MITRE ATT&CK FRAMEWORK</div>
                    </div>
                 </div>
                 <div className={`text-[10px] font-bold px-2 py-1 rounded ${op.status === 'EXECUTING' ? 'bg-red-600 text-white animate-pulse' : 'bg-red-900 text-red-200'}`}>
                   {op.status}
                 </div>
               </div>
             ))}
          </div>
        </div>

        <div className="col-span-4 space-y-6">
           <div className="bg-black border border-red-900 rounded p-4">
              <h3 className="text-xs font-bold mb-4 flex items-center gap-2 text-red-400 uppercase">
                 <Zap className="w-4 h-4" /> Vector_Heatmap
              </h3>
              <div className="space-y-3">
                 {['NETWORK', 'SOCIAL', 'PHYSICAL', 'WEB', 'CLOUD'].map(v => (
                   <div key={v}>
                     <div className="flex justify-between text-[10px] mb-1">
                        <span>{v}_SURFACE</span>
                        <span>{Math.floor(Math.random() * 100)}%</span>
                     </div>
                     <div className="h-1 bg-red-950 rounded-full overflow-hidden">
                        <div className="h-full bg-red-600" style={{width: `${Math.random() * 100}%`}}></div>
                     </div>
                   </div>
                 ))}
              </div>
           </div>

           <div className="bg-red-900/10 border border-red-600 p-4 rounded flex flex-col items-center justify-center text-center">
              <ShieldAlert className="w-12 h-12 mb-2 animate-bounce" />
              <div className="font-black text-lg">HIVE_BREACH_READY</div>
              <div className="text-[10px] uppercase text-red-700">Exploit Chain Fully Validated</div>
              <button className="mt-4 w-full bg-red-600 text-white py-2 font-bold text-xs hover:bg-red-500 transition-colors">
                TRIGGER_TOTAL_COMPROMISE
              </button>
           </div>
        </div>
      </div>
    </div>
  );
};

export default RedMacroView;
