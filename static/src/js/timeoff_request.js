// Bootstrap custom validation
document.addEventListener('DOMContentLoaded', function () {
    const forms = document.querySelectorAll('.needs-validation');
    console.log("DOMContentLoaded", forms);
    Array.from(forms).forEach(form => {
        form.addEventListener('submit', function (e) {
            if (!form.checkValidity()) {
                e.preventDefault();
                e.stopPropagation();
            }
            form.classList.add('was-validated');
        }, false);
    });
});

function on_change_leave_type(selectedLeaveType) {
    // This function is called when the leave type is changed
    // It updates the leave type field in the form
    const selectedOption = selectedLeaveType.options[selectedLeaveType.selectedIndex];
    const attachmentField = selectedOption.dataset.document;
    const request_unit = selectedOption.dataset.request_unit;
    console.log("Selected leave type:", selectedOption);
    console.log("Selected request_unit:", request_unit);
    const attachment_file = document.getElementById('document_attachment');
    const attachment_label = document.getElementById('attachment_label');
    if (attachmentField) {
        attachment_file.classList.remove('d-none');
        attachment_file.required = true;
        attachment_label.classList.remove('d-none');

    } else {
        attachment_file.classList.add('d-none');
        attachment_file.required = false;
        attachment_label.classList.add('d-none');
    }
    const half_day_div = document.getElementById('half_day_div');
    const certain_time_div = document.getElementById('certain_time_div');
    const date_to_div = document.getElementById('date_to_div');
    const custom_period_div = document.getElementById('custom_period_div');
    const custom_hours_div = document.getElementById('custom_hours_div');
    const customHoursInput = document.getElementById("custom_hours")
    const halfDayInput = document.getElementById('half_day')
    console.log("Selected attachment field:", attachmentField);
    console.log("Selected leave type:", request_unit);
    console.log("selectedOption", selectedOption);



    if (request_unit === "" || request_unit === null || request_unit === undefined) {
        console.log("request_unit is empty or null or undefined");
        customHoursInput.checked = false;

        halfDayInput.checked = false;

        half_day_div.classList.add('d-none');
        half_day_div.classList.remove('d-block');
        certain_time_div.classList.add('d-none');
        certain_time_div.classList.remove('d-block');
        custom_period_div.classList.add('d-none');
        custom_period_div.classList.remove('d-block');
        date_to_div.classList.remove('d-none');
        date_to_div.classList.add('d-block');
        custom_hours_div.classList.add('d-none');
        custom_hours_div.classList.remove('d-flex');
    }

    else if (request_unit === 'day') {
             console.log("in day");
        customHoursInput.checked = false;

        halfDayInput.checked = false;

        half_day_div.classList.add('d-none');
        half_day_div.classList.remove('d-block');
        certain_time_div.classList.add('d-none');
        certain_time_div.classList.remove('d-block');
        custom_period_div.classList.add('d-none');
        custom_period_div.classList.remove('d-block');
        date_to_div.classList.remove('d-none');
        date_to_div.classList.add('d-block');

    } else if (request_unit === 'half_day')
        // half day check box will appear
    {
             console.log("in half day");
        customHoursInput.checked = false;

        halfDayInput.checked = false;

        half_day_div.classList.remove('d-none');
        half_day_div.classList.add('d-block');
        certain_time_div.classList.add('d-none');
        certain_time_div.classList.remove('d-block');
    } else if (request_unit === 'hour') {
             console.log("in elif");
        customHoursInput.checked = false;

        halfDayInput.checked = false;

        certain_time_div.classList.add('d-block')
        certain_time_div.classList.remove('d-none')
        //     custom hour check box will appear
        half_day_div.classList.add('d-block')
        half_day_div.classList.remove('d-none')

    } else {
        console.log("in else");
        customHoursInput.checked = false;

        halfDayInput.checked = false;

        half_day_div.classList.add('d-none');
        half_day_div.classList.remove('d-block');
        certain_time_div.classList.add('d-none');
        certain_time_div.classList.remove('d-block');
        custom_period_div.classList.add('d-none');
        custom_period_div.classList.remove('d-block');
        date_to_div.classList.remove('d-none');
        date_to_div.classList.add('d-block');
        custom_hours_div.classList.add('d-none');
        custom_hours_div.classList.remove('d-flex');
    }
    console.log("customHoursInput.checked", customHoursInput.checked);
    console.log("customHoursInput.value", customHoursInput.value);
    console.log("halfDayInput.checked", halfDayInput.checked);
    console.log("halfDayInput.value", halfDayInput.value);


}

