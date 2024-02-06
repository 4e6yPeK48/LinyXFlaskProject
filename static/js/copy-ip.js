let text = "play.linyx.ru";
const copyToClipboard = async () => {
    try {
        await navigator.clipboard.writeText(text);
        const button = document.getElementById('copy-ip');
        button.innerText = 'Скопировано!';
        button.classList.add('copied');
        setTimeout(() => {
            button.innerText = 'IP: play.linyx.ru';
            button.classList.remove('copied');
        }, 3000);
        console.log('Скопировано');
    } catch (err) {
        console.error('Не удалось скопировать: ', err);
    }
}