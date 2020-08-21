const addBtn = document.getElementById("add-btn")
const rowParent = document.getElementsByClassName("row")[0]
// const body = document.getElementsByTagName(body)

rowParent.addEventListener('click', function(e) {
    // console.log(e.target.tagName);
    // console.log(e.target.id);
    if (e.target.tagName === 'A' &&  e.target.id === 'add-btn') {
        // alert('k');
        const parentDiv = e.target.parentElement
        const allChild = parentDiv.childNodes;
        const id = parentDiv.id
        const name = allChild[1].textContent;
        const price = allChild[9].textContent;
        console.log(parentDiv);
        console.log(name);
        console.log(price);
        console.log(id);
    }
    // alert(e.target)
})
