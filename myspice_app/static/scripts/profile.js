function submitComments() {
    var friendship_status = document.getElementById("friends");
    if(!friendship_status) {
        alert("You can only leave comments for your friends!");
        return false;
    }
    return true;
}