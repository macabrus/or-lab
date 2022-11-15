import type { Component } from 'solid-js';
import { lazy } from 'solid-js';
import { Routes, Route, A } from "@solidjs/router"


const Home = lazy(() => import("./pages/Home"));
const Dataset = lazy(() => import("./pages/Dataset"));
const Schema = lazy(() => import("./pages/Schema"));

const App: Component = () => {
  return (<>
    <nav>
      <A href="/home">Home</A>
      <A href="/">Biljke</A>
      <A href='/schema'>Shema</A>
    </nav>
    <Routes>
      <Route path="/home" component={Home} />
      <Route path="/" component={Dataset} />
      <Route path="/schema" component={Schema} />
      {/* <Route path="/about" element={<div>This site was made with Solid</div>} /> */}
    </Routes>
  </>)
};

export default App;
