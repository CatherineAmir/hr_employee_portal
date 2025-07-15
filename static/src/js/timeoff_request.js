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

    window.location.href = '/my/timeoffs/delete/'+id.toString();


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


