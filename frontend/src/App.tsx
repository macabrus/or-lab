import { Component, createSignal, Show } from 'solid-js';
import { lazy } from 'solid-js';
import { Routes, Route, A } from "@solidjs/router"
import { ProfileProvider, useProfile } from './components/ProfileProvider';


const Home = lazy(() => import("./pages/Home"));
const Dataset = lazy(() => import("./pages/Dataset"));
const Schema = lazy(() => import("./pages/Schema"));
const Profile = lazy(() => import('./pages/Profile'));

const App: Component = () => {
  const user = useProfile()
  return (<>
    <nav>
      <A href="/home">Home</A>
      <Show when={user()}>
        <A href="/biljke">Biljke</A>
      </Show>
      <A href='/schema'>Shema</A>
      <Show when={user()}>
        <A href='/profile'>Profile</A>
        <a href='/api/logout'>Log out</a>
      </Show>
      <Show when={!user()}>
        <a href='/api/login'>Log in</a>
      </Show>
    </nav>
    <Routes>
      <Route path="/home" component={Home} />
      <Route path="/biljke" component={Dataset} />
      <Route path="/schema" component={Schema} />
      <Route path="/profile" component={Profile} />
      {/* <Route path="/about" element={<div>This site was made with Solid</div>} /> */}
    </Routes>
  </>)
};

export default App;
