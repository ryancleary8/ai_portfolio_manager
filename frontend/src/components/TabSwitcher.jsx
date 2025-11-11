import React from 'react';
import './TabSwitcher.css';

const tabs = [
  { id: 'performance', label: 'Performance' },
  { id: 'signals', label: 'AI Signals' },
  { id: 'trades', label: 'Trade History' }
];

export default function TabSwitcher({ activeTab, onChange }) {
  return (
    <div className="tab-switcher">
      {tabs.map((tab) => (
        <button
          key={tab.id}
          type="button"
          className={`tab-switcher__button ${activeTab === tab.id ? 'is-active' : ''}`}
          onClick={() => onChange(tab.id)}
        >
          {tab.label}
        </button>
      ))}
    </div>
  );
}

export { tabs };
