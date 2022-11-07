import type { Component } from 'solid-js';
import { lazy } from 'solid-js';
import { Routes, Route, A } from "@solidjs/router"


const About = lazy(() => import("./pages/About"));
const Dataset = lazy(() => import("./pages/Dataset"));

const App: Component = () => {
  return (<>
    <nav>
      <A href="/about">About</A>
      <A href="/">Biljke</A>
    </nav>
    <Routes>
      <Route path="/about" component={About} />
      <Route path="/" component={Dataset} />
      {/* <Route path="/about" element={<div>This site was made with Solid</div>} /> */}
    </Routes>
  </>)
};

export default App;
