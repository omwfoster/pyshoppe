 
    var canvas = null;
    var context = null;
    var images = {};
    
    // initialize an array of rectangles that provide
    // rectangular paths and properties for the images
    var rectangles = [{
        name: "darthVader",
        image: null,
        x: 100,
        y: 40,
        width: 200,
        height: 137,
        dragging: false,
        offsetX: 0,
        offsetY: 0,
    }, {
        name: "yoda",
        image: null,
        x: 350,
        y: 55,
        width: 93,
        height: 104,
        dragging: false,
        offsetX: 0,
        offsetY: 0,
    }];
    
    function loadImages(sources, callback){
        var loadedImages = 0;
        var numImages = 0;
        for (var src in sources) {
            numImages++;
            images[src] = new Image();
            images[src].onload = function(){
                if (++loadedImages >= numImages) {
                    callback();
                }
            };
            images[src].src = sources[src];
        }
    }
    
    function initStage(){
        // map images to rectangles array
        counter = 0;
        for (var img in images) {
            rectangles[counter++]["image"] = images[img];
        }
        
        // when using KineticJS, we need to draw the shapes with the highest z-index
        // first and the shapes with the lowest z-index last in order to 
        // correctly handle shape layering
        context.globalCompositeOperation = "destination-over";
        myStage = new Kinetic.Stage(canvas);
        myStage.setDrawStage(function(){
        
            var mousePos = myStage.getMousePos();
            
            for (var n = 0; n < rectangles.length; n++) {
                var thisRect = rectangles[n];
                if (thisRect.dragging) {
                    thisRect.x = mousePos.x - thisRect.offsetX;
                    thisRect.y = mousePos.y - thisRect.offsetY;
                }
                
                myStage.beginRegion();   
				context.drawImage(thisRect.image, thisRect.x, thisRect.y, thisRect.width, thisRect.height);
                context.beginPath();
				context.rect(thisRect.x, thisRect.y, thisRect.width, thisRect.height);
                context.closePath();
                
                myStage.addRegionEventListener("onmousedown", function(){
                    thisRect.dragging = true;
                    var mousePos = myStage.getMousePos();
                    
                    thisRect.offsetX = mousePos.x - thisRect.x;
                    thisRect.offsetY = mousePos.y - thisRect.y;
                    
                    // place this rect at the beginning of the rectangles
                    // array so that is is rendered on top
                    rectangles.splice(n, 1);
                    rectangles.splice(0, 0, thisRect);
                });
                myStage.addRegionEventListener("onmouseup", function(){
                    thisRect.dragging = false;
                });
                myStage.addRegionEventListener("onmouseover", function(){
                    document.body.style.cursor = "pointer";
                });
                myStage.addRegionEventListener("onmouseout", function(){
                    document.body.style.cursor = "default";
                });
                
                myStage.closeRegion();
            }
            
            context.font = "18pt Calibri";
            context.fillStyle = "black";
            context.fillText("Drag and drop the images...", 10, 25);
        });
    }
    
    window.onload = function(){
        canvas = document.getElementById("myCanvas");
        context = canvas.getContext("2d");
        
        var sources = {
            darthVader: "darth-vader.jpg",
            yoda: "yoda.jpg"
        };
        
        loadImages(sources, function(){
            initStage();
        });
    }

