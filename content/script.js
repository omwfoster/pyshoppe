(function () {
    /**
     *
     * @param config
     */

    Kinetic.pinnedItem = function (config) {
        this._initItem(config);
    };
    Kinetic.pinnedItem.prototype = {
        _initItem: function (config) {
            this.createAttrs();
            this.filename = config.filename;
            this.UID = config.UID;
            this._id = config.UID;
            //         this.item_id = config.item_id;
            Kinetic.Image.call(this, config);
        }
    };

    Kinetic.Util.extend(Kinetic.pinnedItem, Kinetic.Image);
})();


function Model(file, callback) {

    /**
     *
     * @type {Array}
     */

    var contents_as_array = [];


    this.getEntries = function (file, onend) {
        zip.createReader(new zip.BlobReader(file), function (zipReader) {
            zipReader.getEntries(onend);
        }, onerror);
    };


    this.getData = function (entry, writer) {
        var url = window.URL || window.webkitURL;
        entry.getData(writer, function (blob) {
            var imageObj = new Image();
            imageObj.onload = function () {
                callback(this, {x: 20, y: 20}, entry.filename);
            };
            imageObj.src = url.createObjectURL(blob);

        }, onprogress);
    };

    this.getEntryFile = function (entry, creationMethod, onend, onprogress) {
        var writer, zipFileEntry;


        writer = new zip.BlobWriter();
        this.getData(entry, writer);

    }


}

var outputtoconsole = function () {
    console.log("test console output");
}


