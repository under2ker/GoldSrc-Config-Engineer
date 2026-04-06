import { Skeleton } from "@/components/ui/skeleton";

/** Fallback для React.lazy по маршрутам. */
export function PageLoading() {
  return (
    <div className="mx-auto flex w-full max-w-5xl flex-col gap-6 px-1 py-2">
      <div className="space-y-2">
        <Skeleton className="h-6 w-2/3 max-w-md" />
        <Skeleton className="h-4 w-full max-w-xl" />
      </div>
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {Array.from({ length: 6 }).map((_, i) => (
          <div key={i} className="space-y-3 rounded-xl border border-border p-4">
            <Skeleton className="h-5 w-4/5" />
            <Skeleton className="h-3 w-full" />
            <Skeleton className="h-9 w-full" />
          </div>
        ))}
      </div>
      <Skeleton className="h-36 w-full rounded-xl" />
    </div>
  );
}
