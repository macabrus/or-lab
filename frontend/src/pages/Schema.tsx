import schema from './schema.json';


export default function Schema() {
  return <>
    <pre>{JSON.stringify(schema, null, 4)}</pre>
  </>
}
