


class highlighter {
	constructor(){
		this.last_highighlight = undefined;
	}

	highligth(target){
		if(this.last_highighlight != undefined){
			for(var i = 0; i < this.last_highighlight.length; i++){
				this.last_highighlight[i].style.background = "";
			}
		}
		for(var i = 0; i < target.length; i++){
			target[i].style.background = "red";
		}
		this.last_highighlight = target;
	}
}
