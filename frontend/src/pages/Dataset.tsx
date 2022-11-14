import { For, Show} from "solid-js";
import Table from "../components/Table";
import {startCase} from 'lodash-es';
import { FilterProvider, useFilter } from "../components/FilterProvider";


export function downloadFilteredData(format: string) {
  const link = document.createElement('a');
  /* TODO: add query params for filtering */
  link.href = `http://localhost:8080/download/${format}?`;
  link.click();
}

export function PlantForm (props: any) {
  const {search, setSearch, filterField, setFilterField, fields,filterValue, setFilterValue} = useFilter();
  return <>
    <h1>Lista biljaka</h1>
    <div>Pretraži sve: <input value={search()} onInput={e => setSearch(e.currentTarget.value)}></input></div>
    <label for="field">Filtriraj po:</label>
    <select id="fields" value={filterField()} onInput={e => setFilterField(e.currentTarget.value)}>
        <option disabled selected value="null">--- Odaberi svojstvo ---</option>
        <For each={fields()}>{
         (field, id) =>
            <option value={field}>{startCase(field)}</option>
        }</For>
    </select>
    <Show when={filterField()}>
      <input value={filterValue()} onInput={e => setFilterValue(e.currentTarget.value)}></input>
    </Show>
  </>
}

export default function PlantView() {
  return <>
    <FilterProvider
      url='http://localhost:8080'
      resource='plant'>
      <PlantForm/>
      <Table/>
      <button onClick={() => downloadFilteredData('csv')}>Preuzmi CSV</button>
      <button onClick={() => downloadFilteredData('json')}>Preuzmi JSON</button>
    </FilterProvider>
  </>
}
