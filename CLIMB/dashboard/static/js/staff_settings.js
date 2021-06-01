document.addEventListener("DOMContentLoaded", () => {
    const date = new Litepicker({
        element: document.getElementById('datepicker')
    });

    const checked = {}
    const days = ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun'];
    days.forEach((day) => {
        const openButton = document.getElementById(day+'-open');
        checked[day] = openButton.hasAttribute('checked');
        openButton.setAttribute('day', day)
    })

    days.forEach((day) => {
        const openButton = document.getElementById(day+'-open');
        const openTime = document.getElementById(day+'-o-time');
        const closeTime = document.getElementById(day+'-c-time');
        openButton.addEventListener('change', () => {
            checked[day] = !checked[day]
            if (checked[day]) {
                openTime.removeAttribute('disabled');
                closeTime.removeAttribute('disabled');
            } else {
                openTime.setAttribute('disabled', 'true');
                closeTime.setAttribute('disabled', 'true');
            }
        })
    })

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

    function getCustomDateData(date, day) {
        fetch(`${window.origin}/dashboard/custom_day_data`, {
            method: "POST",
            credentials: "include",
            body: JSON.stringify({'date': date, 'day': day}),
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
                setDayValues(data);
            });
        }).catch((error) => {
            console.log("Fetch error: " + error);
        });
    }

    const customOpenButton = document.getElementById('custom-open');
    let customOpenButtonChecked = false;
    const customOpenTime = document.getElementById('custom-o-time');
    const customCloseTime = document.getElementById('custom-c-time');
    customOpenButton.addEventListener('change', () => {
        customOpenButtonChecked = !customOpenButtonChecked;
        if (customOpenButtonChecked) {
            customOpenTime.removeAttribute('disabled');
            customCloseTime.removeAttribute('disabled');
        } else {
            customOpenTime.setAttribute('disabled', 'true');
            customCloseTime.setAttribute('disabled', 'true');
        }
    })

    function setDayValues(data) {
        setButton = document.getElementById('set')
        customOpenButton.removeAttribute('disabled');
        setButton.removeAttribute('disabled');
        if (data.open === 1) {
            customOpenButton.setAttribute('checked', 'true')
            customOpenTime.removeAttribute('disabled');
            customCloseTime.removeAttribute('disabled');
            customOpenButtonChecked = true;
        }
        customOpenTime.setAttribute('value', data.opening_time)
        customCloseTime.setAttribute('value', data.closing_time)
    }

    date.on('selected', (selected_date) => {
        getCustomDateData(formatDate(selected_date), selected_date.getDay());
    })
})