import './Table.module.css';
import './Spinner.css';

import { createEffect, createMemo, createResource, createSignal, For, Show, Suspense } from "solid-js";
import { debounce, startCase } from 'lodash-es';
import { useFilter, fetchResource } from './FilterProvider';


function Spinner() {
  return <div class="lds-spinner"><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div></div>
}

/* table component as a view for rest endpoint */
export default function Table (props: any) {
  const {url, resource, fields, ordering, orderingLabels, search, filterField, filterValue, page, pageSize} = useFilter();
  const [loading, setLoading] = createSignal(false);
  const [objects, {refetch}] = createResource<any[]>(async () => {
    const res = await fetchResource({
      url,
      resource,
      search: search(),
      filterField: filterField(),
      filterValue: filterValue(),
      ordering: ordering(),
      page: page(),
      pageSize: pageSize()
    });
    setLoading(false);
    return res;
  });
  const debouncedRefetch = debounce(refetch, 500);
  createEffect(() => {
    /* Change in any of following variables should trigger a debounced refetch */
    search(); filterValue(); filterField(); ordering(); page(); pageSize();
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
