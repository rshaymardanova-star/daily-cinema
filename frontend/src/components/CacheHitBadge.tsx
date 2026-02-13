interface CacheHitBadgeProps {
  cacheHit?: boolean;
}

export default function CacheHitBadge({ cacheHit }: CacheHitBadgeProps) {
  if (!cacheHit) return null;

  return (
    <span className="inline-flex items-center gap-1 rounded-full bg-emerald-900/40 px-2.5 py-0.5 text-xs font-medium text-emerald-400 ring-1 ring-emerald-500/20">
      <span className="inline-block h-1.5 w-1.5 rounded-full bg-emerald-400" />
      Loaded from cache — no ACU spent
    </span>
  );
}
