import React from 'react';
import PropTypes from 'prop-types';
import { BrowserRouter as Router, Routes, Route, Link, useLocation } from 'react-router-dom';
import { Wifi, Share2, Globe, Shield, Terminal } from 'lucide-react';

import WPAAttackController from './components/WPAAttackController';
import LateralMovementController from './components/LateralMovementController';
import WebAppAttackDashboard from './components/WebAppAttackDashboard';
import SituationalAwarenessDashboard from './components/SituationalAwarenessDashboard';

// eslint-disable-next-line no-unused-vars
const NavLink = ({ to, icon: Icon, label }) => {
  const location = useLocation();
  const active = location.pathname === to;
  return (
    <Link
      to={to}
      className={`flex items-center gap-3 p-3 rounded transition-all ${
        active ? 'bg-green-900/40 text-green-400 border-r-2 border-green-500' : 'text-gray-500 hover:text-gray-300 hover:bg-gray-800'
      }`}
    >
      <Icon className="w-5 h-5" />
      <span className="font-bold tracking-wide">{label}</span>
    </Link>
  );
};

NavLink.propTypes = {
  to: PropTypes.string.isRequired,
  icon: PropTypes.elementType.isRequired,
  label: PropTypes.string.isRequired
};

const App = () => {
  return (
    <Router>
      <div className="flex flex-col h-screen bg-black text-gray-300 overflow-hidden">
        {/* Top Bar */}
        <SituationalAwarenessDashboard />

        <div className="flex flex-1 overflow-hidden">
          {/* Sidebar */}
          <div className="w-64 bg-gray-900 border-r border-green-900 flex flex-col p-4">
             <div className="mb-8 flex items-center gap-2 text-green-500">
                <Shield className="w-8 h-8" />
                <div>
                    <h1 className="font-bold text-lg leading-none">WAR ROOM</h1>
                    <span className="text-xs text-gray-500 tracking-widest">CYBER MUZZLE</span>
                </div>
             </div>

             <nav className="space-y-2 flex-1">
                <div className="text-xs font-bold text-gray-600 mb-2 px-3">OFFENSIVE VECTORS</div>
                <NavLink to="/" icon={Wifi} label="WIFI OPS" />
                <NavLink to="/lateral" icon={Share2} label="LATERAL MOVEMENT" />
                <NavLink to="/web" icon={Globe} label="WEB EXPLOIT" />
             </nav>

             <div className="mt-auto border-t border-gray-800 pt-4">
                 <div className="flex items-center gap-3 text-red-500 p-3 bg-red-900/10 border border-red-900/30 rounded cursor-pointer hover:bg-red-900/20">
                     <Terminal className="w-5 h-5" />
                     <span className="font-bold text-sm">EMERGENCY KILL</span>
                 </div>
             </div>
          </div>

          {/* Main Content Area */}
          <div className="flex-1 bg-black relative overflow-hidden">
              <Routes>
                  <Route path="/" element={<WPAAttackController />} />
                  <Route path="/lateral" element={<LateralMovementController />} />
                  <Route path="/web" element={<WebAppAttackDashboard />} />
              </Routes>
          </div>
        </div>
      </div>
    </Router>
  );
};

export default App;
