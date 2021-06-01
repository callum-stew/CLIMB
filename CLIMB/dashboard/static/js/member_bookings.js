let datePicker
document.addEventListener("DOMContentLoaded", () => {
    function resizeCards() {
        const storeGrid = document.getElementById('make_booking');
        const storeItem = document.getElementById('my_bookings');

        if (window.innerWidth >= 768) {
            let height = window.innerHeight - storeGrid.getBoundingClientRect().y - 50;
            storeGrid.style.height = `${height}px`;
            storeGrid.style.overflow = 'auto';
            height = window.innerHeight - storeItem.getBoundingClientRect().y - 50;
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
        minDate: Date(),
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

    let adultCounter = document.getElementById('numAdult');
    let childCounter = document.getElementById('numChild');

    const timeSelect = document.getElementById('time');

    let s_date;
    datePicker.on('selected', (new_s_date) => {
        s_date = new_s_date;
        getTimeBlocks();
    })

    timeSelect.addEventListener('change', (event) => {
        let submit =  document.getElementById('submit');
        if (event.target.value !== "0") {
            submit.removeAttribute('disabled');
        } else {
            submit.setAttribute('disabled', 'true');
        }
    })

    let total = 0;
    let textTotal = document.getElementById('total');
    adultCounter.addEventListener('change', () => {
        checkPersonTotal()
        updateTotal();
        if (s_date) {
            getTimeBlocks();
        }
    })
    childCounter.addEventListener('change', () => {
        checkPersonTotal()
        updateTotal();
        if (s_date) {
            getTimeBlocks();
        }
    })
    document.getElementById('length').addEventListener('change', () => {
        if (s_date) {
            getTimeBlocks();
        }
    })

    function checkPersonTotal() {
        let maxExtraPeople = maxPeople - (parseInt(adultCounter.value) + parseInt(childCounter.value));
        adultCounter.setAttribute('max', (parseInt(adultCounter.value) + maxExtraPeople).toString());
        childCounter.setAttribute('max', (parseInt(childCounter.value) + maxExtraPeople).toString());
    }

    function updateTotal() {
        let numAdult = adultCounter.value;
        let numChild =childCounter.value;
        total = adultPrice * numAdult + childPrice * numChild
        total = Math.round((total + Number.EPSILON) * 100) / 100;
        if (!isNaN(total)) {
            textTotal.innerText = "£"+total.toString();
        } else {
            textTotal.innerText = "£0";
        }
    }

    function getTimeBlocks(){
        let options = document.getElementsByClassName('timeOption');
        while(options[0]) {
            options[0].parentNode.removeChild(options[0]);
        }
        let selected_date = new Date(s_date.toJSDate());
        const formatted_date = formatDate(selected_date);
        let date_data;

        if (Object.keys(c_data.date).includes(formatted_date)) {
            date_data = c_data.date[formatted_date];
        } else {
            date_data = c_data.day[days[selected_date.getDay()]];
        }

        const length = parseInt(document.getElementById('length').value);
        selected_date.setHours(date_data.opening_time.substring(0,2));
        selected_date.setMinutes(date_data.opening_time.substring(3,5));
        let start_time = selected_date.getTime();
        selected_date.setHours(date_data.closing_time.substring(0,2));
        selected_date.setMinutes(date_data.closing_time.substring(3,5));
        const end_time = selected_date.getTime();
        let timeSlots = {}
        let timeSlotsAvailable = {}
        let blocks = []

        while (start_time + length*60000 <= end_time) {
            timeSlots[start_time] = {}
            timeSlots[start_time].start = start_time
            timeSlots[start_time].end = start_time+length*60000
            timeSlots[start_time].peopleNum = parseInt(adultCounter.value) + parseInt(childCounter.value)
            if (selectedBookingId) {
                timeSlots[start_time].booking_id = selectedBookingId;
            } else {
                timeSlots[start_time].booking_id = NaN;
            }
            blocks.push(start_time)
            start_time += length*60000;
        }

        fetch(`${window.origin}/dashboard/check_booking`, {
            method: "POST",
            credentials: "include",
            body: JSON.stringify(timeSlots),
            cache: "no-cache",
            headers: new Headers({
                "content-type": "application/json"
            })
        }).then((response) => {
            if (response.status !== 200) {
                console.log(`Looks like there was a problem. Status code: ${response.status}`);
                return;
            }
            response.json().then((data) => {
                timeSlotsAvailable = data
                let valid_blocks = 0
                blocks.forEach((block) => {
                    if (!timeSlotsAvailable[block]) {
                        let sTime = new Date(timeSlots[block].start);
                        let eTime = new Date(timeSlots[block].end);
                        let option = document.createElement("option");
                        let sTimeText = sTime.getHours().toString();
                        if (sTime.getHours().toString().length === 1) {
                            sTimeText += '0';
                        }
                        sTimeText += (':'+sTime.getMinutes().toString());
                        if (sTime.getMinutes().toString().length === 1) {
                            sTimeText += '0';
                        }
                        let eTimeText = (' to '+eTime.getHours().toString());
                        if (eTime.getHours().toString().length === 1) {
                            eTimeText += '0';
                        }
                        eTimeText += (':'+eTime.getMinutes().toString());
                        if (eTime.getMinutes().toString().length === 1) {
                            eTimeText += '0';
                        }
                        option.text = sTimeText + eTimeText;
                        option.value = sTime.getTime().toString();
                        option.className = 'timeOption';
                        timeSelect.add(option);
                        valid_blocks ++
                    }
                })
                if (valid_blocks === 0) {
                    document.getElementById('d-time').innerText = "No slots available for this sized group";
                    document.getElementById('time').setAttribute('disabled', 'true');
                } else {
                    document.getElementById('d-time').innerText = "Available time slots";
                    document.getElementById('time').removeAttribute('disabled');
                }
                document.getElementById('submit').setAttribute('disabled', 'true');
            });
        }).catch((error) => {
            console.log("Fetch error: " + error);
        });
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

    updateTotal();
    checkPersonTotal();
    window.onresize = resizeCards;
    resizeCards();
})

function editBooking(id) {
    const url = new URL(location);
    url.searchParams.delete('bid');
    url.searchParams.append('bid', id);
    url.pathname = '/dashboard/bookings';
    window.location.href = url;
}

function  deleteBooking(id) {
    const url = new URL(location);
    const query = {'id': id};
    fetch(`${window.origin}/dashboard/bookings`, {
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
        url.pathname = '/dashboard/bookings';
        url.searchParams.delete('bid');
        window.location.href = url;
    }).catch((error) => {
        console.log("Delete error: " + error);
    });
}