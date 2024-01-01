(function () {
    main();
})();

var allLines = [];
var winner = null;

// Copy paste function for async fetching a file from an URL source.
async function* makeTextFileLineIterator(fileURL) {
    const utf8Decoder = new TextDecoder("utf-8");
    const response = await fetch(fileURL);
    const reader = response.body.getReader();
    let { value: chunk, done: readerDone } = await reader.read();
    chunk = chunk ? utf8Decoder.decode(chunk) : "";

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
            ({ value: chunk, done: readerDone } = await reader.read());
            chunk = remainder + (chunk ? utf8Decoder.decode(chunk) : "");
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
    var ccNode = document.getElementById("contentsContainer");
    var insidePreElement = false;
    var preNode = null;

    for (var i = 0; i < allLines.length; i++) {
        if (!insidePreElement) {
            // If this is a FEN string line in my gtm file, handle a specific way
            if (allLines[i][0] == "|") {
                // Adding dynamically generated chess board picture
                var chessBoardDiv = document.createElement("div");
                chessBoardDiv.id = "chessBoard" + i;
                chessBoardDiv.className = "chessBoard";
                chessBoardDiv.setAttribute(
                    "data-fen",
                    allLines[i].substring(1)
                );
                chessBoardDiv.addEventListener(
                    "click",
                    function () {
                        location.href =
                            "https://lichess.org/analysis/" +
                            encodeURI(this.dataset.fen);
                    },
                    false
                );

                var boardConfig = {
                    position: allLines[i].substring(1),
                    showNotation: false,
                    orientation: winner,
                };

                // Adding the chess board to the DOM, contained within a table.
                var dynamicTable = document.createElement("table");
                dynamicTable.className = "dynamicTable";
                var dynamicTr = document.createElement("tr");
                var dynamicTd1 = document.createElement("td");
                dynamicTd1.appendChild(chessBoardDiv);
                dynamicTr.appendChild(dynamicTd1);
                dynamicTable.appendChild(dynamicTr);
                ccNode.appendChild(dynamicTable);
                var board = Chessboard("chessBoard" + i, boardConfig);
            }
            // Else begin construction of a new pre element
            else {
                preNode = document.createElement("pre");
                insidePreElement = true;
            }
        }

        if (insidePreElement) {
            // Checking for result string
            if (allLines[i].startsWith("Result:"))
                winner = allLines[i].includes("0-1") ? "black" : "white";

            // If the current line is a real move in the game, then bold it.
            var searchPatternW = /^\d+(\.\s\s)/gi;
            var searchPatternB = /^\d+(\.\.\.)/gi;
            if (
                searchPatternW.test(allLines[i]) &&
                !allLines[i].trimEnd().endsWith("]")
            ) {
                var classN = winner == "white" ? "winnerMove" : "loserMove";
                preNode.innerHTML +=
                    "<div class='primaryMove'><span class='" +
                    classN +
                    "'>" +
                    allLines[i] +
                    "</span></div>\n";
            } else if (
                searchPatternB.test(allLines[i]) &&
                !allLines[i].trimEnd().endsWith("]")
            ) {
                var classN = winner == "black" ? "winnerMove" : "loserMove";
                preNode.innerHTML +=
                    "<div class='primaryMove'><span class='" +
                    classN +
                    "'>" +
                    allLines[i] +
                    "</span></div>\n";
            }
            // Else display the line exactly as it is without additional formatting.
            else preNode.innerHTML += allLines[i] + "\n";

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
    var fileInputNode = document.querySelector("#files");

    var loadSelectedChessPubFile = async function (event) {
        for (var i = 0; i < this.files.length; i++) {
            var objectURL = URL.createObjectURL(this.files[i]);
            for await (let line of makeTextFileLineIterator(objectURL)) {
                allLines.push(line);
            }
        }

        fileInputNode.remove();
        parseData();
    };

    fileInputNode.addEventListener("change", loadSelectedChessPubFile, false);
}
