const express = require('express');
const app = express();
const http = require('http');
const server = http.createServer(app);
const {
    Server
} = require("socket.io");
const io = new Server(server);


const readline = require('readline');
readline.emitKeypressEvents(process.stdin);
process.stdin.setRawMode(true);
process.stdin.on('keypress', (str, key) => {


    if (str === 'o') {
        console.log("Open message sent");
        io.emit('OPEN', 'test@aalto.fi');
    } else if (str === 'u') {
        console.log("User data message sent");
        io.emit('USER', 'test@aalto.fi');
    } else {
        throw new Error("Something went badly wrong!")
    }


});


io.on('connection', (socket) => {

    console.log("conneted")

    socket.on('DISCFOUND', (data) => {
        console.log("DISCFOUND" + data)

    });

    socket.on('RETURNSTATUS', (data) => {
        console.log("RETURNSTATUS" + data)
    });

    socket.on('TAKESTATUS', (data) => {
        console.log("TAKESTATUS" + data)
    });

});

server.listen(3000, () => {
    console.log('listening on *:3000');
});