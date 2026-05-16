import React, { useState, useEffect } from 'react';
import { Shield, ShieldCheck, Activity, Lock, Cpu, Globe, AlertCircle } from 'lucide-react';

const BlueMacroView = () => {
  const [stats, setStats] = useState({ learned_states: 0, avg_score: 0 });
  const [alerts, setAlerts] = useState([]);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const res = await fetch('/api/sentinel/status');
        const data = await res.json();
        if (data.success) {
          setStats(data.stats);
        }
      } catch (err) {
        console.error("Failed to fetch blue stats:", err);
      }
    };
    fetchData();
    const interval = setInterval(fetchData, 3000);
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    const possibleAlerts = [
        "Unauthorized SSH attempt on 10.0.0.42 blocked",
        "Large data exfiltration signature detected via DNS",
        "Memory injection attempt mitigated in web-server-01",
        "Suspicious binary 'sys_temp_init' quarantined",
        "Anomalous lateral movement detected from HR-PC-04"
    ];
    setAlerts(possibleAlerts.map((msg, i) => ({ id: i, msg, time: new Date().toLocaleTimeString(), severity: Math.random() > 0.7 ? 'CRITICAL' : 'LOW' })));
  }, []);

  return (
    <div className="min-h-screen bg-black text-blue-500 font-mono p-6">
      <div className="flex justify-between items-center border-b border-blue-900 pb-4 mb-6">
        <div className="flex items-center gap-3">
          <Shield className="w-8 h-8" />
          <div>
            <h1 className="text-2xl font-black tracking-tighter">BLUE_TEAM_DEFENSE_DASHBOARD</h1>
            <div className="text-[10px] text-blue-700 tracking-[0.2em]">RESILIENCE & MITIGATION MONITORING</div>
          </div>
        </div>
        <div className="flex gap-4 items-center">
            <div className="px-3 py-1 bg-blue-900/20 border border-blue-500 rounded flex items-center gap-2">
                <ShieldCheck className="w-4 h-4" />
                <span className="text-xs font-bold uppercase">System Hardened</span>
            </div>
            <div className="text-right border-l border-blue-900 pl-4">
                <div className="text-xs text-blue-800">STATUS: ACTIVE</div>
                <div className="text-xl font-bold uppercase text-white">All Shields Nominal</div>
            </div>
        </div>
      </div>

      <div className="grid grid-cols-4 gap-6 mb-6">
        <div className="bg-blue-950/10 border border-blue-900 p-6 rounded">
          <div className="text-xs uppercase text-blue-800 mb-2">Mitigation Logic</div>
          <div className="text-4xl font-black">{stats.learned_states}</div>
          <div className="text-[10px] mt-1 text-blue-700">HEURISTIC MODELS LOADED</div>
        </div>
        <div className="bg-blue-950/10 border border-blue-900 p-6 rounded">
          <div className="text-xs uppercase text-blue-800 mb-2">Stability Quotient</div>
          <div className="text-4xl font-black">{(stats.avg_score || 0).toFixed(2)}</div>
          <div className="text-[10px] mt-1 text-blue-700">DEFENSIVE RELIABILITY SCORE</div>
        </div>
        <div className="bg-blue-950/10 border border-blue-900 p-6 rounded">
          <div className="text-xs uppercase text-blue-800 mb-2">Network Isolation</div>
          <div className="text-4xl font-black">99.4%</div>
          <div className="text-[10px] mt-1 text-blue-700">TRAFFIC VALIDATION RATE</div>
        </div>
        <div className="bg-blue-950/10 border border-blue-900 p-6 rounded">
          <div className="text-xs uppercase text-blue-800 mb-2">Mean Time To Detect</div>
          <div className="text-4xl font-black">4.2s</div>
          <div className="text-[10px] mt-1 text-blue-700">RESPONSE LATENCY</div>
        </div>
      </div>

      <div className="grid grid-cols-12 gap-6">
        <div className="col-span-7 bg-black border border-blue-900 rounded flex flex-col overflow-hidden">
            <div className="p-3 bg-blue-900/20 border-b border-blue-900 flex items-center justify-between">
                <div className="flex items-center gap-2">
                    <Activity className="w-4 h-4" />
                    <span className="text-xs font-bold uppercase">Threat_Alert_Stream</span>
                </div>
                <div className="animate-pulse w-2 h-2 bg-blue-500 rounded-full"></div>
            </div>
            <div className="p-4 space-y-2 overflow-y-auto max-h-[500px]">
                {alerts.map(alert => (
                    <div key={alert.id} className={`p-3 border rounded text-xs flex justify-between items-center ${alert.severity === 'CRITICAL' ? 'bg-red-900/10 border-red-500 text-red-400' : 'bg-blue-900/5 border-blue-900/40 text-blue-300'}`}>
                        <div className="flex items-center gap-3">
                            <AlertCircle className={`w-4 h-4 ${alert.severity === 'CRITICAL' ? 'text-red-500' : 'text-blue-500'}`} />
                            <div>
                                <div className="font-bold">{alert.msg}</div>
                                <div className="text-[10px] opacity-50">{alert.time} - {alert.severity} PRIORITY</div>
                            </div>
                        </div>
                        <button className="px-2 py-1 border border-current rounded hover:bg-white/10">TRIAGE</button>
                    </div>
                ))}
            </div>
        </div>

        <div className="col-span-5 space-y-6">
            <div className="bg-blue-900/5 border border-blue-900 rounded p-4">
                <h3 className="text-xs font-bold mb-4 flex items-center gap-2 text-blue-400 uppercase">
                    <Lock className="w-4 h-4" /> Endpoint_Hardening_Matrix
                </h3>
                <div className="space-y-4">
                    {['KERNEL_INTEGRITY', 'MEMORY_PROTECTION', 'FS_ENCRYPTION', 'IAM_POLICIES'].map(sys => (
                        <div key={sys}>
                            <div className="flex justify-between text-[10px] mb-1">
                                <span>{sys}</span>
                                <span className="text-green-500">OPTIMAL</span>
                            </div>
                            <div className="h-1 bg-gray-800 rounded-full overflow-hidden">
                                <div className="h-full bg-blue-500 w-[90%]"></div>
                            </div>
                        </div>
                    ))}
                </div>
            </div>

            <div className="bg-black border border-blue-900 rounded p-4 relative overflow-hidden">
                <Globe className="absolute -right-4 -bottom-4 w-24 h-24 text-blue-900/10" />
                <h3 className="text-xs font-bold mb-4 flex items-center gap-2 text-blue-400 uppercase">
                    <Cpu className="w-4 h-4" /> SOC_System_Health
                </h3>
                <div className="grid grid-cols-2 gap-4">
                    <div className="p-3 bg-blue-950/20 border border-blue-900/50 rounded">
                        <div className="text-[10px] text-blue-700">CPU_IDLE</div>
                        <div className="text-xl font-bold">84%</div>
                    </div>
                    <div className="p-3 bg-blue-950/20 border border-blue-900/50 rounded">
                        <div className="text-[10px] text-blue-700">FW_THROUGHPUT</div>
                        <div className="text-xl font-bold">12.4 Gbps</div>
                    </div>
                </div>
            </div>

            <button className="w-full bg-blue-600 text-white py-3 font-black text-sm hover:bg-blue-500 transition-colors rounded shadow-lg shadow-blue-900/20 flex items-center justify-center gap-2">
                <ShieldCheck className="w-5 h-5" /> EXECUTE_SYSTEM_WIDE_LOCKDOWN
            </button>
        </div>
      </div>
    </div>
  );
};

export default BlueMacroView;
