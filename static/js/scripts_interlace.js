function setOperation0(op0, button) {
    document.getElementById("operation0").value = op0;
    const buttons = document.querySelectorAll(".first");
    buttons.forEach(button => button.classList.remove("selected"));

    button.classList.add("selected");
}

function setOperation1(op1, button) {
    document.getElementById("operation1").value = op1;
    const buttons = document.querySelectorAll(".second");
    buttons.forEach(button => button.classList.remove("selected"));

    button.classList.add("selected");
}