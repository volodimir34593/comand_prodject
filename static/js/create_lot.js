var fileInputCount = 1; // Початкова кількість файлових полів
var existingImagesCount = document.querySelectorAll('.carousel-inner .carousel-item').length; // Кількість існуючих зображень

function addFileInput() {
    if (fileInputCount < 10) { // Перевірка на максимальну кількість файлових полів
        var fileInputs = document.getElementById("file_inputs");

        // Створюємо новий елемент div для нового файлового поля
        var newFileInputWrapper = document.createElement("div");
        newFileInputWrapper.classList.add("file-input-wrapper");
        newFileInputWrapper.innerHTML = '<input type="file" name="lot_images[]" accept="image/*" onchange="showPreview(this.files); addFileInput();"><br>';
        fileInputs.appendChild(newFileInputWrapper);
        fileInputCount++;
    } else {
        alert("Максимальна кількість файлів досягнута (10).");
    }
}

function showPreview(files) {
    var carouselInner = document.querySelector('.carousel-inner');
    
    // Додаємо нові зображення
    for (var i = 0; i < files.length; i++) {
        var file = files[i];
        var reader = new FileReader();

        reader.onload = function(e) {
            var div = document.createElement("div");
            div.className = "carousel-item";
            if (carouselInner.children.length === 0) {
                div.className += " active";
            }
            var img = document.createElement("img");
            img.src = e.target.result;
            img.className = "d-block w-100";
            img.style.objectFit = "contain";
            img.style.height = "600px";
            div.appendChild(img);
            
            var closeButton = document.createElement("button");
            closeButton.className = "btn-close position-absolute top-0 end-0";
            closeButton.style.background = "transparent";
            closeButton.style.border = "none";
            closeButton.style.fontSize = "2rem";
            closeButton.style.color = "red";
            closeButton.innerHTML = "&times;";
            closeButton.setAttribute("aria-label", "Close");
            closeButton.addEventListener('click', function() {
                deleteImage(img.src);
            });
            div.appendChild(closeButton);
            
            carouselInner.appendChild(div);

            // Оновити кількість існуючих зображень
            existingImagesCount++;
        }

        reader.readAsDataURL(file);
    }
}

function deleteAllImages() {
    if (confirm('Ви впевнені, що хочете видалити всі фотографії?')) {
        var form = document.createElement("form");
        form.method = "POST";
        form.action = "/delete_images/{{ lot.id }}"; // Оновіть з правильним маршрутом

        var input = document.createElement("input");
        input.type = "hidden";
        input.name = "delete_images";
        input.value = "true";
        form.appendChild(input);

        document.body.appendChild(form);
        form.submit();
    }
}

function deleteImage(imageUrl) {
    if (confirm('Ви впевнені, що хочете видалити це зображення?')) {
        var lotId = getLotId();
        if (!lotId) {
            console.error('Не вдалося отримати ID лота.');
            alert('Не вдалося отримати ID лота.');
            return;
        }
        
        fetch('/delete_image', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                lot_id: lotId,
                image_url: imageUrl
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Remove the image from the carousel
                var carouselItem = document.querySelector(`.carousel-item img[src="${imageUrl}"]`).closest('.carousel-item');
                carouselItem.remove();
                
                // If it was the active image, activate the next one
                if (carouselItem.classList.contains('active')) {
                    var nextItem = document.querySelector('.carousel-item');
                    if (nextItem) {
                        nextItem.classList.add('active');
                    }
                }

                // Оновити кількість існуючих зображень
                existingImagesCount--;
            } else {
                alert('Помилка при видаленні зображення');
            }
        })
        .catch((error) => {
            console.error('Error:', error);
            alert('Помилка при видаленні зображення');
        });
    }
}

function getLotId() {
    var inputElement = document.querySelector('input[name="lot_id"]');
    if (inputElement) {
        return inputElement.value;
    } else {
        console.error('Input element with name "lot_id" not found.');
        return null; // or handle the error as per your application's logic
    }
}

$(document).ready(function() {
    $('.carousel').each(function() {
        var $carousel = $(this);
        var $items = $carousel.find('.carousel-item');
        var $next = $carousel.find('.carousel-control-next');
        var $prev = $carousel.find('.carousel-control-prev');

        // Приховати кнопки "вперед" і "назад", якщо є лише одне зображення
        if ($items.length <= 1) {
            $next.hide();
            $prev.hide();
        }

        // Приховати кнопку "вперед" на останньому слайді і "назад" на першому
        $carousel.on('slid.bs.carousel', function() {
            var $active = $carousel.find('.carousel-item.active');
            $prev.show();
            $next.show();
            if ($active.is(':first-child')) {
                $prev.hide();
            } else if ($active.is(':last-child')) {
                $next.hide();
            }
        });

        // Викликати подію slid.bs.carousel вручну при завантаженні сторінки
        $carousel.trigger('slid.bs.carousel');
    });
})
// Додати перевірку форми перед відправкою
document.getElementById('lot_form').addEventListener('submit', function(event) {
    var fileInputs = document.querySelectorAll('input[type="file"]');
    var filesSelected = false;

    // Перевірити, чи є вибрані файли
    fileInputs.forEach(function(fileInput) {
        if (fileInput.files.length > 0) {
            filesSelected = true;
        }
    });

    // Перевірити, чи є хоча б одне існуюче зображення в каруселі
    var carouselImages = document.querySelectorAll('.carousel-inner .carousel-item');
    var existingImagesCount = carouselImages.length;

    if (!filesSelected && existingImagesCount === 0) {
        event.preventDefault(); // Заборонити відправку форми
        alert('Будь ласка, завантажте принаймні одне зображення або залиште одне зі старих.');
    }
});
