<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <title>Panel de Finanzas</title>
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <style>
    :root {
      --verde: green;
      --rojo: red;
      --gris: #f4f4f4;
      --oscuro: #263238;
    }

    body {
      font-family: 'Segoe UI', sans-serif;
      background-color: var(--gris);
      margin: 0;
      padding: 0;
    }

    .container {
      max-width: 1000px;
      margin: 40px auto;
      background-color: white;
      padding: 30px;
      border-radius: 20px;
      box-shadow: 0 15px 25px rgba(0,0,0,0.1);
    }

    h1, h2 {
      color: var(--oscuro);
      text-align: center;
    }

    .input-group {
      margin-bottom: 20px;
    }

    label {
      font-weight: bold;
      color: #555;
    }

    input, select {
      width: 100%;
      padding: 12px;
      margin-top: 5px;
      border: 1px solid #ccc;
      border-radius: 10px;
      font-size: 15px;
    }

    button {
      background: var(--verde);
      color: white;
      border: none;
      padding: 12px 25px;
      font-size: 15px;
      border-radius: 10px;
      cursor: pointer;
      transition: background 0.3s;
    }

    button:hover {
      background: green;
    }

    .acciones button {
      padding: 6px 15px;
      margin-right: 5px;
      font-size: 13px;
    }

    .acciones .eliminar {
      background: var(--rojo);
    }

    .acciones .eliminar:hover {
      background: red;
    }

    table {
      width: 100%;
      border-collapse: collapse;
      margin-top: 30px;
      font-size: 15px;
    }

    th, td {
      padding: 12px;
      border-bottom: 1px solid #ddd;
      text-align: left;
    }

    th {
      background-color: #eee;
    }

    #resumen {
      display: flex;
      justify-content: space-around;
      margin-top: 30px;
      text-align: center;
    }

    #resumen p {
      font-size: 18px;
      font-weight: bold;
      color: #333;
    }

    #grafico {
      margin-top: 30px;
    }

    @media (max-width: 768px) {
      #resumen {
        flex-direction: column;
        gap: 15px;
      }

      .acciones {
        display: flex;
        flex-direction: column;
      }

      .acciones button {
        margin-bottom: 5px;
      }
    }
  </style>
