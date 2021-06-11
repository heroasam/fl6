from dateutil.relativedelta import relativedelta


def pgdict0(con, sel):
    """Funcion que entrega una lista de valores en formato lista plana
       o flat list entregado por el fetchall sobre un cursor"""
    cur = con.cursor()
    cur.execute(sel)
    rec = cur.fetchone()
    cur.close()
    return rec

def pgdict(con, sel):
    """Funcion que entrega una lista de valores en formato list of list
       entregado por el fetchall sobre un cursor"""
    cur = con.cursor()
    cur.execute(sel)
    rec = cur.fetchall()
    cur.close()
    return rec


def pgonecolumn(con, sel):
    """Funcion que entrega un solo valor como el onecolumn de sqlite
    en caso de que el select no de resultado, lo cual se expresaria en
    el cur.fetchone() = None damos por resultado "", sino damos [0] que
    es el primer elemento de la tupla que normalmente fetchone entrega
    obteniendo con eso un resultado flat para uso directo """
    cur = con.cursor()
    cur.execute(sel)
    res = cur.fetchone()
    if res is None:
        return ""
    else:
        return res[0]
    cur.close()
    return res


def pgddict(con, sel):
    """Funcion que entrega una lista de valores en formato list of list
       entregado por el fetchall sobre un cursor"""
    cur = con.cursor()
    cur.execute(sel)
    rec = cur.fetchall()
    cur.close()
    return rec


def pgllist(con, sel):
    cur = con.cursor()
    cur.execute(sel)
    res = cur.fetchall()
    cur.close()
    return res


def pglflat(con,sel):
    lista = pgllist(con,sel)
    flatlist = []
    for l in lista:
        flatlist.append(l[0])
    return flatlist


def listsql(lista):
    """formatea una lista para usar en un stm sqlite
    o sea del formato (a,b,c), en especial maneja el caso
    en que la lista de longitud 1, y entrega (a) """
    if len(lista)==1:
        sqllist='('+str(lista[0])+')'
    else:
        sqllist=str(tuple(lista))
    return sqllist


def strbuscar(search):
    list = ['%']
    if search is not None:
        searchlist = search.split()
    else:
        searchlist = []
    for s in searchlist:
        list.append(s)
        list.append('%')
    return "".join(list)


def per(periodicidad):
    """Devuelve la periodicidad en una cadena
    legible"""
    if periodicidad==1:
        return "MEN"
    elif periodicidad==3:
        return "SEM"
    else:
        return "QUIN"



def desnull(cadena):
    """filtro que elimina la cadena NULL"""
    if cadena=="NULL":
        return ""
    else:
        return cadena


# def pmovto(con,idvta):
#     ventas = pgdict0(con,f"select * from ventas where id={idvta}")
#     print(ventas)
#     print(ventas['id'])
#     pago = ventas['ent']+ventas['pagado'] if ventas['pp']==0 else ventas['ppagado']
#     icuota = ventas['ic'] if ventas['pp']==0 else ventas['pic']
#     period = ventas['p'] if ventas['pp']==0  else ventas['pper']
#     cntcuotas= ventas['cc'] if ventas['pp']==0  else ventas['pcc']
#     fechainic = ventas['primera'] if ventas['pp']==0 else ventas['pprimera']
#     enteras=round(pago/icuota)
#     if enteras==0:
#         return fechainic
#     #if {$saldo==0} {return {}} ;# este criterio de saldo cero deja pendiente el problema de los saldos negativos
#     # y la resolucion de pago>comprado no sirve para esto pq no contempla los planes de pago.
#     if ventas['saldo']<=0:
#         return ""
#         #aca decia return None y lo cambie or return ""
#     # o sea si esta cancela o por algun motivo tiene saldo negativo
#     #if {$pago>=$comprado} {return {}} ;# Es erroneo en los planes de pago pq el comprado es bajo y el pago supera antes de cancelar
#     if period==1:
#         return fechainic+relativedelta(months=enteras)
#     if period==3:
#         return fechainic+relativedelta(weeks=enteras)
#     if period==2:
#         return fechainic+relativedelta(weeks=enteras*2)


