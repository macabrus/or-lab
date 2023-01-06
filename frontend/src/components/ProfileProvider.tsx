import { useLocation } from "@solidjs/router";
import { Accessor, createContext, createEffect, createResource, createSignal, Resource, useContext } from "solid-js";


interface Profile {
    avatar: string // url
    name: string
    email: string
}

export const ProfileContext = createContext<any>();

export function ProfileProvider(props: any) {
    const loc = useLocation();
    const [user, setUser] = createSignal<Profile | null>(null);
    const [profile, {refetch}] = createResource<Profile>(async () => {
        const res = await fetch('/api/me');
        const json = await res.json();
        const publicRoutes = [
            '/home',
            '/schema'
        ];
        if (!json && !publicRoutes.find(r => r.startsWith(loc.pathname))) {
            window.location.href = "/api/login";
        }
        const u = {
            avatar: json?.userinfo?.picture,
            name: json?.userinfo?.name,
            email: json?.userinfo?.email,
        }
        setUser((old) => json && u);
        return u;
    });

    createEffect(() => {
        loc.pathname;
        refetch();
    });

    return <ProfileContext.Provider value={() => user()}>
        {props.children}
    </ProfileContext.Provider>
}

export function useProfile(): Accessor<Profile> {
    return useContext(ProfileContext);
}