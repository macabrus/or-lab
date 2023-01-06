import { For, Show} from "solid-js";
import Table from "../components/Table";
import {isInteger, startCase} from 'lodash-es';
import { FilterProvider, useFilter, downloadFilteredData } from "../components/FilterProvider";


export function PlantForm (props: any) {
  const {
    search,
    setSearch,
    filterField,
    setFilterField,
    fields,
    filterValue,
    setFilterValue,
    pageSize,
    setPageSize,
    page,
    next,
    previous
  } = useFilter();
  return <>
    <h1>Pregled skupa podataka</h1>
    <div>Pretraži sve: <input value={search()} onInput={e => setSearch(e.currentTarget.value)}></input></div>
    <div>
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
    </div>
    <div>
      <label for="pageSize">Veličina stranice</label>
      <select id="pageSize" value={pageSize()}
              onInput={e => setPageSize(parseInt(e.currentTarget.value))}>
        <option value="5" selected>5</option>
        <option value="10">10</option>
        <option value="15">15</option>
      </select>
    </div>
    <div>
      <span>Stranica: <button onClick={previous}>◀</button> {page()}<button onClick={next}>▶</button></span>
    </div>
  </>
}

function DownloadButtons(props: any) {
  const {search, filterField, filterValue, page, pageSize} = useFilter();
  const downloadHandler = (format: string) => {
    const params = {
      search: search(),
      filterField: filterField(),
      filterValue: filterValue(),
      page: page(),
      pageSize: pageSize(),
    };
    console.log(params);
    const queryParams: any = {};
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
    downloadFilteredData(format, queryParams);
  };
  return <div>
    <button onClick={() => downloadHandler('csv')}>Preuzmi CSV</button>
    <button onClick={() => downloadHandler('json')}>Preuzmi JSON</button>
  </div>
}

export default function PlantView(props: any) {
  return <>
    <FilterProvider
      url=''
      resource='plant'>
        <PlantForm/>
        <Table/>
        <DownloadButtons/>
    </FilterProvider>
  </>
}
