const addBtn = document.getElementById("add-btn")
const rowParent = document.getElementsByClassName("row")[0]
// const body = document.getElementsByTagName(body)

// From Djang doc.
function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}



rowParent.addEventListener('click', function(e) {
    // console.log(e.target.tagName);
    // console.log(e.target.id);
    if (e.target.tagName === 'A' &&  e.target.id === 'add-btn') {
        // alert('k');
        const parentDiv = e.target.parentElement
        const allChild = parentDiv.childNodes;
        const itemId = parentDiv.id
        const name = allChild[1].textContent;
        const price = allChild[9].textContent;
        // console.log(parentDiv);
        // console.log(name);
        // console.log(price);
        // console.log(itemId);

        const url = '/addItem'
        const method = "POST"
        const data = JSON.stringify({
            id: itemId,
            name: name,
            price: price
        })

        console.log(data);

        const xhr = new XMLHttpRequest()
        const csrftoken = getCookie('csrftoken');
        xhr.responseType = 'json'
        xhr.open(method, url)
        xhr.setRequestHeader("Content-Type", "application/json")
        xhr.setRequestHeader('HTTP_X_REQUESTED_WITH', "XMLHttpRequest")
        xhr.setRequestHeader('X-Requested-With', "XMLHttpRequest")
        xhr.setRequestHeader("X-CSRFToken", csrftoken)
        xhr.onload = function() {
            console.log(xhr.response, xhr.status);
        }
        xhr.send(data)
        // return
    }
    // alert(e.target)
})
