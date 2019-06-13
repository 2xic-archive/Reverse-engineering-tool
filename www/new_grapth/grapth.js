function setup_canvas(size_width, size_heigth) {
    var canvas = document.getElementById("canvas");
    var ctx = canvas.getContext("2d");

    canvas.width = size_width;
    canvas.height = size_heigth;

    return ctx;
}


function create_node(x, y, start, finish) {
    var level_node = document.createElement("div");

    level_node.setAttribute("class", "node");

    level_node.style.left = x + "px";
    level_node.style.top = y + "px";

 ///   if(code == undefined){
  // 	if (typeof code === 'undefined') {
    code = code_lookup[".init"];
   // }

 //  console.log(code);

    var table = document.createElement("table");

    console.log([start, finish]);

    var addresses = Object.keys(code["code"]);


    console.log(addresses);
    console.log([start, finish]);

    for (var i = (addresses.indexOf(start)); i <= addresses.indexOf(finish); i++) {
        var tr = document.createElement("tr");

        console.log(i);
        console.log(addresses[i]);
        console.log(code["code"]);

        var code_data = code["code"][addresses[i]];
        console.log(code_data);

        var address = document.createElement("td");
        address.innerText = addresses[i];

        var code_element = document.createElement("td");
        code_element.innerText = code_data["instruction"] + "\t" + code_data["argument"];

        tr.appendChild(address);
        tr.appendChild(code_element);
        table.appendChild(tr);
    }

    level_node.appendChild(table);

    document.getElementById("grapth").appendChild(level_node);
    return level_node;
}




