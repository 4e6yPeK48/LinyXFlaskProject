function showProductDetails() {
    let productDetails = document.getElementById('productDetails');
    productDetails.classList.remove('fade-Out');
    let productGrid = document.getElementById('productGrid');
    productDetails.innerHTML = '<p class="black-white-text">Подождите...</p>';
    productGrid.classList.add('hidden');
    productDetails.classList.remove('hidden');
}

function hideProductDetails() {
    let productDetails = document.getElementById('productDetails');
    let productGrid = document.getElementById('productGrid');

    function addClasses() {
        productDetails.classList.add('fade-Out');
        setTimeout(function () {
            productDetails.classList.add('hidden');
        }, 300);
    }

    addClasses();
    productGrid.classList.remove('hidden');
}