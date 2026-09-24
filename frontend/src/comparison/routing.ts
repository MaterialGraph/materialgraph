import type { CandidateResponse } from '../api';
import type { ObjectiveRequest } from '../objective/contract';
import type { ComparisonLaunchContext } from './launch';

export type DiscoveryContext = { kind: 'discovery'; avoid_element: string | null; prefer_element: string | null; limit: 10; include_substitution_paths: false };
export type ObjectiveContext = { kind: 'objective'; request: ObjectiveRequest };
export type RecordedContext = DiscoveryContext | ObjectiveContext;
export type ComparisonRoute = { source: number; candidates: number[]; workflow: 'discovery' | 'objective'; context: RecordedContext | null };
export type ParseResult = { kind: 'notComparison' } | { kind: 'validComparison'; route: ComparisonRoute } | { kind: 'invalidComparison'; error: string };

const symbols = new Set('H He Li Be B C N O F Ne Na Mg Al Si P S Cl Ar K Ca Sc Ti V Cr Mn Fe Co Ni Cu Zn Ga Ge As Se Br Kr Rb Sr Y Zr Nb Mo Tc Ru Rh Pd Ag Cd In Sn Sb Te I Xe Cs Ba La Ce Pr Nd Pm Sm Eu Gd Tb Dy Ho Er Tm Yb Lu Hf Ta W Re Os Ir Pt Au Hg Tl Pb Bi Po At Rn Fr Ra Ac Th Pa U Np Pu Am Cm Bk Cf Es Fm Md No Lr Rf Db Sg Bh Hs Mt Ds Rg Cn Nh Fl Mc Lv Ts Og'.split(' '));
const keys = ['view', 'v', 'source', 'candidates', 'workflow', 'context'];
const integer = (v: unknown): v is number => typeof v === 'number' && Number.isSafeInteger(v) && v > 0;
const symbol = (v: unknown): v is string => typeof v === 'string' && symbols.has(v);
const exact = (value: Record<string, unknown>, fields: string[]) => Object.keys(value).length === fields.length && fields.every(field => Object.hasOwn(value, field));
const record = (v: unknown): v is Record<string, unknown> => !!v && typeof v === 'object' && !Array.isArray(v);
const array = (v: unknown): v is string[] => Array.isArray(v) && v.length <= 32 && new Set(v).size === v.length && v.every(symbol);

function duplicateKeys(raw: string): boolean {
  // JSON.parse accepts duplicate keys; scan member names outside strings to reject them.
  const stack: Array<Set<string> | null> = [];
  let i = 0, pending: string | null = null;
  while (i < raw.length) {
    const ch = raw[i];
    if (ch === '"') {
      const start = i++;
      while (i < raw.length) { if (raw[i] === '\\') { i += 2; continue; } if (raw[i++] === '"') break; }
      const str = JSON.parse(raw.slice(start, i)) as string;
      let next = i; while (/\s/.test(raw[next] ?? '')) next++;
      if (raw[next] === ':' && stack.at(-1) instanceof Set) pending = str;
      continue;
    }
    if (ch === '{') stack.push(new Set());
    else if (ch === '[') stack.push(null);
    else if (ch === '}' || ch === ']') stack.pop();
    else if (ch === ':' && pending !== null) { const set = stack.at(-1); if (set instanceof Set) { if (set.has(pending)) return true; set.add(pending); } pending = null; }
    i++;
  }
  return false;
}

function validContext(value: unknown, workflow: ComparisonRoute['workflow']): value is RecordedContext {
  if (!record(value) || value.kind !== workflow) return false;
  if (workflow === 'discovery') return exact(value, ['kind','avoid_element','prefer_element','limit','include_substitution_paths']) &&
    (value.avoid_element === null || symbol(value.avoid_element)) && (value.prefer_element === null || symbol(value.prefer_element)) && value.limit === 10 && value.include_substitution_paths === false;
  if (!exact(value, ['kind','request']) || !record(value.request) || !exact(value.request, ['objective','mode','limit'])) return false;
  const req = value.request, obj = req.objective;
  return record(obj) && exact(obj, ['avoid_elements','prefer_elements','preserve_elements','target_family','max_hops','limit','prefer_lower_criticality','require_stable_materials']) &&
    array(obj.avoid_elements) && array(obj.prefer_elements) && array(obj.preserve_elements) &&
    (obj.target_family === null || obj.target_family === 'phosphate') &&
    integer(obj.max_hops) && obj.max_hops <= 3 && integer(obj.limit) && obj.limit <= 20 &&
    typeof obj.prefer_lower_criticality === 'boolean' && typeof obj.require_stable_materials === 'boolean' &&
    ['balanced','exploratory','strict'].includes(String(req.mode)) && integer(req.limit) && req.limit <= 20;
}

