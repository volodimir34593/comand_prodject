document.addEventListener("DOMContentLoaded", function() {
    var countdownElements = document.querySelectorAll("[data-end-time]");
    
    countdownElements.forEach(function(element) {
      var endTime = new Date(element.getAttribute("data-end-time")).getTime();
  
      function updateCountdown() {
        var now = new Date().getTime();
        var distance = endTime - now;
  
        if (distance < 0) {
          element.innerHTML = "Час вийшов";
          clearInterval(interval);
          return;
        }
  
        var days = Math.floor(distance / (1000 * 60 * 60 * 24));
        var hours = Math.floor((distance % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
        var minutes = Math.floor((distance % (1000 * 60 * 60)) / (1000 * 60));
        var seconds = Math.floor((distance % (1000 * 60)) / 1000);
  
        element.innerHTML = days + "д " + hours + "г " + minutes + "хв " + seconds + "с";
      }
  
      var interval = setInterval(updateCountdown, 1000);
      updateCountdown();
    });
  });

// Функція для відправки запиту на оновлення ставки
async function placeBid(itemId, bidAmount, endTime) {
    try {
        const response = await fetch('/place_bid', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                item_id: itemId,
                bid_amount: bidAmount,
                end_time: endTime,
            }),
        });

        if (!response.ok) {
            throw new Error('Network response was not ok');
        }

        const result = await response.json();
        if (result.success) {
            // Оновіть елемент на сторінці, щоб показати нову ціну або інформацію про ставку
            console.log('Bid placed successfully:', result.bid_amount);
        } else {
            console.error('Bid placement failed:', result.error);
        }
    } catch (error) {
        console.error('Error placing bid:', error);
    }
}


function refreshBid(data, form) {
    const lot_info = form.closest('.lot-info');
    const current_price_label = lot_info.querySelector(`span#current_price_${data.lot_id}`);
    const bidInput = form.querySelector("input[type='number']");

    current_price_label.textContent = "$" + data.bid_amount;
    bidInput.min = parseFloat(data.bid_amount) + 0.01;  // Встановлюємо нову мінімальну ставку
    bidInput.value = '';  // Очищаємо поле вводу
}

function updateTimer(timerElement, endTime) {
    const now = new Date().getTime();
    const timeLeft = endTime - now;

    if (timeLeft > 0) {
        const days = Math.floor(timeLeft / (1000 * 60 * 60 * 24));
        const hours = Math.floor((timeLeft % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
        const minutes = Math.floor((timeLeft % (1000 * 60 * 60)) / (1000 * 60));
        const seconds = Math.floor((timeLeft % (1000 * 60)) / 1000);

        timerElement.textContent = `${days}d ${hours}h ${minutes}m ${seconds}s`;
    } else {
        timerElement.textContent = "Аукціон завершено";
        // Можна додати додаткову логіку для завершення аукціону
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
});