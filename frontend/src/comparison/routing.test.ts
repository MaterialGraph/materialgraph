import { describe, expect, it } from 'vitest';
import { parseComparison, serializeComparison, type ComparisonRoute } from './routing';

const discovery: ComparisonRoute = {source:5,candidates:[6,8],workflow:'discovery',context:{kind:'discovery',avoid_element:'Li',prefer_element:'Na',limit:10,include_substitution_paths:false}};
const objective: ComparisonRoute = {source:5,candidates:[6,8],workflow:'objective',context:{kind:'objective',request:{objective:{avoid_elements:['Li','Co'],prefer_elements:['Na','K'],preserve_elements:['Fe','P','O'],target_family:'phosphate',max_hops:2,limit:7,prefer_lower_criticality:true,require_stable_materials:false},mode:'balanced',limit:5}}};
const category = (url:string) => { const result = parseComparison(url); return result.kind === 'invalidComparison' ? result.error : result.kind; };
const encoded = (obj: unknown) => btoa(JSON.stringify(obj)).replaceAll('+','-').replaceAll('/','_').replace(/=+$/,'');

describe('comparison URL v1', () => {
  it('serializes Discovery with exact canonical field order and round-trips two and three candidates', () => {
    for (const candidates of [[6,8],[6,7,8]]) {
      const url = serializeComparison({...discovery,candidates});
      expect(url).toBe(`/?view=compare&v=1&source=5&candidates=${candidates.join(',')}&workflow=discovery&context=eyJraW5kIjoiZGlzY292ZXJ5IiwiYXZvaWRfZWxlbWVudCI6IkxpIiwicHJlZmVyX2VsZW1lbnQiOiJOYSIsImxpbWl0IjoxMCwiaW5jbHVkZV9zdWJzdGl0dXRpb25fcGF0aHMiOmZhbHNlfQ`);
      const parsed = parseComparison(url); expect(parsed.kind).toBe('validComparison');
      if (parsed.kind === 'validComparison') expect(serializeComparison(parsed.route)).toBe(url);
    }
  });
  it('retains nulls and accepts missing context', () => {
    const url = serializeComparison({...discovery,context:{...discovery.context!,kind:'discovery',avoid_element:null,prefer_element:null} as ComparisonRoute['context']});
    expect(url).toContain('bnVsbC');
    expect(parseComparison(url)).toMatchObject({kind:'validComparison',route:{context:{avoid_element:null,prefer_element:null}}});
    expect(parseComparison('/?view=compare&v=1&source=5&candidates=6,8&workflow=discovery')).toMatchObject({kind:'validComparison',route:{context:null}});
  });
  it('preserves Objective arrays, both independent limits, and null family', () => {
    if (objective.context?.kind !== 'objective') throw Error('Fixture');
    const request = objective.context.request;
    for (const family of ['phosphate',null] as const) for (const candidates of [[6,8],[6,7,8]]) {
      const state = {...objective,candidates,context:{kind:'objective' as const,request:{objective:{...request.objective,target_family:family},mode:request.mode,limit:request.limit}}};
      const url = serializeComparison(state);
      const parsed = parseComparison(url);
      expect(parsed).toMatchObject({kind:'validComparison',route:{candidates,context:{request:{objective:{limit:7,target_family:family,avoid_elements:['Li','Co']},limit:5}}}});
      if (parsed.kind === 'validComparison') expect(serializeComparison(parsed.route)).toBe(url);
    }
  });
  it('uses the uninterrupted accepted LiFePO4 Objective reference vector', () => {
    const request = objective.context?.kind === 'objective' ? objective.context.request : null;
    if (!request) throw Error('Fixture');
    const url = serializeComparison({...objective,context:{kind:'objective',request:{...request,objective:{...request.objective,limit:5}}}});
    expect(url).toBe('/?view=compare&v=1&source=5&candidates=6,8&workflow=objective&context=eyJraW5kIjoib2JqZWN0aXZlIiwicmVxdWVzdCI6eyJvYmplY3RpdmUiOnsiYXZvaWRfZWxlbWVudHMiOlsiTGkiLCJDbyJdLCJwcmVmZXJfZWxlbWVudHMiOlsiTmEiLCJLIl0sInByZXNlcnZlX2VsZW1lbnRzIjpbIkZlIiwiUCIsIk8iXSwidGFyZ2V0X2ZhbWlseSI6InBob3NwaGF0ZSIsIm1heF9ob3BzIjoyLCJsaW1pdCI6NSwicHJlZmVyX2xvd2VyX2NyaXRpY2FsaXR5Ijp0cnVlLCJyZXF1aXJlX3N0YWJsZV9tYXRlcmlhbHMiOmZhbHNlfSwibW9kZSI6ImJhbGFuY2VkIiwibGltaXQiOjV9fQ');
  });
  it.each([
    ['v=2','unsupported-version'],['source=','invalid-source'],['source=05','invalid-source'],['source=5.0','invalid-source'],['source=0','invalid-source'],['source=-5','invalid-source'],
    ['candidates=6','invalid-candidates'],['candidates=6,7,8,9','invalid-candidates'],['candidates=6,6','duplicate-material'],['candidates=5,6','duplicate-material'],
    ['workflow=other','invalid-workflow'],
  ])('rejects %s', (replacement,error) => {
    const original = '/?view=compare&v=1&source=5&candidates=6,8&workflow=discovery';
    const name = replacement.split('=')[0];
    expect(category(original.replace(new RegExp(`${name}=[^&]*`),replacement))).toBe(error);
  });
  it('rejects parameter ambiguity and invalid context', () => {
    const base = '/?view=compare&v=1&source=5&candidates=6,8&workflow=discovery';
    expect(category(base.replace('&source=5',''))).toBe('missing-parameter');
    for (const key of ['source','candidates','workflow','context']) expect(category(`${base}&${key}=x`)).toBe(key === 'context' ? 'malformed-context' : 'duplicate-parameter');
    expect(category(`${base}&material=5`)).toBe('unsupported-parameter');
    expect(category(`${base}&other=1`)).toBe('unsupported-parameter');
    expect(category(`${base}&context=%%%`)).toBe('malformed-context');
    expect(category(`${base}&context=${encoded('not-json')}`)).toBe('malformed-context');
    expect(category(`${base}&context=${encoded(objective.context)}`)).toBe('context-kind-mismatch');
    expect(category(`${base}&context=${encoded({kind:'discovery',avoid_element:'Li',prefer_element:'Na',limit:11,include_substitution_paths:false})}`)).toBe('malformed-context');
    expect(category(`${base}&context=${'A'.repeat(1201)}`)).toBe('oversized-context');
    expect(category(`${base}&context=${'A'.repeat(1600)}`)).toBe('oversized-url');
    expect(category(`${base}&context=${encoded({kind:'discovery',avoid_element:'Li',prefer_element:'Na',limit:10,include_substitution_paths:false,padding:'x'.repeat(850)})}`)).toBe('oversized-context');
  });
});
