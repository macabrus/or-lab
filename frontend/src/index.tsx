/* @refresh reload */
import { render } from 'solid-js/web';

import './index.css';
import App from './App';
import { Router } from '@solidjs/router';
import { ProfileProvider } from './components/ProfileProvider';

/* dirty hack for redirecting to login on 401, i really don't care... */
// const tmpFetch = window.fetch
// window.fetch = async (...args) => {
//     console.log('lololol');
//     const res = await tmpFetch(...args)
//     if (res.status === 401) {
//         window.location.href = "/api/login";
//         return res;
//     }
//     return res;
// };

render(() => <Router><ProfileProvider><App /></ProfileProvider></Router>, document.getElementById('root') as HTMLElement);
