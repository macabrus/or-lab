import { createEffect, createResource, createSignal, Show } from "solid-js";
import { useProfile } from "../components/ProfileProvider";


export default function Profile() {
    const user = useProfile();
    console.log(user)

    return <>
        <h1>User Profile</h1>
        <Show when={user()?.avatar}>
            <img src={user()?.avatar}></img>
        </Show>
        <pre>{JSON.stringify(user(), null, 2)}</pre>
    </>
}