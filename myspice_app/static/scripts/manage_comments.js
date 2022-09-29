let display = (id) => {
    let specific_delete_button = document.getElementById(`delete_button_${id}`)
    specific_delete_button.style.display = 'block';
}

let hide = (id) => {
    let specific_delete_button = document.getElementById(`delete_button_${id}`)
    specific_delete_button.style.display = 'none';
}