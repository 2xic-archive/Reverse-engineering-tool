


/*

	only used for benchmarking.

*/
function load_cache() {
	var msg = window.localStorage.getItem('data');
	if (msg != undefined) {
		var base_64 = msg;
		var string_data = atob(base_64);
		var char_data = string_data.split('').map(function(x) {
			return x.charCodeAt(0);
		});

		var binData = new Uint8Array(char_data);
		var data = pako.inflate(binData);

		var string_data = new Uint16Array(data);
		var char_string = "";
		for (var i = 0; i < string_data.length; i++) {
			char_string += String.fromCharCode(string_data[i]);
		}
		var msg = JSON.parse(char_string);
		var start = Date.now();
		return msg;
	}
	return msg;
}

function create_custom(msg) {
	//create_hex_view(msg["hex"]);

	console.log("starting to create");
	start_function("evreything_in_between");

	code_sections = msg["sections"];

	start_function("create_grapth");
	create_blocks(msg["grapth"]);
	create_grapth(msg["grapth"], 0, false);
	end_function("create_grapth");

	var data = create_flat_view(msg["code"]);

	var clusterize = new Clusterize({
		rows: data,
		scrollId: 'scrollArea',
		contentId: 'contentArea'
	});

	end_function("evreything_in_between");
}

function load_view_cache(){
	var force_download = false;
	if (force_download) {
		socket.on('connect', function() {
			socket.emit('test_compress_server');
		});
		socket.on('test_compress', function(msg) {
			console.log("got message");
			var base_64 = msg;
			var string_data = atob(base_64);
			var charData = string_data.split('').map(function(x) {
				return x.charCodeAt(0);
			});
			
			var binData = new Uint8Array(charData);
			var data = pako.inflate(binData);

			var string_data = new Uint16Array(data);
			var char_string = "";
			for (var i = 0; i < string_data.length; i++) {
				char_string += String.fromCharCode(string_data[i]);
			}
			var msg = JSON.parse(char_string);
			create_custom(msg);
			window.localStorage.setItem('data', base_64);
		});
	} else {

		window.onload = function() {
			setTimeout(function() {
				 var loaded_cache = load_cache();
				if (loaded_cache == undefined) {
					alert("no cahce");
				} else {
					create_custom(loaded_cache);
				}
			}, 500);
		};
	}
}