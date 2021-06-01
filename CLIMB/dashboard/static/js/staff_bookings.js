let datePicker
document.addEventListener("DOMContentLoaded", () => {
    function resizeCards() {
        const storeItem = document.getElementById('my_bookings');

        if (window.innerWidth >= 768) {
            height = window.innerHeight - storeItem.getBoundingClientRect().y - 100;
            storeItem.style.height = `${height}px`;
            storeItem.style.overflow = 'auto';
        }
    }

    let closedDates = [];
    let openDates = [];
    let closedDays = [];
    let day_count = 0;
    const days = ['sunday', 'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday'];
    days.forEach((day) => {
        if (c_data.day[day].open === 0) {
            closedDays.push(day_count);
        }
        day_count ++;
    });
    const dates = Object.keys(c_data.date);
    dates.forEach((date) => {
        if (c_data.date[date].open === 0) {
            closedDates.push(new Date(date));
        } else {
            openDates.push(new Date(date));
        }
    });

    const datesAreOnSameDay = (first, second) =>
        first.getFullYear() === second.getFullYear() &&
        first.getMonth() === second.getMonth() &&
        first.getDate() === second.getDate();


    datePicker = new Litepicker({
        element: document.getElementById('datepicker'),
        lockDaysFilter: (day) => {
            const d = day.getDay();
            let available = closedDays.includes(d);
            openDates.forEach((date) => {
                if (datesAreOnSameDay(date, day)) {
                    available = false;
                }
            })
            closedDates.forEach((date) => {
                if (datesAreOnSameDay(date, day)) {
                    available = true;
                }
            })
            return available;
        },
    });

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

    document.querySelectorAll('.booking_start').forEach((e) => {
        sdate = new Date(parseInt(e.getAttribute('timestamp-start'))*1000);
        edate = new Date(parseInt(e.getAttribute('timestamp-end'))*1000);
        e.innerText = formatDate(sdate)+' '+formatTime(sdate, edate);
    })

    if (selectedDate.getTime() !== 0) {
        datePicker.setDate(selectedDate);
        setTimeout(function() {
            document.querySelectorAll('.timeOption').forEach((e) => {
                if (e.value === selectedDate.getTime().toString()) {
                    e.setAttribute('selected', 'true');
                }
            });
        }, 100)
    }

    datePicker.on('selected', (new_date) => {
        const url = new URL(location);
        let selected_date = new Date(new_date.toJSDate());
        url.searchParams.delete('date');
        url.searchParams.append('date', selected_date.getTime());
        window.location.href = url;
    })

    window.onresize = resizeCards;
    resizeCards();
})

function editBooking(id) {
    const url = new URL(location);
    url.searchParams.delete('bid');
    url.searchParams.append('bid', id);
    url.pathname = '/dashboard/edit_bookings';
    window.location.href = url;
}

function newBooking() {
    const url = new URL(location);
    url.searchParams.delete('bid');
    url.searchParams.delete('date');
    url.pathname = '/dashboard/edit_bookings';
    window.location.href = url;
}