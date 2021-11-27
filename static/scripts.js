function enterGame() {
  setCookie("showIntro", "false", 1);
 	document.getElementById('introText').style.display='none';
	document.getElementById('playerTable').style.display='table';
	document.getElementById('stakeTable').style.display='table';
}

function addPlayer() {
	document.getElementById('playerTable').style.display='none';
  document.getElementById('addPlayerForm').style.display='table';
}

function hideForms() {
  var forms = document.getElementsByName("forms");
  console.log("found " + forms.length + " forms");
  for (let c = 0; c < forms.length; c++) {
    forms[c].style.display="none";
  }
}

function clickStake() {
  var elem = event.target;
	var fromId = elem.getAttribute("data-from");
  var toId = elem.getAttribute("data-to");
  if (fromId === null)
    return; // clicked on some form - hack!
  console.log("CLICKED stake! from = " + fromId + ", to = " + toId);
  hideForms(); // minimizes all previously opened dialogs
  document.getElementById("edit-"+fromId+"-"+toId).style.display="unset";
}

function clickEarnings() {
  var elem = event.target;
	var fromId = elem.getAttribute("data-from");
  var toId = elem.getAttribute("data-to");
  console.log("CLICKED earnings! from = " + fromId + ", to = " + toId);
  hideForms(); // minimizes all previously opened dialogs
  document.getElementById("claims-"+fromId+"-"+toId).style.display="unset";
  event.stopPropagation();
}

