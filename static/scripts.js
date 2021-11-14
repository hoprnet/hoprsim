function enterGame() {
	document.getElementById('introText').style.display='none';
	document.getElementById('playerTable').style.display='table';
	document.getElementById('stakeTable').style.display='table';
}

function addPlayer() {
	document.getElementById('playerTable').style.display='none';
  document.getElementById('addPlayerForm').style.display='table';
}

function clickStake() {
  var elem = event.target;
	var fromId = elem.getAttribute("data-from");
  var toId = elem.getAttribute("data-to");
  console.log("CLICKED! from = " + fromId + ", to = " + toId);
  document.getElementById("edit-"+fromId+"-"+toId).style.display="unset"
  document.getElementById("view-"+fromId+"-"+toId).style.display="hidden"
}
