function calcular() {
    try {
        var a = parseInt(document.getElementById("valor1").value) || 0,
        b = parseInt(document.getElementById("valor2").value) || 0;
        document.getElementById("total").value = a * b  / 100;
    } catch (e) {}
}

function suma() {
    try {
        var a = parseInt(document.getElementById("valor1").value) || 0,
        b = parseInt(document.getElementById("total").value) || 0;
        document.getElementById("Pagar").value = a + b ;
    } catch (e) {}
}