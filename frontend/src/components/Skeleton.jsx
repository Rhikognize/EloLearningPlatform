export function Skeleton({ className = '' }) {
  return (
    <div className={`bg-surface-hover rounded-lg animate-pulse ${className}`} />
  )
}

export function CardSkeleton() {
  return (
    <div className="bg-surface rounded-xl p-4 border border-surface-hover">
      <Skeleton className="h-4 w-3/4 mb-3" />
      <Skeleton className="h-3 w-1/2 mb-2" />
      <Skeleton className="h-3 w-1/4" />
    </div>
  )
}

export function ProfileSkeleton() {
  return (
    <div className="bg-surface rounded-xl p-6 border border-surface-hover">
      <div className="flex items-center gap-4 mb-4">
        <Skeleton className="h-16 w-16 rounded-full" />
        <div className="flex-1">
          <Skeleton className="h-5 w-1/3 mb-2" />
          <Skeleton className="h-4 w-1/4" />
        </div>
      </div>
      <Skeleton className="h-3 w-full mb-2" />
      <Skeleton className="h-3 w-5/6" />
    </div>
  )
}