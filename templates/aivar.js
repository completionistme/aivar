var unlocks = [];
$('#subjects').text(JSON.stringify(subjects));
$('#matches').text(JSON.stringify(matches));
$('#results').text(JSON.stringify(results));

/**
 * sort subjects by unlock time
 */
subjects.sort(function (a, b) {
    return a.unlockTimestamp - b.unlockTimestamp;
});

/**
 * collect and clean up matches
 */
matches.map(function (match) {
    var achievements = subjects.filter(function (achievement) {
        return achievement.iconClosed.substring(achievement.iconClosed.lastIndexOf('/') + 1) === match.subject;
    });
    if (achievements) {
        var unlockAtSecond = (parseInt(match.frame.split('.')[0]) - 1) * frameInterval;
        var minutes = Math.floor(unlockAtSecond / 60);
        minutes = minutes < 10 ? '0' + minutes : minutes;
        var seconds = unlockAtSecond % 60;
        seconds = seconds < 10 ? '0' + seconds : seconds;
        match.unlockAtSecond = unlockAtSecond;
        match.unlockAt = minutes + ':' + seconds;
        match.achievements = achievements;
        unlocks.push(match)
    }
});
activeUnlockIds = [];
unlocks.sort(function (a, b) {
    return a.unlockAtSecond - b.unlockAtSecond;
});
var previousUnlock = null;
unlocks.forEach(function (unlock) {
    var assumedUnlock = false;
    var achievementsOut = '';
    unlock.isDupe = false;
    unlock.achievements.forEach(function (achievement) {
        var active = false;
        var possiblyDupe = false;
        var subsequentUnlock = previousUnlock && unlock.unlockAtSecond - previousUnlock.unlockAtSecond <= frameInterval;

        if (subsequentUnlock && previousUnlock.achievements.indexOf(achievement) > -1) {
            possiblyDupe = true;
            unlock.isDupe = true;
        }

        if (!assumedUnlock && activeUnlockIds.indexOf(achievement) === -1) {
            if (subsequentUnlock && previousUnlock.achievements.indexOf(achievement) > -1) {
                possiblyDupe = true;
            } else {
                assumedUnlock = true;
                active = true;
                activeUnlockIds.push(achievement);
            }
        }
        achievementsOut += '<div class="ml-3 p-2 media-body border rounded ' +
            ' ' + (active ? 'border-info' : 'border-dark ' + (possiblyDupe ? 'text-muted' : '')) +
            ' " style="max-width: 400px">' +
            '<b>' + achievement.name + '</b>';
        if (achievement.description) {
            achievementsOut += '<br><small class="text-muted">' + achievement.description + '</small>';
        }
        achievementsOut += '</div>';
    });
    var unlockOut = '<div class="media mb-2 align-content-center p-2 bg-light ' + (unlock.isDupe ? 'text-muted' : '') + '">' +
        '<div class="mr-3 flex-row justify-content-center">' +
        '<a href="#"  onclick="seekTo(' + unlock.unlockAtSecond + ');return false;">' + unlock.unlockAt + '</a>' +
        '</div>' +
        '<img class="" src="' + unlock.achievements[0].iconClosed + '" style="width:64px" alt="">' +
        achievementsOut +
        '</div>';
    if(unlock.isDupe) {
        return;
    }
    $('#unlocked').append(unlockOut);
    previousUnlock = unlock;
});
