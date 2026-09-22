import { useEffect, useState } from 'react';
import { ApiError } from '../api';
import type { ObjectiveRequest, ObjectiveResponse } from './contract';
import { exploreObjective } from './request';

type Submitted = { request: ObjectiveRequest; sequence: number };

export function errorDetails(error: unknown): string[] {
  if (!(error instanceof ApiError)) return ['The investigation could not be completed. Please try again.'];
  if (error.status !== 422) return [error.message];
  const detail = (error.details as { detail?: unknown } | null)?.detail;
  if (!Array.isArray(detail)) return [typeof detail === 'string' ? detail : error.message];
  return detail.map((item: { loc?: unknown; msg?: unknown }) => {
    const field = Array.isArray(item.loc) ? item.loc.filter(part => part !== 'body').join(' → ') : 'Objective';
    return `${field || 'Objective'}: ${String(item.msg ?? 'Invalid value')}`;
  });
}

export function useObjectiveInvestigation(materialId: number) {
  const [submitted, setSubmitted] = useState<Submitted | null>(null);
  const [result, setResult] = useState<ObjectiveResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [errors, setErrors] = useState<string[]>([]);

  useEffect(() => {
    if (!submitted) return;
    const controller = new AbortController();
    setLoading(true);
    setErrors([]);
    setResult(null);
    exploreObjective(materialId, submitted.request, controller.signal)
      .then(response => { if (!controller.signal.aborted) setResult(response); })
      .catch(error => { if (!controller.signal.aborted) setErrors(errorDetails(error)); })
      .finally(() => { if (!controller.signal.aborted) setLoading(false); });
    return () => controller.abort();
  }, [materialId, submitted]);

  function run(request: ObjectiveRequest) {
    setResult(null); setErrors([]); setLoading(true);
    setSubmitted(previous => ({ request, sequence: (previous?.sequence ?? 0) + 1 }));
  }
  function retry() {
    if (submitted) run(submitted.request);
  }
  return { submitted: submitted?.request ?? null, result, loading, errors, run, retry };
}
