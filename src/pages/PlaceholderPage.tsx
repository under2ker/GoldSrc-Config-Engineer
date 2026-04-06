import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { pageShellNarrowClass } from "@/lib/layoutTokens";

export function PlaceholderPage({
  title,
  description,
}: {
  title: string;
  description?: string;
}) {
  return (
    <div className={pageShellNarrowClass}>
    <Card className="w-full border-border bg-card">
      <CardHeader>
        <CardTitle>{title}</CardTitle>
        {description ? (
          <CardDescription>{description}</CardDescription>
        ) : (
          <CardDescription>Раздел в разработке — скоро появится функциональность.</CardDescription>
        )}
      </CardHeader>
      <CardContent className="text-sm text-muted-foreground" />
    </Card>
    </div>
  );
}
