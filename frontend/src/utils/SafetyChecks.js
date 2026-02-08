export const ROE_RULES = {
  allowDisruption: true, // Deauth, DoS
  allowMilitaryTargets: false,
  allowForeignInfrastructure: false,
  maxRiskLevel: 'HIGH'
};

export const checkROECompliance = (action, target) => {
  const violations = [];

  if (action.includes('DEAUTH') && !ROE_RULES.allowDisruption) {
    violations.push('Disruption attacks (DEAUTH) prohibited by ROE.');
  }

  if ((target.domain || '').includes('.mil') && !ROE_RULES.allowMilitaryTargets) {
    violations.push('Military targets restricted under current ROE.');
  }

  return {
    compliant: violations.length === 0,
    violations
  };
};

export const governResponse = (intensity, targetValue) => {
    // Simple limiter
    const MAX_INTENSITY = 10;
    // If target is low value (e.g. 1), max intensity is limited
    const allowedIntensity = Math.min(intensity, targetValue * 2, MAX_INTENSITY);

    if (allowedIntensity < intensity) {
        console.warn(`[GOVERNOR] Intensity reduced from ${intensity} to ${allowedIntensity} for proportional response.`);
    }

    return allowedIntensity;
};