function buttonCancel(event) {


    event.preventDefault();

    window.location.href = '/my/timeoffs';
}


function confirmDelete() {
    // console.log(" in confirm delete id", id);
    const overlay = document.getElementById('deleteOverlay');
    const alertPopUp = document.getElementById('deleteAlertPopup');
    overlay.classList.add('d-block');
    overlay.classList.remove('d-none');
    alertPopUp.classList.add('d-block');
    alertPopUp.classList.remove('d-none');


}

function buttonDelete(id) {
    console.log(" in button delete id", id);
    const overlay = document.getElementById('deleteOverlay');
    const alertPopUp = document.getElementById('deleteAlertPopup');
    overlay.classList.add('d-none');
    overlay.classList.remove('d-block');
    alertPopUp.classList.add('d-none');
    alertPopUp.classList.remove('d-block');

    window.location.href = '/my/timeoffs/delete/' + id.toString();


}


function cancelDelete() {
    const overlay = document.getElementById('deleteOverlay');
    const alertPopUp = document.getElementById('deleteAlertPopup');

    overlay.classList.add('d-none');
    overlay.classList.remove('d-block');
    alertPopUp.classList.add('d-none');
    alertPopUp.classList.remove('d-block');


    // window.location.href = '/my/timeoffs';
}


function onChangeHalfDay(halfDayCheckbox) {
    // This function is called when the half day checkbox is changed
    // It updates the half day field in the form
    const custom_period_div = document.getElementById('custom_period_div');
    const date_to_div = document.getElementById('date_to_div');

    const customHoursInput = document.getElementById("custom_hours")


    console.log("Half day checkbox changed:", halfDayCheckbox.checked);
    if (halfDayCheckbox.checked) {
        customHoursInput.checked = false;

        custom_period_div.classList.remove('d-none');
        custom_period_div.classList.add('d-block');
        date_to_div.classList.add('d-none');
        date_to_div.classList.remove('d-block');


    } else {
        date_to_div.classList.remove('d-none');
        date_to_div.classList.add('d-block');

        custom_period_div.classList.add('d-none');
        custom_period_div.classList.remove('d-block');
    }
}


function onChangeCustomHour(customHourCheckBox) {
    const halfDayInput = document.getElementById('half_day')
    const custom_period_div = document.getElementById('custom_period_div');
    const date_to_div = document.getElementById('date_to_div');
    const custom_hours_div = document.getElementById('custom_hours_div');


    if (customHourCheckBox.checked) {
        halfDayInput.checked = false;

        date_to_div.classList.add('d-none');
        date_to_div.classList.remove('d-block');
        custom_period_div.classList.add('d-none');
        custom_period_div.classList.remove('d-block')
        custom_hours_div.classList.remove('d-none');
        custom_hours_div.classList.add('d-flex');

    } else {
        date_to_div.classList.add('d-block');
        date_to_div.classList.remove('d-none');
        custom_hours_div.classList.remove('d-flex');
        custom_hours_div.classList.add('d-none');


    }
}


function onchangeMorning(Morning) {
    if (Morning.checked) {
        const afternoon = document.getElementById('afternoon');
        afternoon.checked = false;

    }

}

function onchangeAfternoon(afternoon) {
    if (afternoon.checked) {
        const morning = document.getElementById('morning');
        morning.checked = false;

    }
}

