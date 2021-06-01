let basket = {
    product: {},
    booking: {}
};

document.addEventListener("DOMContentLoaded", () => {
    const gridSearch = document.getElementById('store_search');
    const gridBasket = document.getElementById('basket');
    let gridSearchValue;

    const grid = new Muuri('.grid');
    window.grid = grid;

    function initGrid() {
        gridSearch.value = '';

        gridSearchValue = gridSearch.value.toLowerCase();

        gridSearch.addEventListener('keyup', function () {
            const newSearch = gridSearch.value.toLowerCase();
            if (gridSearchValue !== newSearch) {
                gridSearchValue = newSearch;
                filter();
            }
        });
    }

    function filter(onFinish = null) {
        grid.filter(
            (item) => {
                const element = item.getElement();
                return !gridSearchValue ||
                    (element.getAttribute('data-title') || '').toLowerCase().indexOf(gridSearchValue) > -1;
            },
            {onFinish: onFinish}
        );
    }

    function getProduct(target) {
        if (!target.getAttribute("data-title")) {
            target = target.parentElement;
        }

        return {
            product_id: target.getAttribute('data-id'),
            product_name: target.getAttribute('data-title'),
            product_price: target.getAttribute('data-price'),
            product_count: 1
        }
    }

    function addProduct(event) {
        let product = getProduct(event.target);

        if (basket.product[product.product_id] != undefined) {
            basket.product[product.product_id].product_count ++;
        } else {
            basket.product[product.product_id] = product;
        }

        updateBasket();
    }

    function removeProduct(event) {
        let product = getProduct(event.target);

        if (basket.product[product.product_id] != undefined) {
            basket.product[product.product_id].product_count --;
            if (basket.product[product.product_id].product_count === 0) {
                delete basket.product[product.product_id];
            }
        }

        updateBasket();
    }

    function deleteProduct(event) {
        let item_type = event.target.getAttribute('data-type')
        let id = event.target.getAttribute('data-id')

        if (item_type === 'product' && basket.product[id] != undefined) {
            delete basket.product[id];
        } else if (item_type === 'booking' && basket.booking[id] != undefined) {
            delete basket.booking[id];
        }

        updateBasket();
    }

    function productClicked() {
        document.querySelectorAll('.addItem').forEach(button => {
            button.removeEventListener('click', addProduct);
            button.addEventListener('click', addProduct);
        })

        document.querySelectorAll('.removeItem').forEach(button => {
            button.removeEventListener('click', removeProduct);
            button.addEventListener('click', removeProduct);
        });

        document.querySelectorAll('.deleteItem').forEach(button => {
            button.removeEventListener('click', deleteProduct);
            button.addEventListener('click', deleteProduct);
        });
    }

    function updateBasket() {
        document.querySelectorAll('.basket_item').forEach((element) => {
            element.remove();
        });

        let total = 0;

        for (let product_id in basket.product) {
            let product = basket.product[product_id];

            const basketItem = document.createElement("li");
            const basketInfo = document.createElement("div");
            basketItem.className = "list-group-item basket_item";
            basketInfo.className = "d-flex justify-content-between lh-sm";

            const basketItemLeft = document.createElement("div");
            const productName = document.createElement("h6");
            productName.className = "my-0";
            productName.innerText = product.product_name;
            basketItemLeft.appendChild(productName);

            const basketItemRight = document.createElement("div");
            const productPrice = document.createElement("span");
            productPrice.className = "text-muted d-block";
            productPrice.innerText = "£"+product.product_price;
            const productCount = document.createElement("small");
            productCount.innerText = "Quantity: "+product.product_count.toString();
            basketItemRight.appendChild(productPrice);
            basketItemRight.appendChild(productCount);

            basketInfo.appendChild(basketItemLeft);
            basketInfo.appendChild(basketItemRight);

            basketItemControl = document.createElement("div");
            basketItemControl.className = "d-flex justify-content-between";
            
            controlLeft = document.createElement("div");
            controlRight = document.createElement("div");

            const decreaseItem = document.createElement("span");
            decreaseItem.setAttribute("data-feather", "arrow-left");
            decreaseItem.className = "removeItem item-button-w";
            decreaseItem.setAttribute("data-title", product.product_name);
            decreaseItem.setAttribute("data-id", product.product_id);
            decreaseItem.setAttribute("data-price", product.product_price);
            const increaseItem = document.createElement("span");
            increaseItem.setAttribute("data-feather", "arrow-right");
            increaseItem.className = "addItem item-button-w";
            increaseItem.setAttribute("data-title", product.product_name);
            increaseItem.setAttribute("data-id", product.product_id);
            increaseItem.setAttribute("data-price", product.product_price);

            controlLeft.appendChild(decreaseItem);
            controlLeft.appendChild(increaseItem);

            const deleteItem = document.createElement("span");
            deleteItem.setAttribute("data-feather", "x");
            deleteItem.className = "deleteItem item-button-wr";
            deleteItem.setAttribute("data-id", product.product_id);
            deleteItem.setAttribute("data-type", 'product');

            controlRight.appendChild(deleteItem);

            basketItemControl.appendChild(controlLeft);
            basketItemControl.appendChild(controlRight);

            basketItem.appendChild(basketInfo);
            basketItem.appendChild(basketItemControl);

            gridBasket.appendChild(basketItem);

            total += parseFloat(product.product_price) * product.product_count;

            feather.replace();
        }
        for (let booking_id in basket.booking) {
            let booking = basket.booking[booking_id];

            const basketItem = document.createElement("li");
            const basketInfo = document.createElement("div");
            basketItem.className = "list-group-item basket_item";
            basketInfo.className = "d-flex justify-content-between lh-sm";

            const basketItemLeft = document.createElement("div");
            const productName = document.createElement("h6");
            productName.className = "my-0";
            productName.innerText = booking.booking_name;
            basketItemLeft.appendChild(productName);

            const basketItemRight = document.createElement("div");
            const productPrice = document.createElement("span");
            productPrice.className = "text-muted d-block";
            productPrice.innerText = "£" + booking.booking_price;
            basketItemRight.appendChild(productPrice);

            basketInfo.appendChild(basketItemLeft);
            basketInfo.appendChild(basketItemRight);

            basketItemControl = document.createElement("div");
            basketItemControl.className = "d-flex justify-content-end";

            const deleteItem = document.createElement("span");
            deleteItem.setAttribute("data-feather", "x");
            deleteItem.className = "deleteItem item-button-wr";
            deleteItem.setAttribute("data-id", booking.booking_id);
            deleteItem.setAttribute("data-type", 'booking');

            basketItemControl.appendChild(deleteItem);

            basketItem.appendChild(basketInfo);
            basketItem.appendChild(basketItemControl);

            gridBasket.appendChild(basketItem);

            total += parseFloat(booking.booking_price);

            feather.replace();
        }

        const basketTotal = document.getElementById("basketTotal");
        const modalTotal = document.getElementById("orderModalTotal");
        total = Math.round((total + Number.EPSILON) * 100) / 100;
        if (total !== NaN) {
            basketTotal.innerText = "£"+total.toString();
            modalTotal.innerText = "Total: £"+total.toString();
        } else {
            basketTotal.innerText = "£0";
            modalTotal.innerText = "Total: £0";
        }

        productClicked();
    }

    function formatDate(date) {
        let month = '' + (date.getMonth() + 1),
            day = '' + date.getDate(),
            year = date.getFullYear();

        if (month.length < 2)
            month = '0' + month;
        if (day.length < 2)
            day = '0' + day;

        return [year, month, day].join('-');
    }

    function formatTime(sdate, edate) {
        let shour = ''+sdate.getHours(),
            smin = ''+sdate.getMinutes(),
            ehour = ''+edate.getHours(),
            emin = ''+edate.getMinutes()

        if (smin.length < 2)
            smin = '0' + smin;
        if (emin.length < 2)
            emin = '0' + emin;

        return shour+':'+smin+'-'+ehour+':'+emin
    }

    let addBookingToBasketBtn = document.getElementById('addBookingToBasket')
    if (addBookingToBasketBtn) {
        addBookingToBasketBtn.addEventListener('click', (e) => {
            sdate = new Date(parseInt(e.target.getAttribute('timestamp-start'))*1000);
            edate = new Date(parseInt(e.target.getAttribute('timestamp-end'))*1000);
            let booking = {
                booking_id: e.target.getAttribute('data-id'),
                booking_name: (formatDate(sdate)+' '+formatTime(sdate, edate)),
                booking_price: e.target.getAttribute('data-price'),
            }

            basket.booking[booking.booking_id] = booking;

            updateBasket();
        });
    }

    document.querySelectorAll('.booking_start').forEach((e) => {
        sdate = new Date(parseInt(e.getAttribute('timestamp-start'))*1000);
        edate = new Date(parseInt(e.getAttribute('timestamp-end'))*1000);
        e.innerText = formatDate(sdate)+' '+formatTime(sdate, edate);
    })

    initGrid();
    productClicked();
});

function makeSale() {
    const url = new URL(location);
    const member_id = url.searchParams.get('pid');
    if (member_id == null) {
        alert("Please have a member selected.");
        return
    }
    const query = {
        'member_id': member_id,
        'products': [],
        'bookings': []
    }

    for (let product_id in basket.product) {
        let product = basket.product[product_id];
        query.products.push([product.product_id, product.product_count])
    }
    for (let booking_id in basket.booking) {
        let booking = basket.booking[booking_id];
        query.bookings.push(booking.booking_id)
    }

    fetch(`${window.origin}/dashboard/complete_order`, {
        method: "POST",
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
            alert('An error has occurred')
            return
        }
        basket = {}
        url.searchParams.delete('pid');
        window.location.href = url;
    }).catch((error) => {
        console.log("Fetch error: " + error);
    });
}