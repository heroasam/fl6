UPDATE caja
set conciliado = 0
WHERE cuenta = "bancos ingreso clientes"
    and conciliado = 2