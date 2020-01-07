var ws = new WebSocket("ws://192.168.1.23:19002/ws");

ws.onmessage = (event) => {
    console.log(event.data)
    let message_json = JSON.parse(event.data)
};

var p = 0;

var interval_func = setInterval(
    () => {
        if (p < 1000) {
            p++;
        }
        else {
            clearInterval(interval_func);
        }
        if (ws.readyState !== WebSocket.OPEN) {
            console.log(illo.dragRotate.rotate.x);
            //illo.dragRotate.rotate.x = p/100;
            // ws.send(JSON.stringify({
            //     "sender":"js",
            //     "opCode":"moveit",    
            //     "data":{
            //         "param":124, 
            //         "brief":"forward"
            //     }
            // }));
        }
    }, 100);

