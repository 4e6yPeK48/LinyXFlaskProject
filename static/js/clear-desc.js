function showProductDetails() {
    let productGrid = document.getElementById('productGrid');
    productGrid.classList.add('hidden');
    let productDetails = document.getElementById('productDetails');
    productDetails.classList.remove('hidden');
    productDetails.classList.remove('fade-Out');
    productDetails.innerHTML = '<p class="black-white-text">Подождите...</p>';
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

function clearTags() {
    let productDetails = document.getElementById('productDetails');
    if (productDetails) {
        const containers = document.querySelectorAll('.all-products-container');
        containers.forEach(container => {
            container.classList.remove(
                'gradient-color-shulker',
                'gradient-color-vega',
                'gradient-color-eola',
                'gradient-color-chorus',
                'gradient-color-hydra',
                'gradient-color-fenix',
                'gradient-color-leviathan',
                'gradient-color-satira'
            );
        });
        const sticks = document.querySelectorAll('.stick-light-sm');
        sticks.forEach(stick => {
            stick.classList.remove(
                'gradient-color-shulker',
                'gradient-color-vega',
                'gradient-color-eola',
                'gradient-color-chorus',
                'gradient-color-hydra',
                'gradient-color-fenix',
                'gradient-color-leviathan',
                'gradient-color-satira'
            );
        });
    }
}

document.addEventListener('keydown', function (event) {
    if (event.key === "Escape") {
        hideProductDetails();
        clearTags();
    }
});


function showProductDetailsPc(product_id) {
    let productGrid = document.getElementById('productGrid');
    let productDetails = document.getElementById('productDetails');

    if (!productDetails.classList.contains('hidden')) {
        hideProductDetails();
        setTimeout(function () {
            productDetails.classList.remove('hidden');
            productDetails.classList.remove('fade-Out');
            productDetails.innerHTML = '<p class="black-white-text">Подождите...</p>';
            openProductDialog(product_id);
        }, 300);
    } else {
        productGrid.classList.add('hidden');
        productDetails.classList.remove('hidden');
        productDetails.classList.remove('fade-Out');
        productDetails.innerHTML = '<p class="black-white-text">Подождите...</p>';
        openProductDialog(product_id);
    }
}