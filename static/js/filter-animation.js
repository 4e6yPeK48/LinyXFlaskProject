function filterProducts(category) {
    let productGrid = document.getElementById('productGrid');
    let cards = productGrid.getElementsByClassName('card');
    let visibleCards = [];

    for (let i = 0; i < cards.length; i++) {
        let card = cards[i];
        let description = card.getAttribute('data-description');
        let showCard = (category === 'Всё' || description.includes(category));

        if (showCard) {
            visibleCards.push(card);
        } else {
            card.classList.remove('fadeIn');
            card.classList.add('fadeOut');
            setTimeout(() => {
                card.style.display = 'none';
            }, 500);
        }
    }

    setTimeout(() => {
        for (let i = 0; i < visibleCards.length; i++) {
            let card = visibleCards[i];
            card.style.display = 'block';
            setTimeout(() => {
                card.classList.remove('fadeOut');
                card.classList.add('fadeIn');
            }, 10);
        }
    }, 500);
}