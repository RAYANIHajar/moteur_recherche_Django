function showMe() {
  var input = document.getElementById("search");
  console.log("text :" + input.value.length);

  if (input.value.length == 0) {
    document.getElementById("list-data").style.display = "none";
  } else {
    document.getElementById("list-data").style.display = "block";
  }
}
