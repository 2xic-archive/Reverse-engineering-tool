
var table_was_build = false;

function open_close_search() {
	if(!table_was_build){
		build_table();
		table_was_build = true;
	}
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


function build_table(){
	var list = Object.keys(block_list).sort();
	for (var key in list) {
		var key = list[key];
		var element = document.createElement("a");
		element.innerText = block_list[key];
		element.setAttribute("onClick", "find_section(this);");
		element.setAttribute("tabindex", "0");
		document.getElementById("search_content").appendChild(element);
	}
}

function find_section(e){
	document.getElementsByName("row_" + e.innerText.replace("loc_", ""))[0].scrollIntoView();
	open_close_search();
}