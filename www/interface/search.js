

function open_close_search() {
	document.getElementById("search_content").classList.toggle("show");
}

function check_focus(){
	var new_focus = document.activeElement;
	console.log(new_focus);
}

function filter_search() {
	var input = document.getElementById("search");
	var filter = input.value.toUpperCase();
	var div = document.getElementById("search_content");
				
	var a = div.getElementsByTagName("a");
	for (var i = 0; i < a.length; i++) {
		txtValue = a[i].textContent || a[i].innerText;
		if (txtValue.toUpperCase().indexOf(filter) > -1) {
			a[i].style.display = "";
		} else {
			a[i].style.display = "none";
		}
	}
}

function find_section(e){
	document.getElementsByName("row_" + e.innerText)[0].scrollIntoView();
	open_close_search();
}