$(document).ready(function () {

    stage = new Kinetic.Stage({
        container: 'canvasbag',
        width: 800,
        height: 538
    });


    layer = new Kinetic.Layer();
    stage.add(layer);


//     Kinetic js  stage initialisation
    var pinboard_select, dropzone, downloadbtn, defaultdownloadbtn, globalblob,
        imgWidth = 180,
        imgHeight = 180,
        displayfile,
        layer,
        zindex = 0,
        channel = new goog.appengine.Channel(window.token),
        socket = channel.open();


    socket.onopen = function () {
//        alert("open");
    };
    socket.onmessage = function (message) {
        var data = jQuery.parseJSON(message.data);
        var contents = layer.getChildren();
        data.map(function (item) {

            for (var i = 0; i < contents.length; ++i) {
                if (contents[i].hasOwnProperty('UID')) {
                    if (contents[i].UID == item.UID) {
//

                        (function (node, posx, posy) {
                            var tween = new Kinetic.Tween({
                                node: node,
                                x: posx,
                                y: posy,
                                rotationDeg: function (min, max) {
                                    return ~~(Math.random() * (max - min + 1)) + min
                                }(-30,30),
                                duration: 1,
                                easing: Kinetic.Easings.ElasticEaseOut
                            });
                            tween.play();
                        })(contents[i], item.item_xpos, item.item_ypos)
                    }
                }
            }
        })
        layer.draw()
    };
    socket.onerror = function (error) {
        alert();
    };
    socket.onclose = function () {
        alert("bye");
    };
//readsgfdghfhgf
    pinboard_select = $('#pinboard_select');
    pinboard_select.change(function () {
        layer.clear();
        layer.removeChildren();

        //change the pinboard context
        downloadPinboard();
        layer.draw();
    });

    dropzone = $('#canvasbag');
    downloadbtn = $('#downloadbtn');
    dropzone.on('dragover', function () {
        //add hover class when drag over
        dropzone.addClass('hover');
        return false;
    });
    dropzone.on('dragleave', function () {
        //remove hover class when drag out
        dropzone.removeClass('hover');
        return false;
    });
    dropzone.on('drop', function (e) {
        //prevent browser from open the file when drop off
        e.stopPropagation();
        e.preventDefault();
        dropzone.removeClass('hover');
        var files = e.originalEvent.dataTransfer.files;
        var pos = getMousePos(this, e)
        processFiles(files, pos);

        return false;
    });

    function getMousePos(canvas, evt) {
        var rect = canvas.getClientRects();

        return {
            x: evt.originalEvent.clientX - rect[0].left,
            y: evt.originalEvent.clientY - rect[0].top
        };
    }

    displayfile = function (Image, position, UID) {


        var note = new Kinetic.pinnedItem({
            x: position.x,
            y: position.y,
            UID: UID,
            filename: Image.name,
            //          item_id: item_id,
            image: Image,
            width: Image.width,
            height: Image.height,
            draggable: true
        });

        note.on('mouseover', function () {
            document.body.style.cursor = 'pointer';
            this.moveToTop();
        });
        note.on('mouseout', function () {
            document.body.style.cursor = 'default';
        });

        note.on('dragend', function () {
            var xmlhttp = new XMLHttpRequest();
            xmlhttp.open("POST", "/relocate");
            xmlhttp.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
            xmlhttp.send(JSON.stringify({"xpos": this.getPosition().x, "ypos": this.getPosition().y, "UID": UID}));
        });
        layer.add(note);
        //  stage.add(layer);
        layer.draw();

    };

    /* random change */
    var downloadImage = function (arg_UID, callback) {
        var myURL = window.URL || window.webkitURL;
        var filetype;
        var filename;
        var pinboard_url_id;
        var xhr_get = new XMLHttpRequest();
        xhr_get.open('GET', '/canvas' + "?" + "UID=" + arg_UID, true);
        xhr_get.responseType = 'blob';


        xhr_get.onload = function (e) {
            if (this.status == 200) {
                pinboard_url_id = xhr_get.getResponseHeader("X-pinboard");
                blob = new Blob([this.response], {type: filetype});
                var position = {x: parseInt(xhr_get.getResponseHeader("X-xpos")), y: parseInt(xhr_get.getResponseHeader("X-ypos"))};
                var imageObj = new Image();

                imageObj.onload = function () {
                    callback(this, position, arg_UID);
                };
                imageObj.src = myURL.createObjectURL(blob);
            }
        };

        xhr_get.send();

    };

    function unzip(zip, CALLBACK) {
        var model = new Model(zip, CALLBACK);
        model.getEntries(function (entries) {
        });

        model.getEntries(zip, function (entries) {
            entries.forEach(function (entry) {
                model.getEntryFile(entry, "Blob");
            });
        });

    }

    var downloadPinboard = function () {
        var myURL = window.URL || window.webkitURL,
            filetype,
            filename,
            pinboard_url_id,
            xhr_get = new XMLHttpRequest();
        xhr_get.open('GET', encodeURI('/pinboard' + "?" + "pinboard_url_id=" + pinboard_select.val() + '&' + 'token=' + window.token), true);
        xhr_get.responseType = 'blob';
        layer.clear();


        xhr_get.onload = function (e) {
            if (this.status === 200) {
                filetype = xhr_get.getResponseHeader("X-File-Type");
                blob = new Blob([this.response], {type: filetype});
                filename = xhr_get.getResponseHeader("X-File-Name");
                unzip(blob, displayfile);
            }

        };
        xhr_get.send();


    };
    var processFiles = function (files, pos) {
//        pos = {x: e.clientX, y: e.clientY};
        if (files && typeof FileReader !== "undefined") {
            for (var i = 0; i < files.length; i++) {
                readFile(files[i], pos, displayfile);
            }
        } else {

        }
    };

    var readFile = function (file, pos) {


        //   var local_callback = callback
        if (!(/image/i).test(file.type)) {
            //some message for wrong file format
            $('#err').text('*Selected file format not supported!');
        } else {
            var reader = new FileReader();
            //init reader onload event handlers
            reader.onload = function (e) {
                var image = $('<img/>')
                    .load(function () {
                        uploadToServer(file, pos);
                    })
                    .attr('src', e.target.result);
            };
            //begin reader read operation
            reader.readAsDataURL(file);

            $('#err').text('');
        }
    };


    var uploadToServer = function (file, pos) {
        var UUIDv4 = 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function (c) {
            var r = Math.random() * 16 | 0, v = c == 'x' ? r : (r & 0x3 | 0x8);
            return v.toString(16);
        });

        //      var imageobj = new image(file)
        var xhr_post = new XMLHttpRequest();
        xhr_post.open("post", "/upload", true);
        xhr_post.setRequestHeader("Content-Type", "multipart/form-data");
        xhr_post.setRequestHeader("X-File-Name", file.name);
        xhr_post.setRequestHeader("X-File-Type", file.type);
        xhr_post.setRequestHeader("X-pinboard", pinboard_select.val());
//        xhr_post.setRequestHeader("X-token", token);
        xhr_post.setRequestHeader("X-xpos", pos.x);
        xhr_post.setRequestHeader("X-ypos", pos.y);
        xhr_post.setRequestHeader("X-UID", UUIDv4);


        xhr_post.send(file);

        xhr_post.onreadystatechange = function (e) {
            if (4 === this.readyState) {
                return downloadImage(UUIDv4, displayfile);
            }
        };

        if (typeof FileReader === "undefined") {
            //$('.extra').hide();
            $('#err').html('Hey! Your browser does not support <strong>HTML5 File API</strong> <br/>Try using Chrome or Firefox to have it works!');
        } else if (!Modernizr.draganddrop) {
            $('#err').html('Ops! Look like your browser does not support <strong>Drag and Drop API</strong>! <br/>Still, you are able to use \'<em>Select Files</em>\' button to upload file =)');
        } else {
            $('#err').text('');
        }

    };

//Bytes to KiloBytes conversion
    function convertToKBytes(number) {
        return (number / 1024).toFixed(1);
    }

    function compareWidthHeight(width, height) {
        var diff = [];
        if (width > height) {
            diff[0] = width - height;
            diff[1] = 0;
        } else {
            diff[0] = 0;
            diff[1] = height - width;
        }
        return diff;
    }


//convert datauri to blob
    function dataURItoBlob(dataURI) {
        var BlobBuilder = window.WebKitBlobBuilder || window.MozBlobBuilder || window.BlobBuilder;

        //skip if browser doesn't support BlobBuilder object
        if (typeof BlobBuilder === "undefined") {
            $('#err').html('Ops! There have some limited with your browser! <br/>New image produced from canvas can\'t be upload to the server...');
            return dataURI;
        }

        // convert base64 to raw binary data held in a string
        // doesn't handle URLEncoded DataURIs
        var byteString;
        if (dataURI.split(',')[0].indexOf('base64') >= 0)
            byteSmnmtring = atob(dataURI.split(',')[1]);
        else
            byteString = unescape(dataURI.split(',')[1]);

        // separate out the mime component
        var mimeString = dataURI.split(',')[0].split(':')[1].split(';')[0]

        // write the bytes of the string to an ArrayBuffer
        var ab = new ArrayBuffer(byteString.length);
        var ia = new Uint8Array(ab);
        for (var i = 0; i < byteString.length; i++) {
            ia[i] = byteString.charCodeAt(i);
        }

        // write the ArrayBuffer to a blob, and you're done
        var bb = new BlobBuilder();
        bb.append(ab);

        return bb.getBlob(mimeString);
    }

//Black & White image effect
//by Marco Lisci - http://badsharkco.com/
    var grayscale = function (context) {
        var imgd = context.getImageData(0, 0, imgWidth, imgHeight);
        var pix = imgd.data;
        for (var i = 0, n = pix.length; i < n; i += 4) {
            var grayscale = pix[i  ] * .3 + pix[i + 1] * .59 + pix[i + 2] * .11;
            pix[i  ] = grayscale;
            pix[i + 1] = grayscale;
            pix[i + 2] = grayscale;
        }
        context.putImageData(imgd, 0, 0);
    };

//canvas-blur effect
//by Matt Riggott - http://www.flother.com/
    var blurry = function (context, image, diff) {
        var i, x, y,
            blureffect = 4;

        context.globalAlpha = 0.1;
        for (i = 1; i <= blureffect; i++) {
            for (y = -blureffect / 2; y <= blureffect / 2; y++) {
                for (x = -blureffect / 2; x <= blureffect / 2; x++) {
                    context.drawImage(image, diff[0] / 2, diff[1] / 2, image.width - diff[0], image.height - diff[1], x, y, imgWidth, imgHeight);
                }
            }
        }
        context.globalAlpha = 1.0;
    };


    /*****************************
     Get New Canvas Image URL
     *****************************/
    var getCanvasImage = function (image) {
        //get selected effect


        //define canvas
        var canvas = document.createElement('canvas');
        canvas.width = imgWidth;
        canvas.height = imgHeight;
        var ctx = canvas.getContext('2d');

        //default resize variable
        var diff = [0, 0];
        if (croping == 'crop') {
            //get resized width and height
            diff = compareWidthHeight(image.width, image.height);
        }

        //draw canvas image
        ctx.drawImage(image, diff[0] / 2, diff[1] / 2, image.width - diff[0], image.height - diff[1], 0, 0, imgWidth, imgHeight);

        //apply effects if any
        if (effect == 'grayscale') {
            grayscale(ctx);
        } else if (effect == 'blurry') {
            blurry(ctx, image, diff);
        } else {
        }

        //convert canvas to jpeg url
        return canvas.toDataURL("image/jpeg");
    };

    function createJSON(layer) {
        jsonObj = [];
        layer.children.forEach(function () {


            item = {}
            item ["noteUID"] = noteID;
            item ["filename"] = itemFilename;
            item ["pinneditem"] = pinnedItem;
            item ["pinboardID"] = pinboardID;


            jsonObj.push(item);
            jsonObj.stringify(
                JSON.stringify()
            )
        });

        return jsonObj;
    }


})
;


