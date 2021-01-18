
function startup(){
    display_ip()
    start_web_socket()
}

function display_ip(){
    document.getElementById("ip_addr").innerHTML = location.hostname;
}

var webSocket;

function start_web_socket(){
    webSocket = new WebSocket("ws://"+location.hostname)

    webSocket.onmessage = function (event) {
        document.getElementById("data_ex").innerHTML = event.data;
    }
}

function send_ws_cmd(cmd){
    webSocket.send(cmd);
}

var fpga_toggle = 0
function stop_fpga_blink(){
    send_ws_cmd('#FPGA_HALT');
    if(fpga_toggle == 0){
        document.getElementById("stop_fpga_btn").innerHTML = "Start FPGA Blinking"
        fpga_toggle = 1
    }
    else{
        document.getElementById("stop_fpga_btn").innerHTML = "Stop FPGA Blinking"
        fpga_toggle = 0
    }
    
}