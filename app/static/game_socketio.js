
var socket;
var left_buff=[],right_buff=[],ball_buff=[];
var buff_min=20,buff_normal=50;


$(document).ready(function(){
    namespace = '/test';
    socket = io.connect('http://' + document.domain + ':' + location.port+namespace );

    socket.on('arrived', function(data) {
        console.log("arrived:",data.msg)
        $('#game_playground').css("display","block");
    });

    socket.on('status', function(data) {
        $('#chat').val($('#chat').val() + '<' + data.msg + '>\n');
        $('#chat').scrollTop($('#chat')[0].scrollHeight);
    });

    socket.on('gameobject', function(data) {
        
        left_buff.push(data.msg[1][1]);
        right_buff.push(data.msg[2][1]);
        ball_buff.push(data.msg[0]);

        $('#showgame').val($('#showgame').val() + data.msg[1][1]+ '\n');
        $('#showgame').scrollTop($('#showgame')[0].scrollHeight);
    });

    socket.on('message', function(data) {
        $('#chat').val($('#chat').val() + data.msg + '\n');
        $('#chat').scrollTop($('#chat')[0].scrollHeight);
    });
    $('#text').keypress(function(e) {
        var code = e.keyCode || e.which;
        if (code == 13) {
            text = $('#text').val();
            $('#text').val('');
            socket.emit('text', {msg: text});
        }
    });
    $('form#join').submit(function(event) {
        socket.emit('join', {room: $('#join_room').val()});
        return false;
    });

});


function leave_room() {
    socket.emit('left', {}, function() {
        socket.disconnect();

        // go back to the login page
        window.location.href = "{{ url_for('games.index') }}";
    });
}


        function ball_update(position){
            var width = $(".ball").outerWidth();
            var height = $(".ball").outerHeight();
            // console.log($(".ball").left())
            $(".ball").css({"left":position[0]-width/2,"top":position[1]-height/2});
        }
        function left_update(position){
            var windowHeight = $(window).height();
            var height = $(".left-goalkeeper").outerHeight();
            var p_top = position-height/2;
            var topMax = windowHeight - p_top - 5;
            if (p_top < 5) p_top = 5;
            if (p_top > topMax) p_top = topMax;
            $(".left-goalkeeper").css("top",p_top);	
        }
        function right_update(position){
            var windowHeight = $(window).height();
            var height = $(".right-goalkeeper").outerHeight();
            var p_top = position-height/2;
            var topMax = windowHeight - height - 5;
            if (p_top < 5) p_top = 5;
            if (p_top > topMax) p_top = topMax;
            $(".right-goalkeeper").css("top",p_top);	
        }

        
var startTime=new Date();
var speed=10;
var start_flag=0;
setInterval(function(){
    
    if (ball_buff.length>buff_normal){ 
        start_flag=1;
        // console.clear();   
        speed=10;
    }else if(ball_buff.length<buff_min){
        speed=50;
    }

    if (start_flag==1){
        left_update(left_buff.shift());
        right_update(right_buff.shift());
        ball_update(ball_buff.shift());
    }
},speed);