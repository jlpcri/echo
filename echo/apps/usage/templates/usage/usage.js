moment.tz.add('America/Chicago|CST CDT|60 50|01010101010101010101010|1BQT0 1zb0 Op0 1zb0 Op0 1zb0 Op0 1zb0 Op0 1zb0 Op0 1zb0 Rd0 1zb0 Op0 1zb0 Op0 1zb0 Op0 1zb0 Op0 1zb0');

var startDatetime = moment.tz(moment().valueOf(), 'America/Chicago');
var endDatetime = moment.tz(moment().valueOf(), 'America/Chicago');
var sortField = null;
var tabName = null;

function setStartDate(datetime) {
    startDatetime = moment.tz(moment(datetime*1000), 'America/Chicago');
}

function setEndDate(datetime) {
    endDatetime = moment.tz(moment(datetime*1000), 'America/Chicago');
}

function setSort(sort) {
    sortField = sort;
}

function setTab(tab) {
    tabName = tab;
}

function sortHandler(e) {
    loadRecords(e.target.getAttribute('data-field'));
}

function loadRecords(sort) {
    var s = (typeof sort === "undefined") ? null : sort;
    sortField = (s == null) ? ((sortField == null) ? "" : sortField) : sort;
    if (tabName == 'users') {
        window.location.href = "{% url 'usage:users' %}?sort=" + sortField + "&start=" + startDatetime.format('X') + "&end=" + endDatetime.format('X');
    } else if (tabName == 'projects') {
        window.location.href = "{% url 'usage:projects' %}?sort=" + sortField + "&start=" + startDatetime.format('X') + "&end=" + endDatetime.format('X');
    }
}

function attachDateRangePicker() {
    $('#report-range').daterangepicker(
        {
            ranges: {
                'Today': [moment.tz(moment().valueOf(), 'America/Chicago').startOf('day'), moment.tz(moment().valueOf(), 'America/Chicago').endOf('day')],
                'Yesterday': [moment.tz(moment().valueOf(), 'America/Chicago').subtract('days', 1).startOf('day'), moment.tz(moment().valueOf(), 'America/Chicago').subtract('days', 1).endOf('day')],
                'Last 7 Days': [moment.tz(moment().valueOf(), 'America/Chicago').subtract('days', 6).startOf('day'), moment.tz(moment().valueOf(), 'America/Chicago').endOf('day')],
                'Last 30 Days': [moment.tz(moment().valueOf(), 'America/Chicago').subtract('days', 29).startOf('day'), moment.tz(moment().valueOf(), 'America/Chicago').endOf('day')],
                'This Month': [moment.tz(moment().valueOf(), 'America/Chicago').startOf('month').startOf('day'), moment.tz(moment().valueOf(), 'America/Chicago').endOf('month').endOf('day')],
                'Last Month': [moment.tz(moment().valueOf(), 'America/Chicago').subtract('month', 1).startOf('month').startOf('day'), moment.tz(moment().valueOf(), 'America/Chicago').subtract('month', 1).endOf('month').endOf('day')]
            },
            startDate: moment.tz(startDatetime.valueOf(), 'America/Chicago'),
            endDate: moment.tz(endDatetime.valueOf(), 'America/Chicago'),
            maxDate: moment.tz(moment().valueOf(), 'America/Chicago').endOf('day'),
            timePicker: true,
            timePickerIncrement: 1
        },
        function (start, end) {
            $('#report-range-display').html(moment.tz(start.valueOf(), 'America/Chicago').format('MMMM D, YYYY HH:mm') + ' - ' + moment.tz(end.valueOf(), 'America/Chicago').format('MMMM D, YYYY HH:mm'));
            startDatetime = moment.tz(start.valueOf(), 'America/Chicago');
            endDatetime = moment.tz(end.valueOf(), 'America/Chicago');
            loadRecords();
        });
    $('#report-range-display').html(moment.tz(startDatetime.valueOf(), 'America/Chicago').format('MMMM D, YYYY HH:mm') + ' - ' + moment.tz(endDatetime.valueOf(), 'America/Chicago').format('MMMM D, YYYY HH:mm'));
}

$(document).ready(function () {
    moment.tz.add('America/Chicago|CST CDT|60 50|01010101010101010101010|1BQT0 1zb0 Op0 1zb0 Op0 1zb0 Op0 1zb0 Op0 1zb0 Op0 1zb0 Rd0 1zb0 Op0 1zb0 Op0 1zb0 Op0 1zb0 Op0 1zb0');
    $('a.sort-field').on('click', function (e) {
        sortHandler(e);
    });
});