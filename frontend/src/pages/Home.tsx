import { downloadFilteredData } from "../components/FilterProvider";

export default function Home() {
  return <>
  <h1>Skup podataka o biljkama</h1>
  <p>Preuzmite dump baze cijelog skupa podataka:</p>
  <button onClick={() => downloadFilteredData('csv', {})}>Preuzmi kao CSV</button>
  <button onClick={() => downloadFilteredData('json', {})}>Preuzmi kao JSON</button>
  </>
}
