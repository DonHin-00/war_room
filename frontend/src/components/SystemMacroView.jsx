import React, { useState, useEffect } from 'react';
import { Cpu, Activity, Zap, TrendingUp, RefreshCcw, Database, Server, BarChart3 } from 'lucide-react';

const SystemMacroView = () => {
  const [metrics, setMetrics] = useState({ cpu_load: 0, memory_usage: 0, latency_ms: 0, throughput_gbps: 0 });
  const [history, setHistory] = useState([]);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const res = await fetch('/api/macro/dashboard');
        const data = await res.json();
        if (data.success) {
          setMetrics(data.system);
          setHistory(prev => [...prev, data.system].slice(-20));
        }
      } catch (err) {
        console.error("Failed to fetch system stats:", err);
      }
    };
    fetchData();
    const interval = setInterval(fetchData, 2000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="min-h-screen bg-black text-blue-400 font-mono p-6">
      <div className="flex justify-between items-center border-b border-blue-900 pb-4 mb-6">
        <div className="flex items-center gap-3">
          <Server className="w-8 h-8" />
          <div>
            <h1 className="text-2xl font-black tracking-tighter text-white">SYSTEM_FABRIC_HEALTH</h1>
            <div className="text-[10px] text-blue-700 tracking-[0.2em]">INFRASTRUCTURE TELEMETRY & RESOURCE ALLOCATION</div>
          </div>
        </div>
        <div className="flex gap-4">
             <div className="text-right">
                <div className="text-xs text-blue-800 uppercase">Uptime</div>
                <div className="text-lg font-bold text-blue-200">14d 02h 11m 44s</div>
             </div>
             <button className="bg-blue-900/30 border border-blue-700 p-2 rounded hover:bg-blue-700/40">
                <RefreshCcw className="w-4 h-4" />
             </button>
        </div>
      </div>

      <div className="grid grid-cols-12 gap-6">
        {/* Left Column: Live Gauges */}
        <div className="col-span-4 space-y-6">
            <div className="bg-blue-900/10 border border-blue-900 p-6 rounded relative overflow-hidden">
                <div className="flex justify-between items-center mb-4">
                    <h3 className="text-xs font-bold uppercase text-blue-700">CPU Compute Load</h3>
                    <Cpu className="w-4 h-4" />
                </div>
                <div className="text-5xl font-black mb-2">{metrics.cpu_load}%</div>
                <div className="h-2 bg-gray-900 rounded-full overflow-hidden">
                    <div className="h-full bg-blue-500 transition-all duration-1000" style={{ width: `${metrics.cpu_load}%` }}></div>
                </div>
            </div>

            <div className="bg-blue-900/10 border border-blue-900 p-6 rounded relative overflow-hidden">
                <div className="flex justify-between items-center mb-4">
                    <h3 className="text-xs font-bold uppercase text-blue-700">Memory Pressure</h3>
                    <Database className="w-4 h-4" />
                </div>
                <div className="text-5xl font-black mb-2">{metrics.memory_usage}%</div>
                <div className="h-2 bg-gray-900 rounded-full overflow-hidden">
                    <div className="h-full bg-green-500 transition-all duration-1000" style={{ width: `${metrics.memory_usage}%` }}></div>
                </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
                <div className="bg-black border border-blue-900 p-4 rounded">
                    <div className="text-[10px] text-blue-700 uppercase mb-1">Packet Latency</div>
                    <div className="text-2xl font-bold flex items-baseline gap-1">
                        {metrics.latency_ms} <span className="text-xs font-normal">ms</span>
                    </div>
                </div>
                <div className="bg-black border border-blue-900 p-4 rounded">
                    <div className="text-[10px] text-blue-700 uppercase mb-1">Network BW</div>
                    <div className="text-2xl font-bold flex items-baseline gap-1">
                        {metrics.throughput_gbps} <span className="text-xs font-normal">Gbps</span>
                    </div>
                </div>
            </div>
        </div>

        {/* Right Column: Historical Visualizer (Simplified) */}
        <div className="col-span-8 flex flex-col gap-6">
            <div className="flex-1 bg-black border border-blue-900 rounded p-6 flex flex-col">
                <div className="flex justify-between items-center mb-6">
                    <h3 className="text-xs font-bold uppercase flex items-center gap-2">
                        <Activity className="w-4 h-4" /> Resource_Trend_Analysis
                    </h3>
                    <div className="flex gap-4 text-[10px]">
                        <div className="flex items-center gap-1"><div className="w-2 h-2 bg-blue-500"></div> CPU</div>
                        <div className="flex items-center gap-1"><div className="w-2 h-2 bg-green-500"></div> MEM</div>
                    </div>
                </div>

                <div className="flex-1 flex items-end gap-1 px-2 pb-2 border-b border-l border-blue-900/50">
                    {history.map((h, i) => (
                        <div key={i} className="flex-1 flex flex-col justify-end gap-0.5">
                            <div className="bg-blue-500/40 w-full" style={{ height: `${h.cpu_load}%` }}></div>
                            <div className="bg-green-500/40 w-full" style={{ height: `${h.memory_usage}%` }}></div>
                        </div>
                    ))}
                    {history.length === 0 && <div className="w-full text-center text-blue-900 text-xs italic">Awaiting Telemetry...</div>}
                </div>
            </div>

            <div className="h-48 grid grid-cols-3 gap-4">
                 <div className="bg-blue-950/20 border border-blue-900 p-4 rounded">
                    <BarChart3 className="w-4 h-4 mb-2 text-blue-700" />
                    <div className="text-[10px] uppercase text-blue-800">IOPS_SATURATION</div>
                    <div className="text-xl font-black mt-1 text-blue-300">12.4k</div>
                 </div>
                 <div className="bg-blue-950/20 border border-blue-900 p-4 rounded">
                    <Zap className="w-4 h-4 mb-2 text-yellow-500" />
                    <div className="text-[10px] uppercase text-blue-800">POWER_EFFICIENCY</div>
                    <div className="text-xl font-black mt-1 text-blue-300">92%</div>
                 </div>
                 <div className="bg-blue-950/20 border border-blue-900 p-4 rounded">
                    <TrendingUp className="w-4 h-4 mb-2 text-green-500" />
                    <div className="text-[10px] uppercase text-blue-800">SWARM_SYNC_RATE</div>
                    <div className="text-xl font-black mt-1 text-blue-300">99.98%</div>
                 </div>
            </div>
        </div>
      </div>
    </div>
  );
};

export default SystemMacroView;
