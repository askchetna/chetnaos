export async function apiGet(path){
    try{
        const r=await fetch(path,{
            credentials:"same-origin",
            cache:"no-store"
        });
        if(!r.ok) throw new Error(await r.text());
        return await r.json();
    }catch(e){
        console.error(e);
        return {};
    }
}
