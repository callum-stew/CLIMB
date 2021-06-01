Webcam.set({
    width: 320,
    height: 240,
    image_format: 'jpeg',
    jpeg_quality: 90
});
Webcam.attach( '#my_camera' );

const take_snapshot = () => {
    Webcam.snap( (data_uri) => {
        // display results in page
        document.getElementById('results').innerHTML = '<img src=\"'+data_uri+'\" alt=\"Member image\"/>';
        document.getElementById('image').setAttribute('value', data_uri);
        document.getElementById('create').disabled = false;
    });
}

Webcam.on('error', function(err) {
    document.getElementById('camBut').setAttribute('disabled', 'true')
    document.getElementById('create').removeAttribute('disabled')
})