/**
 * Created by sliu on 11/3/14.
 */
moment.tz.add('America/New_York|EST EDT|50 40|01010101010101010101010|1BQT0 1zb0 Op0 1zb0 Op0 1zb0 Op0 1zb0 Op0 1zb0 Op0 1zb0 Rd0 1zb0 Op0 1zb0 Op0 1zb0 Op0 1zb0 Op0 1zb0');

/* make folders collapsible */
function makeCollapsible() {
    // Find list items representing folders and
    // style them accordingly.  Also, turn them
    // into links that can expand/collapse the
    // tree leaf.
    // Missing Files
    $('li > ul.missing_files_list').each(function (i) {
        // Find this list's parent list item.
        var parent_li = $(this).parent('li');

        // Style the list item as folder.
        parent_li.addClass('folder');

        // Temporarily remove the list from the
        // parent list item, wrap the remaining
        // text in an anchor, then reattach it.
        var sub_ul = $(this).remove();
        parent_li.wrapInner('<a/>').find('a').click(function () {
            // Make the anchor toggle the leaf display.
            sub_ul.toggle();
            if ($(sub_ul).is(":hidden")) {
                $("#missing_slots_view").removeClass('fa-minus-square-o');
                $("#missing_slots_view").addClass('fa-plus-square-o');
            } else {
                $("#missing_slots_view").removeClass('fa-plus-square-o');
                $("#missing_slots_view").addClass('fa-minus-square-o');
            }
        });
        parent_li.append(sub_ul);
    });

    // Project Defective
    $('li > table').each(function (i) {
        var parent_li = $(this).parent('li');
        parent_li.addClass('folder');
        var sub_table = $(this).remove();
        parent_li.wrapInner('<a/>').find('a').click(function (){
            sub_table.toggle();
            if ($(sub_table).is(":hidden")){
                $('#project_defect_view').removeClass('fa-minus-square-o');
                $('#project_defect_view').addClass('fa-plus-square-o');
            } else {
                $('#project_defect_view').removeClass('fa-plus-square-o');
                $('#project_defect_view').addClass('fa-minus-square-o');
            }
        });
        parent_li.append(sub_table);
    });

    // Hide all lists except the outermost.
    $('ul ul.missing_files_list').hide();
    $('ul table').hide();
}

var startDatetime = moment.tz(moment().valueOf(), 'America/New_York');
var endDatetime = moment.tz(moment().valueOf(), 'America/New_York');

function setStartDate(datetime) {
    startDatetime = moment.tz(moment(datetime*1000), 'America/New_York');
//    startDatetime = moment(datetime*1000);
}

function setEndDate(datetime) {
    endDatetime = moment.tz(moment(datetime*1000), 'America/New_York');
//    endDatetime = moment(datetime*1000);
}

//function attachDateRangePicker() {
//    $('#report-range').daterangepicker(
//        {
//            ranges: {
//                'Today': [moment().valueOf().startOf('day'), moment().valueOf().endOf('day')],
//                'Yesterday': [moment().valueOf().subtract('days', 1).startOf('day'), moment().valueOf().subtract('days', 1).endOf('day')],
//                'Last 7 Days': [moment().valueOf().subtract('days', 6).startOf('day'), moment().valueOf().endOf('day')],
//                'Last 30 Days': [moment().valueOf().subtract('days', 29).startOf('day'), moment().valueOf().endOf('day')],
//                'This Month': [moment().valueOf().startOf('month').startOf('day'), moment().valueOf().endOf('month').endOf('day')],
//                'Last Month': [moment().valueOf().subtract('month', 1).startOf('month').startOf('day'), moment().valueOf().subtract('month', 1).endOf('month').endOf('day')]
//            },
//            startDate: startDatetime,
//            endDate: endDatetime,
//            timePicker: true,
//            timePickerIncrement: 1
//        },
//        function (start, end) {
//            $('#report-range-display').html(start.format('MMMM D, YYYY HH:mm') + ' - ' + end.format('MMMM D, YYYY HH:mm'));
//            startDatetime = start;
//            endDatetime = end;
////            loadRecords(sourceType);
//        });
//    $('#report-range-display').html(startDatetime.format('MMMM D, YYYY HH:mm') + ' - ' + endDatetime.format('MMMM D, YYYY HH:mm'));
//}

function loadRecords() {
    window.location.href = "{% url 'reports:report_project' project.id %}?start=" + startDatetime.format('X') + "&end=" + endDatetime.format('X');
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
    makeCollapsible();
    moment.tz.add('America/New_York|EST EDT|50 40|01010101010101010101010|1BQT0 1zb0 Op0 1zb0 Op0 1zb0 Op0 1zb0 Op0 1zb0 Op0 1zb0 Rd0 1zb0 Op0 1zb0 Op0 1zb0 Op0 1zb0 Op0 1zb0');
});