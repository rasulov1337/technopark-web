function main() {
    const delBtn = document.querySelector('.del-question-btn')
    if (!delBtn)
        return
    const questionId = document.querySelector('.question').dataset.questionId
    delBtn.onclick = () => {
        const request = new Request(`/question/${questionId}`, {
            method: 'DELETE',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            }
        })

        fetch(request)
            .then((response) => document.location.href = '/',
                (error) => alert('Error: ' + error))
    }
}

main()