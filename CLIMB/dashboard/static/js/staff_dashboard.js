const shopGrid = document.getElementById('store');
const shopBasket = document.getElementById('basket');

document.addEventListener("DOMContentLoaded", () => {
    function resize() {
        if (window.innerWidth >= 768) {
            let height = window.innerHeight - shopGrid.getBoundingClientRect().y - 50;
            shopGrid.style.height = `${height}px`;
            shopGrid.style.overflow = 'auto'
            height = window.innerHeight - shopBasket.getBoundingClientRect().y - 92;
            shopBasket.style.height = `${height}px`;
            shopBasket.style.overflow = 'auto'
        }
    }

    window.onresize = resize
    resize()
})

const editMember = () => {
    const url = new URL(location);
    url.pathname = url.pathname+'member';
    window.location.href = url;
}

const closeMember = () => {
    const url = new URL(location);
    url.searchParams.delete('pid');
    window.location.href = url;
}

function createBooking() {
    const url = new URL(location);
    url.pathname = '/dashboard/edit_bookings';
    window.location.href = url;
}