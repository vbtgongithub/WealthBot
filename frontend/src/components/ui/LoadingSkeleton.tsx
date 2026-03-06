export function SkeletonCard({ className = '' }: { className?: string }) {
  return (
    <div className={`card animate-pulse ${className}`}>
      <div className="h-4 w-1/3 rounded bg-background-hover mb-4" />
      <div className="space-y-3">
        <div className="h-3 w-full rounded bg-background-hover" />
        <div className="h-3 w-2/3 rounded bg-background-hover" />
      </div>
    </div>
  );
}

export function SkeletonText({ lines = 3, className = '' }: { lines?: number; className?: string }) {
  return (
    <div className={`space-y-2 animate-pulse ${className}`}>
      {Array.from({ length: lines }).map((_, i) => (
        <div
          key={i}
          className="h-3 rounded bg-background-hover"
          style={{ width: `${80 - i * 15}%` }}
        />
      ))}
    </div>
  );
}
