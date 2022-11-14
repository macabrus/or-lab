import './Table.module.css';
import './Spinner.css';

import { createEffect, createMemo, createResource, createSignal, For, Show, Suspense } from "solid-js";
import { debounce, startCase } from 'lodash-es';
import { useFilter } from './FilterProvider';
import pako from 'pako';
import {bytesToBase64} from './base64';


/* Encode query parameters with compression, base64 and urlencoding */
function encodeQueryParams(p: any) {
  const r = Object.entries(p)
  .map(([k, v]) => { // serialize all values
    if (v instanceof Object || Array.isArray(v) || v instanceof Number) {
      return [k, bytesToBase64(pako.deflate(JSON.stringify(v)))];
    }
    return [k, v];
  })
  .map((kv: any) => kv.map(encodeURIComponent).join("="))
  .join("&");
  console.log(Object.entries(p));
  return r;
}

async function fetchResource(params: any) {
  const queryParams: any = {}; //encodeQueryParams(params?.query || {});
  if (params.search) {
    queryParams.filter = { '*': params.search };
  }
  else if (params.filterField && params.filterValue) {
    queryParams.filter = { [params.filterField]: params.filterValue };
  }
  const encodedParams = encodeQueryParams(queryParams);
  console.log(encodedParams);
  const uri = `${params.url}/api/${params.resource}?${encodedParams}`;
  console.log(uri);
  const data = await (await fetch(uri)).json();
  console.log(data);
  return data;
}

function Spinner() {
  return <div class="lds-spinner"><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div></div>
}

/* table component as a view for rest endpoint */
export default function Table (props: any) {
  const {url, resource, fields, ordering, orderingLabels, search, filterField, filterValue} = useFilter();
  const [loading, setLoading] = createSignal(false);
  const [objects, {refetch}] = createResource<any[]>(async () => {
    const res = await fetchResource({
      url,
      resource,
      search: search(),
      filterField: filterField(),
      filterValue: filterValue(),
      ordering: ordering()
    });
    setLoading(false);
    return res;
  });
  const debouncedRefetch = debounce(refetch, 500);
  createEffect(() => {
    /* Change in any of following variables should trigger a debounced refetch */
    search(); filterValue(); filterField(); ordering();
    setLoading(true);
    debouncedRefetch();
  });
  return <>
    <Show when={!loading()} fallback={<div><Spinner></Spinner></div>}>
      <table>
        <thead>
          <For each={fields()}>{
            (column, id) =>
              <th>
                <span>{startCase(column)}</span>
                <button>{orderingLabels[ordering()[id()]]}</button>
              </th>
          }</For>
        </thead>
        <tbody>
          <For each={objects()}>{
            (item, id) =>
              <tr>
                <For each={fields()}>{
                  (field, id) =>
                    <td>{String(item[field])}</td>
                }</For>
              </tr>
          }</For>
        </tbody>
      </table>
    </Show>
  </>
}
