$(document).ready(function() {

    function createCookie(name,value,days) {
        var expires;
        var date;
        if (days) {
            date = new Date();
            date.setTime(date.getTime()+(days*24*60*60*1000));
            expires = "; expires="+date.toGMTString();
        }
        else {
            expires = "";
        }
        document.cookie = name+"="+value+expires+"; path=/";
    }
    function readCookie(name) {
        var nameEQ = name + "=";
        var ca = document.cookie.split(';');
        for(var i=0;i < ca.length;i++) {
            var c = ca[i];
            while (c.charAt(0)==' ') c = c.substring(1,c.length);
            if (c.indexOf(nameEQ) == 0) return c.substring(nameEQ.length,c.length);
        }
        return null;
    }

var newsId = $('.content-box.single-post')
    .first()
    .attr('data-newsid');

    if(typeof newsId !== typeof undefined && newsId !== false && readCookie('popularCounter' + newsId) !== '1'){
        $.ajax({
            url: "?type=6666666&tx_news_pi1[action]=increaseMostPopularCounterForNews&tx_news_pi1[controller]=News&tx_news_pi1[news]=" + newsId,
            contentType: "application/json",
            success: function(){
                /*sets a cookie if so mostpopular can be updated only once in 24h per user*/
                createCookie('popularCounter' + newsId, 1, 1);
            }
        });
    }
});


