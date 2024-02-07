function filterProducts(category) {
    let productGrid = document.getElementById('productGrid');
    let cards = productGrid.getElementsByClassName('card');

    for (let card of cards) {
        card.classList.add('fadeOut');
    }

    setTimeout(() => {
        for (let card of cards) {
            card.style.display = 'none';
        }

        for (let card of cards) {
            let description = card.getAttribute('data-description');
            let showCard = (category === 'Всё' || description.includes(category));
            if (showCard) {
                card.style.display = 'block';
            }
        }

        setTimeout(() => {
            for (let card of cards) {
                if (card.style.display === 'block') {
                    card.classList.remove('fadeOut');
                    card.classList.add('fadeIn');
                }
            }
        }, 10);
    }, 500);
}
