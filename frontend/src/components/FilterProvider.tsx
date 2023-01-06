import { createSignal, createEffect, createResource, createContext, useContext, Resource, Accessor, Setter } from "solid-js";
import pako from 'pako';
import {bytesToBase64} from './base64';
import { isInteger } from "lodash-es";


async function fetchProperties() {
  const res = await fetch('/api/schema/plant');
  const json = await res.json();
  return json;
}

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

export function prepareQueryParams(model: FilterModel): object {
  return {
    url: model.url,
    resource: model.resource,
    search: model.search(),
    filterField: model.filterField(),
    filterValue: model.filterValue(),
    ordering: model.ordering(),
    page: model.page(),
    pageSize: model.pageSize()
  }
}

export async function fetchResource(params: any) {
  const queryParams: any = {}; //encodeQueryParams(params?.query || {});
  if (params.search) {
    queryParams.filter = { '*': params.search };
  }
  else if (params.filterField && params.filterValue) {
    queryParams.filter = { [params.filterField]: params.filterValue };
  }
  if (isInteger(params.page)) {
    queryParams.page = params.page;
  }
  if (isInteger(params.pageSize)) {
    queryParams.size = params.pageSize;
  }
  const encodedParams = encodeQueryParams(queryParams);
  const uri = `${params.url}/api/${params.resource}?${encodedParams}`;
  console.log(uri);
  const data = await (await fetch(uri)).json();
  return data;
}

export function downloadFilteredData(format: string, queryParams: any) {
  const query = encodeQueryParams(queryParams);
  const link = document.createElement('a');
  link.href = `/api/download/${format}?${query}`;
  console.log(`Link: ${link.href}`);
  link.click();
}

export const FilterContext = createContext<any>();

interface FilterModel {
    url: string
    resource: string
    orderingLabels: string[]
    fields: Resource<string[]>
    search: Accessor<any>
    setSearch: Setter<any>
    filterField: Accessor<any>
    setFilterField: Setter<any>
    filterValue: Accessor<any>
    setFilterValue: Setter<any>
    ordering: Accessor<number[]>
    setOrdering: Setter<number[]>
    page: Accessor<number>
    setPage: Setter<number>
    pageSize: Accessor<number>
    setPageSize: Setter<number>
    next: () => void
    previous: () => void
}

/* Filtering context */
export function FilterProvider(props: any) {
  const url = props.url;
  const resource = props.resource;
  const [fields] = createResource<string[]>(fetchProperties);
  const [search, setSearch] = createSignal<string>(props.search || '');
  const [filterField, setFilterField] = createSignal(props.filterField || null);
  const [filterValue, setFilterValue] = createSignal(props.filterValue || null);
  const [page, setPage] = createSignal(props.page || 0);
  const [pageSize, setPageSize] = createSignal(props.pageSize || 5);
  const [ordering, setOrdering] = createSignal(props.page || []);

  createEffect(() => filterField() && setSearch(''));
  createEffect(() => search() && setFilterField(null));
  createEffect(() => {
    console.log('Search input changed:', search());
  });
  const orderingLabels = ['Unordered', 'Descending', 'Ascending'];
  const ctx = {
    next: () => setPage(page() + 1),
    previous: () => page() > 0 && setPage(page() - 1),
    orderingLabels, url, resource, pageSize, setPageSize,
    fields, search, setSearch, filterField, setFilterField,
    filterValue, setFilterValue, page, setPage, ordering, setOrdering
  }

  return <FilterContext.Provider value={ctx as typeof ctx}>
      {props.children}
    </FilterContext.Provider>
}

export function useFilter(): FilterModel {
  return useContext(FilterContext);
}
