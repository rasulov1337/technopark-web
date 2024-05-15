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
    const likeControlElements = document.querySelectorAll('.question-like-control')
    for (const element of likeControlElements) {
        const likeBtn = element.getElementsByClassName('like-btn')[0]
        const counter = element.getElementsByClassName('like-counter')[0]
        const dislikeBtn = element.getElementsByClassName('dislike-btn')[0]
        const questionId = element.dataset.questionId

        function likeOrDislikeQuestion(isLike) {
            const request = new Request(`/like-question/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: JSON.stringify({
                    questionId: questionId,
                    isLike: isLike
                })
            })
            fetch(request)
                .then((response) => response.json())
                .then((data) => {
                    counter.innerHTML = data.score
                })
        }

        likeBtn.onclick = () => likeOrDislikeQuestion(true)
        dislikeBtn.onclick = () => likeOrDislikeQuestion(false)
    }
}


main()