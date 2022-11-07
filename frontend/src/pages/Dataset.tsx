import { createEffect, createSignal } from "solid-js";
import Table from "../components/Table";

export default function Dataset () {

  const [search, setSearch] = createSignal('');
  createEffect(() => {
    console.log('Search input changed:', search());
  });

  return <>
    <h1>Lista biljaka</h1>
    <p>Pretraži sve: <input onInput={e => setSearch(e.currentTarget.value)}></input></p>
    <Table url='http://localhost:8080/api/plant'></Table>
  </>
}