# def trigger_pago(con,idvta):
#     cur = con.cursor()
#     pp = pgonecolumn(con, f"select pp from ventas where id={idvta}")
#     if pp==0:
#         upd1 = f"update ventas set pagado=COALESCE((select sum(imp) from pagos where idvta={idvta}),0) where id={idvta}"
#     else:
#         upd1 = f"update ventas set ppagado=COALESCE((select sum(imp) from pagos where idvta={idvta} and fecha>=ventas.pfecha),0) where id={idvta}"
#     upd3 = f"update ventas set ultpago=COALESCE((select max(fecha) from pagos where idvta={idvta}),NULL) where id={idvta}"
#     cur.execute(upd1)
#     cur.execute(upd3)
#     con.commit()
#     # Saldo segun si es cuenta normal o PLAN DE PAGOS
#     pp = pgonecolumn(con, f"select pp from ventas where id={idvta}")
#     if pp==0:
#         upd4 = f"update ventas set saldo=comprado-ent-pagado where id={idvta}"
#     else:
#         upd4 = f"update ventas set saldo=(pic*pcc)-ppagado where id={idvta}"
#     cur.execute(upd4)
#     con.commit()
#     # fin sector saldo
#     fpmovto = pmovto(con, idvta)
#     if fpmovto is None:
#         upd5 = f"update ventas set pmovto=NULL where id={idvta}"
#     else:
#         upd5 = f"update ventas set pmovto='{fpmovto}' where id={idvta}"
#     cur.execute(upd5)
#     con.commit()
#     idcliente = pgonecolumn(con, f"select idcliente from ventas where id={idvta}")
#     upd6 = f"update pagos set idcliente={idcliente} where idvta={idvta}"
#     upd7 = f"update clientes set deuda=COALESCE((select sum(saldo) from ventas where idcliente={idcliente}),0) where id={idcliente}"
#     upd8 = f"update clientes set pmovto=COALESCE((select max(pmovto) from ventas where idcliente={idcliente} and devuelta=0),NULL) where id={idcliente}"
#     upd9 = f"update clientes set ultpago=COALESCE((select max(ultpago) from ventas where idcliente={idcliente} and devuelta=0),NULL) where id={idcliente}"
#     cur.execute(upd6)
#     cur.execute(upd7)
#     cur.execute(upd8)
#     cur.execute(upd9)
#     con.commit()
#     cur.close()


# def venta_trigger(con,idvta):
#     cur = con.cursor()
#     idcliente = pgonecolumn(con, f"select idcliente from ventas where id={idvta}")
#     pp = pgonecolumn(con, f"select pp from ventas where id={idvta}")
#     upd1 = f"update ventas set comprado=(ic*cc) where id={idvta}"
#     upd2 = f"update clientes set comprado=COALESCE((select sum(comprado) from ventas where idcliente={idcliente}),0) where id={idcliente}"
#     upd3 = f"update ventas set saldo=(ic*cc)-ent-pagado where id={idvta}"
#     upd4 = f"update clientes set deuda=COALESCE((select sum(saldo) from ventas where idcliente={idcliente}),0) where id={idcliente}"
#     fpmovto = pmovto(con,idvta)
#     upd5 = f"update ventas set pmovto='{fpmovto}' where id={idvta}"
#     upd6 = f"update clientes set pmovto=COALESCE((select min(pmovto) from ventas where idcliente={idcliente} and devuelta=0),NULL) where id={idcliente}"
#     upd7 = f"update ventas set ultpago=fecha where id={idvta}"
#     upd8 = f"update clientes set ultcompra=COALESCE((select max(fecha) from ventas where idcliente={idcliente} and devuelta=0),NULL) where id={idcliente}"
#     upd9 = f"update clientes set cuota=COALESCE((select sum(ic) from ventas where idcliente={idcliente} and saldo>0),0) where id={idcliente}"
#     cur.execute(upd1)
#     cur.execute(upd2)
#     cur.execute(upd3)
#     cur.execute(upd4)
#     cur.execute(upd5)
#     cur.execute(upd6)
#     cur.execute(upd7)
#     cur.execute(upd8)
#     cur.execute(upd9)
#     con.commit()
#     cur.close()

