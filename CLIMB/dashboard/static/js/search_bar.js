const user_search = document.getElementById('user_search');

function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

document.addEventListener("DOMContentLoaded", () => {
    user_search.addEventListener("input", (e) => {
        if (user_search.value.length > 0) {
            results()
        } else {
            removeResults();
        }
    });
    user_search.addEventListener('blur', () => {
        sleep(200).then(() => {
            removeResults();
        });
    });
});

const results = () => {
    const query = {
        user_search: user_search.value
    }

    fetch(`${window.origin}/dashboard/user_search`, {
        method: "POST",
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
        response.json().then((data) => {
            displayResults(data)
        });
    }).catch((error) => {
        console.log("Fetch error: " + error);
    });
}

// TODO: allow use of arrow keys on results

const displayResults = (result_data) => {
    removeResults();

    let text;

    if (!result_data) {
        return;
    }

    if (result_data.member_count > 0) {
        text = 'Members: '+result_data.member_count.toString()+' | View all';
        displayItem(true, 'MEMBER', text, user_search.value);

        if (result_data.member_count <= 5) {
            result_data.members.forEach((item) => {
                text = '\xa0\xa0\xa0\xa0Name: '+item.full_name+'\xa0\xa0\xa0\xa0Email: '+item.email+' | Use';
                displayItem(false, 'MEMBER', text, item.id);
            });
        }
    }

    if (result_data.staff_count > 0) {
        text = 'Staff: '+result_data.staff_count.toString()+' | View all';
        displayItem(true, 'STAFF', text, user_search.value);

        if (result_data.staff_count <= 5) {
            result_data.staff.forEach((item) => {
                text = '\xa0\xa0\xa0\xa0Name: '+item.full_name+'\xa0\xa0\xa0\xa0Email: '+item.email+' | Use';
                displayItem(false, 'STAFF', text, item.id);
            });
        }
    }

    if (result_data.member_count + result_data.staff_count === 0) {
        displayItem(true, 'ADD', 'No users found | Add new member');
    } else {
        displayItem(true, 'ADD', 'Add new member');
    }
}

const displayItem = (header, type, text, id) => {
    const resultItem = document.createElement("div");
    resultItem.className = "search_result col-md-9 ms-sm-auto col-lg-10 py-2";
    if (type === 'ADD') {
        resultItem.setAttribute('onclick', 'createMember()');
    } else if (header) {
        resultItem.classList.add('search_result_header');
        resultItem.setAttribute("header", 'true');
        if (type === 'MEMBER') {
            resultItem.setAttribute("search", id);
            resultItem.setAttribute('onclick', 'showMembers(this)');
        } else if (type === 'STAFF') {
            resultItem.setAttribute("search", id);
            resultItem.setAttribute('onclick', 'showStaff(this)');
        }
    } else {
        if (type === 'MEMBER') {
            resultItem.setAttribute("personID", id);
            resultItem.setAttribute('onclick', 'getMember(this)');
        } else if (type === 'STAFF') {
            resultItem.setAttribute("personID", id);
            resultItem.setAttribute('onclick', 'getStaff(this)');
        }
    }

    const itemContent = document.createTextNode(text);
    resultItem.appendChild(itemContent);

    const main = document.getElementById('main');
    const parent = main.parentNode;
    parent.insertBefore(resultItem, main);
}

const removeResults = () => {
    document.querySelectorAll('.search_result').forEach((element) => {
        element.remove();
    });
}

const getMember = (el) => {
    const id = el.getAttribute('personID');
    const url = new URL(location);
    url.searchParams.delete('pid');
    url.searchParams.append('pid', id);
    url.pathname = '/dashboard';
    window.location.href = url;
}

const getStaff = (el) => {
    const id = el.getAttribute('personID');
    const url = new URL(location);
    url.searchParams.delete('pid');
    url.searchParams.append('pid', id);
    url.pathname = '/dashboard/staff_edit';
    window.location.href = url;
}

const createMember = () => {
    const url = new URL(location);
    url.pathname = url.pathname+'member';
    url.searchParams.delete('pid');
    window.location.href = url;
}

const showMembers = (el) => {
    const url = new URL(location);
    url.searchParams.delete('pid');
    url.searchParams.delete('type');
    url.searchParams.delete('search');
    url.searchParams.append('type', 'member');
    url.searchParams.append('search', user_search.value);
    url.pathname = '/dashboard/people';
    window.location.href = url;
}

const showStaff = (el) => {
    const url = new URL(location);
    url.searchParams.delete('pid');
    url.searchParams.delete('type');
    url.searchParams.delete('search');
    url.searchParams.append('type', 'staff');
    url.searchParams.append('search', user_search.value);
    url.pathname = '/dashboard/people';
    window.location.href = url;
}