import { Component } from "react";
import type { ErrorInfo, ReactNode } from "react";
import { Button } from "@/components/ui/button";

interface Props {
  children: ReactNode;
}

interface State {
  hasError: boolean;
  error: Error | null;
}

export default class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, info: ErrorInfo) {
    console.error("ErrorBoundary caught:", error, info.componentStack);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="flex min-h-screen flex-col items-center justify-center gap-4 p-8">
          <h1 className="text-2xl font-bold">Something went wrong</h1>
          <p className="max-w-md text-center text-muted-foreground">
            An unexpected error occurred. You can try reloading the page.
          </p>
          <pre className="max-w-lg overflow-auto rounded border bg-muted p-4 text-xs">
            {this.state.error?.message}
          </pre>
          <Button onClick={() => window.location.reload()}>Reload page</Button>
        </div>
      );
    }

    return this.props.children;
  }
}
