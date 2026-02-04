import React, { useEffect, useRef, useState } from 'react';
import { Wifi, Server, Smartphone, Lock, Unlock, ShieldAlert } from 'lucide-react';

const CyberBattlefieldMap = ({ networks = [], hosts = [], onSelectEntity }) => {
  const canvasRef = useRef(null);
  const [selectedId, setSelectedId] = useState(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');

    // Resize canvas
    canvas.width = canvas.parentElement.clientWidth;
    canvas.height = canvas.parentElement.clientHeight;

    const render = () => {
      ctx.clearRect(0, 0, canvas.width, canvas.height);

      // Draw Networks (Signal Clouds)
      networks.forEach(net => {
        // Cloud gradient
        const gradient = ctx.createRadialGradient(net.x, net.y, 20, net.x, net.y, net.range || 100);
        gradient.addColorStop(0, 'rgba(0, 255, 0, 0.1)');
        gradient.addColorStop(1, 'rgba(0, 255, 0, 0)');

        ctx.fillStyle = gradient;
        ctx.beginPath();
        ctx.arc(net.x, net.y, net.range || 100, 0, Math.PI * 2);
        ctx.fill();

        // AP Icon placeholder (rendered by React usually, but simplistic here for canvas mixing)
        // We'll just draw nodes
        ctx.fillStyle = selectedId === net.id ? '#0f0' : '#0a0';
        ctx.beginPath();
        ctx.arc(net.x, net.y, 10, 0, Math.PI * 2);
        ctx.fill();

        // Label
        ctx.fillStyle = '#fff';
        ctx.font = '12px monospace';
        ctx.fillText(net.ssid, net.x - 20, net.y + 25);
      });

      // Draw Hosts
      hosts.forEach(host => {
        ctx.fillStyle = selectedId === host.id ? '#f00' : '#a00';
        ctx.fillRect(host.x - 10, host.y - 10, 20, 20);

        ctx.fillStyle = '#fff';
        ctx.fillText(host.ip, host.x - 25, host.y + 25);
      });

      requestAnimationFrame(render);
    };

    render();

    // Basic click handler
    const handleClick = (e) => {
      const rect = canvas.getBoundingClientRect();
      const x = e.clientX - rect.left;
      const y = e.clientY - rect.top;

      // Check networks
      const clickedNet = networks.find(n => Math.hypot(n.x - x, n.y - y) < 20);
      if (clickedNet) {
        setSelectedId(clickedNet.id);
        onSelectEntity(clickedNet, 'NETWORK');
        return;
      }

      // Check hosts
      const clickedHost = hosts.find(h => Math.abs(h.x - x) < 15 && Math.abs(h.y - y) < 15);
      if (clickedHost) {
        setSelectedId(clickedHost.id);
        onSelectEntity(clickedHost, 'HOST');
        return;
      }
    };

    canvas.addEventListener('mousedown', handleClick);
    return () => canvas.removeEventListener('mousedown', handleClick);
  }, [networks, hosts, selectedId, onSelectEntity]);

  return (
    <div className="relative w-full h-full bg-black border border-green-900 rounded overflow-hidden">
      <div className="absolute top-2 left-2 text-green-500 font-mono text-xs z-10">
        BATTLESPACE VISUALIZATION // LIVE
      </div>
      <canvas ref={canvasRef} className="w-full h-full block" />
    </div>
  );
};

export default CyberBattlefieldMap;
