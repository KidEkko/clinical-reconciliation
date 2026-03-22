type TabNavProps = {
  tabs: Array<{ label: string; value: number }>;
  activeTab: number;
  onTabChange: (tab: number) => void;
  disabled?: boolean;
};

export default function TabNav({ tabs, activeTab, onTabChange, disabled = false }: TabNavProps) {
  return (
    <nav className="bg-card/50">
      <div className="flex gap-2">
        {tabs.map((tab) => {
          const isActive = activeTab === tab.value;
          return (
            <button
              key={tab.value}
              onClick={() => onTabChange(tab.value)}
              disabled={disabled}
              className={`
                relative px-6 py-3 text-sm font-medium transition-all rounded-t-lg
                ${isActive
                  ? 'border-l border-t border-r border-primary bg-primary/20 text-primary hover:bg-primary/30'
                  : 'bg-muted/40 text-muted-foreground hover:bg-muted/60 hover:text-foreground'
                }
                ${disabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}
              `}
            >
              {tab.label}
            </button>
          );
        })}
      </div>
    </nav>
  );
}
