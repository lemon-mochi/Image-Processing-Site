function setOperation(op, button) {
    // Set the operation value
    document.getElementById("operation").value = op;
    
    // Remove 'selected' class from all buttons
    const buttons = document.querySelectorAll(".button-container button");
    buttons.forEach(button => button.classList.remove("selected"));
    
    // Add 'selected' class to the clicked button
    button.classList.add("selected");
}