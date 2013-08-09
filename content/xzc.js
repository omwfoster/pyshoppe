var model = (function () {

    return {
        getEntries: function (file, onend) {
            zip.createReader(new zip.BlobReader(file), function (zipReader) {
                zipReader.getEntries(onend);
            }, onerror);
        },
        getEntryFile: function (entry, creationMethod, onend, onprogress) {
            var writer, zipFileEntry;

            function getData() {
                entry.getData(writer, function (blob) {

                    //read the blob, grab the base64 data, send to upload function
                    oFReader = new FileReader()
                    oFReader.onloadend = function (e) {
                        upload(this.result.split(',')[1]);
                    };
                    oFReader.readAsDataURL(blob);

                }, onprogress);
            }

            writer = new zip.BlobWriter();
            getData();
        }
    };
})();


/**
 * Created with PyCharm.
 * User: oliver
 * Date: 09/08/13
 * Time: 21:26
 * To change this template use File | Settings | File Templates.
 */
