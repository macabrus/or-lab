import { createSignal, createEffect, createResource, createContext, useContext, Resource, Accessor, Setter } from "solid-js";

async function fetchProperties() {
  const res = await fetch('http://localhost:8080/api/schema/plant');
  const json = await res.json();
  return json;
}

const FilterContext = createContext<any>();

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
  const [ordering, setOrdering] = createSignal(props.page || []);
  createEffect(() => filterField() && setSearch(''));
  createEffect(() => search() && setFilterField(null));
  createEffect(() => {
    console.log('Search input changed:', search());
  });
  const orderingLabels = ['Unordered', 'Descending', 'Ascending'];
  const ctx = {
    orderingLabels, url, resource,
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
