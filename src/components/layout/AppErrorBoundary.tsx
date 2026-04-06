import { Component, type ErrorInfo, type ReactNode } from "react";
import { AlertTriangle } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";

type Props = { children: ReactNode };

type State = { error: Error | null };

/** Не даёт одному упавшему экрану сломать весь shell (ТЗ «ошибки не ломают UI»). */
export class AppErrorBoundary extends Component<Props, State> {
  state: State = { error: null };

  static getDerivedStateFromError(error: Error): State {
    return { error };
  }

  componentDidCatch(error: Error, info: ErrorInfo) {
    console.error("AppErrorBoundary:", error, info.componentStack);
  }

  render() {
    if (this.state.error) {
      return (
        <div className="flex min-h-[40vh] items-center justify-center p-6">
          <Card className="max-w-lg border-destructive/30">
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-destructive">
                <AlertTriangle className="size-5" />
                Что-то пошло не так
              </CardTitle>
              <CardDescription>
                Ошибка в этом разделе. Остальная программа продолжает работать — откройте другой пункт меню.
              </CardDescription>
            </CardHeader>
            <CardContent>
              <pre className="max-h-40 overflow-auto rounded-md border bg-muted/40 p-3 font-mono text-xs break-words whitespace-pre-wrap">
                {this.state.error.message}
              </pre>
            </CardContent>
            <CardFooter>
              <Button
                type="button"
                variant="secondary"
                onClick={() => this.setState({ error: null })}
              >
                Попробовать снова
              </Button>
            </CardFooter>
          </Card>
        </div>
      );
    }
    return this.props.children;
  }
}
