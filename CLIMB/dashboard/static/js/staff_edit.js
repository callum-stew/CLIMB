let count = 0;

const delete_staff = (id) => {
    const url = new URL(location);
    if (id == null) {
        id = url.searchParams.get('pid');
    }
    const query = {'id': id};
    fetch(`${window.origin}/dashboard/staff_edit`, {
        method: "DELETE",
        credentials: "include",
        body: JSON.stringify(query),
        cache: "no-cache",
        headers: new Headers({
            "content-type": "application/json"
        })
    }).then((response) => {
        if (response.status !== 200) {
            if (response.status === 418) {
                if (count > 5) {
                    alert('Hyper Text Coffee Pot Control Protocol for Tea Efflux Appliances: 418 I\'m a teapot');
                }
                alert('The admin account can not be deleted');
                count ++;
            }
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