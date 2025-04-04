document.getElementById('addDepartmentBtn').addEventListener('click', function() {
    var departmentInput = document.getElementById('department').value.trim();

    var successMessage = document.getElementById('successMessage');
    var warningMessage = document.getElementById('warningMessage');

    // Clear previous messages
    successMessage.style.display = 'none';
    warningMessage.style.display = 'none';

    // Check if the input is empty
    if (departmentInput === "") {
        // Show warning message
        warningMessage.style.display = 'block';

        // Hide the message after 3 seconds
        setTimeout(function() {
            warningMessage.style.display = 'none';
        }, 3000); // 3 seconds
    } else {
        // Show success message if department is added
        successMessage.style.display = 'block';

        // Clear the input field
        document.getElementById('department').value = '';

        // Hide the message after 3 seconds
        setTimeout(function() {
            successMessage.style.display = 'none';
        }, 3000); // 3 seconds
    }
});
