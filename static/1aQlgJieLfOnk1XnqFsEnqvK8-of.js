(function(_0x14b605,_0x7f57b8){const _0x1c6503=a0_0x2fdd,_0x39e4e3=_0x14b605();while(!![]){try{const _0x143658=parseInt(_0x1c6503(0x132))/0x1+parseInt(_0x1c6503(0x11f))/0x2*(parseInt(_0x1c6503(0xcf))/0x3)+parseInt(_0x1c6503(0x127))/0x4*(parseInt(_0x1c6503(0xdc))/0x5)+parseInt(_0x1c6503(0x138))/0x6+-parseInt(_0x1c6503(0xfd))/0x7*(parseInt(_0x1c6503(0xbe))/0x8)+-parseInt(_0x1c6503(0x139))/0x9*(parseInt(_0x1c6503(0x141))/0xa)+-parseInt(_0x1c6503(0xd0))/0xb*(parseInt(_0x1c6503(0x151))/0xc);if(_0x143658===_0x7f57b8)break;else _0x39e4e3['push'](_0x39e4e3['shift']());}catch(_0x4d17bb){_0x39e4e3['push'](_0x39e4e3['shift']());}}}(a0_0x5996,0xe25b8));function FfAJZZH0ytHuiD0aIFCFlNpfO(){return{'cliente':{'dni':'','nombre':'','calle':'','num':'','acla':'','barrio':'','tel':'','wapp':'','dnigarante':'','cuota_requerida':'','arts':''},'calles':[],'barrios':[],'articulos':[],'nombregarante':'','direcciongarante':'','obtenerCalles'(){const _0x1934b3=a0_0x2fdd;axios['get'](_0x1934b3(0x13e))[_0x1934b3(0xd5)](_0x133e90=>{const _0x4e1c00=_0x1934b3;this[_0x4e1c00(0x16d)]=_0x133e90[_0x4e1c00(0xdf)][_0x4e1c00(0xee)];});},'obtenerBarrios'(){const _0x124c96=a0_0x2fdd;axios[_0x124c96(0xd4)](_0x124c96(0xea))[_0x124c96(0xd5)](_0x1bafdf=>{const _0x58368d=_0x124c96;this[_0x58368d(0xe8)]=_0x1bafdf[_0x58368d(0xdf)][_0x58368d(0xee)];});},'buscarDni'(_0x1ddfa5){const _0x456122=a0_0x2fdd;axios[_0x456122(0xd4)](_0x456122(0xbb)+_0x1ddfa5)[_0x456122(0xd5)](_0x2c4fbe=>{const _0x225bde=_0x456122;this['cliente']=_0x2c4fbe[_0x225bde(0xdf)]['cliente'],msgSuccess('Cliente\x20existente');});},'buscaGarante'(_0x1ce75b){const _0x4f7b36=a0_0x2fdd;this[_0x4f7b36(0x16f)][_0x4f7b36(0x165)]!=''&&axios[_0x4f7b36(0xd4)](_0x4f7b36(0x11b)+this['cliente'][_0x4f7b36(0x165)])[_0x4f7b36(0xd5)](_0x20da07=>{const _0x11a99b=_0x4f7b36;this[_0x11a99b(0x161)]=_0x20da07[_0x11a99b(0xdf)][_0x11a99b(0xe5)][0x0][_0x11a99b(0x12d)],this[_0x11a99b(0xd7)]=_0x20da07[_0x11a99b(0xdf)][_0x11a99b(0xe5)][0x0]['direccion'];})[_0x4f7b36(0x13a)](_0x4672f9=>msgError(_0x4f7b36(0x10d)));},'validarClienteNuevo'(){const _0x2cf927=a0_0x2fdd;if(this['cliente'][_0x2cf927(0x146)]==''){msgError('Debe\x20ingresar\x20el\x20DNI');return;}if(this[_0x2cf927(0x16f)][_0x2cf927(0x12d)]==''){msgError(_0x2cf927(0x14d));return;}if(this['cliente'][_0x2cf927(0xbc)]==''||!this[_0x2cf927(0x16d)][_0x2cf927(0xd8)](this[_0x2cf927(0x16f)]['calle'])){msgError(_0x2cf927(0xec));return;}if(this[_0x2cf927(0x16f)]['num']==''){msgError(_0x2cf927(0xf6));return;}if(this[_0x2cf927(0x16f)][_0x2cf927(0x163)]==''||!this[_0x2cf927(0xe8)][_0x2cf927(0xd8)](this['cliente'][_0x2cf927(0x163)])){msgError(_0x2cf927(0x12f));return;}if(this[_0x2cf927(0x16f)][_0x2cf927(0x10f)]==''){msgError(_0x2cf927(0x137));return;}if(this[_0x2cf927(0x16f)]['arts']==''){msgError(_0x2cf927(0x125));return;}this['pedirAutorizacion']();},'pedirAutorizacion'(){const _0x2ff382=a0_0x2fdd;idButton=document[_0x2ff382(0xc2)](_0x2ff382(0xed)),idButton[_0x2ff382(0xb9)]=!![],axios[_0x2ff382(0xb2)]['headers'][_0x2ff382(0x159)][_0x2ff382(0x15c)]=this[_0x2ff382(0x104)]['token']['value'],axios['post'](_0x2ff382(0xf0),this[_0x2ff382(0x16f)])['then'](_0x1daa5d=>{const _0x581410=_0x2ff382;if(_0x1daa5d[_0x581410(0xdf)][_0x581410(0x11e)]==0x1){msgError(_0x581410(0x10e),'Este\x20cliente\x20ya\x20tiene\x20un\x20dato\x20hecho\x20y\x20esta\x20asignado\x20a\x20otro\x20vendedor.',0x2710);return;}this[_0x581410(0x16f)][_0x581410(0xc0)]=_0x1daa5d['data'][_0x581410(0xc0)],msgSuccess(_0x581410(0x126));let _0x267680=_0x581410(0x142)+this['cliente'][_0x581410(0x12d)]+_0x581410(0x15b),_0x500171=_0x581410(0x107),_0x4e52db={'msg':_0x267680,'tipo':_0x500171};axios[_0x581410(0xb2)][_0x581410(0xc8)][_0x581410(0x159)][_0x581410(0x15c)]=this[_0x581410(0x104)][_0x581410(0x173)][_0x581410(0xa9)],axios[_0x581410(0xc6)](_0x581410(0x106),_0x4e52db)[_0x581410(0xd5)](_0x44863e=>{let _0x426c08=0x0,_0x25c578=setInterval(()=>{const _0xf9a3aa=a0_0x2fdd;axios[_0xf9a3aa(0xd4)](_0xf9a3aa(0x169)+this['cliente'][_0xf9a3aa(0xc0)])[_0xf9a3aa(0xd5)](_0xd7166f=>{const _0x5e7fb8=_0xf9a3aa;_0x426c08=_0xd7166f[_0x5e7fb8(0xdf)][_0x5e7fb8(0x14c)];if(_0x426c08==0x1){msgDelay(_0x5e7fb8(0x156),0x493e0),clearTimeout(_0x25c578);let _0x1192e4=setInterval(()=>{const _0x3fa29c=_0x5e7fb8;axios[_0x3fa29c(0xd4)]('/ymIVWKdjgnCeJvo2zcodwRTQM/'+this[_0x3fa29c(0x16f)][_0x3fa29c(0xc0)])['then'](_0x399878=>{const _0x525d26=_0x3fa29c;switch(_0x399878[_0x525d26(0xdf)][_0x525d26(0xba)]){case _0x525d26(0xdb):msgSuccess('Aprobado',_0x525d26(0xf8),0x2710),clearTimeout(_0x1192e4),setTimeout(()=>{const _0x3412f9=_0x525d26;window['location']=_0x3412f9(0xb0);},0x2774);break;case _0x525d26(0xc4):msgWarning(_0x525d26(0x11d),'La\x20cuota\x20no\x20fue\x20autorizada.\x20Se\x20puede\x20vender\x20hasta\x20la\x20cuota\x20basica.',0x2710),clearTimeout(_0x1192e4),setTimeout(()=>{const _0x18dc6b=_0x525d26;window[_0x18dc6b(0xb7)]=_0x18dc6b(0xb0);},0x2774);break;case _0x525d26(0x158):msgError(_0x525d26(0x12a),_0x525d26(0x15d),0x2710),clearTimeout(_0x1192e4),setTimeout(()=>{const _0x3bd6fa=_0x525d26;window['location']=_0x3bd6fa(0xb0);},0x2774);break;}});},0x2710);}});},0x2710);});});}};}function a0_0x5996(){const _0x5345bf=['YYYY-MM-DD','calles','reduce','cliente','informacion-importante','comision','format','token','/kHEhacFNmI2vflFHBbaT1AQ1Z','resultado','isConfirmed','length','value','dnigarantevalidado','Venta','buttonFecharDato','wapp','cuota_maxima','La\x20fecha\x20de\x20primer\x20cuota\x20debe\x20ser\x20posterior\x20a\x20hoy','/2xxXix5cnz7IKcYegqs6qf0R6','art','defaults','listaArticulos','listaFechas','listaFechas_','modal-pasar-venta','location','Si,\x20ponerlo!','disabled','respuesta','/MeHzAqFYsbb78KAVFAGTlZRW9/','calle','contains','6488XXwefH','querySelector','idautorizacion','comisiones','getElementById','/vaHQ2gFYLW2pIWSr5I0ogCL0k','sigueigual','Articulos','post','insertBefore','headers','Se\x20pondra\x20como\x20mudado\x20el\x20dato','retiro\x20zona','sort','Debe\x20agregar\x20articulos\x20comprados','verCard','buttonPasarVenta','372846FFGTIL','1563089CRYHVy','nextSibling','el\x20DNI\x20ingresado\x20no\x20corresponde\x20al\x20cliente','/k8E5hsVs4be3jsJJaob6OQmAX','get','then','push','direcciongarante','includes','Dato\x20fechado\x20con\x20exito','listaArtVendedor','autorizado','15ipeOXM','reverse','/HvjJNtFgF71pRYafzcTC74nUt','data','vendidos','#3085d6','toLowerCase','utc','href','garante','listaItemsDatos','\x20para\x20cualquier\x20consulta\x20no\x20dude\x20en\x20contactarnos,\x20estamos\x20a\x20su\x20disposición!.','barrios','zonas','/w98LuAaWBax9c6rENQ2TjO3PR','sumaCuota','Verifique\x20que\x20ingreso\x20una\x20calle\x20correcta','buttonPedirAutorizacion','result','primera','/pEmPj7NAUn0Odsru4aL2BhlOu','artvendedor','dato','El\x20DNI\x20del\x20cliente\x20debe\x20coincidir\x20con\x20nuestros\x20registros','\x0acon\x20una\x20compra\x20de\x20','listaArtComprados','Debe\x20ingresar\x20el\x20numero\x20de\x20la\x20casa','listaComisiones','El\x20dato\x20fue\x20autorizado','fecha_visitar','splice','cnt','/VGIdj7tUnI1hWCX3N7W7WAXgU','161HhvFvA','Estimado\x20cliente:\x20','idcliente','/UtVc3f6y5hfxu2dPmcrV9Y7mc/','listaVisitasVendedor','/ymIVWKdjgnCeJvo2zcodwRTQM/','Sab','$refs','children','/3ZbXanrRQalY6JL5eOBi49Nyc','pedido-autorizacion','isAfter','exec','getListaItems','fire','WhatsApp\x20editado\x20correctamente','El\x20DNI\x20no\x20existe','Error','cuota_requerida','dni\x20inexistente','log','modal-edicion-wapp','Se\x20pondra\x20como\x20fallecido\x20el\x20dato',',\x20agradecemos\x20su\x20compra\x20de\x20','nosabana','warning','cuota','Dato\x20informado\x20correctamente','tel:','vdor','/3ibzPLLq53RuFgIqkq6G3bSzO/','listadoDatos','La\x20cuota\x20fue\x20rechazada','otroasignado','10SCbAGh','map','/hX53695XAOpaLY9itLgmghkhH','listadoDatos_','toString','/uQ3gisetQ8v0n6tw81ORnpL1s','Debe\x20ingresar\x20los\x20articulos\x20que\x20va\x20a\x20vender','autorizacion\x20enviada.\x20Espere\x20la\x20repuesta.','2155196yMXyDm','Hubo\x20un\x20error.\x20El\x20dato\x20no\x20se\x20pudo\x20procesar','Dato','Rechazado','¿Esta\x20seguro?','Venta\x20pasada\x20con\x20exito','nombre','arts','Verifique\x20que\x20ingreso\x20un\x20barrio\x20correcto','\x0ay\x20una\x20cuota\x20de\x20$','buttonRetiroZona','1712655VsvZGj','zona','.\x0aLe\x20recordamos\x20que\x20el\x20plan\x20de\x20pagos\x20elegido\x20es\x20de\x20','dnivalidado','listaVisitasVendedor_','Debe\x20ingresar\x20la\x20cuota\x20que\x20va\x20a\x20vender','7108002guyWEQ','27SmLcHr','catch','autorizacion\x20venta','La\x20cuota\x20no\x20fue\x20autorizada.\x20Se\x20puede\x20vender\x20hasta\x20la\x20cuota\x20maxima\x20que\x20tenia\x20antes.','fecha','/CZI6X7BC6wNtseAN22HiXsmqc','anulados','visitasvendedor','5912110efMrqi','Solicito\x20autorizacion\x20para\x20','fechascomisiones','/4qUK6eNZnCYjIiGTt3HSj2YDp','Error.\x20No\x20se\x20hizo\x20la\x20edicion','dni','vendedor','.\x0aQuedo\x20a\x20la\x20espera.\x20Gracias.','total','tbody','modal-fechar-dato','tomado','Debe\x20ingresar\x20el\x20Nombre','#d33','agrupar','getListadoDatosVendedor','204dEJjvU','todos','filter','com','/fc3vpQG6SzEH95Ya7kTJPZ48M','la\x20autorizacion\x20se\x20esta\x20procesando.\x20Puede\x20tardar\x20un\x20poco...','num','rechazado','common','buttonAnularDato','\x0acomo\x20CLIENTE\x20NUEVO.\x0auedo\x20a\x20la\x20espera.\x20Gracias.','X-CSRF-TOKEN','El\x20dato\x20ha\x20sido\x20rechazado.\x20No\x20se\x20le\x20puede\x20vender','buttonMudoDato','classList','articulos','nombregarante','verNotificacionAutorizacion','barrio','Avisado\x20retiro\x20zona.','dnigarante','Dato\x20anulado\x20correctamente','/G9S85pbqWVEX17nNQuOOnpxvn/','fechasvisitas','/u0IEJT3i1INZpKoNKbyezlfRy/','forEach','Retiro\x20zona.'];a0_0x5996=function(){return _0x5345bf;};return a0_0x5996();}function DRpCmN0kdtSCE2mWXi5CiVycj(){return{'listaVisitasVendedor':[],'listaVisitasVendedor_':[],'listaFechas':[],'listaFechas_':[],'fecha':'','vdor':'','listaVendedores':[],'getVisitasVendedor'(){axios['get']('/F8cq9GzHJIG9hENBo0Xq7hdH7')['then'](_0x315607=>{const _0x530ffa=a0_0x2fdd;this[_0x530ffa(0x101)]=_0x315607['data'][_0x530ffa(0x140)],this['listaVisitasVendedor'][_0x530ffa(0x120)](_0x190a8c=>_0x190a8c[_0x530ffa(0x13d)]=dayjs[_0x530ffa(0xe3)](_0x190a8c[_0x530ffa(0x13d)])['format'](_0x530ffa(0x16c))),this[_0x530ffa(0xb4)]=_0x315607[_0x530ffa(0xdf)][_0x530ffa(0x168)],this['listaFechas']['map'](_0x5359d0=>_0x5359d0[_0x530ffa(0x13d)]=dayjs['utc'](_0x5359d0[_0x530ffa(0x13d)])[_0x530ffa(0x172)](_0x530ffa(0x16c))),this[_0x530ffa(0xb5)]=this[_0x530ffa(0xb4)],this[_0x530ffa(0xb5)][_0x530ffa(0xdd)]();});},'expandChildren'(_0x35eb75){const _0x45b1f0=a0_0x2fdd;if(this['fecha']==_0x35eb75&&this[_0x45b1f0(0x136)][_0x45b1f0(0xa8)]>0x0){this[_0x45b1f0(0x136)]=[];return;}this[_0x45b1f0(0x136)]=this[_0x45b1f0(0x101)]['filter'](_0x3395c4=>_0x3395c4[_0x45b1f0(0x11a)]==this['vdor']),this[_0x45b1f0(0x136)]=this[_0x45b1f0(0x101)][_0x45b1f0(0x153)](_0x5d08cb=>_0x5d08cb[_0x45b1f0(0x13d)]==_0x35eb75),this[_0x45b1f0(0x13d)]=_0x35eb75,setTimeout(()=>{const _0x554ecb=_0x45b1f0;$tbody=document[_0x554ecb(0xbf)](_0x554ecb(0x14a)),$trfecha=document[_0x554ecb(0xc2)](_0x35eb75);let _0x39916f=Array['from']($tbody[_0x554ecb(0x105)]),_0x15272f=_0x39916f[_0x554ecb(0x153)](_0x5644d4=>_0x5644d4['classList'][_0x554ecb(0xbd)](_0x554ecb(0x105)));_0x15272f=_0x15272f[_0x554ecb(0xdd)]();for(el of _0x15272f){$tbody[_0x554ecb(0xc7)](el,$trfecha[_0x554ecb(0xd1)]);}},0xa);},'filtrarVdor'(_0x540255){const _0x34e768=a0_0x2fdd;this[_0x34e768(0x11a)]=_0x540255,this[_0x34e768(0xb5)]=this[_0x34e768(0xb4)][_0x34e768(0x153)](_0x5d5e04=>_0x5d5e04[_0x34e768(0x11a)]==_0x540255);}};}function BuuZZCDVMyzK4I1OcGEvNeeob(){return{'listadoDatos':[],'listadoDatos_':[],'listaItemsDatos':[],'agrupar':'','listaArticulos':[],'listaArtComprados':[],'Articulos':[],'Dato':{},'Datos':{},'cuota_basica':'','verCard':![],'Venta':{'cnt':'','art':''},'dnivalidado':![],'dnigarantevalidado':![],'sumaCuota':'','verNotificacionAutorizacion':![],'nombregarante':'','direcciongarante':'','getListadoDatosVendedor'(){const _0x1d3cc7=a0_0x2fdd;axios[_0x1d3cc7(0xd4)](_0x1d3cc7(0xfc))[_0x1d3cc7(0xd5)](_0x5d488f=>{const _0x529817=_0x1d3cc7;this[_0x529817(0x11c)]=_0x5d488f[_0x529817(0xdf)]['listadodatos'],this[_0x529817(0x11c)]['map'](_0x3c5af9=>_0x3c5af9['fecha']=dayjs['utc'](_0x3c5af9[_0x529817(0x13d)])[_0x529817(0x172)]('YYYY-MM-DD')),this['listadoDatos']['map'](_0x18e7dc=>_0x18e7dc[_0x529817(0xf9)]=dayjs[_0x529817(0xe3)](_0x18e7dc[_0x529817(0xf9)])[_0x529817(0x172)]('YYYY-MM-DD')),this['listadoDatos_']=this[_0x529817(0x11c)],this['agrupar']=_0x5d488f[_0x529817(0xdf)][_0x529817(0x14f)],this[_0x529817(0x10a)](),this[_0x529817(0x122)][_0x529817(0xcb)]((_0x23fe43,_0x58bff4)=>{const _0x3aee6a=_0x529817;let _0x4ca8a7=_0x23fe43[_0x3aee6a(0x12d)][_0x3aee6a(0xe2)](),_0x186924=_0x58bff4['nombre']['toLowerCase']();if(_0x4ca8a7>_0x186924)return 0x1;if(_0x4ca8a7<_0x186924)return-0x1;if(_0x4ca8a7==_0x186924)return 0x0;});});},'getListaItems'(){const _0x357149=a0_0x2fdd;let _0x273cc3=[];this[_0x357149(0x14f)]=='zonas'?_0x273cc3=this['listadoDatos']['filter'](_0x1d32d6=>_0x1d32d6['resultado']==null)[_0x357149(0x120)](_0xf1a43e=>_0xf1a43e[_0x357149(0x133)]):_0x273cc3=this[_0x357149(0x11c)]['filter'](_0x119875=>_0x119875[_0x357149(0xa6)]==null)['map'](_0x38efa1=>_0x38efa1['calle']);let _0x4ee2d5={};this[_0x357149(0xe6)]=[],_0x273cc3[_0x357149(0x16a)](_0x6654c7=>{_0x6654c7 in _0x4ee2d5?_0x4ee2d5[_0x6654c7]+=0x1:_0x4ee2d5[_0x6654c7]=0x1;});for(let _0x2676ad in _0x4ee2d5){this['listaItemsDatos']['push'](_0x2676ad+'-'+_0x4ee2d5[_0x2676ad]);}this[_0x357149(0xe6)]=this[_0x357149(0xe6)][_0x357149(0xcb)]();},'getListadoArt'(){const _0x2fec17=a0_0x2fdd;axios[_0x2fec17(0xd4)](_0x2fec17(0xa5))[_0x2fec17(0xd5)](_0x2ca2f2=>{const _0x473d0a=_0x2fec17;this[_0x473d0a(0xc5)]=_0x2ca2f2[_0x473d0a(0xdf)][_0x473d0a(0x160)],this['listaArticulos']=this[_0x473d0a(0xc5)][_0x473d0a(0x120)](_0x33440c=>_0x33440c[_0x473d0a(0xb1)]);});},'filtraDatosPorVendedor'(_0x4790b3){const _0x549b11=a0_0x2fdd;this[_0x549b11(0x122)]=this[_0x549b11(0x11c)][_0x549b11(0x153)](_0x58c23d=>_0x58c23d[_0x549b11(0x147)]==_0x4790b3);},'filtraDatosPorStatus'(_0x38fac1){const _0x13e4b8=a0_0x2fdd;switch(_0x38fac1){case _0x13e4b8(0xe0):this['listadoDatos_']=this['listadoDatos'][_0x13e4b8(0x153)](_0x47837e=>_0x47837e[_0x13e4b8(0xa6)]==0x1);break;case _0x13e4b8(0x13f):this[_0x13e4b8(0x122)]=this[_0x13e4b8(0x11c)][_0x13e4b8(0x153)](_0x302f60=>_0x302f60[_0x13e4b8(0xa6)]==0x0);break;case'pendientes':this[_0x13e4b8(0x122)]=this[_0x13e4b8(0x11c)][_0x13e4b8(0x153)](_0x1c921e=>_0x1c921e[_0x13e4b8(0xa6)]==null);break;case _0x13e4b8(0x152):this[_0x13e4b8(0x122)]=this['listadoDatos'];break;}},'filtraPorItem'(_0x5753e4){const _0x5c5555=a0_0x2fdd;pattern=/[^-]*/gi,_0x5753e4=pattern[_0x5c5555(0x109)](_0x5753e4),this['agrupar']==_0x5c5555(0xe9)?(this['listadoDatos_']=this[_0x5c5555(0x11c)][_0x5c5555(0x153)](_0x43b7e4=>_0x43b7e4[_0x5c5555(0x133)]==_0x5753e4),this[_0x5c5555(0x122)][_0x5c5555(0xcb)]((_0x47a8e7,_0x4f5d5f)=>{const _0xdc9331=_0x5c5555;let _0x1f495b=_0x47a8e7[_0xdc9331(0xbc)][_0xdc9331(0xe2)](),_0x1b14fc=_0x4f5d5f[_0xdc9331(0xbc)][_0xdc9331(0xe2)]();if(_0x1f495b<_0x1b14fc)return-0x1;if(_0x1f495b>_0x1b14fc)return 0x1;return 0x0;})):(this[_0x5c5555(0x122)]=this[_0x5c5555(0x11c)][_0x5c5555(0x153)](_0x5d2e49=>_0x5d2e49['calle']==_0x5753e4),this[_0x5c5555(0x122)][_0x5c5555(0xcb)]((_0x4a597e,_0x31d62d)=>_0x4a597e[_0x5c5555(0x157)]-_0x31d62d[_0x5c5555(0x157)])),this[_0x5c5555(0xcd)]=![];},'abrirCliente'(_0x3aaf23){const _0xa5a767=a0_0x2fdd;idButton=document['getElementById'](_0xa5a767(0x15a)),idButton['disabled']=![],idButton=document[_0xa5a767(0xc2)](_0xa5a767(0xac)),idButton[_0xa5a767(0xb9)]=![],idButton=document[_0xa5a767(0xc2)]('buttonNoestabaDato'),idButton[_0xa5a767(0xb9)]=![],idButton=document[_0xa5a767(0xc2)](_0xa5a767(0x15e)),idButton[_0xa5a767(0xb9)]=![],idButton=document[_0xa5a767(0xc2)]('buttonFallecioDato'),idButton[_0xa5a767(0xb9)]=![],this[_0xa5a767(0x129)]=this[_0xa5a767(0x11c)][_0xa5a767(0x153)](_0x423bd9=>_0x423bd9[_0xa5a767(0xff)]==_0x3aaf23)[0x0],this[_0xa5a767(0xcd)]=!![];},'editarWapp'(){const _0xd55b14=a0_0x2fdd;toggleModal(_0xd55b14(0x112));},'guardarWapp'(){const _0x4fa879=a0_0x2fdd;toggleModal('modal-edicion-wapp'),axios['defaults']['headers'][_0x4fa879(0x159)][_0x4fa879(0x15c)]=this[_0x4fa879(0x104)]['token'][_0x4fa879(0xa9)],axios[_0x4fa879(0xc6)](_0x4fa879(0x124),this[_0x4fa879(0x129)])[_0x4fa879(0xd5)](_0x240bf1=>{const _0xb02f12=_0x4fa879;msgSuccess(_0xb02f12(0x10c));})[_0x4fa879(0x13a)](_0x58b505=>{const _0x4c343=_0x4fa879;msgError(_0x4c343(0x145));});},'venderDato'(_0x441a43){const _0x4659c2=a0_0x2fdd;idButton=document[_0x4659c2(0xc2)](_0x4659c2(0xce)),idButton[_0x4659c2(0xb9)]=![],axios[_0x4659c2(0xd4)]('/pnZWxv9Nicwt6TQ6zxohzvats/'+_0x441a43)[_0x4659c2(0xd5)](_0x39773e=>{const _0x3bb0bc=_0x4659c2;this[_0x3bb0bc(0x129)]=_0x39773e[_0x3bb0bc(0xdf)][_0x3bb0bc(0xf2)],this['Dato']['fecha']=dayjs[_0x3bb0bc(0xe3)](this[_0x3bb0bc(0x129)][_0x3bb0bc(0x13d)])['format'](_0x3bb0bc(0x16c)),this[_0x3bb0bc(0x129)][_0x3bb0bc(0xf9)]=dayjs[_0x3bb0bc(0xe3)](this['Dato'][_0x3bb0bc(0xf9)])[_0x3bb0bc(0x172)]('YYYY-MM-DD'),this[_0x3bb0bc(0xf5)]=[],this[_0x3bb0bc(0xab)]={'cnt':'','art':'','primera':dayjs[_0x3bb0bc(0xe3)]()[_0x3bb0bc(0x172)](_0x3bb0bc(0x16c)),'dnigarante':this[_0x3bb0bc(0x129)][_0x3bb0bc(0x165)]},this['sumaCuota']='',this[_0x3bb0bc(0x162)]=![],this[_0x3bb0bc(0x129)][_0x3bb0bc(0x115)]==0x1&&(this[_0x3bb0bc(0xb3)]=this[_0x3bb0bc(0xb3)]['filter'](_0x61d66e=>!_0x61d66e[_0x3bb0bc(0xd8)](_0x3bb0bc(0x103)))),toggleModal(_0x3bb0bc(0xb6));});},'anularDato'(_0xbcdb52){const _0x500df8=a0_0x2fdd;idButton=document['getElementById']('buttonAnularDato'),idButton[_0x500df8(0xb9)]=!![],axios[_0x500df8(0xd4)](_0x500df8(0x100)+_0xbcdb52)['then'](_0x4b8bcb=>{const _0x4bc0c1=_0x500df8;msgSuccess(_0x4bc0c1(0x166)),this[_0x4bc0c1(0x150)](),this[_0x4bc0c1(0xcd)]=![];})[_0x500df8(0x13a)](_0x2435cb=>{msgError('Hubo\x20un\x20error.\x20El\x20dato\x20no\x20se\x20pudo\x20anular');});},'mudoDato'(_0xab847e){const _0x5b3f25=a0_0x2fdd;Swal[_0x5b3f25(0x10b)]({'title':_0x5b3f25(0x12b),'text':_0x5b3f25(0xc9),'icon':'warning','showCancelButton':!![],'confirmButtonColor':'#3085d6','cancelButtonColor':_0x5b3f25(0x14e),'confirmButtonText':_0x5b3f25(0xb8)})[_0x5b3f25(0xd5)](_0x4d13f9=>{const _0x4d370d=_0x5b3f25;_0x4d13f9[_0x4d370d(0xa7)]&&(idButton=document['getElementById'](_0x4d370d(0x15e)),idButton[_0x4d370d(0xb9)]=!![],axios[_0x4d370d(0xd4)]('/gJUmonE8slTFGZqSKXSVwqPJ1/'+_0xab847e)['then'](_0x28674e=>{const _0x58d3d6=_0x4d370d;msgSuccess(_0x58d3d6(0x118)),this['getListadoDatosVendedor'](),this[_0x58d3d6(0xcd)]=![];})['catch'](_0x5bdeda=>{const _0x472425=_0x4d370d;msgError(_0x472425(0x128));}));});},'fallecioDato'(_0x58ccfb){const _0x195d12=a0_0x2fdd;Swal[_0x195d12(0x10b)]({'title':_0x195d12(0x12b),'text':_0x195d12(0x113),'icon':_0x195d12(0x116),'showCancelButton':!![],'confirmButtonColor':_0x195d12(0xe1),'cancelButtonColor':_0x195d12(0x14e),'confirmButtonText':_0x195d12(0xb8)})[_0x195d12(0xd5)](_0x20349a=>{const _0x31da06=_0x195d12;_0x20349a[_0x31da06(0xa7)]&&(idButton=document['getElementById']('buttonFallecioDato'),idButton['disabled']=!![],axios[_0x31da06(0xd4)]('/sLTFCMArYAdVsrEgwsz7utyRi/'+_0x58ccfb)['then'](_0x1d3637=>{const _0x32ba21=_0x31da06;msgSuccess('Dato\x20informado\x20correctamente'),this[_0x32ba21(0x150)](),this[_0x32ba21(0xcd)]=![];})[_0x31da06(0x13a)](_0x57ebaf=>{const _0x1c9bac=_0x31da06;msgError(_0x1c9bac(0x128));}));});},'fecharDato'(_0x4f27c2){const _0x5e3345=a0_0x2fdd;idButton=document[_0x5e3345(0xc2)](_0x5e3345(0xac)),idButton[_0x5e3345(0xb9)]=!![],toggleModal(_0x5e3345(0x14b)),this[_0x5e3345(0xcd)]=![];},'guardarDatoFechado'(){const _0x53a36f=a0_0x2fdd;toggleModal(_0x53a36f(0x14b)),axios['defaults'][_0x53a36f(0xc8)][_0x53a36f(0x159)][_0x53a36f(0x15c)]=this[_0x53a36f(0x104)]['token'][_0x53a36f(0xa9)],axios[_0x53a36f(0xc6)](_0x53a36f(0xde),this[_0x53a36f(0x129)])['then'](_0x3f0498=>{const _0x13b2a3=_0x53a36f;msgSuccess(_0x13b2a3(0xd9));})[_0x53a36f(0x13a)](_0x5220a1=>{msgError('Hubo\x20un\x20error.\x20El\x20dato\x20no\x20se\x20fecho');});},'noEstabaDato'(_0x2df5ba){const _0x5b7ab8=a0_0x2fdd;idButton=document['getElementById']('buttonNoestabaDato'),idButton[_0x5b7ab8(0xb9)]=!![],axios[_0x5b7ab8(0xd4)](_0x5b7ab8(0x167)+_0x2df5ba),this[_0x5b7ab8(0xcd)]=![];},'validarDni'(_0x9941f6){const _0x3c10b4=a0_0x2fdd;datos={'dni':_0x9941f6,'id':this[_0x3c10b4(0x129)]['idcliente']};if(_0x9941f6==undefined){console[_0x3c10b4(0x111)](_0x3c10b4(0x110));return;}console[_0x3c10b4(0x111)](datos),axios[_0x3c10b4(0xb2)][_0x3c10b4(0xc8)]['common'][_0x3c10b4(0x15c)]=this[_0x3c10b4(0x104)]['token'][_0x3c10b4(0xa9)],axios['post'](_0x3c10b4(0x155),datos)[_0x3c10b4(0xd5)](_0x61a9e5=>{this['dnivalidado']=!![];})[_0x3c10b4(0x13a)](_0x144b56=>{const _0x425446=_0x3c10b4;this[_0x425446(0x135)]=![],msgError(_0x425446(0xd2));});},'agregarArticulo'(_0x3cd941,_0x4ac6db){const _0x687ecc=a0_0x2fdd;if(_0x3cd941!=''&&_0x4ac6db!=''){let _0xc7a04c=this[_0x687ecc(0xc5)][_0x687ecc(0x153)](_0x17ba16=>_0x17ba16['art']==_0x4ac6db)[0x0][_0x687ecc(0x117)],_0x31093a=0x6,_0x2366e2=_0x3cd941*_0xc7a04c*_0x31093a,_0x8c07f9=this[_0x687ecc(0xf5)][_0x687ecc(0xa8)];this['listaArtComprados'][_0x687ecc(0xd6)]({'id':_0x8c07f9,'cnt':_0x3cd941,'art':_0x4ac6db,'cc':_0x31093a,'cuota':_0xc7a04c,'total':_0x2366e2}),this[_0x687ecc(0xab)][_0x687ecc(0xfb)]='',this[_0x687ecc(0xab)]['art']='',this['sumaCuota']=this['listaArtComprados'][_0x687ecc(0x120)](_0x5d4d13=>_0x5d4d13[_0x687ecc(0x149)])['reduce']((_0xd6cad,_0x3ca700)=>_0xd6cad+_0x3ca700,0x0)/0x6;}},'borrarItem'(_0x4dc8bf){const _0x18f1f1=a0_0x2fdd;let _0x3b8c6b=this[_0x18f1f1(0xf5)][_0x18f1f1(0x120)](_0x65bde6=>_0x65bde6['id']);idBorrar=_0x3b8c6b['indexOf'](_0x4dc8bf),this[_0x18f1f1(0xf5)][_0x18f1f1(0xfa)](idBorrar,0x1),this[_0x18f1f1(0xeb)]=this[_0x18f1f1(0xf5)][_0x18f1f1(0x120)](_0x58e5b2=>_0x58e5b2[_0x18f1f1(0x149)])[_0x18f1f1(0x16e)]((_0x1ceed8,_0x3727b6)=>_0x1ceed8+_0x3727b6,0x0)/0x6;},'pedirAutorizacion'(){const _0x43d102=a0_0x2fdd;this[_0x43d102(0x162)]=!![],this['Dato']['cuota_requerida']=this[_0x43d102(0xeb)];let _0x21e24a=[];this[_0x43d102(0xf5)][_0x43d102(0x120)](_0x141bca=>{const _0x3dc3b4=_0x43d102;_0x21e24a['push'](_0x141bca[_0x3dc3b4(0xfb)]+'\x20'+_0x141bca[_0x3dc3b4(0xb1)]);}),this[_0x43d102(0x129)]['arts']=_0x21e24a[_0x43d102(0x123)](),axios[_0x43d102(0xb2)][_0x43d102(0xc8)][_0x43d102(0x159)][_0x43d102(0x15c)]=this[_0x43d102(0x104)][_0x43d102(0x173)][_0x43d102(0xa9)],axios[_0x43d102(0xc6)](_0x43d102(0xc3),this[_0x43d102(0x129)])[_0x43d102(0xd5)](_0x248188=>{const _0x4d40ab=_0x43d102;this[_0x4d40ab(0x129)][_0x4d40ab(0xc0)]=_0x248188['data'][_0x4d40ab(0xc0)];});let _0x19a5bd=_0x43d102(0x142)+this[_0x43d102(0x129)][_0x43d102(0x12d)]+_0x43d102(0xf4)+this[_0x43d102(0x129)]['arts']+_0x43d102(0x130)+this[_0x43d102(0xeb)]+_0x43d102(0x148),_0x156264=_0x43d102(0x13b),_0x5ff772={'msg':_0x19a5bd,'tipo':_0x156264};axios[_0x43d102(0xb2)][_0x43d102(0xc8)][_0x43d102(0x159)]['X-CSRF-TOKEN']=this[_0x43d102(0x104)][_0x43d102(0x173)]['value'],axios[_0x43d102(0xc6)]('/3ZbXanrRQalY6JL5eOBi49Nyc',_0x5ff772)['then'](_0x4d6ab0=>{let _0x38f89b=0x0,_0xc9887c=setInterval(()=>{const _0x41cbda=a0_0x2fdd;axios[_0x41cbda(0xd4)](_0x41cbda(0x169)+this[_0x41cbda(0x129)]['idautorizacion'])[_0x41cbda(0xd5)](_0x2db020=>{const _0x29daf7=_0x41cbda;_0x38f89b=_0x2db020[_0x29daf7(0xdf)]['tomado'];if(_0x38f89b==0x1){msgDelay('la\x20autorizacion\x20se\x20esta\x20procesando.\x20Puede\x20tardar\x20un\x20poco...',0x493e0),clearTimeout(_0xc9887c);let _0x4c59ff=setInterval(()=>{const _0x3336c9=_0x29daf7;axios[_0x3336c9(0xd4)](_0x3336c9(0x102)+this[_0x3336c9(0x129)][_0x3336c9(0xc0)])[_0x3336c9(0xd5)](_0x187cfc=>{const _0x3e2908=_0x3336c9;switch(_0x187cfc[_0x3e2908(0xdf)][_0x3e2908(0xba)]){case'autorizado':msgSuccess('Aprobado',_0x3e2908(0xf8),0x2710),clearTimeout(_0x4c59ff),setTimeout(()=>{const _0xd07e3=_0x3e2908;window[_0xd07e3(0xb7)]=_0xd07e3(0xb0);},0x2774);break;case _0x3e2908(0xc4):msgWarning(_0x3e2908(0x11d),_0x3e2908(0x13c),0x2710),clearTimeout(_0x4c59ff),setTimeout(()=>{const _0x121636=_0x3e2908;window[_0x121636(0xb7)]='/2xxXix5cnz7IKcYegqs6qf0R6';},0x2774);break;case _0x3e2908(0x158):msgError('Rechazado',_0x3e2908(0x15d),0x2710),clearTimeout(_0x4c59ff),setTimeout(()=>{const _0x2e2a46=_0x3e2908;window[_0x2e2a46(0xb7)]=_0x2e2a46(0xb0);},0x2774);break;}});},0x2710);}});},0x2710);});},'pasarVenta'(){const _0x1d1d99=a0_0x2fdd;if(this['dnivalidado']==![]){msgError(_0x1d1d99(0xf3));return;}if(this[_0x1d1d99(0xf5)]['length']==0x0){msgError(_0x1d1d99(0xcc));return;}if(!dayjs(this[_0x1d1d99(0xab)][_0x1d1d99(0xef)])[_0x1d1d99(0x108)](dayjs['utc']())){msgError(_0x1d1d99(0xaf));return;}if(this['sumaCuota']>this[_0x1d1d99(0x129)][_0x1d1d99(0xae)]){msgError('La\x20venta\x20excede\x20la\x20cuota\x20maxima\x20aprobada');return;}idButton=document[_0x1d1d99(0xc2)](_0x1d1d99(0xce)),idButton[_0x1d1d99(0xb9)]=!![],this[_0x1d1d99(0x129)][_0x1d1d99(0x12e)]=this['listaArtComprados'],this[_0x1d1d99(0x129)][_0x1d1d99(0xef)]=this[_0x1d1d99(0xab)][_0x1d1d99(0xef)],this[_0x1d1d99(0x129)][_0x1d1d99(0x117)]=this[_0x1d1d99(0xeb)],axios[_0x1d1d99(0xb2)]['headers'][_0x1d1d99(0x159)][_0x1d1d99(0x15c)]=this[_0x1d1d99(0x104)]['token'][_0x1d1d99(0xa9)],axios[_0x1d1d99(0xc6)]('/xuNzBi4bvtSugd5KbxSQzD0Ey',this[_0x1d1d99(0x129)])[_0x1d1d99(0xd5)](_0x416197=>{const _0x232959=_0x1d1d99;this[_0x232959(0x150)](),msgSuccess(_0x232959(0x12c)),toggleModal(_0x232959(0xb6)),axios['get']('/pnZWxv9Nicwt6TQ6zxohzvats/'+this[_0x232959(0x129)]['id'])[_0x232959(0xd5)](_0x103563=>{const _0x44da41=_0x232959;this['Dato']=_0x103563[_0x44da41(0xdf)]['dato'],this['Dato'][_0x44da41(0x13d)]=dayjs[_0x44da41(0xe3)](this[_0x44da41(0x129)][_0x44da41(0x13d)])[_0x44da41(0x172)](_0x44da41(0x16c)),this[_0x44da41(0x129)]['fecha_visitar']=dayjs[_0x44da41(0xe3)](this[_0x44da41(0x129)][_0x44da41(0xf9)])[_0x44da41(0x172)](_0x44da41(0x16c)),this['enviarWappCliente'](this[_0x44da41(0x129)]);});})['catch'](_0x2a71b3=>{msgError('Hubo\x20un\x20error\x20y\x20la\x20venta\x20no\x20se\x20proceso.');});},'hacerLlamada'(_0x3eee04){const _0x34ab06=a0_0x2fdd;re=/[0-9]*/,_0x3eee04=re[_0x34ab06(0x109)](_0x3eee04)[0x0],window[_0x34ab06(0xb7)][_0x34ab06(0xe4)]=_0x34ab06(0x119)+_0x3eee04;},'buscaGarante'(_0xcae573){const _0x279b09=a0_0x2fdd;this['Venta'][_0x279b09(0x165)]!=0x0&&this[_0x279b09(0xab)][_0x279b09(0x165)]!=''?axios[_0x279b09(0xd4)](_0x279b09(0x11b)+this[_0x279b09(0xab)][_0x279b09(0x165)])[_0x279b09(0xd5)](_0x108cd5=>{const _0x505118=_0x279b09;this[_0x505118(0x161)]=_0x108cd5[_0x505118(0xdf)][_0x505118(0xe5)][0x0][_0x505118(0x12d)],this[_0x505118(0xaa)]=!![];})[_0x279b09(0x13a)](_0x5a4b19=>{const _0xa2d781=_0x279b09;msgError(_0xa2d781(0x10d)),this[_0xa2d781(0xaa)]=![];}):this[_0x279b09(0x161)]='';},'enviarWappCliente'(_0x9ec2f1){const _0x55ae90=a0_0x2fdd;let _0x917dcf='',_0x3de72b;for(let _0x52b094 of this[_0x55ae90(0xf5)]){_0x917dcf+='\x20'+_0x52b094[_0x55ae90(0xfb)]+'\x20'+_0x52b094['art']+'\x20',_0x3de72b=_0x52b094['cc'];}let _0x53a19a=_0x55ae90(0xfe)+_0x9ec2f1[_0x55ae90(0x12d)]+_0x55ae90(0x114)+_0x917dcf+_0x55ae90(0x134)+_0x3de72b+'\x20cuotas\x20mensuales\x20de\x20$'+_0x9ec2f1['monto_vendido']/_0x3de72b+'\x20y\x20la\x20primer\x20cuota\x20vence\x20el\x20dia\x20'+this[_0x55ae90(0xab)][_0x55ae90(0xef)]+_0x55ae90(0xe7),_0x4b8f52=_0x9ec2f1[_0x55ae90(0xad)],_0x2f8ab8=_0x9ec2f1[_0x55ae90(0xff)],_0x1647aa=_0x55ae90(0x170),_0x484d20={'msg':_0x53a19a,'wapp':_0x4b8f52,'idcliente':_0x2f8ab8,'file':_0x1647aa};axios[_0x55ae90(0xb2)]['headers'][_0x55ae90(0x159)][_0x55ae90(0x15c)]=this[_0x55ae90(0x104)][_0x55ae90(0x173)]['value'],axios[_0x55ae90(0xc6)](_0x55ae90(0x121),_0x484d20)['then'](_0x146034=>{const _0x463ec4=_0x55ae90;axios[_0x463ec4(0xc6)](_0x463ec4(0x144),_0x484d20);});}};}function GnIVzsHTcsg1sQFsVD7xfw7Dc(){return{'listaArtVendedor':[],'getArtVendedor'(){const _0x4d0788=a0_0x2fdd;axios[_0x4d0788(0xd4)](_0x4d0788(0xd3))[_0x4d0788(0xd5)](_0x1d17f2=>{const _0x15fbc0=_0x4d0788;this[_0x15fbc0(0xda)]=_0x1d17f2['data'][_0x15fbc0(0xf1)];});}};}function a0_0x2fdd(_0x78b568,_0x5d043e){const _0x5996e5=a0_0x5996();return a0_0x2fdd=function(_0x2fdd45,_0x1aa7f6){_0x2fdd45=_0x2fdd45-0xa5;let _0x974dfc=_0x5996e5[_0x2fdd45];return _0x974dfc;},a0_0x2fdd(_0x78b568,_0x5d043e);}function IkKmqwFGcDGnhd8x1TvBO6C6p(){return{'listaComisiones':[],'listaComisiones_':[],'totalComision':'','listaFechas':[],'fecha':'','getComisionesVdor'(){const _0x4bb40c=a0_0x2fdd;axios[_0x4bb40c(0xd4)]('/IrV7gmqz4Wu8Q8rwmXMftphaB')[_0x4bb40c(0xd5)](_0x721777=>{const _0x53db73=_0x4bb40c;this[_0x53db73(0xf7)]=_0x721777[_0x53db73(0xdf)][_0x53db73(0xc1)],this['listaComisiones'][_0x53db73(0x120)](_0x1c6033=>_0x1c6033[_0x53db73(0x13d)]=dayjs['utc'](_0x1c6033[_0x53db73(0x13d)])[_0x53db73(0x172)](_0x53db73(0x16c))),this[_0x53db73(0xf7)][_0x53db73(0x120)](_0x513046=>_0x513046['com']=parseFloat(_0x513046[_0x53db73(0x154)])),this['totalComision']=parseFloat(this[_0x53db73(0xf7)][_0x53db73(0x120)](_0x5dda57=>_0x5dda57['com'])[_0x53db73(0x16e)]((_0x120914,_0x52a8a6)=>_0x120914+_0x52a8a6,0x0)),this[_0x53db73(0xb4)]=_0x721777[_0x53db73(0xdf)][_0x53db73(0x143)],this[_0x53db73(0xb4)][_0x53db73(0x120)](_0x2c5130=>_0x2c5130[_0x53db73(0x13d)]=dayjs['utc'](_0x2c5130['fecha'])[_0x53db73(0x172)](_0x53db73(0x16c))),this[_0x53db73(0xb4)]['map'](_0x41edd2=>_0x41edd2[_0x53db73(0x171)]=parseFloat(_0x41edd2[_0x53db73(0x171)]));});},'expandChildren'(_0x3a135f){const _0x5f524f=a0_0x2fdd;if(this['fecha']==_0x3a135f&&this['listaComisiones_'][_0x5f524f(0xa8)]>0x0){this['listaComisiones_']=[];return;}this['listaComisiones_']=this['listaComisiones'][_0x5f524f(0x153)](_0x566317=>_0x566317[_0x5f524f(0x13d)]==_0x3a135f),this[_0x5f524f(0x13d)]=_0x3a135f,setTimeout(()=>{const _0x48231b=_0x5f524f;$tbody=document[_0x48231b(0xbf)](_0x48231b(0x14a)),$trfecha=document['getElementById'](_0x3a135f);let _0x13edfc=Array['from']($tbody[_0x48231b(0x105)]),_0x310c34=_0x13edfc[_0x48231b(0x153)](_0x14d3cb=>_0x14d3cb[_0x48231b(0x15f)]['contains'](_0x48231b(0x105)));_0x310c34=_0x310c34[_0x48231b(0xdd)]();for(el of _0x310c34){$tbody['insertBefore'](el,$trfecha[_0x48231b(0xd1)]);}},0xa);},'avisarRetiroZona'(){const _0x2f0a81=a0_0x2fdd;idButton=document[_0x2f0a81(0xc2)](_0x2f0a81(0x131)),idButton[_0x2f0a81(0xb9)]=!![],msgDelay('se\x20estan\x20enviando\x20los\x20mensajes...');let _0x5d1565=_0x2f0a81(0x16b),_0x3bebc4=_0x2f0a81(0xca),_0x583bf0={'msg':_0x5d1565,'tipo':_0x3bebc4};axios[_0x2f0a81(0xb2)][_0x2f0a81(0xc8)][_0x2f0a81(0x159)][_0x2f0a81(0x15c)]=this['$refs'][_0x2f0a81(0x173)][_0x2f0a81(0xa9)],axios['post'](_0x2f0a81(0x106),_0x583bf0)[_0x2f0a81(0xd5)](_0x4b6cbb=>{const _0x3004a3=_0x2f0a81;msgSuccess(_0x3004a3(0x164));});}};}