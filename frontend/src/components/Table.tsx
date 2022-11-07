import { createEffect, createMemo, createResource, createSignal, For } from "solid-js";

function encodeQueryParams(p: any) {
  return Object.entries(p)
  .map((kv: any) => kv.map(encodeURIComponent).join("="))
  .join("&");
}

async function fetchResource(params: any) {
  const queryParams = encodeQueryParams(params?.query || {});
  const data = await (await fetch(`${params.url}?${queryParams}`)).json();
  console.log(data);
  return data;
}

/* table component as a view for rest endpoint */
export default function Table (props: any) {
  const [objects] = createResource(() => [], () => fetchResource(props));
  const columns = createMemo((old: any): string[] => {
    const obj = objects()?.length > 0 ? objects()[0] : {};
    const cols = new Set(Object.keys(obj));
    const oldCols = new Set(old);
    if (cols === oldCols) {
      return old;
    }
    return Array.from(cols);
  });
  const [order, setOrder] = createSignal([] as string[]);
  createEffect(() => setOrder((old) => new Array(columns().length).fill('UNORDERED')));
  createEffect(() => console.log(order()));
  return <table>
    <thead>
      <For each={columns()}>{
        (column, id) =>
          <th><span>{column}</span><button>{order().at(id())}</button></th>
      }</For>
    </thead>
    <tbody>
      <For each={objects()}>{
        (item: any, id) =>
          <tr>
            <For each={columns()}>{
              (column, id) =>
                <td>{item[column]}</td>
            }</For>
          </tr>
      }</For>
    </tbody>
  </table>
}
