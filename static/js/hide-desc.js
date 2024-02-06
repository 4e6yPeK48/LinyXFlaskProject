function addTags() {
    let productGrid = document.getElementById('productGrid');
    productGrid.classList.add('hidden');
}

function removeTags() {
    let productDetail = document.getElementById('productDetails');
    let productGrid = document.getElementById('productGrid');
    productDetail.classList.add('hidden');
    productGrid.classList.remove('hidden');
}