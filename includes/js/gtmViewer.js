(function() {
    main();
})();

var allLines = [];
var winner = null;

// Copy paste function for async fetching a file from an URL source.
async function* makeTextFileLineIterator(fileURL) {
    const utf8Decoder = new TextDecoder('utf-8');
    const response = await fetch(fileURL);
    const reader = response.body.getReader();
    let {value: chunk, done: readerDone} = await reader.read();
    chunk = chunk ? utf8Decoder.decode(chunk) : '';

    const re = /\n|\r|\r\n/gm;
    let startIndex = 0;
    let result;

    for (;;) {
        let result = re.exec(chunk);
        if (!result) {
            if (readerDone) {
                break;
            }
            let remainder = chunk.substr(startIndex);
            ({value: chunk, done: readerDone} = await reader.read());
            chunk = remainder + (chunk ? utf8Decoder.decode(chunk) : '');
            startIndex = re.lastIndex = 0;
            continue;
        }
        yield chunk.substring(startIndex, result.index);
        startIndex = re.lastIndex;
    }
    if (startIndex < chunk.length) {
        // Last line didn't end in a newline char.
        yield chunk.substr(startIndex);
    }
}

// Responsible for walking every line of the supplied gtm file(s) and determining how to add that content to the DOM.
function parseData() {
    var ccNode = document.getElementById('contentsContainer');
    var insidePreElement = false;
    var preNode = null;

    for (var i = 0; i < allLines.length; i++) {
        if (!insidePreElement) {
            // If this is a FEN string line in my gtm file, handle a specific way
            if (allLines[i][0] == '|') {
                // Adding dynamically generated chess board picture
                var chessBoardDiv = document.createElement('div');
                chessBoardDiv.id = 'chessBoard' + i;
                chessBoardDiv.className = 'chessBoard';

                var boardConfig = {
                    position: allLines[i].substring(1),
                    showNotation: false,
                    orientation: winner,
                };

                // Adding dynamically generated QR code of said board
                var xmlns = 'http://www.w3.org/2000/svg';
                var svgElem = document.createElementNS(xmlns, 'svg');
                svgElem.setAttribute('xmlns:xlink', 'http://www.w3.org/1999/xlink');
                svgElem.setAttribute('class', 'qrCode');
                svgElem.setAttribute('height', 44);
                svgElem.setAttribute('width', 44);
                var g = document.createElementNS(xmlns, 'g');
                g.setAttribute('id', 'qrCode' + i);
                svgElem.appendChild(g);

                var qrCodeConfig = {
                    text: allLines[i].substring(1),
                    colorDark: '#000000',
                    colorLight: '#ffffff',
                    correctLevel: QRCode.CorrectLevel.L,
                    useSVG: true,
                };

                // Adding the chess board and qrcode to the DOM, contained within a table.
                var dynamicTable = document.createElement('table');
                dynamicTable.className = 'dynamicTable';
                var dynamicTr = document.createElement('tr');
                var dynamicTd1 = document.createElement('td');
                var dynamicTd2 = document.createElement('td');
                dynamicTd1.appendChild(chessBoardDiv);
                dynamicTd2.appendChild(svgElem);
                dynamicTr.appendChild(dynamicTd1);
                dynamicTr.appendChild(dynamicTd2);
                dynamicTable.appendChild(dynamicTr);
                ccNode.appendChild(dynamicTable);
                var board = Chessboard('chessBoard' + i, boardConfig);
                var qrCode = new QRCode(document.getElementById('qrCode' + i), qrCodeConfig);
            }
            // Else begin construction of a new pre element
            else {
                preNode = document.createElement('pre');
                insidePreElement = true;
            }
        }

        if (insidePreElement) {
            // Checking for result string
            if (allLines[i].startsWith('Result:')) winner = allLines[i].includes('0-1') ? 'black' : 'white';

            // If the current line is a real move in the game, then bold it.
            var searchPattern = /^\d+(\.\.\.|\. )/gi;
            if (searchPattern.test(allLines[i]) && !allLines[i].trimEnd().endsWith(']')) preNode.innerHTML += '<b>' + allLines[i] + '</b>\n';
            // Else display the line exactly as it is without additional formatting.
            else preNode.innerHTML += allLines[i] + '\n';

            // Test condition to break apart pre elements
            if (allLines[i].length == 0) {
                ccNode.appendChild(preNode);
                insidePreElement = false;
            }
        }
    }
}

function main() {
    var URL = window.URL || window.webkitURL;
    var fileInputNode = document.querySelector('#files');

    var loadSelectedChessPubFile = async function(event) {
        for (var i = 0; i < this.files.length; i++) {
            var objectURL = URL.createObjectURL(this.files[i]);
            for await (let line of makeTextFileLineIterator(objectURL)) {
                allLines.push(line);
            }
        }

        fileInputNode.remove();
        parseData();
    };

    fileInputNode.addEventListener('change', loadSelectedChessPubFile, false);
}
