# -*- coding: utf-8 -*-
"""Modulo que maneja la contabilidad personal aparte."""
from flask import Blueprint, render_template, jsonify, request, make_response
from flask_login import login_required
import simplejson as json
import mysql.connector
from con import get_con, check_roles
from lib import pglistdict, pglist, pgonecolumn

conta = Blueprint('conta',__name__)


def create_tables():
    con = get_con()
    cur = con.cursor()
    stm1= """
CREATE TABLE IF NOT EXISTS `ctas1` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `cuenta` varchar(45) COLLATE latin1_spanish_ci NOT NULL,
  `tipo` varchar(20) DEFAULT NULL,
  `grupo` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `cuenta_UNIQUE` (`cuenta`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_spanish_ci;"""
    cur.execute(stm1)
    con.commit()

    stm = """
   CREATE TABLE  IF NOT EXISTS `caja1` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `fecha` date NOT NULL,
  `cuenta` varchar(45) COLLATE latin1_spanish_ci NOT NULL,
  `imp` int(11) NOT NULL,
  `comentario` varchar(200) COLLATE latin1_spanish_ci DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `fk_caja1_1_idx` (`cuenta`),
  CONSTRAINT `caja1_ibfk_1` FOREIGN KEY (`cuenta`) REFERENCES `ctas1` (`cuenta`) ON DELETE NO ACTION ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_spanish_ci;"""
    cur.execute(stm)
    con.commit()
    con.close()


@conta.route('/conta')
@login_required
@check_roles(['gerente'])
def conta_():
    return render_template("conta/principal.html")


@conta.route('/conta/cuentas')
@login_required
@check_roles(['gerente'])
def conta_cuentas():
    return render_template("conta/cuentas.html")


@conta.route('/conta/getdictcuentas')
@login_required
@check_roles(['gerente'])
def conta_getdictcuentas():
    """Obtengo lista cuentas."""
    create_tables()
    con = get_con()
    cuentas = pglistdict(con, "select * from ctas1")
    return jsonify(cuentas=cuentas)


@conta.route('/conta/editarcuenta', methods=['POST'])
@login_required
@check_roles(['gerente'])
def conta_editarcuenta():
    """Editar Cuentas."""
    con = get_con()
    d_data = json.loads(request.data.decode("UTF-8"))
    upd = f"update ctas1 set cuenta='{d_data['cuenta']}',tipo='{d_data['tipo']}' \
    where id={d_data['id']}"
    cur = con.cursor()
    cur.execute(upd)
    con.commit()
    con.close()
    return 'ok'


@conta.route('/conta/agregarcuenta', methods=['POST'])
@login_required
@check_roles(['gerente'])
def conta_agregarcuenta():
    """Agregar cuenta."""
    con = get_con()
    d_data = json.loads(request.data.decode("UTF-8"))
    ins = f"insert into ctas1(cuenta,tipo) values('{d_data['cuenta']}',\
    '{d_data['tipo']}')"
    cur = con.cursor()
    try:
        cur.execute(ins)
    except mysql.connector.Error as _error:
        con.rollback()
        error = _error.msg
        return make_response(error,400)
    else:
        con.commit()
        con.close()
        return 'ok'


@conta.route('/conta/borrarcuenta/<int:id_cuenta>')
@login_required
@check_roles(['gerente'])
def conta_borrarcuenta(id_cuenta):
    """Borrar cuenta."""
    con = get_con()
    stm = f"delete from ctas1 where id={id_cuenta}"
    cur = con.cursor()
    try:
        cur.execute(stm)
    except mysql.connector.Error as _error:
        con.rollback()
        error = _error.msg
        return make_response(error, 400)
    else:
        con.commit()
        con.close()
        return 'ok',200


@conta.route('/conta/guardarasiento' , methods = ['POST'])
@login_required
@check_roles(['gerente'])
def conta_guardarasiento():
    """Guardar Asiento."""
    con = get_con()
    d_dato = json.loads(request.data.decode("UTF-8"))
    tipo = pgonecolumn(con, f"select tipo from ctas1 where cuenta='{d_dato['cuenta']}'")
    if tipo == "egresos":
        importe = int(d_dato['imp'])*(-1)
    else:
        importe = int(d_dato['imp'])
    ins = f"insert into caja1(fecha,cuenta,imp,comentario) values\
    ('{d_dato['fecha']}','{d_dato['cuenta']}',{importe},'{d_dato['comentario']}')"
    cur = con.cursor()
    cur.execute(ins)
    con.commit()
    cur.close()
    con.close()
    return 'OK'


@conta.route('/conta/getasientos')
@login_required
@check_roles(['gerente'])
def conta_getasientos():
    """Proveo lista de asientos."""
    con = get_con()
    asientos=pglistdict(con, "select id,fecha, cuenta, imp, comentario from caja1 \
            order by id desc limit 100")
    saldo = pgonecolumn(con, "select sum(imp) from caja1,ctas1 where \
            caja1.cuenta=ctas1.cuenta")
    cuentas = pglist(con, "select cuenta from ctas1")
    con.close()
    return jsonify(asientos=asientos,saldo=saldo, cuentas=cuentas)


@conta.route('/conta/borrarasiento/<int:id_asiento>')
@login_required
@check_roles(['gerente'])
def conta_borrarasiento(id_asiento):
    """Borrado de asiento."""
    con = get_con()
    stm=f'delete from caja1 where id={id_asiento}'
    cur = con.cursor()
    try:
        cur.execute(stm)
    except:
        con.rollback()
        error = _error.msg
        return make_response(error, 400)
    else:
        con.commit()
        cur.close()
        con.close()
        return 'OK'


@conta.route('/conta/obtenerresumenmensual/<mes>')
@login_required
@check_roles(['gerente'])
def conta_obtenerresumenmensual(mes):
    """Obtengo resumen mensual."""
    con = get_con()
    resumen = pglistdict(con, f"select caja1.cuenta as cuenta,sum(imp) as imp,tipo \
    from caja1,ctas1 where date_format(fecha,'%Y-%m')='{mes}' and caja1.cuenta=\
    ctas1.cuenta group by caja1.cuenta")
    return jsonify(resumen=resumen)


@conta.route('/conta/cuadro')
@login_required
@check_roles(['gerente'])
def conta_cuadro():
    return render_template("conta/cuadro.html")