# def detvta_trigger(con,idvta):
#     cur = con.cursor()
#     upd1 = f"update ventas set cnt=(select sum(cnt) from detvta where idvta={idvta}) where id={idvta}"
#     upd2 = f"update ventas set costo=(select sum(costo) from detvta where idvta={idvta}) where id={idvta}"
#     cur.execute(upd1)
#     cur.execute(upd2)
#     con.commit()
#     cur.close()

# def venta_trigger_delete(con,idcliente):
#     cur = con.cursor()
#     upd1 = f"update clientes set comprado=COALESCE((select sum(comprado) from ventas where idcliente={idcliente}),0) where id={idcliente}"
#     upd2 = f"update clientes set deuda=COALESCE((select sum(saldo) from ventas where idcliente={idcliente}),0) where id={idcliente}"
#     upd3 = f"update clientes set pmovto=COALESCE((select min(pmovto) from ventas where idcliente={idcliente} and devuelta=0),NULL) where id={idcliente}"
#     upd4 = f"update clientes set ultcompra=COALESCE((select max(fecha) from ventas where idcliente={idcliente} and devuelta=0),NULL) where id={idcliente}"
#     upd5 = f"update clientes set cuota=COALESCE((select sum(ic) from ventas where idcliente={idcliente} and saldo>0),0) where id={idcliente}"
#     cur.execute(upd1)
#     cur.execute(upd2)
#     cur.execute(upd3)
#     cur.execute(upd4)
#     cur.execute(upd5)
#     con.commit()
#     cur.close()


def venta_trigger_condonada(con,idvta):
    cur = con.cursor()
    condonada = pgonecolumn(con, f"select condonada from ventas where id={idvta}")
    pp = pgonecolumn(con, f"select pp from ventas where id={idvta}")
    idcliente = pgonecolumn(con, f"select idcliente from ventas where id={idvta}")
    if condonada==1:
        upd1 = f"update ventas set saldo=0,pmovto=NULL where id={idvta}"
    else:
        fpmovto = pmovto(con, idvta)
        if pp==0:
            if fpmovto is None:
                upd1 = f"update ventas set saldo=(ic*cc)-ent-pagado,pmovto=NULL where id={idvta}"
            else:
                upd1 = f"update ventas set saldo=(ic*cc)-ent-pagado,pmovto='fpmovto' where id={idvta}"
        else:
            if fpmovto is None:
                upd1 = f"update ventas set saldo=(pic*pcc)-ppagado,pmovto=NULL where id={idvta}"
            else:
                upd1 = f"update ventas set saldo=(pic*pcc)-ppagado,pmovto='fpmovto' where id={idvta}"

    
    upd2 = f"update clientes set deuda=COALESCE((select sum(saldo) from ventas where idcliente={idcliente}),0) where id={idcliente}"
    upd3 = f"update clientes set pmovto=COALESCE((select min(pmovto) from ventas where idcliente={idcliente} and devuelta=0),NULL) where id={idcliente}"
    upd4 = f"update clientes set cuota=COALESCE((select sum(ic) from ventas where idcliente={idcliente} and saldo>0),0) where id={idcliente}"
    upd5 = f"delete from cuotas where idvta={idvta}"
    cur.execute(upd1)
    cur.execute(upd2)
    cur.execute(upd3)
    cur.execute(upd4)
    cur.execute(upd5)
    con.commit()
    cur.close()


