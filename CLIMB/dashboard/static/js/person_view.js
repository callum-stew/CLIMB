function view_person(type, id) {
    const url = new URL(location);
    url.searchParams.delete('pid');
    url.searchParams.delete('type');
    url.searchParams.delete('search');
    url.searchParams.append('pid', id);
    if (type === 'staff') {
        url.pathname = '/dashboard/staff_edit';
    } else {
        url.pathname = '/dashboard/member';
    }
    window.location.href = url;
}

function select_person(type, id) {
    const url = new URL(location);
    url.searchParams.delete('pid');
    url.searchParams.delete('type');
    url.searchParams.delete('search');
    url.searchParams.append('pid', id);
    url.pathname = '/dashboard';
    window.location.href = url;
}

function new_person(type) {
    const url = new URL(location);
    url.searchParams.delete('pid');
    url.searchParams.delete('type');
    url.searchParams.delete('search');
    if (type === 'staff') {
        url.pathname = '/dashboard/staff_edit';
    } else {
        url.pathname = '/dashboard/member';
    }
    window.location.href = url;
}