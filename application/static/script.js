let random_p_colors = [
    '#3333ff',
    '#4775d1',
    '#000000',
    '#00e6e6',
    '#666699',
    '#00e600'
]

function BoldCardDetails(id_) {
    const el = document.getElementById(id_)
    el.style.fontWeight = 'bold';
   el.style.color = random_p_colors[Math.floor(Math.random() * random_p_colors.length)];
}

function BoldCardDetailsOff(id_) {
    const el = document.getElementById(id_)
    el.style.fontWeight = 'normal';
    el.style.color='#000000';
}