function canonicalContext(value: RecordedContext): RecordedContext {
  if (value.kind === 'discovery') return {kind:'discovery',avoid_element:value.avoid_element,prefer_element:value.prefer_element,limit:10,include_substitution_paths:false};
  const o = value.request.objective;
  return {kind:'objective',request:{objective:{avoid_elements:[...o.avoid_elements],prefer_elements:[...o.prefer_elements],preserve_elements:[...o.preserve_elements],target_family:o.target_family,max_hops:o.max_hops,limit:o.limit,prefer_lower_criticality:o.prefer_lower_criticality,require_stable_materials:o.require_stable_materials},mode:value.request.mode,limit:value.request.limit}};
}
const encode = (v: string) => { const bytes = new TextEncoder().encode(v); let binary = ''; bytes.forEach(b => {binary += String.fromCharCode(b);}); return btoa(binary).replaceAll('+','-').replaceAll('/','_').replace(/=+$/,''); };
function decode(encoded: string): string {
  if (!/^[A-Za-z0-9_-]+$/.test(encoded) || encoded.length % 4 === 1) throw Error('base64');
  const binary = atob(encoded.replaceAll('-','+').replaceAll('_','/') + '='.repeat((4 - encoded.length % 4) % 4));
  return new TextDecoder('utf-8', {fatal:true}).decode(Uint8Array.from(binary, c => c.charCodeAt(0)));
}

export function serializeComparison(route: ComparisonRoute): string {
  if (!integer(route.source) || ![2,3].includes(route.candidates.length) || !route.candidates.every(integer) || new Set([route.source,...route.candidates]).size !== route.candidates.length + 1 || !['discovery','objective'].includes(route.workflow)) throw Error('Invalid comparison');
  const params = new URLSearchParams();
  params.set('view','compare'); params.set('v','1'); params.set('source',String(route.source));
  params.set('candidates',route.candidates.join(',')); params.set('workflow',route.workflow);
  if (route.context !== null) {
    if (!validContext(route.context,route.workflow)) throw Error('Invalid context');
    const json = JSON.stringify(canonicalContext(route.context));
    if (new TextEncoder().encode(json).length > 900) throw Error('Oversized context');
    params.set('context',encode(json));
  }
  const url = `/?${params.toString().replaceAll('%2C',',')}`;
  if (url.length > 1600 || (params.get('context')?.length ?? 0) > 1200) throw Error('Oversized URL');
  return url;
}

export function parseComparison(search: string): ParseResult {
  const query = search.startsWith('/?') ? search.slice(1) : search;
  const params = new URLSearchParams(query);
  if (!params.has('view')) return {kind:'notComparison'};
  const invalid = (error:string): ParseResult => ({kind:'invalidComparison',error});
  if (query.length + 1 > 1600) return invalid('oversized-url');
  for (const key of new Set(params.keys())) if (params.getAll(key).length > 1) return invalid('duplicate-parameter');
  if ([...params.keys()].some(key => !keys.includes(key))) return invalid('unsupported-parameter');
  if (params.get('view') !== 'compare') return invalid('unsupported-view');
  for (const key of keys.slice(0,5)) if (!params.has(key)) return invalid('missing-parameter');
  if (params.get('v') !== '1') return invalid('unsupported-version');
  const parseId = (s: string) => /^[1-9][0-9]*$/.test(s) && Number.isSafeInteger(Number(s));
  const sourceText = params.get('source')!;
  if (!parseId(sourceText)) return invalid('invalid-source');
  const candidateTexts = params.get('candidates')!.split(',');
  if (![2,3].includes(candidateTexts.length) || !candidateTexts.every(parseId)) return invalid('invalid-candidates');
  const source = Number(sourceText), candidates = candidateTexts.map(Number);
  if (new Set([source,...candidates]).size !== candidates.length + 1) return invalid('duplicate-material');
  const workflow = params.get('workflow');
  if (workflow !== 'discovery' && workflow !== 'objective') return invalid('invalid-workflow');
  let context: RecordedContext | null = null;
  if (params.has('context')) {
    const encoded = params.get('context')!;
    if (encoded.length > 1200) return invalid('oversized-context');
    try {
      const json = decode(encoded);
      if (new TextEncoder().encode(json).length > 900) return invalid('oversized-context');
      if (duplicateKeys(json)) return invalid('malformed-context');
      const parsed: unknown = JSON.parse(json);
      if (record(parsed) && parsed.kind !== workflow) return invalid('context-kind-mismatch');
      if (!validContext(parsed,workflow)) return invalid('malformed-context');
      context = parsed;
      if (encode(JSON.stringify(canonicalContext(context))) !== encoded) return invalid('malformed-context');
    } catch { return invalid('malformed-context'); }
  }
  return {kind:'validComparison',route:{source,candidates,workflow,context}};
}

export function routeFromDiscovery(launch: ComparisonLaunchContext, result: CandidateResponse): ComparisonRoute {
  return {source:launch.sourceMaterialId,candidates:launch.selectedMaterials.map(m=>m.id),workflow:'discovery',context:{kind:'discovery',avoid_element:result.discovery_goal.avoid_element,prefer_element:result.discovery_goal.prefer_element,limit:10,include_substitution_paths:false}};
}
export function routeFromObjective(launch: ComparisonLaunchContext, request: ObjectiveRequest): ComparisonRoute {
  return {source:launch.sourceMaterialId,candidates:launch.selectedMaterials.map(m=>m.id),workflow:'objective',context:{kind:'objective',request}};
}
