import React, { useState, useEffect } from 'react';
import { Activity, ShieldCheck, Cpu, Wifi } from 'lucide-react';

const SituationalAwarenessDashboard = () => {
  const [stats, setStats] = useState({
      activeAttacks: 0,
      targetsDiscovered: 12,
      cpuLoad: 15,
      netLoad: 2
  });

  useEffect(() => {
      // Simulate live updates
      const interval = setInterval(() => {
          setStats(s => ({
              ...s,
              cpuLoad: Math.floor(Math.random() * 30) + 10,
              netLoad: Math.floor(Math.random() * 10)
          }));
      }, 2000);
      return () => clearInterval(interval);
  }, []);

  return (
    <div className="flex bg-black border-t border-green-900 text-green-500 font-mono text-sm py-1 px-4 justify-between items-center h-10 select-none">

        <div className="flex gap-6">
            <div className="flex items-center gap-2">
                <ShieldCheck className="w-4 h-4 text-green-400" />
                <span className="font-bold text-white">SYSTEM: READY</span>
            </div>

            <div className="flex items-center gap-2">
                <Activity className="w-4 h-4 text-red-500" />
                <span>ACTIVE OPS: <span className="text-white font-bold">{stats.activeAttacks}</span></span>
            </div>

            <div className="flex items-center gap-2">
                <span className="text-blue-400">TARGETS:</span>
                <span className="text-white">{stats.targetsDiscovered}</span>
            </div>
        </div>

        <div className="flex gap-6">
            <div className="flex items-center gap-2 w-32">
                <Cpu className="w-4 h-4" />
                <div className="flex-1 bg-gray-800 h-2 rounded overflow-hidden">
                    <div className="bg-green-500 h-full transition-all duration-500" style={{ width: `${stats.cpuLoad}%` }}></div>
                </div>
                <span className="text-xs w-8">{stats.cpuLoad}%</span>
            </div>

             <div className="flex items-center gap-2 w-32">
                <Wifi className="w-4 h-4" />
                <div className="flex-1 bg-gray-800 h-2 rounded overflow-hidden">
                    <div className="bg-blue-500 h-full transition-all duration-500" style={{ width: `${stats.netLoad}%` }}></div>
                </div>
                <span className="text-xs w-8">UP</span>
            </div>

            <div className="text-gray-500">
                v1.0.4-ALPHA
            </div>
        </div>

    </div>
  );
};

export default SituationalAwarenessDashboard;
