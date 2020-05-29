function fresh(){
    var del1 = window.parent.document.getElementById('parentNoti1')
    var del1child = window.parent.document.getElementById('notificationsCnt1')
    del1.removeChild(del1child)
    var del2 = window.parent.document.getElementById('parentNoti2')
    var del2child = window.parent.document.getElementById('notificationsCnt2')
    del2.removeChild(del2child)
}