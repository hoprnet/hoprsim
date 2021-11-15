function enterGame() {
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

