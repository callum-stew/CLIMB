// Example starter JavaScript for disabling form submissions if there are invalid fields
(function () {
    'use strict'

    // Fetch all the forms we want to apply custom Bootstrap validation styles to
    const forms = document.querySelectorAll('.needs-validation');

    // Loop over them and prevent submission
    Array.prototype.slice.call(forms)
        .forEach(function (form) {
            form.addEventListener('submit', function (event) {
                if (!form.checkValidity()) {
                    event.preventDefault();
                    event.stopPropagation();

                    // go back to first page
                    while (current_step !== 0) {
                        current_step--;
                        let previous_step = current_step + 1;
                        prevBtn.classList.add('d-none');
                        prevBtn.classList.add('d-inline-block');
                        step[current_step].classList.remove('d-none');
                        step[current_step].classList.add('d-block')
                        step[previous_step].classList.remove('d-block');
                        step[previous_step].classList.add('d-none');
                        if (current_step < stepCount) {
                            submitBtn.classList.remove('d-inline-block');
                            submitBtn.classList.add('d-none');
                            nextBtn.classList.remove('d-none');
                            nextBtn.classList.add('d-inline-block');
                            prevBtn.classList.remove('d-none');
                            prevBtn.classList.add('d-inline-block');
                        }
                    }

                    // remove previous button
                    if (current_step == 0) {
                        prevBtn.classList.remove('d-inline-block');
                        prevBtn.classList.add('d-none');
                    }

                    // update progress bar and change message
                    progress((100 / stepCount) * current_step);
                    let message = document.getElementById('start_message');
                    message.innerText="There is an issues with your form responses.";
                    message.className="text-danger"
                }

                form.classList.add('was-validated');
            }, false);
        })
})()

let step = document.getElementsByClassName('step');
let prevBtn = document.getElementById('prev-btn');
let nextBtn = document.getElementById('next-btn');
let submitBtn = document.getElementById('submit-btn');
let form = document.getElementsByTagName('form')[0];

form.onsubmit = () => {
    return false
}

// initialise form
let current_step = 0;
let stepCount = 3
step[current_step].classList.add('d-block');
if (current_step == 0) {
    prevBtn.classList.add('d-none');
    submitBtn.classList.add('d-none');
    nextBtn.classList.add('d-inline-block');
}

// set progress bar length
const progress = (value) => {
    document.getElementsByClassName('progress-bar')[0].style.width = `${value}%`;
}

nextBtn.addEventListener('click', () => {
    // show next form page
    current_step++;
    let previous_step = current_step - 1;
    if ((current_step > 0) && (current_step <= stepCount)) {
        prevBtn.classList.remove('d-none');
        prevBtn.classList.add('d-inline-block');
        step[current_step].classList.remove('d-none');
        step[current_step].classList.add('d-block');
        step[previous_step].classList.remove('d-block');
        step[previous_step].classList.add('d-none');
        if (current_step == stepCount) {
            submitBtn.classList.remove('d-none');
            submitBtn.classList.add('d-inline-block');
            nextBtn.classList.remove('d-inline-block');
            nextBtn.classList.add('d-none');
            form.onsubmit = () => {
                return true
            }
        }
    }
    progress((100 / stepCount) * current_step);
});


prevBtn.addEventListener('click', () => {
    // show previous form page
    if (current_step > 0) {
        current_step--;
        let previous_step = current_step + 1;
        prevBtn.classList.add('d-none');
        prevBtn.classList.add('d-inline-block');
        step[current_step].classList.remove('d-none');
        step[current_step].classList.add('d-block')
        step[previous_step].classList.remove('d-block');
        step[previous_step].classList.add('d-none');
        if (current_step < stepCount) {
            submitBtn.classList.remove('d-inline-block');
            submitBtn.classList.add('d-none');
            nextBtn.classList.remove('d-none');
            nextBtn.classList.add('d-inline-block');
            prevBtn.classList.remove('d-none');
            prevBtn.classList.add('d-inline-block');
        }
    }

    // remove button if first page
    if (current_step == 0) {
        prevBtn.classList.remove('d-inline-block');
        prevBtn.classList.add('d-none');
    }
    progress((100 / stepCount) * current_step);
});

document.addEventListener("DOMContentLoaded", () => {
    const checked = {}
    const days = ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun'];

    // get initial days open
    days.forEach((day) => {
        const openButton = document.getElementById(day + '-open');
        checked[day] = openButton.hasAttribute('checked');
        openButton.setAttribute('day', day)
    })

    // add event listener to enable and disable time inputs based on if day is open
    days.forEach((day) => {
        const openButton = document.getElementById(day + '-open');
        const openTime = document.getElementById(day + '-o-time');
        const closeTime = document.getElementById(day + '-c-time');
        openButton.addEventListener('change', () => {
            checked[day] = !checked[day]
            if (checked[day]) {
                openTime.removeAttribute('disabled');
                closeTime.removeAttribute('disabled');
            } else {
                openTime.setAttribute('disabled', 'true');
                closeTime.setAttribute('disabled', 'true');
            }
        });
    });
});