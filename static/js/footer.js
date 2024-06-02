document.addEventListener("DOMContentLoaded", function() {
    var footer = document.createElement("footer");
    footer.className = "footer";
    var paragraph = document.createElement("p");
    //ALTERAR AQUI
    paragraph.innerHTML = "&copy; 2024 Dev Scientist Solutions. Todos os direitos reservados. &copy;Versão 1.5 2024";
    footer.appendChild(paragraph);
    document.body.appendChild(footer);
});