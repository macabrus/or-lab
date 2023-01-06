import { useLocation } from "@solidjs/router";
import { Accessor, createContext, createEffect, createResource, createSignal, Resource, Signal, useContext } from "solid-js";


interface Profile {
    avatar: string // url
    name: string
    email: string
}

export const ProfileContext = createContext<any>();

export function ProfileProvider(props: any) {
    const loc = useLocation();
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
        return {
            avatar: json?.userinfo?.picture,
            name: json?.userinfo?.name,
            email: json?.userinfo?.email,
        }
    });


    createEffect(() => {
        loc.pathname;
        refetch();
    });

    return <ProfileContext.Provider value={profile}>
        {props.children}
    </ProfileContext.Provider>
}

export function useProfile(): Resource<Profile> {
    return useContext(ProfileContext);
}