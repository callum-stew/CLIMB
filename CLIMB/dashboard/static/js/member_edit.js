const delete_member = (id) => {
    const url = new URL(location);
    if (id == null) {
        id = url.searchParams.get('pid');
        const query = {'id': id};
        fetch(`${window.origin}/dashboard/member`, {
            method: "DELETE",
            credentials: "include",
            body: JSON.stringify(query),
            cache: "no-cache",
            headers: new Headers({
                "content-type": "application/json"
            })
        }).then((response) => {
            if (response.status !== 200) {
                console.log(`Looks like there was a problem. Status code: ${response.status}`);
                return;
            }
            url.pathname = '/dashboard/';
            url.searchParams.delete('pid');
            window.location.href = url;
        }).catch((error) => {
            console.log("Delete error: " + error);
        });
    } else {
        const query = {'id': id};
        fetch(`${window.origin}/dashboard/personal_info`, {
            method: "DELETE",
            credentials: "include",
            body: JSON.stringify(query),
            cache: "no-cache",
            headers: new Headers({
                "content-type": "application/json"
            })
        }).then((response) => {
            if (response.status !== 200) {
                console.log(`Looks like there was a problem. Status code: ${response.status}`);
                return;
            }
            url.pathname = '/dashboard/';
            url.searchParams.delete('pid');
            window.location.href = url;
        }).catch((error) => {
            console.log("Delete error: " + error);
        });
    }
}