export const calculateFeasibility = (target, attackType) => {
  let score = 0;

  // WiFi-specific factors
  if (attackType === 'WIFI') {
    // Signal strength mapping (approximate)
    // -30dBm = 100, -90dBm = 10
    const signalScore = Math.max(0, Math.min(100, 100 - (Math.abs(target.signal) - 30) * (90/60)));
    score += signalScore * 0.4;

    score += target.encryption === 'WPA2' ? 30 :
             target.encryption === 'WEP' ? 50 : 10;

    // Client presence increases capture probability
    score += (target.clients || 0) > 0 ? 20 : 0;
  }

  // Network attack factors
  if (attackType === 'NETWORK') {
    score += (target.openPorts || []).length * 5;
    score += (target.vulnerabilities || []).length * 15;
    score += (target.os || '').toLowerCase().includes('windows') ? 10 : 0; // Arbitrary example factor
  }

  return Math.round(Math.min(100, Math.max(0, score)));
};
