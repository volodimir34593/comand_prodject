document.addEventListener('DOMContentLoaded', function () {
    var countryCodeInput = document.getElementById('country_code'); // Поле вибору коду країни
    var phoneNumberInput = document.getElementById('phone_number'); // Поле для введення номера телефону
    var phoneError = document.getElementById('phone_error'); // Елемент для відображення помилки

    // Очищаємо поле для введення номера телефону і приховуємо повідомлення про помилку при зміні коду країни
    countryCodeInput.addEventListener('change', function () {
        phoneNumberInput.value = countryCodeInput.value; // Встановлюємо введений код країни з "+" в поле для введення номера телефону
        phoneError.style.display = 'none'; // Приховуємо повідомлення про помилку
        phoneNumberInput.focus(); // Переводимо фокус на поле введення номера телефону
    });

    // При введенні номера телефону перевіряємо, чи введено лише цифри або "+"
    phoneNumberInput.addEventListener('input', function () {
        var phoneNumber = phoneNumberInput.value.trim();
        var isValid = /^[0-9+]+$/.test(phoneNumber); // Перевірка на наявність цифр або "+"

        if (!isValid) {
            phoneError.style.display = 'block'; // Показуємо повідомлення про помилку
        } else {
            phoneError.style.display = 'none'; // Приховуємо повідомлення про помилку
        }
    });

    // Перевірка при зміні фокусу з поля введення номера телефону
    phoneNumberInput.addEventListener('blur', function () {
        phoneError.style.display = 'none'; // Приховуємо повідомлення про помилку при зміні фокусу
    });

    // Функція, що додає код країни до номера телефону перед відправкою форми
    function prependCountryCode(e) {
        var countryCode = document.getElementById('country_code').value;
        var phoneNumber = phoneNumberInput.value.trim();

        if (!/^[0-9]+$/.test(phoneNumber)) {
            e.preventDefault(); // Зупиняємо відправку форми, якщо номер містить недопустимі символи
            phoneError.style.display = 'block'; // Показуємо повідомлення про помилку
        } else {
            phoneError.style.display = 'none'; // Приховуємо повідомлення про помилку
            if (!phoneNumber.startsWith(countryCode)) {
                phoneNumberInput.value = countryCode + phoneNumber;
            }
        }
    }

    var loginForm = document.querySelector('form');
    if (loginForm) {
        loginForm.addEventListener('submit', prependCountryCode);
    }
});
