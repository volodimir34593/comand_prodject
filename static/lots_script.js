function placeBid(lotId) {
    var bidInput = document.getElementById('bid-' + lotId);
    console.log('bid-' + lotId)
    console.log(bidInput)
    var bidValue = parseFloat(bidInput.value);

    if (isNaN(bidValue) || bidValue <= 0) {
        alert('Будь ласка, введіть дійсну суму ставки.');
        return false;
    }

    // Відправка ставки на сервер через fetch API
    fetch('/place_bid', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            lot_id: lotId,
            bid: bidValue
        })
    }).then(response => response.json())
      .then(data => {
          if (data.success) {
              alert('Ваша ставка прийнята!');
              location.reload(); // Перезавантажує сторінку для відображення нової ставки
          } else {
              alert('Помилка: ' + data.error);
          }
      });

    return false; // Запобігає відправці форми
}
//alert ('Завантажується')