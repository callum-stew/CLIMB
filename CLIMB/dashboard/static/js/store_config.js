

document.addEventListener("DOMContentLoaded", () => {
    const url = new URL(location);

    const grid = new Muuri('.grid', {dragEnabled: true});
    window.grid = grid;

    let gridOrder = getItemIds();
    let newGridOrder = getItemIds();

    function getItemIds() {
        return grid.getItems().map((item) => {
            return item.getElement().getAttribute('data-id');
        });
    }

    function initGrid() {
        grid.on('move', () => {
            gridOrder = newGridOrder;
            newGridOrder = getItemIds();
        });

        grid.on('dragReleaseEnd', (item) => {
            if (JSON.stringify(gridOrder) === JSON.stringify(newGridOrder)) {
                url.searchParams.delete('sid');
                url.searchParams.append('sid', item.getElement().getAttribute('data-id'));
                window.location.href = url;
            } else {
                saveLayout(newGridOrder);
                gridOrder = newGridOrder;
            }
        });
    }

    function saveLayout(itemIds) {
        fetch(`${window.origin}/dashboard/update_store_order`, {
            method: "PUT",
            credentials: "include",
            body: JSON.stringify(itemIds),
            cache: "no-cache",
            headers: new Headers({
                "content-type": "application/json"
            })
        }).then((response) => {
            if (response.status == 403) {
                alert('You do not have permission to do that.')
            }
            if (response.status !== 200) {
                console.log(`Looks like there was a problem. Status code: ${response.status}`);
            }
        }).catch((error) => {
            console.log("Fetch error: " + error);
        });
    }

    function resizeCards() {
        const storeGrid = document.getElementById('store_items');
        const storeItem = document.getElementById('item_edit');

        if (window.innerWidth >= 768) {
            let height = window.innerHeight - storeGrid.getBoundingClientRect().y - 50;
            storeGrid.style.height = `${height}px`;
            storeGrid.style.overflow = 'auto';
            height = window.innerHeight - storeItem.getBoundingClientRect().y - 50;
            storeItem.style.height = `${height}px`;
            storeItem.style.overflow = 'auto';
        }
    }

    window.onresize = resizeCards;
    resizeCards();
    initGrid();
});

function closeProduct() {
    const url = new URL(location);
    url.searchParams.delete('sid');
    window.location.href = url;
}

function deleteProduct() {
    const url = new URL(location);
    const id = url.searchParams.get('sid');
    const query = {'id': id};
    fetch(`${window.origin}/dashboard/store_config`, {
        method: "DELETE",
        credentials: "include",
        body: JSON.stringify(query),
        cache: "no-cache",
        headers: new Headers({
            "content-type": "application/json"
        })
    }).then((response) => {
        if (response.status == 403) {
            alert('You do not have permission to do that.')
            return
        }
        if (response.status !== 200) {
            console.log(`Looks like there was a problem. Status code: ${response.status}`);
            return;
        }
        url.pathname = '/dashboard/store_config';
        url.searchParams.delete('sid');
        window.location.href = url;
    }).catch((error) => {
        console.log("Delete error: " + error);
    });
}