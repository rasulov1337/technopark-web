const centrifugoData = document.querySelector('.centrifugo-data').dataset

const container = document.getElementById('counter');

const centrifuge = new Centrifuge(centrifugoData.url, {
    token: centrifugoData.token
});

centrifuge.on('connecting', function (ctx) {
    console.log(`connecting: ${ctx.code}, ${ctx.reason}`);
}).on('connected', function (ctx) {
    console.log(`connected over ${ctx.transport}`);
}).on('disconnected', function (ctx) {
    console.log(`disconnected: ${ctx.code}, ${ctx.reason}`);
}).connect();

const sub = centrifuge.newSubscription(centrifugoData.wsChannelName);

sub.on('publication', function (ctx) {
    console.log(ctx)
    const answersContainer = document.querySelector('.answers-container')
    const sampleAnswerElement = document.querySelector('.answer').cloneNode(true)  // The first element is the hidden template answer
    sampleAnswerElement.querySelector('.answer-text').innerHTML = ctx.data.text
    sampleAnswerElement.querySelector('.correct-answer-checkbox').innerHTML = ctx.data.isCorrect
    sampleAnswerElement.querySelector('.score-counter').innerHTML = ctx.data.score
    sampleAnswerElement.querySelector('img').src = ctx.data.avatarLink

    console.log(sampleAnswerElement.style)
    sampleAnswerElement.style.display = "block"

    answersContainer.appendChild(sampleAnswerElement)
}).subscribe();