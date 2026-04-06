import { useCallback, useState } from "react";

export type UseAsyncState<TResult> = {
  data: TResult | null;
  error: unknown;
  loading: boolean;
};

/** Состояние для асинхронных вызовов (IPC, fetch). */
export function useAsyncFn<TArgs extends unknown[], TResult>(
  fn: (...args: TArgs) => Promise<TResult>,
) {
  const [state, setState] = useState<UseAsyncState<TResult>>({
    data: null,
    error: null,
    loading: false,
  });

  const execute = useCallback(
    async (...args: TArgs) => {
      setState({ data: null, error: null, loading: true });
      try {
        const data = await fn(...args);
        setState({ data, error: null, loading: false });
        return data;
      } catch (error) {
        setState({ data: null, error, loading: false });
        throw error;
      }
    },
    [fn],
  );

  const reset = useCallback(() => {
    setState({ data: null, error: null, loading: false });
  }, []);

  return { ...state, execute, reset };
}
