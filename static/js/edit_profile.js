document.addEventListener('DOMContentLoaded', function() {
    var userPhoneNumber = "{{ user.phone_number }}"; // Отримуємо номер телефону користувача
    var countryCodeInput = document.getElementById('country_code'); // Поле вибору коду країни
    var phoneNumberInput = document.getElementById('phone_number'); // Поле для введення номера телефону

    // Очищаємо поле для введення номера телефону при виборі нового коду країни
    countryCodeInput.addEventListener('change', function() {
        phoneNumberInput.value = countryCodeInput.value; // Встановлюємо введений код країни без "+"
    });

    // При завантаженні сторінки встановлюємо значення полів на основі збереженого номера т

    // Функція для оновлення номера телефону з урахуванням вибраного коду країни
    function updatePhoneNumber() {
        var selectedCountryCode = countryCodeInput.value; // Отримуємо вибраний код країни
        var cleanedPhoneNumber = userPhoneNumber.trim().replace(/\D/g, ''); // Очищаємо номер телефону користувача від нецифрових символів

        // Перевіряємо, чи номер телефону починається з вибраного коду країни
        if (!cleanedPhoneNumber.startsWith(selectedCountryCode)) {
            phoneNumberInput.value = selectedCountryCode; // Встановлюємо введений код країни без "+"
        }
    }
});

// Цей код створює кругле зображення після завантаження файлу
document.getElementById('avatar').addEventListener('change', function(event) {
    const file = event.target.files[0];
    const reader = new FileReader();

    reader.onload = function(e) {
        const img = new Image();
        img.src = e.target.result;

        img.onload = function() {
            const canvas = document.createElement('canvas');
            const ctx = canvas.getContext('2d');
            const size = Math.min(img.width, img.height);
            
            canvas.width = size;
            canvas.height = size;
            ctx.beginPath();
            ctx.arc(size / 2, size / 2, size / 2, 0, Math.PI * 2);
            ctx.closePath();
            ctx.clip();
            ctx.drawImage(img, 0, 0, size, size);

            const roundedImage = new Image();
            roundedImage.src = canvas.toDataURL('image/png');

            // Отримуємо контейнер для попереднього перегляду аватара
            const avatarPreview = document.getElementById('avatar-preview');
            avatarPreview.innerHTML = ''; // Очищаємо попередній попередній перегляд
            avatarPreview.appendChild(roundedImage);
        };
    };

    reader.readAsDataURL(file);
});
