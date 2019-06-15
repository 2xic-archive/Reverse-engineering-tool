
var table_was_build = false;

function open_close_search() {
	if(!table_was_build){
		build_table();
		table_was_build = true;
	}
	if(document.getElementById("search_content").style.display.length == 0 || 
		document.getElementById("search_content").style.display == "none"){
		document.getElementById("search_content").style.display = "block";
	}else{
		document.getElementById("search_content").style.display = "none";
	}
}

function check_focus(){
	if(document.activeElement.nodeName != "BUTTON"){
		var new_focus = document.activeElement;
		document.getElementById("search_content").style.display = "none";
	}
}

function filter_search() {
	var input = document.getElementById("search");
	var filter = input.value.toUpperCase();
	var div = document.getElementById("search_content");
				
	var text_element = div.getElementsByTagName("a");
	for (var i = 0; i < text_element.length; i++) {
		txtValue = text_element[i].textContent || text_element[i].innerText;
		if (txtValue.toUpperCase().indexOf(filter) > -1) {
			text_element[i].style.display = "";
		} else {
			text_element[i].style.display = "none";
		}
	}
}


function build_table(){
	var list = Object.keys(code_lookup);//.sort();
	for (var i = 0; i < list.length; i++) {
		var key = list[i];
		var element = document.createElement("a");
		element.innerText = key;
		element.setAttribute("orgin", key);
		element.setAttribute("onClick", "find_section(this);");
		element.setAttribute("tabindex", "0");
		document.getElementById("search_content").appendChild(element);
	}
}

function find_section(e){
	document.getElementsByName("row_" + e.getAttribute("orgin") )[0].scrollIntoView();
	open_close_search();
}

window.onload = function(){
	document.getElementsByTagName("body")[0].onclick = check_focus;
};