var nextTickTime
var countdown
function onPageShow(nextTick) {
  nextTickTime = new Date(nextTick)
  now = new Date(Date.now())
  deltaSeconds = Math.ceil(nextTickTime - now)

  playerId = parseInt(getCookie("playerId"))

  printCountdown(deltaSeconds)
  if (deltaSeconds > 0)
    countdown = setInterval(renderCountdown, 1000)

  if (getCookie("showIntro") == "false")
    enterGame()

  var opts = {
    method: 'GET',      
    headers: {}
  };
  fetch('/getCache', opts).then(function (response) {
    return response.json();
  })
    .then(function (gameCache) {
      console.log("got game cache: " + JSON.stringify(gameCache))

      var stake = gameCache.stake;
      var members = gameCache.members;
      var len = stake.length;

      // calculate total stake, num channels in, num channels out
      var totalStake = [];
      var numIn = []
      var numOut = []
      for (var i = 0; i < len; i++) {
        var tmpStake = 0;
        numIn.push(0);
        numOut.push(0);
        for (var j = 0; j < len; j++) {
          tmpStake += stake[i][j];
        }
        totalStake.push(tmpStake);
      }
      console.log("total stake: " + JSON.stringify(totalStake));

      // calculate importance score of each player
      var importance = []
      for (var i = 0; i < len; i++) {
        var channelWeight = 0;
        for (var j = 0; j < len; j++) {
          if (stake[i][j] > 0) {
            numIn[j]++;
            numOut[i]++;
            channelWeight += Math.sqrt(stake[i][j] / totalStake[i] * totalStake[j]);
          }
        }
        importance.push(totalStake[i] * channelWeight);
      }
      console.log("importance: " + JSON.stringify(importance));

      // render menu
      if (!isNaN(playerId)) {
        if (playerId > members.length) {
          console.log("ERROR: player ID " + playerId + " invalid, members list in game cache has only " + members.length + " entries!");
          return;
        }
        player = members[playerId - 1]
        document.getElementById("PlayerName").innerText = "Player: " + player[1];
        document.getElementById("PlayerBalance").innerText = "Balance: " + player[2];
        document.getElementById("PlayerScore").innerText = "χοπρ score: " + importance[playerId - 1];
      }
      else {
        document.getElementById("PlayerName").innerText = "[no name]";
        document.getElementById("PlayerBalance").innerText = "[no balance]";
        document.getElementById("PlayerScore").innerText = "[no χοπρ score]";
      }

      // remove existing rows in player table
      var playerRows = document.getElementsByName("tableRow");
      var numRows = playerRows.length;
      for (var i = 0; i < numRows; i++) {
        playerRows[0].remove();
      }

      // render rows in player table
      var table = document.getElementById("playerOverviewTable");
      for (var numRows = 1; numRows < len + 1; numRows++) {
        var newRow = table.insertRow(numRows);
        
        if (numRows % 2 == 1) {
          console.log("row2");
          newRow.className = "row2";
        }

        // player id
        var cell1 = newRow.insertCell(0);
        cell1.innerText = numRows.toString();

        // player name
        var cell2 = newRow.insertCell(1);
        cell2.innerText = members[numRows - 1][1];

        // player balance
        var cell3 = newRow.insertCell(2);
        cell3.innerText = members[numRows - 1][2].toLocaleString("en-US");

        // player importance
        var cell4 = newRow.insertCell(3);
        cell4.innerText = importance[numRows - 1].toLocaleString("en-US", {
          style: "decimal",
          minimumFractionDigits: 1,
          maximumFractionDigits: 1,
        });

        // player total stake
        var cell5 = newRow.insertCell(4);
        cell5.innerText = totalStake[numRows - 1].toLocaleString("en-US");

        // number of incoming channels
        var cell6 = newRow.insertCell(5);
        cell6.innerText = numIn[numRows - 1];

        // number of outgoing channels
        var cell7 = newRow.insertCell(6);
        cell7.innerText = numOut[numRows - 1];
      }

      // render stake table
      tableStake = document.getElementById("tableStake");
      for (var i = 0; i < len; i++) {
        var newRow = tableStake.insertRow(i + 1);
        
        if (i % 2 == 0) {
          console.log("row2");
          newRow.className = "row2";
        }

        var headerCell = document.createElement("TH");
        headerCell.innerText = i + 1;
        newRow.appendChild(headerCell);
        for (var j = 0; j < len; j++) {
          var newCell = newRow.insertCell(j + 1);
          console.log("stake: " + stake[i][j]);
          newCell.innerHTML = stake[i][j].toString() + "<div id='edit-" + (i+1) + "-" + (j+1) + "', style='display: none; position: relative;' name='forms'> \
              <form action = '/setStake' method = 'post'> \
                <input type='number' name='stakeAmount' value='" + stake[i][j] + " style='width: 60px;' /> \
                <input type='hidden' name='fromId' value='" + (i+1) + "'/> \
                <input type='hidden' name='toId' value='" + (j+1) + "'/> \
                <input type='submit' value='update' class='button'/> \
              </form> \
            </div>";
          newCell.onclick = clickStake;
          newCell.setAttribute("data-from", i + 1);
          newCell.setAttribute("data-to", j + 1);
          newCell.setAttribute("id", "view-" + (i + 1) + "-" + (j + 1)); 
        }
      }
    });
}

function renderCountdown() {
  console.log("rendering countdown...");
  now = Date.now();
  deltaSeconds = Math.ceil(nextTickTime - now);
  printCountdown(deltaSeconds)
  if (deltaSeconds <= 0)
    clearInterval(countdown);
}

function printCountdown(deltaSeconds) {
  arrivalTime = deltaSeconds > 0 ? Math.ceil(deltaSeconds/1000) : 0;
  document.getElementById("Countdown").innerText = "Next travelers: " + arrivalTime + "s";
}

function getCookie(cname) {
  let name = cname + "=";
  let decodedCookie = decodeURIComponent(document.cookie);
  let ca = decodedCookie.split(';');
  for(let i = 0; i <ca.length; i++) {
    let c = ca[i];
    while (c.charAt(0) == ' ') {
      c = c.substring(1);
    }
    if (c.indexOf(name) == 0) {
      return c.substring(name.length, c.length);
    }
  }
  return "";
}

function setCookie(cname, cvalue, exdays) {
  const d = new Date();
  d.setTime(d.getTime() + (exdays * 24 * 60 * 60 * 1000));
  let expires = "expires="+d.toUTCString();
  document.cookie = cname + "=" + cvalue + ";" + expires + ";path=/";
}