def venta_trigger_devolucion(con,idvta):
    cur = con.cursor()
    idcliente = pgonecolumn(con, f"select idcliente from ventas where id={idvta}")
    upd1 = f"update ventas set saldo=0 where id={idvta}"
    upd2 = f"update clientes set comprado=COALESCE((select sum(comprado) from ventas where idcliente={idcliente}),0) where id={idcliente}"
    upd3 = f"update clientes set deuda=COALESCE((select sum(saldo) from ventas where idcliente={idcliente}),0) where id={idcliente}"
    upd4 = f"update clientes set pmovto=COALESCE((select min(pmovto) from ventas where idcliente={idcliente} and devuelta=0),NULL) where id={idcliente}"
    upd5 = f"update clientes set ultcompra=COALESCE((select max(fecha) from ventas where idcliente={idcliente} and devuelta=0),NULL) where id={idcliente}"
    upd6 = f"update clientes set cuota=COALESCE((select sum(ic) from ventas where idcliente={idcliente} and saldo>0),0) where id={idcliente}"
    upd7 = f"update detvta set devuelta=1 where idvta={idvta}"
    del1 = f"delete from cuotas where idvta={idvta}"
    cur.execute(upd1)
    cur.execute(upd2)
    cur.execute(upd3)
    cur.execute(upd4)
    cur.execute(upd5)
    cur.execute(upd6)
    cur.execute(upd7)
    cur.execute(del1)
    con.commit()
    cur.close()


def venta_trigger_anuladevolucion(con,idvta):
    cur = con.cursor()
    pp = pgonecolumn(con, f"select pp from ventas where id={idvta}")
    idcliente =  pgonecolumn(con, f"select idcliente from ventas where id={idvta}")
    del1 = f"delete from devoluciones where idvta={idvta}"
    del2 = f"delete from comentarios where comentario like '%DEVOLUCION%{idvta}%'"
    upd1 = f"update ventas set devuelta=0 where id={idvta}"
    upd2 = f"update ventas set comprado=(ic*cc) where id={idvta}"
    upd3 = f"update clientes set comprado=COALESCE((select sum(comprado) from ventas where idcliente={idcliente}),0) where id={idcliente}"
    if pp==0:
        upd4 = f"update ventas set saldo=(ic*cc)-ent-pagado where id={idvta}"
    else:
        upd4 = f"update ventas set saldo=(pic*pcc)-ppagado where id={idvta}"
    upd5 = f"update clientes set deuda=COALESCE((select sum(saldo) from ventas where idcliente={idcliente}),0) where id={idcliente}"
    fpmovto = pmovto(con, idvta)
    if fpmovto is None:
        upd6 = f"update ventas set pmovto=NULL  where id={idvta}"
    else:
        upd6 = f"update ventas set pmovto='fpmovto'  where id={idvta}"

    upd7 = f"update clientes set pmovto=COALESCE((select min(pmovto) from ventas where idcliente={idcliente} and devuelta=0),NULL) where id={idcliente}"
    upd8 = f"update ventas set ultpago=fecha where id={idvta}"
    upd9 = f"update clientes set ultcompra=COALESCE((select max(fecha) from ventas where idcliente={idcliente} and devuelta=0),NULL) where id={idcliente}"
    upd10 = f"update clientes set cuota=COALESCE((select sum(ic) from ventas where idcliente={idcliente} and saldo>0),0) where id={idcliente}"
    upd11 = f"update detvta set devuelta=0 where idvta={idvta}"
    cur.execute(del1)
    cur.execute(del2)
    cur.execute(upd1)
    cur.execute(upd2)
    cur.execute(upd3)
    cur.execute(upd4)
    cur.execute(upd5)
    cur.execute(upd6)
    cur.execute(upd7)
    cur.execute(upd8)
    cur.execute(upd9)
    cur.execute(upd10)
    cur.execute(upd11)
    con.commit()
    cur.close()