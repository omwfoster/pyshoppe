/****************************
 server communication
 ****************************/


$(document).ready(function () {

//     Kinetic js  stage initialisation

    var pinboard_select, dropzone, downloadbtn, defaultdownloadbtn, globalblob,
        imgWidth = 180,
        imgHeight = 180,
        displayfile,
        layer,
        zindex = 0;

    stage = new Kinetic.Stage({
        container: 'canvasbag',
        width: 800,
        height: 538
    });
    layer = new Kinetic.Layer();
    stage.add(layer);
    displayfile = function (Image, filename, filetype) {


        var note = new Kinetic.Image({
            x: stage.getWidth() / 2 - 200 / 2,
            y: stage.getHeight() / 2 - 137 / 2,
            image: Image,
            width: Image.width,
            height: Image.height,
            draggable: true
        });

        // add cursor styling

        note.on('mouseover', function () {
            document.body.style.cursor = 'pointer';
            this.moveToTop();
        });
        note.on('mouseout', function () {
            document.body.style.cursor = 'default';
        });
        // add the shape to the layer

        layer.add(note);
        //  stage.add(layer);
        layer.draw();
        // add the layer to the stage

    };


    var model = (function () {

        return {
            getEntries: function (file, onend) {
                zip.createReader(new zip.BlobReader(file), function (zipReader) {
                    zipReader.getEntries(onend);
                }, onerror);
            },
            getEntryFile: function (entry, creationMethod, onend, onprogress) {
                var writer, zipFileEntry;
                var url = window.URL || window.webkitURL;


                function getData() {
                    entry.getData(writer, function (blob) {
                        var imageObj = new Image();
                        imageObj.onload = function () {
                            displayfile(this, entry.filename);
                        };

                        imageObj.src = url.createObjectURL(blob);

                    }, onprogress);
                }

                writer = new zip.BlobWriter();
                getData();
            }
        };
    })();


    //    appengine channels api
    channel = new goog.appengine.Channel(token);
    socket = channel.open();
    socket.onopen = function () {
        outputtoconsole('Channel established.');
    };
    socket.onmessage = function (message) {
        console.log(message);
        var data = jQuery.parseJSON(message.data);
//            var row = $('<tr />');
//            for(var i = 0; i < columns.length; i++) {
//                $('<td />', {
//                    'text': data.data[columns[i]],
//                }).appendTo(row);
//            }
//            row.appendTo('#results');
    };
    socket.onerror = function (error) {
        outputtoconsole('Channel error: ' + error.description);
    };
    socket.onclose = function () {
        outputtoconsole('Channel closed.');
    };

    // appengine channels api

    pinboard_select = $('#pinboard_select');
    pinboard_select.change(function () {
        layer.clear();
        layer.removeChildren();

        //change the pinboard context
        downloadPinboard();
        layer.draw();
    });
//    pinboard_select.(function () {
//        layer.clear();
//
//        //change the pinboard context
//        downloadPinboard();
//        layer.draw();
//
//
//    });
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
        processFiles(files);

        return false;
    });


    var uploadToServer = function (file) {
        var filename = null;
        var xhr_post = new XMLHttpRequest();
        xhr_post.open("post", "/upload", true);
        //     xhr_post.open("post", "/upload" + "?" + "token=" + token , true);
        xhr_post.setRequestHeader("Content-Type", "multipart/form-data");
        xhr_post.setRequestHeader("X-File-Name", file.name);
        xhr_post.setRequestHeader("X-File-Type", file.type);
        xhr_post.setRequestHeader("X-pinboard", pinboard_select.val());
        xhr_post.setRequestHeader("X-token", token);
        xhr_post.send(file);

        xhr_post.onreadystatechange = function (e) {
            if (4 === this.readyState) {
                downloadImage(file.name);
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
        return file.name;
    };
    /* random change */
    var downloadImage = function (arg_filename) {
        var myURL = window.URL || window.webkitURL;
        var filetype;
        var filename;
        var pinboard_url_id;
        var token;
        var xhr_get = new XMLHttpRequest();
        xhr_get.open('GET', '/canvas' + "?" + "filename=" + arg_filename, true);
        xhr_get.responseType = 'blob';


        xhr_get.onload = function (e) {
            if (this.status == 200) {
                pinboard_url_id = xhr_get.getResponseHeader("X-pinboard");
                token = xhr_get.getResponseHeader("X-token");
                filetype = xhr_get.getResponseHeader("X-File-Type");
                blob = new Blob([this.response], {type: filetype});
                filename = xhr_get.getResponseHeader("X-File-Name");
                var imageObj = new Image();

                imageObj.onload = function () {
                    displayfile(this, filename);
                };

                imageObj.src = myURL.createObjectURL(blob);

            }
        };

        xhr_get.send();


    };

    function unzip(zip) {
        //      layer.removeChildren();
        model.getEntries(zip, function (entries) {
            entries.forEach(function (entry) {
                model.getEntryFile(entry, "Blob");
            });
        });

    }

    var downloadPinboard = function (arg_filename) {
        var myURL = window.URL || window.webkitURL;
        var filetype;
        var filename;
        var pinboard_url_id;
        var token;
        var xhr_get = new XMLHttpRequest();
        xhr_get.open('GET', '/pinboard' + "?" + "pinboard_url_id=" + pinboard_select.val(), true);
        xhr_get.responseType = 'blob';
        layer.clear()


        xhr_get.onload = function (e) {
            if (this.status == 200) {
                filetype = xhr_get.getResponseHeader("X-File-Type");
                blob = new Blob([this.response], {type: filetype});
                filename = xhr_get.getResponseHeader("X-File-Name");
                unzip(blob);
            }

        };
        xhr_get.send();
    };
    var processFiles = function (files) {
        if (files && typeof FileReader !== "undefined") {
            for (var i = 0; i < files.length; i++) {
                readFile(files[i]);
            }
        } else {

        }
    };

    var outputtoconsole = function () {


        console.log("test console output");
    };

    var readFile = function (file) {
        if (!(/image/i).test(file.type)) {
            //some message for wrong file format
            $('#err').text('*Selected file format not supported!');
        } else {
            var reader = new FileReader();
            //init reader onload event handlers
            reader.onload = function (e) {
                var image = $('<img/>')
                    .load(function () {
//                        var newimageurl = getCanvasImage(this);
//                        createPreview(file, newimageurl);
                        var local_filename = uploadToServer(file);

                    })
                    .attr('src', e.target.result);
            };
            //begin reader read operation
            reader.readAsDataURL(file);

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

            var id = $(this).attr("title");
            var email = $(this).val();

            item = {}
            item ["title"] = id;
            item ["email"] = email;


            jsonObj.push(item);
            jsonObj.stringify(
                JSON.stringify()
            )
        });

        return jsonObjsonObj;
    }


});


