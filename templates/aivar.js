var unlocks = [];
$('#subjects').text(JSON.stringify(subjects));
$('#matches').text(JSON.stringify(matches));
$('#results').text(JSON.stringify(results));
matches.map(function (match) {
    var achievement = subjects.find(function (achievement) {
        return achievement.iconClosed.substring(achievement.iconClosed.lastIndexOf('/')+1) === match.subject;
    });
    if (achievement
    //&& achievement.indexOf(achievement) < 0
    ) {
        var unlockAtSecond = (parseInt(match.frame.split('.')[0]) - 1) * frameInterval;
        var minutes = Math.floor(unlockAtSecond / 60)
        minutes = minutes < 10 ? '0'+minutes : minutes
        var seconds = unlockAtSecond % 60
        seconds = seconds < 10 ? '0'+seconds : seconds
        achievement.unlockAtSecond = unlockAtSecond;
        achievement.unlockAt = minutes + ':' + seconds;
        unlocks.push(achievement)
    }
});
unlocks.forEach(function (unlock) {
    $('#unlocks').append('<div class="media mb-2 align-content-center p-2 bg-light">' +
        '<div class="mr-3 flex-row justify-content-center">' +
        '<a href="#"  onclick="seekTo(' + unlock.unlockAtSecond + ');">' + unlock.unlockAt + '</a>' +
        '</div>' +
        '<img class="mr-3" src="' + unlock.iconClosed + '" style="width:32px" alt="">' +
        '<div class="media-body">' +
        '<b>' + unlock.name + '</b><br>' +
        '<small class="text-muted">' + unlock.description + '</small>' +
        '</div>' +
        '</div>'
    )
})