</head>
<body>
  <div class="container">
    <h1>💸 Panel de Finanzas</h1>

    <h2 id="form-title">Registrar Ingreso o Gasto</h2>
    <div class="input-group">
      <label for="tipo">Tipo</label>
      <select id="tipo">
        <option value="ingreso">Ingreso</option>
        <option value="gasto">Gasto</option>
      </select>
    </div>
    <div class="input-group">
      <label for="monto">Monto</label>
      <input type="number" id="monto" min="0.01" step="0.01">
    </div>
    <div class="input-group">
      <label for="descripcion">Descripción</label>
      <input type="text" id="descripcion">
    </div>
    <div class="input-group">
      <label for="fecha">Fecha</label>
      <input type="date" id="fecha">
    </div>
    <button onclick="guardarRegistro()" id="btn-guardar">Guardar registro</button>

    <h2>Resumen</h2>
    <div class="input-group">
      <label for="rango">Filtrar por</label>
      <select id="rango" onchange="mostrarResumen()">
        <option value="hoy">Hoy</option>
        <option value="7">Últimos 7 días</option>
        <option value="30">Últimos 30 días</option>
        <option value="todos">Todos</option>
      </select>
    </div>

    <div id="resumen">
      <p>Ingresos: $<span id="ingresos">0.00</span></p>
      <p>Gastos: $<span id="gastos">0.00</span></p>
      <p>Balance: $<span id="balance">0.00</span></p>
    </div>

    <div id="alerta-equilibrio" style="display:none; text-align:center; margin-top:20px; font-weight:bold; color:#00796b; background:#b2dfdb; padding:15px; border-radius:10px;">
  ⚖️ ¡Tus ingresos y gastos están equilibrados!
     </div>

    <table id="tabla">
      <thead>
        <tr><th>Tipo</th><th>Monto</th><th>Descripción</th><th>Fecha</th><th>Acciones</th></tr>
      </thead>
      <tbody></tbody>
    </table>

    <canvas id="grafico" height="100"></canvas>
  </div>

  <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
  <script>
    let editIndex = -1;

    function getRegistros() {
      return JSON.parse(localStorage.getItem("finanzas")) || [];
    }

    function guardarRegistros(data) {
      localStorage.setItem("finanzas", JSON.stringify(data));
    }

    function guardarRegistro() {
      const tipo = document.getElementById("tipo").value;
      const monto = parseFloat(document.getElementById("monto").value);
      const descripcion = document.getElementById("descripcion").value.trim();
      const fecha = document.getElementById("fecha").value;

      if (!descripcion || !fecha || isNaN(monto)) {
        alert("Completa todos los campos correctamente.");
        return;
      }

      let registros = getRegistros();

      if (editIndex >= 0) {
        registros[editIndex] = { tipo, monto, descripcion, fecha };
        editIndex = -1;
        document.getElementById("form-title").textContent = "Registrar Ingreso o Gasto";
        document.getElementById("btn-guardar").textContent = "Guardar registro";
      } else {
        registros.push({ tipo, monto, descripcion, fecha });
      }

      guardarRegistros(registros);
      limpiarFormulario();
      mostrarResumen();
    }

    function limpiarFormulario() {
      document.getElementById("tipo").value = "ingreso";
      document.getElementById("monto").value = "";
      document.getElementById("descripcion").value = "";
      document.getElementById("fecha").value = new Date().toISOString().split("T")[0];
    }

    function editarRegistro(index) {
      const registros = getRegistros();
      const r = registros[index];
      document.getElementById("tipo").value = r.tipo;
      document.getElementById("monto").value = r.monto;
      document.getElementById("descripcion").value = r.descripcion;
      document.getElementById("fecha").value = r.fecha;
      document.getElementById("form-title").textContent = "Editar Registro";
      document.getElementById("btn-guardar").textContent = "Guardar cambios";
      editIndex = index;
    }

    function eliminarRegistro(index) {
      if (!confirm("¿Estás seguro de eliminar este registro?")) return;
      let registros = getRegistros();
      registros.splice(index, 1);
      guardarRegistros(registros);
      mostrarResumen();
    }

    function mostrarResumen() {
      const rango = document.getElementById("rango").value;
      const hoy = new Date();
      let inicio;

      if (rango === "hoy") {
        inicio = new Date(hoy.toISOString().split("T")[0]);
      } else if (rango === "7" || rango === "30") {
        inicio = new Date();
        inicio.setDate(hoy.getDate() - parseInt(rango));
      } else {
        inicio = new Date("1970-01-01");
      }

      const registros = getRegistros();
      const filtrados = registros.filter(r => new Date(r.fecha) >= inicio);

      let ingresos = 0, gastos = 0;
      const tbody = document.querySelector("#tabla tbody");
      tbody.innerHTML = "";

      filtrados.forEach((r, i) => {
        if (r.tipo === "ingreso") ingresos += r.monto;
        else gastos += r.monto;

        const fila = `<tr>
          <td>${r.tipo}</td>
          <td>$${r.monto.toFixed(2)}</td>
          <td>${r.descripcion}</td>
          <td>${r.fecha}</td>
          <td class="acciones">
            <button onclick="editarRegistro(${i})">Editar</button>
            <button class="eliminar" onclick="eliminarRegistro(${i})">Eliminar</button>
          </td>
        </tr>`;
        tbody.innerHTML += fila;
      });

      document.getElementById("ingresos").textContent = ingresos.toFixed(2);
      document.getElementById("gastos").textContent = gastos.toFixed(2);
      document.getElementById("balance").textContent = (ingresos - gastos).toFixed(2);
      const alerta = document.getElementById("alerta-equilibrio");
        if (Math.abs(ingresos - gastos) < 0.01) {
        alerta.style.display = "block";
        } else {
        alerta.style.display = "none";
        }

      mostrarGrafico(ingresos, gastos);
    }

    function mostrarGrafico(ingresos, gastos) {
      const ctx = document.getElementById("grafico").getContext("2d");
      if (window.miGrafico) window.miGrafico.destroy();

      window.miGrafico = new Chart(ctx, {
        type: "bar",
        data: {
          labels: ["Ingresos", "Gastos"],
          datasets: [{
            label: "Resumen",
            data: [ingresos, gastos],
            backgroundColor: ["green", "red"]
          }]
        },
        options: {
          responsive: true,
          plugins: {
            legend: { display: false }
          }
        }
      });
    }

    window.onload = () => {
      document.getElementById("fecha").value = new Date().toISOString().split("T")[0];
      mostrarResumen();
    };
  </script>
</body>
</html>
