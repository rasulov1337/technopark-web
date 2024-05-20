"use strict"


function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}


function main() {
    const likeControlElements = document.querySelectorAll('.answer-like-control')
    for (const element of likeControlElements) {
        const likeBtn = element.getElementsByClassName('like-btn')[0]
        const counter = element.getElementsByClassName('like-counter')[0]
        const dislikeBtn = element.getElementsByClassName('dislike-btn')[0]
        const answerId = element.dataset.answerId

        function likeOrDislikeAnswer(isLike) {
            const request = new Request(`/like-answer/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: JSON.stringify({
                    answerId: answerId,
                    isLike: isLike
                })
            })
            fetch(request)
                .then((response) => response.json())
                .then((data) => {
                    counter.innerHTML = data.score
                })
        }

        likeBtn.onclick = () => likeOrDislikeAnswer(true)
        dislikeBtn.onclick = () => likeOrDislikeAnswer(false)
    }

    const questionId = document.querySelector('.question-like-control').dataset.questionId
    const correctAnswerCheckboxes = document.querySelectorAll('.correct-answer-checkbox')
    for (const checkbox of correctAnswerCheckboxes) {
        const answerId = checkbox.dataset.answerId
        checkbox.onchange = () => {
            const request = new Request(`/mark-answer/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: JSON.stringify({
                    questionId: questionId,
                    answerId: answerId
                })
            })
            fetch(request)
        }
    }
}


main()