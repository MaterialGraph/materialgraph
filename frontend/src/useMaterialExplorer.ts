import { useEffect, useState } from 'react';
import { candidates, listMaterials, materialDetail, type CandidateResponse, type Material, type MaterialDetail } from './api';

export function initialMaterialId(search: string): number {
  const id = Number(new URLSearchParams(search).get('material'));
  return Number.isSafeInteger(id) && id > 0 ? id : 0;
}

export function useMaterialExplorer() {
  const [selected, setSelected] = useState(() => initialMaterialId(location.search));
  const [items, setItems] = useState<Material[]>([]);
  const [offset, setOffset] = useState(0);
  const [listRetry, setListRetry] = useState(0);
  const [detailRetry, setDetailRetry] = useState(0);
  const [listError, setListError] = useState('');
  const [listLoading, setListLoading] = useState(false);
  const [detail, setDetail] = useState<MaterialDetail | null>(null);
  const [detailError, setDetailError] = useState('');
  const [detailLoading, setDetailLoading] = useState(false);
  const [avoid, setAvoid] = useState('');
  const [prefer, setPrefer] = useState('');
  const [result, setResult] = useState<CandidateResponse | null>(null);
  const [candidateError, setCandidateError] = useState('');
  const [candidateLoading, setCandidateLoading] = useState(false);
  const [request, setRequest] = useState<{ id: number; avoid: string; prefer: string; sequence: number } | null>(null);

  useEffect(() => {
    const controller = new AbortController();
    setListLoading(true); setListError('');
    listMaterials(offset, controller.signal).then(page => setItems(previous => offset ? [...previous, ...page] : page))
      .catch(error => { if (!controller.signal.aborted) setListError(error.message); })
      .finally(() => { if (!controller.signal.aborted) setListLoading(false); });
    return () => controller.abort();
  }, [offset, listRetry]);

  useEffect(() => {
    if (!selected) return;
    const controller = new AbortController();
    setDetail(null); setResult(null); setRequest(null); setDetailError(''); setDetailLoading(true);
    materialDetail(selected, controller.signal).then(setDetail)
      .catch(error => { if (!controller.signal.aborted) setDetailError(error.message); })
      .finally(() => { if (!controller.signal.aborted) setDetailLoading(false); });
    return () => controller.abort();
  }, [selected, detailRetry]);

  useEffect(() => {
    if (!request) return;
    const controller = new AbortController();
    setResult(null); setCandidateError(''); setCandidateLoading(true);
    candidates(request.id, request.avoid, request.prefer, controller.signal).then(setResult)
      .catch(error => { if (!controller.signal.aborted) setCandidateError(error.message); })
      .finally(() => { if (!controller.signal.aborted) setCandidateLoading(false); });
    return () => controller.abort();
  }, [request]);

  function select(id: number) {
    setSelected(id);
    const url = new URL(location.href);
    url.searchParams.set('material', String(id));
    history.replaceState(null, '', url);
  }
  function searchCandidates() {
    setRequest(previous => ({ id: selected, avoid, prefer, sequence: (previous?.sequence ?? 0) + 1 }));
  }
  return {
    selected, select, items, offset, loadMore: () => setOffset(items.length), listError, listLoading,
    retryList: () => setListRetry(n => n + 1), detail, detailError, detailLoading,
    retryDetail: () => setDetailRetry(n => n + 1), avoid, setAvoid, prefer, setPrefer,
    result, candidateError, candidateLoading, searchCandidates,
  };
}
