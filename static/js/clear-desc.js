function showProductDetails() {
    let productDetails = document.getElementById('productDetails');
    productDetails.innerHTML = '<p class="black-white-text">Подождите...</p>';
    productDetails.classList.remove('hidden');
}

function hideProductDetails() {
    let productDetails = document.getElementById('productDetails');
    productDetails.innerHTML = '<p class="black-white-text">Подождите...</p>';
    productDetails.classList.add('hidden');
}