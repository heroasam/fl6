from fpdf import FPDF 
from lib import pgdict0, pgddict, per, desnull,pglflat

def ficha(con, ldni):
    pdf=FPDF()
    pdf.set_margins(30,10)
    pdf.add_page()
    pdf.set_font("Helvetica","",10)
    lpg ='('
    for dni in ldni:
        lpg+=dni+','
    lpg = lpg[0:-1]+')'
    listdni = pglflat(con,f"select dni from clientes where dni::numeric in {lpg} order by calle,num")

    for dni in listdni:
        #regla para que no comience un encabezado con poco espacio
        if (pdf.get_y()>250):
            pdf.add_page()
            pdf.set_y(15)
        cliente = pgdict0(con,f"select * from clientes where dni='{dni}'")
        pdf.set_font_size(12)
        pdf.cell(100,6,cliente['nombre'][0:38],0,0)
        pdf.set_font_size(10)
        pdf.cell(30,6,desnull(cliente['tel'][0:8]),1,0,'C')
        pdf.cell(30,6,desnull(cliente['wapp']),1,1,'C')
        pdf.cell(80,6,cliente['calle'],1,0)
        pdf.cell(10,6,cliente['num'][0:4],1,0)
        pdf.cell(70,6,cliente['barrio'],1,1)
        if cliente['acla']:
            pdf.set_font_size(7)
            pdf.cell(0,4,cliente['acla'],0,1)
        if cliente['mjecobr']:
            pdf.set_font_size(7)
            pdf.cell(0,4,cliente['mjecobr'],0,1)
        if cliente['horario']:
            pdf.set_font_size(7)
            pdf.cell(0,4,cliente['horario'],0,1)
        if len(cliente['num'])>4:
            pdf.set_font_size(7)
            pdf.cell(0,4,f"En numero se registra lo siguiente:{cliente['num']}",0,1) 
        if len(cliente['tel'])>8:
            pdf.set_font_size(7)
            pdf.cell(0,4,f"En telefono se registra lo siguiente:{cliente['tel']}",0,1)       
        pdf.ln(2)

        ventas=pgddict(con,f"select * from ventas where saldo>0 and idcliente={cliente['id']}")
        for venta in ventas:
            pdf.set_font_size(10)
            pdf.cell(15,6,f"{venta['id']}",1,0,'C')
            pdf.cell(25,6,f"{venta['fecha']}",1,0,'C')
            pdf.cell(50,6,f"{venta['cc']} cuotas de ${venta['ic']} {per(venta['p'])}",1,0,'C')
            pdf.cell(35,6,f"Saldo ${venta['saldo']}",1,1,'C')
            detvtas=pgddict(con,f"select * from detvta where idvta={venta['id']}")
            for detvta in detvtas:
                pdf.set_font_size(8)
                pdf.cell(10,4,f"{detvta['cnt']}",1,0,'C')
                pdf.cell(80,4,f"{detvta['art']}",1,0)
                pdf.cell(35,4,f"{detvta['cc']} cuotas de ${detvta['ic']}",1,1,'C')
            cur =con.cursor()
            cur.execute(f"select gc({venta['id']})")
            cur.close()
            cuotas = pgddict(con, f"select * from cuotas where debe>0 and idvta={venta['id']}")
            pagadas = pgddict(con, f"select * from pagos where idvta={venta['id']} order by fecha")
            # Calculo el largo total que tendra la grilla de pagos
            if (len(cuotas)>len(pagadas)):
                max=len(cuotas)
            else:
                max=len(pagadas)
            # Formula para el calculo del espacio ocupable
            if ((pdf.get_y()+max*7)>280):
                pdf.add_page()
                pdf.set_y(15)

            pdf.ln(2)
            pdf.set_font_size(10)
            y0 = pdf.get_y()
            pdf.cell(80,6,"Cuotas a Pagar",0,1)
            pdf.set_font_size(8)
            for cuota in cuotas:
                pdf.cell(5,4,f"{cuota['nc']}",1,0,'C')
                pdf.cell(25,4,f"{cuota['vto']}",1,0,'C')
                pdf.cell(15,4,f"${cuota['debe']}",1,1,'C')
            pdf.ln(2)    
            y1=pdf.get_y()
            pgy1 = pdf.page_no()
            pdf.set_y(y0)
            pdf.set_x(90)
            pdf.set_font_size(10)
            pdf.cell(80,6,"Cuotas Pagadas",0,1)
            pdf.set_font_size(8)
            for pagada in pagadas:
                pdf.set_x(90)
                pdf.cell(25,4,f"{pagada['fecha']}",1,0,'C')
                pdf.cell(20,4,f"${pagada['imp']}",1,0,'C')
                pdf.cell(15,4,f"${pagada['rec']}",1,0,'C')
                pdf.cell(20,4,f"{pagada['rbo']}",1,0,'C')
                pdf.cell(10,4,f"{pagada['cobr']}",1,1,'C')
            if (y1>pdf.get_y() and pgy1==pdf.page_no()):
                pdf.set_y(y1)
            if (y1<pdf.get_y() and pgy1<pdf.page_no()):
                pdf.set_y(pdf.get_y())
            pdf.set_x(30)
            pdf.ln(10)
            pdf.line(10,pdf.get_y()-5,200,pdf.get_y()-5)
            
    pdf.output("ficha.pdf")
