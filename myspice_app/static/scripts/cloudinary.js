let CLOUDINARY_URL = 'https://api.cloudinary.com/v1_1/danheecho/upload';
let CLOUDINARY_UPLOAD_PRESET = 'yxzjmvur';

let hiddenInput = document.getElementById('hiddenInput');
let fileUpload = document.getElementById('file-upload');

fileUpload.addEventListener('change', function(e) {
    let file = e.target.files[0];
    let formData = new FormData();
    formData.append('file', file);
    formData.append('upload_preset', CLOUDINARY_UPLOAD_PRESET);

    axios({
        url: CLOUDINARY_URL, 
        method: 'POST', 
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded'
        }, 
        data: formData
    }).then(function(res) {
        let imageUrl = res.data.secure_url;
        console.log(imageUrl);
        hiddenInput.setAttribute('value', imageUrl);
    }).catch(function(err) {
        console.log(err);
    })
})