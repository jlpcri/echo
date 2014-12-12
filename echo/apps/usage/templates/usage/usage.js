moment.tz.add('America/New_York|EST EDT|50 40|01010101010101010101010|1BQT0 1zb0 Op0 1zb0 Op0 1zb0 Op0 1zb0 Op0 1zb0 Op0 1zb0 Rd0 1zb0 Op0 1zb0 Op0 1zb0 Op0 1zb0 Op0 1zb0');

var startDatetime = moment.tz(moment().valueOf(), 'America/New_York');
var endDatetime = moment.tz(moment().valueOf(), 'America/New_York');
var sortField = null;
var tabName = null;

function setStartDate(datetime) {
    startDatetime = moment.tz(moment(datetime*1000), 'America/New_York');
}

function setEndDate(datetime) {
    endDatetime = moment.tz(moment(datetime*1000), 'America/New_York');
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
                'Today': [moment.tz(moment().valueOf(), 'America/New_York').startOf('day'), moment.tz(moment().valueOf(), 'America/New_York').endOf('day')],
                'Yesterday': [moment.tz(moment().valueOf(), 'America/New_York').subtract('days', 1).startOf('day'), moment.tz(moment().valueOf(), 'America/New_York').subtract('days', 1).endOf('day')],
                'Last 7 Days': [moment.tz(moment().valueOf(), 'America/New_York').subtract('days', 6).startOf('day'), moment.tz(moment().valueOf(), 'America/New_York').endOf('day')],
                'Last 30 Days': [moment.tz(moment().valueOf(), 'America/New_York').subtract('days', 29).startOf('day'), moment.tz(moment().valueOf(), 'America/New_York').endOf('day')],
                'This Month': [moment.tz(moment().valueOf(), 'America/New_York').startOf('month').startOf('day'), moment.tz(moment().valueOf(), 'America/New_York').endOf('month').endOf('day')],
                'Last Month': [moment.tz(moment().valueOf(), 'America/New_York').subtract('month', 1).startOf('month').startOf('day'), moment.tz(moment().valueOf(), 'America/New_York').subtract('month', 1).endOf('month').endOf('day')]
            },
            startDate: moment.tz(startDatetime.valueOf(), 'America/New_York'),
            endDate: moment.tz(endDatetime.valueOf(), 'America/New_York'),
            maxDate: moment.tz(moment().valueOf(), 'America/New_York').endOf('day'),
            timePicker: true,
            timePickerIncrement: 1
        },
        function (start, end) {
            $('#report-range-display').html(moment.tz(start.valueOf(), 'America/New_York').format('MMMM D, YYYY HH:mm') + ' - ' + moment.tz(end.valueOf(), 'America/New_York').format('MMMM D, YYYY HH:mm'));
            startDatetime = moment.tz(start.valueOf(), 'America/New_York');
            endDatetime = moment.tz(end.valueOf(), 'America/New_York');
            loadRecords();
        });
    $('#report-range-display').html(moment.tz(startDatetime.valueOf(), 'America/New_York').format('MMMM D, YYYY HH:mm') + ' - ' + moment.tz(endDatetime.valueOf(), 'America/New_York').format('MMMM D, YYYY HH:mm'));
}

$(document).ready(function () {
    moment.tz.add('America/New_York|EST EDT|50 40|01010101010101010101010|1BQT0 1zb0 Op0 1zb0 Op0 1zb0 Op0 1zb0 Op0 1zb0 Op0 1zb0 Rd0 1zb0 Op0 1zb0 Op0 1zb0 Op0 1zb0 Op0 1zb0');
    $('a.sort-field').on('click', function (e) {
        sortHandler(e);
    });
});