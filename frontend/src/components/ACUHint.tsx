interface ACUHintProps {
  level: "low" | "high" | "info";
  children: React.ReactNode;
}

const LEVEL_STYLES = {
  low: "text-green-400/70",
  high: "text-amber-400/70",
  info: "text-gray-500",
};

export default function ACUHint({ level, children }: ACUHintProps) {
  return (
    <span className={`inline-flex items-center gap-1 text-xs ${LEVEL_STYLES[level]}`}>
      <span className="inline-block h-1.5 w-1.5 rounded-full bg-current opacity-60" />
      {children}
    </span>
  );
}
