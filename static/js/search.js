"use strict"

const searchElement = document.querySelector('.search')
const dropdownList = document.getElementById('dropdown-list')
const dropdownWrapper = document.querySelector('.dropdown')

const QUESTION_URL = '/question/'


function clearSuggestions(element) {
    element.innerHTML = ''
}

searchElement.addEventListener('focus', () => {
    if (dropdownList.childElementCount)
        dropdownWrapper.classList.remove('d-none')
})


searchElement.addEventListener('input', function (event) {
    dropdownWrapper.classList.remove('d-none')

    const request = new Request(`/search?q=${this.value}`)
    fetch(request)
    .then((response) => response.json())
    .then((data) => {
        clearSuggestions(dropdownList)
        if (!data || !data.data.length) {
            dropdownList.insertAdjacentHTML('beforeend', `<li><a class="dropdown-item">No results!</a></li>`)            
            return;
        }
        data.data.forEach((val) => {
            const questionTitle = val['title']
            const questionID = val['id']
            dropdownList.insertAdjacentHTML('beforeend', `<li><a class="dropdown-item" href="${QUESTION_URL + questionID}">${questionTitle}</a></li>`)
        });
    })
})

searchElement.addEventListener('focusout', () => {
    // HACK: If we hide the element immediately the link user clicked will hide too.
    // And therefore the user won't actually click the link because it is hidden.
    // So that's why we need to add some delay.
    setTimeout(() => dropdownWrapper.classList.add('d-none'), 100)
})

