import { downloadFilteredData } from "../components/FilterProvider";
import flask from '../assets/flask.png';
import solidjs from '../assets/solidjs.png';
import sqlite from '../assets/sqlite.png';

export default function Home() {
  return <>
  <h1>Skup podataka o biljkama</h1>
  <p>Preuzmite dump baze cijelog skupa podataka:</p>
  <button onClick={() => downloadFilteredData('csv', {})}>Preuzmi kao CSV</button>
  <button onClick={() => downloadFilteredData('json', {})}>Preuzmi kao JSON</button>
  <p>Posebne zahvale autorima ovih nevjerojatnih tehnologija:</p>
  <img src={sqlite}/> <img src={flask}/> <img src={solidjs}/>
  ♥️
  </>
}
